# SVG 模块深度分析

> 分析对象：`E:/pptx-designer/`
>
> 分析日期：2026-08-24
>
> 分析范围：SVG 编译器、PPTX 渲染接入、支持边界、文档示例和测试覆盖。

> 状态说明：本文最初审计时记录了旧版入口冲突。后续源码已修复该问题：`PrecisionRenderer` 现在直接导入正式 compiler，`renderer/svg_compiler.py` 已变为兼容转发 shim。下文保留历史问题和验证依据，但当前结论以“已解决”标记为准。

## 结论摘要

项目中存在一套功能较完整的 SVG 编译器，可以把常用 SVG 元素转换成可编辑的 PPTX 原生形状。历史版本曾存在两套同名 `SVGCompiler` 实现，生产渲染器曾导入未实现的旧桩；当前源码已经将主流程切换到正式 compiler，并将旧模块改为兼容转发 shim。

因此，当前状态是：

1. 直接调用 `pptx_designer.compiler.SVGCompiler` 可以生成 PPTX 形状；
2. `PrecisionRenderer` 的 `svg_diagram` 主流程现在调用正式 SVG 编译器；
3. 主流程现在会记录 SVG warning 和编译错误；
4. README 和示例引用了不存在的 `pptx_designer.tools.svg`；
5. 现有自动化测试没有覆盖 SVG 主链路。

最优先修复项是统一 SVG 入口，并为 `PrecisionRenderer` 增加集成测试。

## 一、模块结构

### 1. 正式编译器

正式实现位于：

- [`src/pptx_designer/compiler/_compiler.py`](../src/pptx_designer/compiler/_compiler.py)
- [`src/pptx_designer/compiler/_path.py`](../src/pptx_designer/compiler/_path.py)
- [`src/pptx_designer/compiler/_paint.py`](../src/pptx_designer/compiler/_paint.py)
- [`src/pptx_designer/compiler/_text.py`](../src/pptx_designer/compiler/_text.py)
- [`src/pptx_designer/compiler/_affine.py`](../src/pptx_designer/compiler/_affine.py)
- [`src/pptx_designer/compiler/_dash.py`](../src/pptx_designer/compiler/_dash.py)
- [`src/pptx_designer/compiler/_sanitizer.py`](../src/pptx_designer/compiler/_sanitizer.py)
- [`src/pptx_designer/compiler/_theme.py`](../src/pptx_designer/compiler/_theme.py)

对外导出集中在 [`src/pptx_designer/compiler/__init__.py`](../src/pptx_designer/compiler/__init__.py)。推荐入口是：

```python
from pptx_designer.compiler import SVGCompiler

result = SVGCompiler(C=context).compile(
    svg_text,
    slide,
    (x, y, width, height),
)
```

### 2. renderer 兼容入口

历史版本的 [`src/pptx_designer/renderer/svg_compiler.py`](../src/pptx_designer/renderer/svg_compiler.py) 曾定义一个未实现的占位类。当前文件已经改为转发 shim：

```python
from pptx_designer.compiler import SVGCompileError, SVGCompiler, SVGResult
```

因此旧导入路径目前与正式 compiler 指向同一实现；新代码仍应优先使用 `pptx_designer.compiler`。

## 二、实际编译流程

正式编译器的入口是 [`_compiler.py:210`](../src/pptx_designer/compiler/_compiler.py#L210) 的 `SVGCompiler.compile()`，流程如下：

```text
SVG 字符串
  ↓
sanitize：解析、清理、展开有限 style、推断 viewBox
  ↓
读取 viewBox 和目标 PPTX 矩形
  ↓
收集 defs：渐变、clipPath、带 id 的可引用元素
  ↓
递归遍历 SVG 节点
  ↓
应用 transform，转换 SVG 坐标到 PPT 英寸
  ↓
创建原生矩形、Freeform 或布尔几何形状
  ↓
应用 fill、stroke、渐变、透明度、虚线样式
  ↓
输出 SVGResult，并检查文本重叠
```

它不是把 SVG 当作一张图片嵌入 PPT，而是尽量生成可编辑的 PowerPoint 形状。

## 三、已实现的 SVG 能力

### 1. 基础图形

在 [`_compiler.py:376`](../src/pptx_designer/compiler/_compiler.py#L376) 附近，已处理：

- `rect`
- `circle`
- `ellipse`
- `polygon`
- `polyline`
- `line`
- `path`

普通无圆角矩形且没有描边时，会走 PowerPoint 原生矩形的快速路径。其它复杂图形通常由 [`renderer/freeform_builder.py`](../src/pptx_designer/renderer/freeform_builder.py) 生成 OOXML Freeform 自定义几何。

### 2. Path

[`compiler/_path.py`](../src/pptx_designer/compiler/_path.py) 支持常用 SVG 1.1 路径命令，包括：

`M/m`、`L/l`、`H/h`、`V/v`、`C/c`、`S/s`、`Q/q`、`T/t`、`A/a`、`Z/z`。

路径中的弧线会转换为 cubic Bézier 段，再写入 PPTX Freeform。因此它实现的是“几何等价转换”，而不是保留 SVG path 本身。

### 3. 分组、引用与变换

[`_compiler.py:604`](../src/pptx_designer/compiler/_compiler.py#L604) 递归处理：

- `g`
- `svg`
- `defs`
- `use`
- `transform`

[`compiler/_affine.py`](../src/pptx_designer/compiler/_affine.py) 支持 `translate`、`scale`、`rotate` 和 `matrix`，并将父级和子级变换组合。

### 4. 文本

[`compiler/_text.py`](../src/pptx_designer/compiler/_text.py) 负责将 SVG 文本转换为 PPTX 文本框，支持：

- `text`
- `tspan`
- 字体大小、字体族、粗体、斜体
- `text-anchor`
- `dominant-baseline`
- `alignment-baseline`
- 多行文本
- 基础 CJK 文本测量

编译结束后，编译器会扫描本次新增的文本框，并为可能的重叠写入 warning。

### 5. 填充、颜色与渐变

颜色解析支持：

- `#RGB`、`#RRGGBB`
- `rgb()`、`rgba()`
- `hsl()`、`hsla()`
- 常见 named color
- `currentColor`
- `var(--token)`
- 来自 `C` context 的颜色键

渐变模块 [`compiler/_paint.py`](../src/pptx_designer/compiler/_paint.py) 支持：

- `linearGradient`
- `radialGradient`
- 多个 `stop`
- `stop-color`
- `stop-opacity`
- `fill="url(#id)"`
- `stroke="url(#id)"`

渐变最终通过 PPTX OOXML 应用，而不是单纯依赖 `python-pptx` 的高层 API。

### 6. clipPath 和 evenodd

当 SVG 使用 `clip-path` 或 `fill-rule="evenodd"` 时，编译器会进入 [`_compiler.py:775`](../src/pptx_designer/compiler/_compiler.py#L775) 的布尔几何路径。

该流程依赖 `shapely`，大致是：

```text
SVG 曲线
  ↓
展平为多边形
  ↓
Shapely Polygon
  ↓
union / intersection / buffer(0)
  ↓
PPTX 自定义几何
```

这是实现裁剪和孔洞效果的关键，但也会带来曲线离散化、拓扑错误和复杂图形性能问题。

## 四、已确认的问题

### P0（已解决）：主渲染器曾导入未实现的旧桩

初次审计时，在 [`precision.py`](../src/pptx_designer/renderer/precision.py) 的 SVG 分支中发现了如下旧导入：

```python
from pptx_designer.renderer.svg_compiler import SVGCompileError, SVGCompiler
```

而真正的实现导出于：

```python
from pptx_designer.compiler import SVGCompileError, SVGCompiler
```

这在历史版本中导致 `PrecisionRenderer.render_slide()` 的 `svg_diagram` 分支调用未实现桩。历史运行验证结果为：

```text
pptx_designer.compiler.SVGCompiler：基础 circle 生成 1 个 shape
pptx_designer.renderer.svg_compiler.SVGCompiler：生成 0 个 shape
```

当前源码已经修复：`precision.py` 现在从 `pptx_designer.compiler` 导入，`renderer/svg_compiler.py` 也已经变为兼容转发 shim。因此该 P0 不再是当前 baseline 的问题。

### P1（已解决）：编译异常曾被静默吞掉

初次审计时，[`precision.py`](../src/pptx_designer/renderer/precision.py) 直接执行：

```python
try:
    SVGCompiler(C=C).compile(...)
except SVGCompileError:
    pass
```

当前代码已经接收编译结果、逐条记录 warning，并记录 `SVGCompileError`。因此该问题已解决；仍建议增加回归测试，避免后续重构时错误可观测性退化。

### P1：文档和示例引用不存在的模块

以下文件引用：

```python
from pptx_designer.tools.svg import svg_chart
```

涉及：

- [`README.md:165`](../README.md#L165)
- [`README.zh-CN.md:161`](../README.zh-CN.md#L161)
- [`examples/svg_diagrams.py:3`](../examples/svg_diagrams.py#L3)

但项目中不存在 `src/pptx_designer/tools/svg.py`，因此这些示例不能按文档直接运行。

### P1：测试没有覆盖 SVG 主链路

根目录虽然有多个 `test_svg*.py` 和调试脚本，但标准测试配置的 `testpaths` 是 `tests`。当前 `tests` 中没有有效的 SVG 编译器或 `PrecisionRenderer` SVG 集成测试。

已运行现有 pytest，结果为：

```text
20 passed
```

但这并不能证明 SVG 主流程正常，因为旧入口导入错误没有被测试捕获。

### P2：`SVGResult.shapes` 没有填充，且主渲染器连结果对象都没有保留

[`_compiler.py:194`](../src/pptx_designer/compiler/_compiler.py#L194) 中的 `SVGResult` 暴露了 `shapes` 字段，但编译过程中实际维护的是内部的 `shape_count`，并没有把生成的 PPTX shape 对象写入 `result.shapes`。

此外，当前 [`precision.py:1246`](../src/pptx_designer/renderer/precision.py#L1246) 直接调用 `compile()`，没有接收返回值，因此主渲染器目前连 `shape_count`、`warnings` 和 `features` 都不会消费。这里比“只检查 shape_count”更准确的判断是：当前生产调用方完全忽略 `SVGResult`。

因此当前结果对象更像统计信息，而不是完整的编译产物引用；未来如果需要对 SVG 生成的 shape 做批量透明度、动画、可访问性或后处理，缺少 shape 引用会增加实现成本。

### P2：`<use>` 目前不加载外部资源，但存在扩展时的安全边界

`<use>` 的实现位于 [`_compiler.py:634`](../src/pptx_designer/compiler/_compiler.py#L634)。它只从已在当前 SVG 文档中收集的 `_defs` 字典查找元素。对如下引用：

```svg
<use href="https://example.com/diagram.svg#node" />
```

当前代码不会发起网络请求，而是将整个 href 去掉开头的 `#` 后作为本地 id 查找；找不到时只产生 `unknown id` warning。因此当前实现没有发现“外部 SVG 被自动下载并执行”的直接漏洞。

但这仍然是一个需要明确记录的安全边界：如果未来为了兼容 SVG 标准而给 `<use>` 增加外部文件或 URL 加载，必须限制协议、禁用网络访问、限制文件系统路径，并避免递归资源引用和资源耗尽。当前 sanitizer 删除 `<script>`，也不能替代外部资源加载层面的隔离。

同理，`image`、`filter` 和 `mask` 在 [`_compiler.py:625`](../src/pptx_designer/compiler/_compiler.py#L625) 只是记录 feature、写 warning 后跳过，并不会被解析或执行。

### P2：布尔几何性能风险已通过基准复现

`clipPath` 和 `fill-rule="evenodd"` 会进入 Shapely 布尔运算。为了量化风险，在当前 Windows 环境使用 `python-pptx`、Shapely 和正式 `SVGCompiler` 做了单次冷启动后的基准，目标区域为 `10 × 7.5` 英寸：

| 场景 | 生成形状 | `compile_ms` |
|---|---:|---:|
| 100 个普通矩形 | 100 | 约 230 ms |
| 500 个普通矩形 | 500 | 约 2,396 ms |
| 1 个圆形 clipPath + 100 个矩形 | 88 | 约 1,606 ms |

这不是跨机器的性能承诺，但足以说明两个事实：

1. 大量 SVG 元素会带来明显的线性甚至超线性开销；
2. 对每个元素重复执行 clipPath 布尔计算时，100 个元素的裁剪场景明显慢于同规模普通矩形。

建议后续增加：

- clipPath 结果缓存；
- 对同一裁剪区域的批量合并；
- 路径展平精度的可配置项；
- 元素数量和编译耗时阈值；
- 大 SVG 的 warning 或降级策略。

### P2：能力声明明显宽于实际实现

README 和 CHANGELOG 使用了“完整 SVG 编译器”“full SVG 1.1 support”等表述，但实际遍历逻辑只处理有限标签。以下能力没有作为通用 SVG 功能实现：

- `image`
- `filter`
- `mask`
- 通用 CSS selector / class
- 完整 `<style>` 规则
- SVG 动画
- marker / marker-end
- pattern
- symbol 的完整 viewBox 语义
- foreignObject

遇到 `image`、`filter`、`mask` 时，编译器会写入 unsupported warning 并跳过，见 [`_compiler.py:625`](../src/pptx-designer/compiler/_compiler.py#L625)。

## 五、Sanitizer 的边界

[`compiler/_sanitizer.py`](../src/pptx_designer/compiler/_sanitizer.py) 会：

- 解析 XML；
- 删除 `<script>`；
- 删除 `<style>`；
- 将有限的 `style="..."` 属性展开；
- 从 `width` / `height` 推断缺失的 `viewBox`。

它不能提供完整 CSS 支持。例如：

```svg
<style>.box { fill: red; }</style>
<rect class="box" />
```

其中 `<style>` 会被删除，`.box` 规则不会应用。编译器会发出类似：

```text
stripped <style> element (CSS class-based styling lost)
```

对于 LLM 生成的 SVG，建议优先使用元素直接属性：

```svg
<rect fill="#FF0000" stroke="#000000" />
```

## 六、建议的修复顺序

### 第一步：统一入口

修改 `PrecisionRenderer`，从正式 compiler 包导入：

```python
from pptx_designer.compiler import SVGCompileError, SVGCompiler
```

同时建议让旧模块改成兼容转发，避免其它调用方继续得到未实现行为：

```python
from pptx_designer.compiler import SVGCompileError, SVGCompiler, SVGResult
```

### 第二步：保留错误可观测性

至少把 `SVGCompileError` 写入 renderer 日志或页面渲染结果。不要继续使用空的 `pass`。

### 第三步：统一公开 API

二选一：

1. 实现 `pptx_designer.tools.svg.svg_chart`，内部调用正式 `SVGCompiler`；
2. 删除 README 和示例中的 `tools.svg` API，统一使用 `pptx_designer.compiler.SVGCompiler`。

从当前代码结构看，建议保留一个轻量的 `tools.svg` 兼容封装，因为 README 已经公开了该 API。

### 第四步：增加自动化测试

建议新增：

```text
tests/test_svg_compiler.py
tests/test_svg_renderer_integration.py
tests/test_svg_sanitizer.py
```

至少覆盖：

- 基础形状；
- path 的绝对和相对命令；
- 文本与 tspan；
- linear/radial gradient；
- transform；
- clipPath；
- `contain`、`cover`、`stretch`；
- unsupported feature warning；
- `PrecisionRenderer` 实际生成 shape；
- 编译异常不会静默消失。

### 第五步：修正文档的能力描述

将“完整 SVG 1.1”改为：

> 支持常用 SVG 形状、路径、文本、渐变、变换、引用和裁剪，并将其转换为可编辑 PPTX 原生形状。

这样与当前实现边界一致，也能减少用户把复杂 SVG 直接交给编译器时产生的预期偏差。

## 七、最终判断

SVG 底层实现本身已经具备较好的模块化基础：路径解析、Affine 变换、paint/gradient、文本、sanitizer、dash 和主题桥接都已拆分。

当前最主要的缺陷是集成层，而不是几何算法：

```text
完整 compiler 已存在
        ↓
PrecisionRenderer 仍引用旧 renderer 桩
        ↓
svg_diagram 主流程实际不渲染
        ↓
异常又被静默吞掉
