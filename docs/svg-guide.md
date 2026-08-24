# SVG 编译器指南

> 适用版本：`1.0.0-beta.2`。
> 定位：把常见静态 SVG 转换为 PowerPoint 原生、尽可能可编辑的形状和文本。

## 快速使用

```python
from pptx_designer.tools.svg import svg_chart
from pptx_designer.compiler import SVGCompileError

svg = '''<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="360" height="160" rx="16" fill="#0F766E"/>
  <text x="200" y="112" text-anchor="middle" font-size="28"
        font-weight="bold" fill="#FFFFFF">可编辑标题</text>
</svg>'''

try:
    report = svg_chart(slide, svg, x=1, y=1, w=8, h=4)
except SVGCompileError as exc:
    # 格式错误、输入安全限额或无法安全原生化的情况
    raise RuntimeError(f"SVG 编译失败：{exc}") from exc

print(report.shape_count)
for warning in report.warnings:
    print("SVG warning:", warning)
```

`x`、`y`、`w`、`h` 的单位是英寸；SVG 内部坐标由 `viewBox` 映射到该目标矩形。优先提供 `viewBox`。没有 `viewBox` 时，编译器使用默认坐标空间，结果可能不符合预期。

## 返回值与诊断

`svg_chart()` 与 `SVGCompiler.compile()` 都返回 `SVGResult`（兼容别名 `SVGRenderReport`）：

| 字段 | 用途 |
|---|---|
| `shape_count` / `shapes` | 本次新建的 PowerPoint 对象数量及对象引用 |
| `native_shapes` | 当前原生输出对象 |
| `warnings` / `errors` | 跳过、近似、文本重叠及其他诊断信息 |
| `features` / `feature_levels` | 输入 SVG 使用的特性与当前处理级别 |
| `source_to_output` | SVG 源 `id` 到本次输出对象的运行期映射 |
| `metrics` / `compile_ms` | 节点数、路径命令数、耗时等诊断数据 |
| `ir_document` | 供诊断和后续规划使用的只读 SVG IR 快照 |

`source_to_output` 中保存的是本次运行的对象引用；保存并重新打开 PPTX 后，不能把它当作永久定位标识。

## 已支持的常用能力

- 图形：`rect`、`circle`、`ellipse`、`line`、`polygon`、`polyline`、`path`；
- 结构：`svg`、`g`、`defs`、内部 `use`；
- 文本：`text`、`tspan`、常用字体、字号、粗斜体、锚点与基础透明度；
- 绘制：实色、描边、虚线、线性/径向渐变、常用 transform；
- 裁剪：受支持形状的 `clipPath` 与 `fill-rule="evenodd"` 近似流程；
- 样式：内联属性和受限 CSS 选择器/级联处理。

这些能力输出的是 PowerPoint 原生对象，通常可在 PowerPoint 中直接选中和编辑。

## 重要边界

以下不是完整或像素级兼容能力：

- `filter`、`mask`、`pattern`、混合模式、`isolation` 与 SVG 动画；
- 外部资源、外部 `<use>` 引用和远程 URL；
- `textPath`、复杂文字描边、复杂字体排版；
- `gradientUnits="userSpaceOnUse"`、`spreadMethod="reflect/repeat"` 等复杂渐变语义；
- `symbol`/`use` 的完整 viewBox 与 `preserveAspectRatio` 语义。

遇到不支持元素时，编译器可能警告并跳过该元素；遇到会导致原生输出明显错误的组合语义（例如某些 group opacity 情况）会抛出 `SVGCompileError`。不要以 `shape_count > 0` 作为唯一验收条件；应同时检查 warning 和生成的 PPTX。

## 输入安全与资源限制

编译器在解析后限制 SVG 大小、节点数、路径命令数和树深度，以避免不受控的 CPU 或内存消耗。默认阈值可在创建编译器时按受信任程度调整：

```python
from pptx_designer.compiler import SVGCompiler

compiler = SVGCompiler(limits={
    "max_svg_bytes": 500_000,
    "max_nodes": 2_000,
    "max_path_commands": 20_000,
    "max_tree_depth": 100,
})
report = compiler.compile(svg, slide, (1, 1, 8, 4))
```

不要为不可信输入简单取消所有限制；应保留合理上限并捕获 `SVGCompileError`。

## 面向 LLM 生成 SVG 的建议

1. 使用 `viewBox`，坐标采用明确数值；
2. 优先使用 `rect`、`path`、`text`、`line`、简单渐变和内联样式；
3. 为需追踪的文字和形状提供唯一 `id`；
4. 避免 filter/mask/pattern、外部图片/引用与复杂 CSS；
5. 每次生成后记录 `warnings`、`features` 和 `metrics`，并打开 PPTX 人工检查。

项目后续方向是“可编辑性优先的近似降级”，详见 [P3 路线图](svg-p3-editability-first-roadmap.md)。该路线尚未实现，不应据此假定当前支持局部 PNG 或稳定的持久 source-to-output 映射。
