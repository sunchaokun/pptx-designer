# SVG P3：可编辑性优先路线图（预留）

> 状态：预留设计，未进入实现。
> 适用版本：`1.0.0-beta.2`。
> 决策日期：2026-08-24。

## 1. 项目定位与最高原则

`pptx-designer` 的 SVG 模块首先是一套 **SVG 到可编辑 PowerPoint 对象** 的编译器，而不是浏览器级 SVG 截图器。

P3 采用以下优先级：

```text
可编辑对象可用性  >  结构与层级正确性  >  视觉近似度  >  像素级等价
```

因此，遇到当前不能原生表达的 SVG 能力时，默认策略是产生可编辑的近似结果并报告降级原因；不以局部或全页 PNG 作为常规输出。PNG 只作为明确启用的保真模式或无法得到有效 PPT 页面时的最后兜底。

## 2. 为什么调整方向

通用的 raster island（局部 PNG）方案能改善滤镜、蒙版等效果的视觉保真，但它会带来高工程复杂度：组合上下文、裁剪、透明度、引用依赖、z-order 与用户可编辑文本之间都可能产生错误边界。

对于本项目，更有价值的结果是：用户能在 PowerPoint 中选中、修改、移动标题、标签、数值、箭头与基本图形，即便阴影、发光、复杂蒙版或图案填充被简化。把这些对象封进 PNG 会直接违背核心价值。

## 3. P3 的默认决策矩阵

| SVG 情形 | 默认输出 | 可编辑性 | 报告行为 |
|---|---|---:|---|
| 基本形状、路径、普通文本、已支持的 transform | 原生 PPT 形状/文本 | 保留 | 无降级或 `native` |
| CSS 规则可解析但某个样式属性不支持 | 保留对象，忽略或近似该属性 | 保留 | `style_property_approximated` |
| 简单渐变无法完整映射 | 简化渐变或代表色纯色填充 | 保留 | `gradient_approximated` |
| `filter`（阴影、发光、模糊） | 保留基础几何/文字；省略效果或使用简单 PPT 近似 | 保留 | `filter_omitted` / `filter_approximated` |
| `mask`、复杂 `clipPath` | 尽可能保留基础对象；无法安全表达时忽略裁剪或简化边界 | 尽量保留 | `mask_approximated` / `clip_approximated` |
| `pattern`、复杂 marker | 用纯色、线条或基础箭头近似 | 保留 | `pattern_approximated` / `marker_approximated` |
| `<use>/<symbol>` 的复杂 viewBox 语义 | 展开为原生对象；失败时跳过实例而非整页栅格化 | 尽量保留 | `use_instance_skipped` |
| 外部资源、无法解析的对象或超限输入 | 跳过受影响对象；保留其余页面 | 其余保留 | `element_skipped` |
| 用户显式要求高保真，或无有效原生页面可产出 | 可选整图 PNG 兜底 | 不保留 | `whole_slide_raster_fallback` |

原则：**每次降级必须可观察、可统计、可测试；不得静默把可编辑内容替换为 PNG。**

## 4. 需要建设的能力

### 4.1 降级策略与 RenderReport（优先）

在现有 `SVGResult` / `RenderReport` 基础上补齐机器可读的降级条目：源节点、能力、采取的近似方式、对编辑性的影响、是否可由用户选择更高保真模式。示例：

```json
{
  "source_id": "sales-title",
  "feature": "filter",
  "action": "omitted",
  "output": "native_text",
  "editable": true,
  "message": "drop-shadow omitted; text remains editable"
}
```

### 4.2 原生高频能力补齐

优先顺序由“可编辑覆盖收益”决定，而不是 SVG 规范完整度：

1. CSS 子集稳定性、继承与诊断；
2. `use` / `symbol` 的 viewBox、width、height 映射；
3. `gradientUnits="userSpaceOnUse"` 与 `spreadMethod` 的近似策略；
4. marker 的常见箭头近似；
5. 文本样式、CJK、长文本、文字描边的明确近似规则；
6. pattern、filter、mask 的基础近似，而非通用像素保真。

### 4.3 稳定来源映射与可编辑对象契约

所有原生输出对象应拥有稳定键，优先采用 `data-pptx-key`，其次 SVG `id`，最后使用可重现的源顺序键。写入的 PowerPoint shape 名称建议为：

```text
svg:{key}
svg:{key}::part:{n}
```

并输出 sidecar 映射，供 build 代码只替换同一键的对象。该能力服务于可编辑对象的增量更新，不依赖 `E:/PPT-Design-Skill`；历史 skill 仅可作为实现经验参考，当前实现必须归属 `pptx-designer` 标准库。

### 4.4 最后兜底：可选整图 PNG

不实现默认的通用 raster island。若未来提供 PNG fallback，必须满足：

- 由调用方显式选择 `fidelity_mode="raster"`（名称以实际 API 设计为准）；
- 默认模式仍为原生可编辑近似；
- 输出报告说明哪些对象失去可编辑性；
- 失败时不产生半页、无报告的产物；
- PNG 模式不替代原生能力建设的测试指标。

## 5. 分阶段预留计划

| 阶段 | 交付物 | 预估投入 | 完成判据 |
|---|---|---:|---|
| P3-A | 降级动作枚举、结构化报告、样本基线 | 3–5 人日 | 每个不支持能力都有原因与 action |
| P3-B | `use/symbol`、渐变、marker 等高频原生近似 | 8–15 人日 | 代表 SVG 的原生对象覆盖率提升且无静默跳过 |
| P3-C | 稳定 shape naming、sidecar map、增量更新测试 | 3–5 人日 | 修改一个 key 只影响对应 PPT 对象 |
| P3-D | 可选整图 PNG fallback POC | 3–5 人日 | 显式模式、报告完整、默认输出不变 |
| P3-E（按需） | 局部 PNG/raster island 可行性研究 | 10–25 人日 | 仅在真实高保真需求证明价值后立项 |

P3-A 至 P3-D 的合理总量为 **17–30 人日**。P3-E 不是既定承诺；其复杂度高，必须以实际需求和样本收益决定是否启动。

## 6. 验收指标

每个阶段使用真实 SVG 样本集验证，至少包括普通图形、图表、LLM 生成 SVG、CJK 文本、复杂渐变、filter/mask 和 `use/symbol`。

- **可编辑覆盖率**：文本与基础图形按节点统计，原生输出比例应持续提升；
- **降级可观察性**：不支持能力 100% 产生结构化 warning/action；
- **结构正确性**：PPTX 可重新打开，shape 顺序与来源映射可验证；
- **视觉可接受性**：采用人工审阅加场景化容差，不把 SSIM 作为阻止可编辑近似的唯一门槛；
- **回归保护**：每个新近似规则有正例、边界例与失败例测试。

## 7. 当前不做的事项

- 不在 P3 初期引入通用 SVG IR 重写；现有 P2b IR 继续增量扩展；
- 不默认输出局部 PNG，不把文字“盖回”完整 SVG 截图上；
- 不以浏览器级 SVG 1.1/2.0 像素一致为完成标准；
- 不依赖或 import 早期 `PPT-Design-Skill` 的 `build_helpers.py`；
- 不在缺乏样本与用户需求验证的情况下实现多岛拆分算法。

## 8. 立项门槛

后续启动任一 P3 子阶段前，应先明确：目标样本、希望保留的可编辑对象、允许的视觉降级、验收测试和公开 API 影响。若无法明确这些信息，优先补充样本与报告，不启动高复杂度渲染工作。
