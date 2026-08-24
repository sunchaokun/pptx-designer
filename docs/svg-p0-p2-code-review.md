# SVG P0–P2 代码审查报告

> 审查日期：2026-08-24
>
> 审查对象：`E:/pptx-designer/`
>
> 状态更新：本报告的初次审查后，已完成 P1 foundation、P2a CSS 子集强化和 P2b 的增量只读 IR。当前结论：P0、P1 foundation、P2a、P2b（第一增量）完成；尚未进入 IR 驱动的 planner、区域拆分或后端迁移。

## 一、验证结果

已执行：

```text
pytest -q
129 passed
```

当前测试全部通过，覆盖了简单 SVG、CSS 子集、IR 树/特性/源 ID 索引和 renderer 接入；仍未覆盖 `symbol/viewBox`、`gradientUnits`、fallback、视觉 golden 与性能门禁。

## 二、阶段完成度

| 阶段 | 状态 | 判断 |
|---|---|---|
| P0 / Phase 0：入口、shim、主流程、基础测试 | 完成 | 已接入正式 compiler，旧入口为 shim，`tools.svg` 已存在，主流程记录 warning/error |
| P1 / Phase 1：报告、能力矩阵、限制、映射 | foundation 完成 | `SVGResult` 现在兼作 `SVGRenderReport`，包含 shape、feature level、metrics、source 映射与资源上限 |
| P2a / CSS 子集 | 完成（限定子集） | 支持简单 tag/class/id/`:root` selector、级联、变量、继承与 `!important`；复杂 selector 不在本阶段范围 |
| P2b / 增量 SVG IR | 完成（第一增量） | 新增不可变 `SVGIRDocument` / `SVGIRNode`；在 sanitize/CSS 后构建，保留 `_walk()` 渲染后端，并写入编译报告 |

## 三、P0 / Phase 0 审查

### 已完成项

主渲染器现在从正式 compiler 导入：

- [`precision.py:1241`](../src/pptx_designer/renderer/precision.py#L1241)

并且保存编译结果、记录 warning，编译异常会写入 logger：

- [`precision.py:1249`](../src/pptx_designer/renderer/precision.py#L1249)
- [`precision.py:1253`](../src/pptx_designer/renderer/precision.py#L1253)

旧入口已经是兼容转发 shim：

- [`renderer/svg_compiler.py:13`](../src/pptx_designer/renderer/svg_compiler.py#L13)

高层工具也已经补上：

- [`tools/svg.py`](../src/pptx_designer/tools/svg.py)
- [`tests/test_svg_tools.py`](../tests/test_svg_tools.py)

主流程和兼容导入都有测试：

- [`tests/test_renderer/test_svg_integration.py`](../tests/test_renderer/test_svg_integration.py)
- [`tests/test_svg_compiler_integration.py`](../tests/test_svg_compiler_integration.py)

### P0 遗留项

README 和示例现在可以找到 `tools.svg` 实现，但仍建议增加一次“从 README 示例运行”的 smoke test，防止 API 签名、包安装和示例路径再次漂移。

另外，renderer 方法只记录 `SVGResult` 的 warning，仍没有把完整结果向上层 `render_slide()` 返回。对 P0 来说可以接受，但它是 P1 报告能力未完成的直接原因。

## 四、P1 / Phase 1 审查

### 4.1 `SVGRenderReport` foundation 已实现

当前 `SVGResult` 仍是：

- [`compiler/_compiler.py:194`](../src/pptx_designer/compiler/_compiler.py#L194)

现有字段主要是：

- `shapes`
- `warnings`
- `features`
- `compile_ms`
- `shape_count`

编译器现在填充 `result.shapes`，并增加：

- `native_shapes` / `fallback_shapes`
- `errors`
- `feature_levels`
- `source_to_output`
- 结构化 `metrics`

`SVGRenderReport` 是 `SVGResult` 的兼容别名，避免破坏既有 API。当前没有 fallback 后端，因此 `fallback_shapes` 为空；这是准确表达实现状态，而非缺字段。

### 4.2 基础能力矩阵已实现

编译器现在将 feature 映射为：

```text
NATIVE / NATIVE_APPROX / OOXML_EFFECT / HYBRID / RASTER / REJECTED
```

当前矩阵是基础版：普通形状为 `NATIVE`，渐变为 `OOXML_EFFECT`，裁剪/布尔语义为 `NATIVE_APPROX`。filter/mask/fallback 的分级将在后续 fallback 后端完成。

### 4.3 输入限制已实现

`SVGCompiler(limits=...)` 现在限制：

- 最大 XML 字节数；
- 最大节点数；
- 最大 path 命令数；
- 最大嵌套深度、最大布尔运算次数、最大 fallback 像素数和最大编译时长仍待后续阶段实现。

当前限制覆盖 SVG 字节数、节点数和 path 命令数；它们为现有解析和几何路径提供了第一道资源防护。

### 4.4 测试迁移部分完成

新增了：

- compiler 集成测试；
- sanitizer 测试；
- CSS 测试；
- renderer SVG 集成测试；
- `tools.svg` 测试。

但根目录的 `test_svg*.py`、调试脚本和旧测试样本仍然存在，尚未完全整理为 golden SVG 测试集，也没有视觉回归或跨软件验证。

## 五、P2a / CSS 子集审查

### 已完成能力

实现位于：

- [`compiler/_css.py`](../src/pptx_designer/compiler/_css.py)
- [`compiler/_sanitizer.py:139`](../src/pptx_designer/compiler/_sanitizer.py#L139)

当前支持：

- 简单 tag selector；
- `.class` selector；
- `#id` selector；
- 逗号分隔 selector；
- 注释删除；
- 常见属性应用；
- 部分 inherited 属性向子节点传播；
- 多个 `<style>` block；
- inline style 优先于 CSS 规则的基础场景。

这已经解决了最常见的 LLM SVG class 样式完全丢失问题。

### 已修复：CSS cascade 和变量

CSS 计算现在按 `!important`、specificity 和 source order 比较 declaration；presentation attribute 作为低优先级声明，inline `style` 具有高优先级。

已复现：

```css
.a { fill: red; }
.b { fill: blue; }
```

```svg
<rect class="a b" />
```

现在结果为 `blue`，符合该 CSS 子集的 cascade 规则。

已覆盖并有测试的场景：

- `rect { ... }` 与 `.class { ... }` 的 specificity；
- CSS 规则覆盖 presentation attribute；
- `!important`；
- 后出现的同 specificity 规则覆盖前规则；
- `:root` custom property 与 `var(--name)` 替换。

组合 selector 和 descendant selector 仍不在安全 CSS 子集范围内。

### CSS variables 已完成基础作用域

`:root` 和元素级 custom property 会进入 CSS 计算侧表并沿树继承，随后替换 `var(--name)`。不会把 `--name` 写入 lxml XML attribute，因为该名称在 lxml 中非法。

普通 inherited properties 和 CSS custom properties 都已覆盖基础路径。

### `opacity` 继承语义已修正，但 group compositing 仍是后续工作

`opacity` 已从 CSS inheritable property 列表移除；直接作用于形状的 opacity 会与 fill/stroke opacity 合并。完整 group compositing 在重叠子元素时仍需要 group/raster 后端支持。

### CSS 解析器边界

当前 parser 没有支持：

- 组合 selector；
- 属性 selector；
- 伪类；
- `@media`；
- `@import`；
- `!important`；
- 完整 specificity；
- CSS custom property 作用域；
- `currentColor` 的完整 CSS 继承语义。

所以 P2a 应评为“第一版可用子集”，不能标记为完成全部计划目标。

## 六、仍未覆盖的复杂 SVG 能力

当前代码仍未实现或未完整实现：

- filter；
- mask；
- image；
- marker；
- pattern；
- `symbol` 的 `viewBox` / `preserveAspectRatio` 映射；
- `gradientUnits="userSpaceOnUse"`；
- `spreadMethod="reflect/repeat"` 的真实语义；
- raster fallback；
- hybrid raster island；
- source-to-output 映射。

特别需要注意：虽然 [`compiler/_paint.py`](../src/pptx_designer/compiler/_paint.py) 的辅助函数对非 `pad` spreadMethod 会抛出异常，但当前 `_compiler.py` 在 `_collect_defs()` 中手动收集渐变，没有使用这些辅助收集函数。因此当前 `spreadMethod="repeat"` 不一定报错，而是可能被当作默认 `pad` 处理，属于静默视觉错误风险。

同样，`<use>` 引用 `symbol` 当前可以生成 shape，但 [`_compiler.py:628`](../src/pptx_designer/compiler/_compiler.py#L628) 主要是递归子节点并平移，没有实现 symbol 的 viewBox 到 use 宽高区域映射。

## 七、最终审查结论

### 可以确认完成

- 正式 SVG compiler 已接入主 renderer；
- 旧入口已安全转发；
- SVG 高层 helper 已补齐；
- warning/error 基础可观测性已补齐；
- CSS `<style>` 不再被直接全部丢弃；
- 基础 CSS class/id/tag 场景已覆盖测试；
- 基础 renderer/compiler 集成测试已建立。

### 部分完成

- CSS cascade：仅支持简单规则，不是完整级联；
- CSS inheritance：部分实现，`opacity` 语义有风险；
- 测试体系：有单元/集成测试，但缺少 golden、视觉和性能门禁。

### 尚未完成

- IR 驱动的 planner、区域拆分和后端迁移；
- filter/mask/image fallback；
- symbol viewBox、gradientUnits、spreadMethod 正确语义。

综合判断：当前 P0、P1 foundation、P2a 与 P2b 的只读 IR 基线已完成。IR 是诊断和后续 planner 的稳定输入，现有 `_walk()` 渲染输出保持不变；但还不能支撑多后端 fallback、复杂 SVG 区域降级或 IR 驱动的渲染替换。

## 八、审查问题修复验证

本报告提出的四项代码问题已修复并加入回归测试：

- `total_ms` 现在在文本重叠检测后计算，包含完整后处理时间；
- `<use>` 同时记录 use 节点和被引用源 id 的输出映射；
- walker 跳过 `display="none"`、`visibility="hidden"` 和 `visibility="collapse"` 节点；
- SVG 文本现在将 element/fill/stroke opacity 写入 PPTX run 的 alpha。

验证结果：

```text
pytest -q: passed
git diff --check: passed
```

`ruff check` 对本轮新增的 CSS 模块通过；全量 compiler/text 静态检查仍包含已有的 import 排序、`C` 参数命名和空白行告警，不属于上述四项功能修复。

## 九、P2b 增量 SVG IR 验证

本阶段新增 [`compiler/_ir.py`](../src/pptx_designer/compiler/_ir.py)，其只读节点模型记录：源顺序、父子关系、CSS 计算后的属性、文本、源 `id` 索引与能力特征。`SVGCompiler.compile()` 在 sanitize 之后构建该模型，并将其写入 `SVGResult.ir_document`；报告增加 `ir_node_count` 与 `ir_build_ms`。现有 `_walk()` 仍从 lxml 树渲染，因此此阶段不改变输出路径或可编辑性。

IR 对 `filter`、`mask`、`image`、`pattern`、`marker` 等标记为 `RASTER_FALLBACK_CANDIDATE`，为 Phase 3a 的整体 PNG fallback 提供可审计的决策输入；这不是 fallback 本身。

验证结果：

```text
pytest -q: 129 passed
pytest -q tests/test_compiler/test_ir.py tests/test_svg_compiler_integration.py: 31 passed
ruff check src/pptx_designer/compiler/_ir.py tests/test_compiler/test_ir.py tests/test_svg_compiler_integration.py: passed
git diff --check: passed
```
