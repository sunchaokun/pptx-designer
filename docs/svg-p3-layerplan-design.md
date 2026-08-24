# SVG P3：面向 pptx-designer 的 LayerPlan 与混合渲染设计

> **已调整的历史设计稿。** 原方案以“局部 PNG 与原生对象混合输出”为默认方向。经项目目标复核，P3 的默认原则现调整为“可编辑性优先，视觉保真可控降级”。后续开发应以 [SVG P3 可编辑性优先路线图](svg-p3-editability-first-roadmap.md) 为准；本文件保留，供未来确有高保真需求时参考其 LayerPlan 与 raster island 设计。

> 状态：设计评审稿；本阶段不直接改写 P3 生产渲染路径。
> 目标：在复杂 SVG 中保留尽可能多的可编辑 PPTX 对象，只有无法原生表达的局部区域才栅格化，并支持 build 代码按稳定对象键增量更新。

## 1. 决策结论

P3 不采用“SVG 编译失败就整张 PNG”的默认策略。它应产出一个按 SVG 原始 paint order 排列的 `LayerPlan`，再由 **pptx-designer 内部的 LayerPlanExecutor** 逐项写入 slide。整体 PNG 仅在 planner 无法证明局部拆分安全时使用。

```text
SVG → sanitize/CSS → SVG IR → capability/context analysis → LayerPlan
                                                          ↓
          pptx-designer LayerPlanExecutor: raster island / native SVG / editable text
                                                          ↓
                                                 PPTX + persisted map
```

这样用户修改标题、标签、数字或普通图形时，build 只替换具有稳定 key 的原生对象；局部 PNG 不会吞掉整页的可编辑性。

## 2. 已验证的工程边界

当前仓库中：

- `tools/svg.py::svg_chart()` 可把一段 SVG 编译为原生对象，但只能走现有整体 compiler；
- `tools/text.py::text()`、`tools/shapes.py`、`tools/images.py` 可被 build 逐项调用；`slide.shapes` 的追加顺序对应前后图层顺序；
- `SVGResult.source_to_output` 已可提供运行期来源映射，但保存的是对象引用，PPTX 重开后不可作为稳定定位依据；
- P2b IR 已有节点顺序、父子关系、样式物化后的属性和 feature 标记；
- `E:/PPT-Design-Skill` 是早期 skill，`build_helpers.py` 只能作为历史实现经验参考，不是本库依赖、运行时接口或代码落点；
- P3 的 planner、executor、映射和测试均放在 `pptx-designer` 内部。不得让当前标准库 import 或依赖早期 skill 文件。

特别注意：当前 `text()` 默认 `word_wrap=True`。P3 的 editable text 不应直接复用它的默认行为，而应使用专门的 `add_svg_text()` 执行器，继承 compiler 已修复的字号、测宽、anchor 与 opacity 语义。

## 3. LayerPlan 数据契约

`LayerPlan` 是可序列化 dataclass/JSON，而不是对 lxml/PPTX 对象的引用：

```json
{
  "version": 1,
  "canvas": {"viewBox": [0, 0, 1280, 720], "targetRectIn": [0, 0, 13.333, 7.5]},
  "operations": [
    {
      "z": 12,
      "key": "hero-title",
      "kind": "editable_text",
      "sourceIds": ["title"],
      "bbox": [80, 54, 640, 66],
      "style": {"fontFamily": "Arial", "fontSize": 42, "fill": "#102A43"}
    },
    {
      "z": 13,
      "key": "hero-glow",
      "kind": "raster_island",
      "sourceIds": ["glow-group"],
      "bbox": [440, 170, 360, 260],
      "reason": ["filter", "group_opacity"],
      "svgFragment": "…",
      "editable": false
    }
  ],
  "fallback": {"kind": "none"}
}
```

支持的 operation：

| kind | `LayerPlanExecutor` 动作 | 可编辑性 |
|---|---|---|
| `native_svg_fragment` | 调用 native compiler 渲染一个已证明安全的 SVG 子树 | 是 |
| `editable_text` | 调用 `add_svg_text()`，而非默认可换行的 `text()` | 是 |
| `raster_island` | 将局部 SVG 以确定性渲染器生成 PNG，再 `add_picture()` | 否 |
| `native_image` | 插入或链接原始图片；用户可替换资源 | 图片可替换 |
| `whole_slide_raster` | 最后兜底，生成一张全页 PNG | 否 |

每个 operation 必须有 `z`、`key`、`sourceIds`、`bbox`、`reason`、`editable`。不存在“未解释的 PNG”。

## 4. 稳定对象键与用户编辑契约

优先键：`data-pptx-key`；其次 SVG `id`；最后才是由 `tag + source-order + parent-key` 生成的稳定 hash。仅靠 `id` 不足，因为 LLM SVG 常没有 id 或会重复。

`LayerPlanExecutor` 应写入：

```text
shape.name = "svg:{key}"                 # 例如 svg:hero-title
shape.name = "svg:{key}::part:{n}"       # 一个源节点生成多个 PPTX 对象
```

同时写 `exports/<deck>.svgmap.json`：

```json
{"hero-title": {"kind": "editable_text", "shapeNames": ["svg:hero-title"], "sourceIds": ["title"]}}
```

首版使用 sidecar manifest，避免先引入自定义 OOXML part。后续如需 PPTX 单文件可携带性，再把同一 JSON 放入 custom XML part。

更新规则：同一 key 的 native 对象由 build 重新生成/替换；无 key 的对象视为不可增量更新。手工在 PowerPoint 中改过的内容不会自动反向同步回 SVG，除非未来单独实现 import/merge 工作流。

## 5. 可编辑资格与 raster island 规则

### 5.1 可直接原生化

节点满足以下条件才可成为 `native_svg_fragment` 或 `editable_text`：

- 节点及所有祖先没有 `filter`、`mask`、`group opacity`、blend mode 或 isolation；
- 未依赖 `pattern`、复杂 marker、外部资源或不支持的 `image` 语义；
- text 不使用 `textPath`、复杂 stroke、pattern/gradient text fill、不可解析字体或复杂 clip；
- 子树边界不跨越由 `clipPath`、mask 或 filter 建立的组合上下文；
- planner 能将其放回原始 `z` 序，且不与待 raster 子树发生不可分的互相遮挡。

普通 title、label、数值、箭头、矩形、路径和简单渐变图形通常可保留原生。

### 5.2 不可分的 raster island

以下情形必须把“效果宿主及所有参与组合的子节点”作为一个 island：

- `filter` 引用及其 filter region；
- `mask`、clip 与不支持的 mask/filter 链组合；
- `<g opacity>` 或 blend/isolation；
- pattern、marker、复杂 image 或外部资源；
- 文字被上述效果上下文影响。

核心不变量：**绝不从会影响组合结果的父组中单独抽取文字。** 例如发光标题、带透明组的标签，即使文字本身可编辑，也必须随 island rasterize；否则会有双重边缘、错误 alpha 或 z-order 错误。

### 5.3 拆分算法

1. IR 遍历时计算每个节点的 `effect_context`，包括自身和祖先；
2. 标记不支持特性时向上寻找最小的组合边界（通常是 effect 的 `<g>` 宿主）；
3. 合并相交或父子包含的边界，得到互不重叠的 islands；
4. 在 source order 中把 island 视为一个原子 operation，其外部兄弟继续逐项规划；
5. 若 island 与可编辑候选交错且无法由边界表达，升级为最近共同父节点 island；
6. 若根节点成为 island，使用 `whole_slide_raster` 并记录升级原因。

不允许通过“先渲完整 SVG 再在上面盖文本”的方式拆分。PNG 片段必须从只含该 island 的 SVG fragment 渲染，避免原始文字残留造成双绘制。

## 6. pptx-designer 执行协议

伪代码：

```python
plan = planner.plan(svg_text, target_rect)
for operation in sorted(plan.operations, key=lambda op: op.z):
    if operation.kind == "raster_island":
        shape = executor.add_raster_svg(operation.svg_fragment, operation.bbox)
    elif operation.kind == "editable_text":
        shape = executor.add_svg_text(operation.text_spec, operation.bbox)
    elif operation.kind == "native_svg_fragment":
        shapes = executor.add_native_svg(operation.svg_fragment, operation.bbox)
    elif operation.kind == "native_image":
        shape = executor.add_image(operation.asset, operation.bbox)
    executor.name_outputs(operation.key, shape or shapes)
executor.write_svg_map(plan)
```

执行器必须：

- 严格按 `z` 追加 shape；不得按 kind 批量重排；
- 在每项写入后检查 bbox 与预期是否相容；
- raster island 采用固定 DPI、固定 SVG renderer、固定背景/alpha 参数，便于 hash 与视觉回归；
- 单项失败时不保留半页产物：要么升级该 operation/最近边界，要么停止并返回 `RenderReport.errors`；
- `add_svg_text()` 关闭自动换行，使用 P2b 的文字测宽/字号换算实现。

## 7. 需要先补齐的 P3 前置能力

1. IR 特性检测：目前不仅要识别标签，还要识别 `filter="url(#…)"`、`mask`、`mix-blend-mode`、`isolation`、`clip-path`、`marker-*`、`pattern` 等属性引用；
2. IR 几何信息：每个节点需要 SVG-space bbox（保守 bbox 可先行），供 island 裁切、错误定位与 output map 使用；
3. defs 依赖闭包：fragment 必须包含其使用的 gradient、clip、symbol、filter、mask 等 defs；
4. 确定性 rasterizer：以一个独立 POC 选择并锁定实现，比较 SVG 1.1 支持、安全限制、Windows 部署和输出一致性；
5. shape naming/manifest helper：不能把 source-to-output 的内存对象引用直接当作可持久映射。

## 8. 分阶段实施与停止条件

| 阶段 | 交付 | 不做什么 | 进入下一阶段条件 |
|---|---|---|---|
| P3.0 | LayerPlan dataclass、JSON snapshot、能力/上下文分析 | 不写 PNG、不改变 compiler 输出 | 20+ SVG 的 planner snapshot 审查通过 |
| P3.1 | `LayerPlanExecutor.add_svg_text`、shape naming、sidecar map | 不拆复杂 effects | 修改文本只影响对应 named shape 的测试通过 |
| P3.2 | 单 island POC：一个 filter 或一个 group opacity island + 两个原生文本层 | 不做嵌套/交错岛 | z-order、无双绘制、视觉对比通过 |
| P3.3 | 多 island、defs 闭包、升级规则与全页兜底 | 不做区域最小化优化 | 复杂样本无 partial output、全部有 report reason |
| P3.4 | 性能、缓存、可编辑性统计和跨版本兼容测试 | 不扩展 SVG 特性 | 指标达到门槛后再考虑 P4 |

任一阶段出现“无法证明视觉等价”的拆分，必须提升 raster 边界，不能用猜测性 native 输出继续。

## 9. 验收样本与硬门禁

最少建立 24 个样本：

- 8 个纯原生图：文本、tspan、use、clip、渐变、路径；
- 6 个文本可编辑 + 局部特效背景图；
- 4 个 group opacity/filter/mask 边界图；
- 3 个 z-order 交错图；
- 3 个字体/CJK/长文本样本。

每个样本至少检查：

1. plan snapshot：island 范围、原因、`z` 与 key 正确；
2. PPTX structural：shape name、sidecar map、source key 映射、可编辑对象数量；
3. 修改测试：改一个 title/label 后，只允许其 key 的 native shape XML 改变，PNG hash 不变；
4. 视觉测试：原 SVG 与 PPTX→PDF/PNG 进行人工审阅和 SSIM/像素容差比较；
5. 失败测试：rasterizer 失败、未知 defs、超限输入、无法拆分时不得产生部分成功 PPTX。

建议初始门槛：安全拆分样本的 SSIM ≥ 0.95；可编辑文本覆盖率按文本节点计 ≥ 90%；每一个 raster island 与 whole-slide fallback 都必须有 machine-readable reason。

## 10. 当前建议

下一步不是直接开发 rasterizer，而是实施 P3.0：在 `pptx-designer` 内用现有 P2b IR 生成 LayerPlan snapshot，并用标准库的 build-mode API 验证“标题、标签、数字”的 key/map 契约。只有在 `LayerPlanExecutor` 的 shape naming、追加顺序和文本执行器验证完毕后，才进入一个受控的单 island POC。

## 附：历史 skill 的正确使用边界

`E:/PPT-Design-Skill/src/ppt_pro_max/build_helpers.py` 可用于理解早期 build 脚本如何逐项添加 shape、text 和 image，也可作为 API ergonomics 的参考；但它不是 P3 的代码来源。P3 的实现必须采用 `pptx_designer` 的包结构、依赖管理、测试套件和公开 API，避免标准库与 skill 发生循环依赖或版本漂移。
