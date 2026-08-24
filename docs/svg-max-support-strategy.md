# 复杂 SVG 最大化支持方案

> 目标：在保持 PPTX 可编辑性的同时，最大化支持复杂、特效丰富和 LLM 生成的 SVG。
>
> 前置资料：[`svg-module-analysis.md`](./svg-module-analysis.md)
>
> 状态：研究设计，暂不代表已实施。

## 1. 核心目标

复杂 SVG 支持不应被理解为“把所有 SVG 标签逐个翻译成 PowerPoint shape”。SVG 和 PPTX 的图形模型并不等价：SVG 可以使用滤镜、遮罩、混合模式、任意路径和 CSS；PPTX 原生图形更适合可编辑形状、文本和有限的渐变。

因此目标应分为三层：

```text
视觉一致性优先
        ↓
可编辑性优先的原生转换
        ↓
不可表达效果的局部降级或混合渲染
```

最终策略：

1. 能稳定表达为 PPTX 原生对象的部分，转换为可编辑 shape；
2. 能近似表达但不能完全等价的效果，进行可控降级；
3. 无法安全或稳定转换的局部区域，渲染为 SVG/PNG 图片；
4. 任意模式都必须产生可观测的能力报告、warning 和降级原因。

## 1.1 当前 baseline 与收益估算修正

本方案最初基于旧版源码设计；当前源码已经完成两项关键修复：

- `PrecisionRenderer` 直接从 `pptx_designer.compiler` 导入正式 `SVGCompiler`；
- `renderer/svg_compiler.py` 已变为兼容转发 shim，主流程会接收结果并记录 warning/error。

因此，当前主流程 SVG 成功率不能再按“接近 0%”估计。基于现有支持子集和内联样式静态 SVG 的能力，建议暂用以下工程估算，待 20 个以上真实样本测量后替换：

| 指标 | 当前估算 | Phase 0–1 后 | 完整方案后 |
|---|---:|---:|---:|
| 主流程成功率 | 70%–85% | 85%–92% | 95%–98% |
| 常见静态 SVG 视觉还原 | 65%–80% | 75%–85% | 90%–98% |
| SVG 原生可编辑比例 | 55%–70% | 60%–75% | 65%–85% |
| 复杂 SVG 可交付率 | 60%–75% | 80%–90% | 95%+ |

这些数字是待验证的假设，不是承诺值。建议定义如下：

- 主流程成功率：`SVGCompiler` 不抛异常且 `shape_count > 0`；
- 视觉还原：PPTX 导出 PDF 与 SVG 参考图的 SSIM 达到预设阈值，并通过人工检查；
- 原生可编辑比例：`native_shapes / total_output_objects`，由 RenderReport 统计；
- 复杂 SVG 可交付率：编译成功、无 critical warning 且输出可打开、可渲染。

预计收益拐点不在已经完成的入口修复，而在后续能力扩展：

| 阶段 | 预期收益 | 主要来源 |
|---|---:|---|
| Phase 0（当前已基本完成） | +5%–10% | 入口统一、错误可观测性和测试保护 |
| Phase 1 | +3%–5% | RenderReport、能力矩阵、限制和回归测试 |
| Phase 2a | +15%–25% | CSS class、style、继承和变量解析 |
| Phase 3a | +10%–15% | 复杂 SVG 从失败或缺失效果变为 PNG 可交付 |
| Phase 3b | +5%–10% | 局部 raster island 提升主体可编辑性 |

Phase 2a 是从“内联静态 SVG 能用”走向“LLM 生成 SVG 更可靠”的主要拐点。所有百分比都应在建立样本集后重新计算。

## 2. 总体架构

建议将当前单一 `SVGCompiler` 逐步演进为编排器加多个后端，但不应在第一阶段一次性重写为完整 IR 架构。当前单次遍历已经覆盖大量常用 SVG，IR 的引入应服务于样式计算、能力分析和降级决策，而不是为了替换已经工作的几何转换。

```text
SVG 输入
  ↓
安全解析与规范化
  ↓
CSS / style / defs 解析
  ↓
统一中间表示 SVG IR
  ↓
能力分析与区域分组
  ↓
┌──────────────────────────────┐
│ Native Backend                │ → PPTX shape / text / gradient
│ OOXML Effect Backend          │ → blur / glow / custom XML
│ Raster/Vector Fallback        │ → SVG / PNG image
└──────────────────────────────┘
  ↓
图层合成与 z-order 校验
  ↓
PPTX 输出 + RenderReport
```

建议新增模块：

```text
compiler/
  _parser.py          XML 解析和节点模型
  _css.py             CSS、class、继承和级联
  _ir.py              SVG 中间表示
  _capabilities.py    特性检测和后端选择
  _planner.py         区域拆分和降级计划
  _native_backend.py  原生 PPTX shape 编译
  _effect_backend.py  OOXML/PPTX 特效编译
  _fallback_backend.py SVG/PNG fallback
  _report.py          编译报告、warning、指标
```

现有 `_path.py`、`_paint.py`、`_text.py`、`_affine.py`、`_dash.py` 和 `_sanitizer.py` 可以作为基础组件保留。短期内仍由 `_compiler.py` 编排；在测试保护充分后，再逐步把样式计算和能力规划抽离，避免形成没有行为覆盖的新骨架。

## 3. 统一中间表示 SVG IR

当前代码直接从 XML 节点进入 PPTX shape，导致能力判断、样式继承、降级和后处理难以扩展。建议增加中间表示层。

### 3.1 IR 节点

每个节点至少包含：

```python
class SVGNode:
    tag: str
    id: str | None
    parent_id: str | None
    children: list["SVGNode"]
    geometry: Geometry | None
    computed_style: ComputedStyle
    transform: Affine
    opacity: float
    clip_refs: list[str]
    mask_ref: str | None
    filter_refs: list[str]
    source_order: int
    source_element: object
```

### 3.2 计算样式

`computed_style` 应在进入后端之前完成：

- presentation attributes；
- inline `style`；
- `<style>` 中的 selector；
- class；
- id selector；
- 继承属性；
- `currentColor`；
- CSS variables；
- opacity 合成；
- fill/stroke 的默认值。

这样后端不需要重复判断 XML 属性和样式继承，也能准确识别一个区域是否只是颜色问题，还是依赖不可表达的滤镜。

## 4. 支持级别矩阵

不要将支持状态简单分为“支持/不支持”，而应定义多个等级：

| 等级 | 含义 | 输出 | 示例 |
|---|---|---|---|
| NATIVE | 语义和视觉都可稳定转换 | 可编辑 PPTX shape | rect、line、基础 path、text |
| NATIVE_APPROX | 可编辑但有轻微视觉差异 | PPTX shape + warning | dash、部分 marker、渐变近似 |
| OOXML_EFFECT | 需要底层 XML 或 PPTX 特效 | 可编辑或半可编辑 | 透明度、部分阴影、渐变填充 |
| HYBRID | 图形主体原生，局部特效图片化 | 混合输出 | path + blur、文字 + glow |
| RASTER | 无法稳定表达 | PNG/SVG image | filter、mask、复杂 blend |
| REJECTED | 不安全、超限或解析失败 | 明确错误 | 外部资源、超大路径、恶意 XML |

编译报告应逐个 feature 记录：

```json
{
  "feature": "filter:gaussianBlur",
  "level": "HYBRID",
  "backend": "raster",
  "reason": "PPTX native shape cannot preserve SVG filter semantics",
  "source_ids": ["glow-1"]
}
```

## 5. 后端选择策略

### 5.1 原生后端

优先处理：

- rect、circle、ellipse、line；
- polygon、polyline；
- path 和 cubic Bézier；
- text、tspan；
- solid fill；
- linear/radial gradient；
- transform；
- clipPath 的简单几何；
- fill-rule；
- 常见 dash、linecap、linejoin。

原生后端应继续使用：

- PowerPoint 原生 shape；
- FreeformBuilder；
- OOXML custom geometry；
- Shapely 布尔运算。

### 5.2 OOXML Effect 后端

对可用 PPTX XML 表达的效果进行封装，不允许各处散落字符串拼接。候选能力包括：

- solid fill alpha；
- gradient fill；
- line alpha；
- shadow；
- glow；
- soft edges；
- 部分 3D / bevel；
- z-order 和 group metadata。

每个效果都要有 PowerPoint、LibreOffice 和 PDF 渲染验证，因为 OOXML 特效的跨渲染器一致性不能假设。

### 5.3 Hybrid 后端

复杂 SVG 不应该“一旦遇到 filter 就整张图片化”。应按区域拆分：

```text
背景矩形       → 原生 shape
主路径         → 原生 Freeform
渐变           → 原生渐变
发光复制层     → PNG/SVG fallback
标签文字       → 原生文本框
```

这样主体仍然可编辑，只有不可表达的视觉效果被图片化。

区域拆分的基本原则：

1. 以 `<g>`、带 filter 的节点和独立 z-order 组为边界；
2. 不跨越 clipPath 或 mask 边界强行拆分；
3. 对具有共同 opacity、blend 或 filter 的节点作为一个 raster island；
4. 保留原始节点 id 到输出 shape/image 的映射。

### 5.4 Fallback 后端

Fallback 分为两种，但默认顺序应以兼容性为中心：

- 默认渲染 PNG：兼容较老版本 PowerPoint、LibreOffice 和 PDF 转换链；
- 可选嵌入 SVG：保留矢量清晰度，但作为 opt-in，因为不同 Office 版本对 SVG 的支持范围和渲染结果并不一致。

复杂滤镜、mask、混合模式和跨软件交付场景默认走 PNG。只有调用方明确要求矢量 fallback，且目标环境已验证支持 SVG 时，才使用 SVG 嵌入。

Fallback 需要明确 DPI、尺寸、透明背景和裁剪边界，并记录：

- 原始 SVG bbox；
- fallback bbox；
- 生成分辨率；
- 是否发生裁剪；
- 使用的渲染器。

## 6. 复杂特性的实施路线

### 6.1 CSS 和样式系统

这是当前 Sanitizer 最明显的能力缺口，建议拆成独立 CSS 计算器。

第一阶段支持：

- tag selector；
- `.class`；
- `#id`；
- 属性直接声明；
- inline style；
- 常见继承属性；
- CSS variables。

第二阶段支持：

- selector specificity；
- `:root`；
- 多个 selector 组合；
- `!important`；
- presentation attribute 与 CSS cascade 的优先级。

不建议第一阶段实现完整浏览器 CSS，而应定义 SVG CSS 子集并在报告中说明。

### 6.2 `<use>`、`symbol` 和 viewBox

当前 `_render_use()` 对内部 `symbol` 或 `svg` 的处理主要是递归子节点，只应用 `use` 的 `x/y` 平移；没有完整实现 `symbol` 的 `viewBox`、`preserveAspectRatio`、`width/height` 到使用区域的映射。

这对图标库很重要，因为大量 SVG 图标通过：

```svg
<symbol id="icon" viewBox="0 0 24 24">...</symbol>
<use href="#icon" x="10" y="10" width="48" height="48" />
```

实现路线应是：

1. 建立 symbol 的独立 viewBox；
2. 解析 `use` 的 x/y/width/height；
3. 按 `preserveAspectRatio` 计算 contain/meet/slice 对齐；
4. 将 symbol 的局部 transform 与 use 的 transform 合并；
5. 记录 source id 到所有输出 shape 的映射。

外部 `<use>` 默认保持拒绝，不加载网络或文件资源。

### 6.3 Marker 和箭头

`marker-start`、`marker-mid`、`marker-end` 适合转换为：

- PPTX connector arrowhead；
- Freeform 末端三角形；
- marker path 的局部 Freeform。

必须考虑：

- `markerUnits`；
- `orient="auto"`；
- stroke width 缩放；
- marker 与 path transform；
- marker 的 fill/stroke 继承。

### 6.4 Pattern

Pattern 可分三种处理：

1. 简单线条/网格：转换为 PPTX pattern fill；
2. 小型可重复图形：生成纹理图片；
3. 复杂 pattern：局部 raster fallback。

### 6.5 Filter

建议按滤镜拆分，而不是一次实现全部：

| Filter | 建议策略 |
|---|---|
| Gaussian blur | raster island 或 OOXML soft edge |
| Drop shadow | OOXML shadow，无法匹配时 raster |
| Glow | raster island |
| Color matrix | 预处理颜色或 raster |
| Blend | raster island |
| Morphology | raster |
| Displacement map | raster |
| Turbulence | raster |
| Composite | 根据输入决定 native/hybrid/raster |

### 6.6 Mask 和 clipPath

clipPath 优先保留为几何布尔运算；mask 通常包含 alpha 或灰度语义，建议默认进入 hybrid/raster。

优化方向：

- 对同一个 clipPath 预计算几何；
- 对同一 mask 复用渲染缓存；
- 对多个同源节点合并 raster island；
- 对曲线展平使用自适应误差，而不是固定采样数；
- 对 Shapely 结果进行合法性校验和复杂度限制。

### 6.7 Gradient units 和 spreadMethod

当前渐变实现隐式按 objectBoundingBox 处理，未完整区分：

- `gradientUnits="objectBoundingBox"`：坐标相对于目标形状边界；
- `gradientUnits="userSpaceOnUse"`：坐标位于 SVG 用户空间，受全局 transform 和 viewBox 影响。

复杂 SVG，尤其是带全局坐标渐变和 transform 的图表，常使用 `userSpaceOnUse`。实现路线应先在 IR 中保存 gradient 的坐标空间，再在目标 shape 变换后计算实际渐变向量。不能简单把两个百分比值直接交给 PPTX 渐变角度。

`spreadMethod` 当前只接受 `pad`；`reflect` 和 `repeat` 会在 [`compiler/_paint.py`](../src/pptx_designer/compiler/_paint.py) 中抛出 `SVGCompileError`，可能导致整张 SVG 编译中断。策略上应调整为：

1. 检测到 `reflect/repeat` 时标记 `NATIVE_APPROX` 或 `RASTER`；
2. 对简单线性渐变可通过扩展 stop 近似；
3. 对无法稳定近似的渐变局部 raster fallback；
4. 只有安全解析或资源限制失败时才终止整个编译。

### 6.8 文本描边的视觉差异

当前文本描边使用“双层文本框”近似：后层使用更大的粗体文字作为 outline，前层使用正常 fill 覆盖。它不是 SVG 的真实 stroke：SVG stroke 通常以字形轮廓为中心向内外扩展，而双层文字会改变字宽、字重、边角和排版。

因此文本 stroke 应在能力报告中标记为 `NATIVE_APPROX`，并提供三种策略：

- `editable`: 当前双层文本框，保持文字可编辑；
- `visual`: 将描边文字 rasterize，优先保证视觉；
- `outline-path`: 将字形转成 path，编辑性下降但几何更准确。

默认建议对普通标题使用 `editable`，对大字号 logo 或装饰文字使用 `visual` 或 `outline-path`。

## 7. 安全设计

SVG 输入可能来自 LLM、用户文件或外部服务，必须建立输入边界。

### 7.1 XML 安全

- 禁用外部实体；
- 禁止 DTD 或明确使用安全解析器配置；
- 限制 XML 总字节数；
- 限制节点数量和嵌套深度；
- 对解析恢复模式设置失败阈值；
- 删除 script、event handler 和未知执行属性。

### 7.2 外部资源

默认拒绝：

- `http://`、`https://` 外部 href；
- `file://`；
- data URI 中的超大资源；
- 外部 `<use>`；
- 外部图片和字体。

如果未来需要支持外部资源，应通过显式资源提供器加载，并设置：

- allowlist；
- 超时；
- 最大响应大小；
- 最大递归深度；
- 缓存和去重；
- 禁止重定向到不允许协议。

### 7.3 资源耗尽

需要限制：

- 最大节点数；
- 最大 path 命令数；
- 最大 SVG bbox；
- 最大 raster fallback 像素数；
- 最大 clip/mask 布尔运算次数；
- 最大编译时间。

超过阈值时应进入可解释的 fallback 或返回 `SVGCompileError`，不能无限消耗 CPU 和内存。

## 8. 性能方案

当前基准已经显示：普通 SVG 的节点数量增加会显著增加编译耗时，重复 clipPath 布尔运算成本尤其高。

建议按以下顺序优化：

### 8.1 解析阶段

- 只遍历一次 XML；
- 预编译 style selector；
- 缓存颜色、字体和 transform；
- 预先统计 feature，避免无意义后端初始化。

### 8.2 几何阶段

- 缓存相同 path；
- 缓存相同 transform 组合；
- clipPath 几何缓存；
- 合并同 fill/stroke/opacity 的相邻节点；
- 使用自适应 Bézier 展平；
- 避免每个 clip 节点都重复创建 Shapely 对象。

### 8.3 输出阶段

- 批量创建或复用 OOXML XML 节点；
- 减少重复 wrapper/proxy；
- 将 shape 句柄存入 RenderReport；
- 对 raster island 使用缓存 key 去重。

建议每次编译输出指标：

```json
{
  "parse_ms": 0,
  "plan_ms": 0,
  "geometry_ms": 0,
  "render_ms": 0,
  "total_ms": 0,
  "node_count": 0,
  "native_shape_count": 0,
  "fallback_count": 0,
  "boolean_ops": 0,
  "peak_estimated_pixels": 0
}
```

## 9. 输出数据结构

建议将现在的 `SVGResult` 扩展为稳定的 `SVGRenderReport`：

```python
@dataclass
class SVGRenderReport:
    shape_count: int
    native_shapes: list
    fallback_shapes: list
    warnings: list[str]
    errors: list[str]
    features: set[str]
    feature_levels: dict[str, str]
    source_to_output: dict[str, list]
    metrics: dict[str, float | int]
```

`source_to_output` 很重要，例如：

```python
{
    "title": [pptx_textbox],
    "hero-path": [pptx_freeform],
    "glow-1": [pptx_image]
}
```

它允许后续实现：

- 批量修改颜色或透明度；
- 添加动画；
- 重新定位元素；
- 生成可访问性描述；
- 诊断某个 SVG 节点对应的 PPTX 输出。

## 10. 质量验证体系

复杂 SVG 支持不能只检查“有没有生成 shape”，需要多层验证。

### 10.1 单元测试

覆盖：

- XML sanitizer；
- CSS cascade；
- 颜色和透明度；
- path 解析；
- transform；
- gradient；
- dash；
- text baseline；
- clipPath；
- feature planner。

### 10.2 Golden SVG 测试集

建立固定样本：

- LLM 架构图；
- 复杂流程图；
- 多层渐变海报；
- logo/path；
- filter glow；
- mask；
- pattern；
- CJK 文本；
- 外部资源引用；
- 大型数据图表。

每个样本保存：

- 原始 SVG；
- 预期 feature；
- 期望 backend；
- PPTX 输出；
- 渲染 PNG/PDF；
- 差异阈值；
- 可接受 warning。

### 10.3 视觉回归

建议至少比较：

- SVG 原图与 PPTX 导出 PDF 的像素差；
- SVG 原图与 PPTX 截图的 bbox 差异；
- 文字基线和换行；
- 渐变方向和颜色端点；
- z-order；
- clipPath 边界。

### 10.4 可编辑性回归

统计：

- 原生 shape 数量；
- 文本框数量；
- fallback 图片数量；
- 可选中/可修改的节点比例；
- shape 与 source id 的映射完整度。

### 10.5 跨软件验证

至少验证：

- Microsoft PowerPoint；
- LibreOffice；
- PPTX 转 PDF；
- PowerPoint 再编辑并重新保存。

## 11. 分阶段实施计划

### Phase 0：修复现有链路（当前源码已基本完成）

- [x] 统一 `PrecisionRenderer` 的导入入口；
- [x] 将旧 `renderer/svg_compiler.py` 改为转发 shim；
- [x] 保留 warning 和编译错误日志；
- [ ] 增加 `PrecisionRenderer` SVG 集成测试；
- [ ] 修复 README / example 的 API。

Phase 0 的剩余工作主要是测试和文档，不应再被描述为“恢复 SVG 主流程”。

### Phase 1：稳定现有 compiler

- 增加 `SVGRenderReport`；
- 增加 source id 到 PPTX shape 的映射；
- 将现有 root 脚本迁移到 pytest；
- 增加节点数量、路径长度和编译时间限制；
- 明确 capability matrix。

### Phase 2a：CSS 计算与能力分析

- 在现有 XML 遍历上增加 computed style；
- 支持 class、id、tag selector；
- 支持 CSS variables 和继承；
- 将 sanitizer 从“删除 style”升级为“解析安全 CSS 子集”。

这一阶段不重写几何后端，先让现有 compiler 能识别“可原生化”和“需要降级”的节点。

### Phase 2b：增量引入 SVG IR

- 先为已经计算完成的节点建立只读 IR；
- 保留现有 `_walk()` 作为兼容后端；
- 用 IR 驱动 feature report 和 source id 映射；
- 以少量 golden SVG 验证 IR 与旧路径输出一致；
- 只有当 IR 覆盖率和视觉回归稳定后，再迁移后端。

### Phase 3a：整体 fallback

- 实现 filter/mask 检测；
- 默认整张 SVG 生成 PNG fallback；
- SVG 嵌入作为显式 opt-in；
- 生成明确的 fallback reason 和性能指标；
- 先保证复杂 SVG 不丢失视觉结果，不在此阶段拆分区域。

### Phase 3b：区域拆分与 raster island

- 在 IR 上识别 opacity/filter/mask/blend 的继承边界；
- 按 `<g>`、clipPath 和 z-order 构建渲染区域；
- 对同一效果上下文的节点建立 raster island；
- 验证拆分前后 z-order、裁剪边界和透明度合成；
- 使用一个具体 LLM 架构图样本完成 proof-of-concept，再决定是否全面推进。

该阶段是全方案风险最高的部分。不能仅凭递归 `_walk()` 拆分，因为 group 继承、clipPath 边界和跨层级 z-order 会影响最终合成。

### Phase 3c：source-to-output 映射

- 为每个 IR 节点记录输出 shape/image；
- 支持一个源节点对应多个输出对象；
- 允许后处理、重新着色和诊断；
- 将映射写入 `SVGRenderReport`。

3c 依赖 3b 的区域模型，不应在没有明确输出分组语义时提前承诺完整映射。

### Phase 4：扩展图形能力

- marker；
- pattern；
- 更多渐变语义；
- 复杂 clipPath 优化；
- 更多 OOXML 效果；
- group metadata 和后处理 API。

### Phase 5：性能和跨平台质量

- clipPath 和路径缓存；
- 大 SVG 分区并行或增量处理；
- Golden SVG 视觉回归；
- PowerPoint/LibreOffice/PDF 交叉验证；
- 性能基准门禁。

## 12. 推荐的最终产品行为

调用方不应只收到一个 `shape_count`，而应能看到：

```text
SVG 编译完成
  原生形状：42
  原生文本：8
  局部 fallback：2
  跳过节点：0
  warning：3
  总耗时：184 ms
```

当复杂 SVG 无法完全原生化时，系统应明确告诉用户：

```text
节点 #glow-1 使用 raster fallback：PPTX 原生形状无法保留 SVG Gaussian blur。
节点 #title 已转换为可编辑文本框。
节点 #chart-area 使用 native clipPath。
```

这比简单返回“成功”或“失败”更适合 LLM 生成和调试场景。

## 最终建议

最大化支持复杂 SVG 的关键不是继续堆叠标签支持，而是建立：

```text
SVG IR
  + 能力分级
  + 多后端渲染
  + 局部 hybrid fallback
  + 安全资源边界
  + 性能指标
  + 视觉/可编辑性双重回归
```

在当前源码状态下，工程顺序应调整为：先建立 20 个以上真实 SVG 样本的 baseline，补齐 Phase 0 剩余测试和文档，再做 RenderReport 与 CSS 子集解析，之后以 proof-of-concept 验证整体 fallback，最后再决定是否投入高风险的 IR 驱动区域拆分和 hybrid backend。这样可以避免用已经解决的入口问题衡量收益，也不会在“支持更多 SVG”过程中失去现有稳定性。

## 13. 时间与资源估算

以下是工程估算，不是承诺排期。假设 1 名熟悉 Python、`python-pptx`、OOXML、SVG 和图像渲染的工程师全职投入，并且能够使用 PowerPoint、LibreOffice 和 PDF 渲染环境。估算不包含完整浏览器级 CSS、SVG 动画、外部资源加载，或 PPTX 其它渲染模块的大规模重写。

| 阶段 | 工程人日 | 单人自然周 |
|---|---:|---:|
| Baseline：20–30 个样本和指标 | 3–5 | 1 |
| Phase 0 收尾：集成测试、文档、示例 | 3–5 | 1 |
| Phase 1：RenderReport 和能力矩阵 | 8–12 | 2–3 |
| Phase 2a：CSS 子集解析 | 15–25 | 3–5 |
| Phase 2b：增量 SVG IR | 15–25 | 3–5 |
| Phase 3a：整体 PNG fallback | 8–15 | 2–3 |
| Phase 3b：raster island 区域拆分 | 25–45 | 5–9 |
| Phase 3c：source-to-output 映射 | 10–18 | 2–4 |
| Phase 4–5：扩展能力、性能和跨软件回归 | 35–60 | 7–12 |

单人全职累计估算：Baseline + Phase 0–1 约 3–5 周；加入 Phase 2a 约 6–10 周；加入 Phase 2b + Phase 3a 约 11–18 周；完成 Phase 3b–3c 约 18–31 周；完成 Phase 4–5 约 25–43 周。

推荐在第 14 周设置决策点：先完成 baseline、Phase 0 收尾、Phase 1、Phase 2a 和 Phase 3a，再用一个真实复杂 SVG 做 Hybrid POC，决定是否投入 5–9 周的 Phase 3b。若 POC 无法稳定处理 z-order、透明度和 clip 边界，可以停在 Phase 3a；整体 PNG fallback 仍能显著提高复杂 SVG 的可交付率。
