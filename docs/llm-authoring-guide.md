# LLM 编写手册：使用 pptx-designer 生成可编辑 PPTX

> 适用版本：`1.0.0b7`。
> 目标读者：生成、审查或修改 `pptx-designer` Python 代码的 LLM 与开发者。
> 本文是用户文档与训练/上下文材料；只描述当前公开且已验证的 API。

## 1. 不可违背的契约

`pptx-designer` 是一个 Python 库。它的输入是 Python 代码和数据，输出是 `.pptx` 文件；不是一个需要调用远程 LLM 的聊天接口。

生成代码时必须遵守：

1. 只从 `pptx_designer` 的公开模块导入，不能臆造函数、参数或模块；
2. 所有位置和尺寸使用 **英寸**，参数名为 `left`、`top`、`width`、`height`；
3. 使用 `Presentation()` 创建文稿，并通过 `prs.slides.add_slide(prs.slide_layouts[6])` 创建空白页；
4. 每个脚本最后调用 `prs.save("output/name.pptx")`；
5. 对重要结果运行脚本并打开 PPTX，不能仅凭代码声称页面正确；
6. 优先输出原生形状、文本、图表和图示；SVG 编译后必须检查 warning；
7. 不要使用私有属性（名称以 `_` 开头）实现业务功能，除非任务明确要求修改库内部。

## 2. 最小可运行模板

以下是任何 Build 模式脚本的推荐起点：

```python
from pptx_designer.core.pipeline import Presentation
from pptx_designer.tools.layout import page_header
from pptx_designer.tools.shapes import rect
from pptx_designer.tools.text import text

C = {
    "primary": "#2563EB",
    "accent": "#F97316",
    "background": "#FFFFFF",
    "text_dark": "#172554",
    "text_body": "#475569",
    "text_muted": "#64748B",
    "border": "#E2E8F0",
}

prs = Presentation()  # default: 16:9, 13.333 × 7.5 inches
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank slide

rect(slide, left=0, top=0, width=13.333, height=7.5, fill="background", C=C)
page_header(slide, "Quarterly review", "Code-first PowerPoint", C=C)
text(slide, left=0.7, top=1.5, width=8.5, height=0.5,
     txt="Every important object is created by explicit Python code.",
     font_size=20, color="text_body", C=C)

prs.save("output/quarterly-review.pptx")
```

`C` 是颜色角色字典。传入 `fill="primary"` 或 `color="text_body"` 时，函数会从 `C` 中解析颜色；也可以直接传入 `"#RRGGBB"`。

## 3. 公开模块与可靠 API

### 3.1 文稿和主题

| 导入 | 何时使用 | 关键事实 |
|---|---|---|
| `from pptx_designer import Presentation, set_presentation_theme, set_slide_theme` | 创建或读取文稿，并应用 Build Mode 主题继承 | `Presentation(template_path=None, theme=None)` 默认使用 16:9；主题只在当前 presentation/slide 生效。 |
| `from pptx_designer import generate_ppt` | 快速生成完整 deck | 可传 `query` 或结构化 `content`；二者都是 FreeStyle 输入，不是 Build Mode。可传已解析 `theme` 锁定视觉结果。 |
| `from pptx_designer import svg_chart` | 将静态 SVG 编译为原生对象 | 推荐 SVG 公共入口；必须检查返回的 `warnings` 和 `errors`。 |
| `from pptx_designer.renderer.theme import ThemeComposer` | 需要主题数据 | 正式交付应显式指定 palette/fonts 等，避免依赖未固定的默认选择。 |

结构化生成的最小数据格式：

```python
from pptx_designer import generate_ppt

result = generate_ppt(
    content={
        "title": "Business review",
        "pages": [
            {"goal": "hook", "title": "2026 Q1", "subtitle": "A focused update"},
            {"goal": "content", "title": "Metrics", "bullets": ["Revenue +23%", "Retention 89%"]},
        ],
    },
    style="professional",
    output="output/business-review.pptx",
)
```

主题锁定后的 Build Mode 推荐写法：

```python
from pptx_designer import Presentation
from pptx_designer.renderer.theme import ThemeComposer
from pptx_designer.tools.layout import page_header
from pptx_designer.tools.shapes import rect
from pptx_designer.tools.text import text

theme = ThemeComposer().compose(style="warm-elegant", seed=17)
prs = Presentation(theme=theme)
slide = prs.slides.add_slide(prs.slide_layouts[6])

# 现有 helpers 自动继承 background / font_body 等；显式参数仍可局部覆盖。
rect(slide, 0, 0, 13.333, 7.5, "background")
page_header(slide, "Quarterly review", "Theme-aware and editable")
text(slide, 0.7, 1.5, 8.5, 0.5, "The presentation inherits its visual language.", font_size=20)
```

不要把 Theme Lock 当作页面模板。主题负责颜色角色、字体、装饰和空间倾向；LLM
仍须根据每页目标选择构图、焦点和公共 API 组合。

### 3.1.1 VI Build：模板规则由 Build 消费

模板分析必须使用统一的 `ResolvedDesignContext`，不能把 `extract_design_dna()`
的原始结果另存为下游不会读取的 VI 字典。推荐顺序为：

1. `extract_design_context(template.pptx)` 获取确定性证据；
2. 人工确认可写文本槽位及其 bounds，低置信度槽位不得自动替换；
3. 选择一个提取出的 archetype，并给出其允许的组件；
4. 用 `VIBuildSession` 先预检资产、锁定项和槽位容量；
5. 仅当状态为 `READY` 时创建新页，随后执行 PPTX → PDF → PNG 审查。

需要照片的 archetype 在缺少合规本地图片时会返回 `NEEDS_ASSET`，而不是生成
没有视觉锚点的纯文字或色块页。系统固定使用 16:9（13.333 × 7.5 英寸）画布。
`generate_ppt(content=...)` 仍属于 FreeStyle，不会自动启用 VI Build。

### 3.2 基础形状：`pptx_designer.tools.shapes`

所有形状函数接收 `slide` 和英寸坐标。最常用函数如下：

| 函数 | 签名要点 | 用途 |
|---|---|---|
| `rect` | `(slide, left, top, width, height, fill, line=None, C=None)` | 矩形、背景、分隔条。 |
| `rrect` | 与 `rect` 相同 | 圆角矩形；没有 `rounded_rect()`。 |
| `oval` | 与 `rect` 相同 | 椭圆；不是 `cx/cy/size` 签名。 |
| `hexagon`、`diamond`、`star5` | `(slide, cx, cy, size, fill, ...)` | 中心点图形。 |
| `triangle`、`arrow`、`chevron` | `(slide, left, top, width, height, fill, ...)` | 方向或流程元素。 |
| `dashed_rect` | 额外支持 `line_color`、`line_width`、`dash` | 虚线框。 |

```python
from pptx_designer.tools.shapes import arrow, oval, rect, rrect

rrect(slide, left=0.8, top=2.0, width=3.0, height=1.2, fill="primary", C=C)
arrow(slide, left=4.1, top=2.35, width=0.9, height=0.5, fill="accent", C=C)
oval(slide, left=5.3, top=2.0, width=1.2, height=1.2, fill="#10B981", C=C)
rect(slide, left=0.8, top=3.6, width=8.0, height=0.02, fill="border", C=C)
```

### 3.3 文字：`pptx_designer.tools.text`

| 函数 | 适用场景 | 注意事项 |
|---|---|---|
| `text(...)` | 单段文字 | `txt` 为文字参数；`align` 仅接受 `left`、`center`、`right`。 |
| `multiline(...)` | 多段文字 | `lines` 是字符串列表。 |
| `dramatic_text(...)` | 大数字/主副标题组合 | 返回多个 shape。 |
| `gradient_text(...)` | 需要文字渐变 | 使用 PowerPoint OOXML 效果，仍应在目标 Office 中检查。 |
| `vertical_text(...)` | CJK 竖排文字 | 需要显式设置适合目标机器的字体。 |
| `text_outline(...)`、`text_shadow(...)`、`text_glow(...)` | 装饰效果 | 是近似/效果实现，不适合承载唯一关键信息。 |

```python
from pptx_designer.tools.text import multiline, text

text(slide, left=0.8, top=4.0, width=6.5, height=0.55,
     txt="Revenue", font_size=28, color="text_dark", bold=True, C=C)
multiline(slide, left=0.8, top=4.6, width=6.5, height=1.0,
          lines=["+23% year over year", "Growth is led by enterprise accounts"],
          font_size=15, color="text_body", C=C)
```

### 3.4 页面与组件

| 导入 | 可靠入口 |
|---|---|
| `pptx_designer.tools.layout` | `page_header`、`top_bar`、`page_number`、`set_widescreen`、`clean_save` |
| `pptx_designer.tools.cards` | `kpi_card`、`highlight_cards`、`code_block`、`section_divider`、`hero_slide`、`cta_slide` |

特别注意：`page_header` 来自 **`tools.layout`**，不在 `tools.cards`。

```python
from pptx_designer.tools.cards import kpi_card
from pptx_designer.tools.layout import page_header, page_number

page_header(slide, "Key metrics", "Q1 operating review", C=C)
kpi_card(slide, left=0.8, top=1.7, width=3.0, height=1.5,
         number="$12.8M", label="Revenue", trend="+23%", C=C)
page_number(slide, current=2, total=6, C=C)
```

### 3.5 图表：`pptx_designer.tools.charts`

| 函数 | 输入约定 |
|---|---|
| `bar_chart(slide, left, top, data, ...)` | `data` 中每一项为 `(label, fraction, displayed_value)`；`fraction` 为 `0.0–1.0` 数值。 |
| `comparison_bars(slide, left, top, metrics, ...)` | 每一项为 `(label, old_text, new_text, old_fraction, new_fraction)`。 |
| `donut_chart(slide, cx, cy, radius, inner_radius, sectors, ...)` | 当前 beta 版本不要作为 LLM 生成代码的默认选择；多分区默认路径依赖尚未实现的 native chart builder。 |
| `native_chart(slide, left, top, width, height, chart_type, ...)` | 当前 beta 版本不可作为可靠 API；其底层 `ChartBuilder` 尚未实现。 |

```python
from pptx_designer.tools.charts import bar_chart

bar_chart(slide, left=2.0, top=2.0,
          data=[("Revenue", 0.85, "$12.8M"), ("Retention", 0.89, "89%")], C=C)
```

当前应优先使用 `bar_chart()` 和 `comparison_bars()`，或由基础形状组合数据展示。待 native chart builder 完成并具备回归测试后，再将 `native_chart()` 和多分区 `donut_chart()` 纳入默认训练语料。

### 3.6 图示：`pptx_designer.diagrams`

图示不是 `flowchart.render(...)` 形式的模块级函数。必须创建 diagram 实例，再调用 `.render(slide)`：

```python
from pptx_designer.diagrams import DiagramStyle, FlowchartDiagram, Region

diagram = FlowchartDiagram(
    data={
        "direction": "horizontal",
        "nodes": [{"label": "Discover"}, {"label": "Build"}, {"label": "Review"}],
    },
    style=DiagramStyle(),
    region=Region(left=1.0, top=2.0, width=11.0, height=2.0),
)
diagram.render(slide)
```

可用的类包括 `FlowchartDiagram`、`TimelineDiagram`、`SwotDiagram`、`MatrixDiagram`、`TableDiagram`、`HierarchyDiagram`、`VennDiagram`、`CycleDiagram`、`FunnelDiagram` 和 `PyramidDiagram`。不同图示的数据结构不同；生成复杂图示前应先读取对应模块 docstring 或已有测试。

### 3.7 图片与 SVG

| 入口 | 规则 |
|---|---|
| `cover_image(slide, left, top, width, height, image_path)` | 本地文件不存在时返回 `None`，生成代码应处理该情况。 |
| `ai_image(...)` | 图片搜索/生成的高层可选入口；可能需要 API Key。 |
| `svg_chart(slide, svg_text, x, y, w, h, C=None)` | 将受支持 SVG 子集编译为可编辑原生对象，返回 `SVGResult`。 |

```python
from pptx_designer.compiler import SVGCompileError
from pptx_designer import svg_chart

svg = '''<svg viewBox="0 0 240 120" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="220" height="100" rx="12" fill="#2563EB"/>
  <text x="120" y="70" text-anchor="middle" font-size="22" fill="#FFFFFF">Native SVG text</text>
</svg>'''

try:
    report = svg_chart(slide, svg, x=8.0, y=5.5, w=4.5, h=1.5, C=C)
except SVGCompileError as exc:
    raise RuntimeError(f"SVG compilation failed: {exc}") from exc

if report.warnings:
    print("SVG warnings:", report.warnings)
```

SVG 不是浏览器级实现。详细支持边界、warning 与输入限额见 [SVG 编译器指南](svg-guide.md)。

## 4. 排版和颜色规则

- 默认页面为 13.333 × 7.5 英寸；不要假设 A4 或 4:3；
- 给边缘留出约 0.5–0.8 英寸安全区，避免把文字贴在页边；
- 同一页面先定义 `C`，不要在每个元素上散落无意义的随机颜色；
- 文本框 `height` 必须与字号和文案长度相称；长文本用 `multiline`，不要依赖自动换行挤进很小的区域；
- 先放背景，再放内容，最后放装饰；PowerPoint shape 的追加顺序就是视觉叠放顺序；
- 对需要后续定位的对象，可在创建后设置 `shape.name = "meaningful-key"`。

## 5. 常见错误：禁止生成

| 不要这样做 | 原因与替代 |
|---|---|
| `from pptx_designer.tools.shapes import rounded_rect` | 不存在；使用 `rrect`。 |
| `rect(slide, x=1, y=1, w=4, h=2, ...)` | 参数名不正确；使用 `left/top/width/height`。 |
| `oval(slide, cx=..., cy=..., size=...)` | `oval` 使用矩形边界；使用 `left/top/width/height`。 |
| `from pptx_designer.tools.cards import page_header` | 错误模块；从 `tools.layout` 导入。 |
| `flowchart.render(...)` | 不是公开的模块级对象；创建 `FlowchartDiagram(...)`。 |
| 不检查 `svg_chart()` 的结果 | SVG 可以产生 warning 或抛出 `SVGCompileError`。 |
| 直接使用 `slide.shapes.add_picture()` 拉伸图片 | 优先 `cover_image()` 保持裁切比例。 |
| 在没有验证的情况下声称“像素级一致” | PowerPoint、字体和 Office 版本都会影响最终外观。 |

## 6. 生成后的验收清单

生成或修改 PPT 构建脚本后，LLM/开发者应执行：

1. 运行 Python 脚本，确认 `.pptx` 已写入预期路径；
2. 重新用 `python-pptx` 打开文件，确认 slide 数和 shape 数合理；
3. 检查文字是否溢出、重叠或被裁切；
4. 检查图片路径、SVG warning、图表数据和颜色角色；
5. 在目标 PowerPoint 或 LibreOffice 中打开/渲染关键页面；
6. 将可复现的输入数据、主题选择和构建脚本一并提交。

最小 reopen 检查：

```python
from pptx import Presentation as OpenPresentation

check = OpenPresentation("output/quarterly-review.pptx")
assert len(check.slides) >= 1
assert len(check.slides[0].shapes) >= 1
```

## 7. 可直接提供给 LLM 的简版指令

```text
You are writing a runnable Python build script using pptx-designer.

- Use only documented public imports from pptx_designer.
- Create Presentation(), add prs.slide_layouts[6], and save a .pptx file.
- Use inches: left, top, width, height. Do not invent x/y/w/h aliases.
- Use rrect, not rounded_rect; import page_header from tools.layout.
- Prefer native shapes, text, charts, and diagram classes over screenshots.
- For SVG, call svg_chart(), catch SVGCompileError, and inspect warnings.
- Keep colors in a C dictionary and use named arguments.
- Run the script and verify the resulting PPTX before reporting success.
```

在需要中文输出时，可以保留同一套 API 与坐标规则，只需将文案和 `font_name`/`C["font_cjk"]` 选择为目标环境中已安装的字体。
