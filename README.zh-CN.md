<div align="center">

# pptx-designer

**面向 LLM 编程工作流的、代码优先的可编辑 PPT Python 标准库**

[![PyPI version](https://img.shields.io/pypi/v/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![Python](https://img.shields.io/pypi/pyversions/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

用可组合的演示文稿原语、设计数据与 PowerPoint 原生对象，将可审查的 Python 代码构建为可编辑 `.pptx`。

[安装](#安装) · [快速开始](#快速开始) · [Build 模式](#build-模式) · [LLM 编写手册](https://github.com/sunchaokun/pptx-designer/blob/main/docs/llm-authoring-guide.md) · [文档索引](https://github.com/sunchaokun/pptx-designer/tree/main/docs)

</div>

---

## 为什么选择 pptx-designer？

越来越多的软件在 LLM 的协作下完成。此时真正适合审查、版本管理、测试和迭代的单位是生成出来的 **代码**，而不是不可追溯的提示词结果。`pptx-designer` 是为这种工作方式设计的 Python 标准库：AI 助手负责组合明确的函数调用，开发者仍可检查、修改、测试并重复运行同一份 Python 文件。

它不是演示文稿 SaaS，也不是提示词到图片的黑盒。只要所选组件能够表达，输出的 `.pptx` 就由 PowerPoint 原生对象构成。

| 设计取舍 | 实际含义 |
|---|---|
| **代码即唯一事实来源** | 布局、文案、颜色和数据保存在 Python 中，可进入 Git 审查。 |
| **面向 LLM 的公共 API** | 小而具名、可组合的辅助函数减少生成和修改代码时的歧义。 |
| **确定性构建路径** | 相同输入、包版本、字体和运行环境对应可重复的构建目标。 |
| **原生对象优先** | 形状、文本、图表、图示和已支持 SVG 元素尽可能输出为原生 PPT 对象。 |
| **渐进式控制** | 先用 `generate_ppt()`；需要精确构图时转入 Build 模式。 |
| **AI 服务可选** | 核心布局与绘制不需要 API Key；图片生成/搜索按需启用。 |

### 范围与真实边界

`pptx-designer` 在 `python-pptx` 之上提供面向演示文稿的高层封装；它不替代 PowerPoint 渲染引擎，也不实现所有演示文稿或 SVG 特性。原生可编辑性和视觉还原度取决于具体组件及目标 Office 环境。SVG 编译器有意只支持可编辑子集，而不是浏览器级完整 SVG。请把 PPTX 视为构建产物：交付前应在目标应用中打开并审查关键页面。

---

## 安装

```bash
pip install pptx-designer
```

可选功能：

```bash
pip install pptx-designer[images]      # 素材搜索（Unsplash/Pexels）
pip install pptx-designer[ai-images]   # AI 图片生成（OpenAI 等）
```

**要求**：Python 3.10+

---

## 快速开始

### 一页代码优先的幻灯片

当 AI 编码助手生成 PPT 代码时，输出如下：

```python
from pptx_designer.tools.shapes import rect
from pptx_designer.tools.text import text, multiline
from pptx_designer.tools.cards import kpi_card
from pptx_designer.tools.layout import page_header
from pptx_designer.tools.images import cover_image
from pptx_designer.core.pipeline import Presentation

C = {
    "primary": "#1D78FA",
    "accent": "#FF6B35",
    "text_dark": "#1A1A1A",
    "text_body": "#4A4A4A",
    "background": "#FFFFFF",
}

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

page_header(slide, "Q4 营收报告", "财务摘要", C=C)
kpi_card(slide, 1.0, 2.0, 3.5, 1.5, "$12.8M", "营收", "+23%", C=C)
kpi_card(slide, 5.0, 2.0, 3.5, 1.5, "89%", "留存率", "+5pp", C=C)
rect(slide, 0.5, 6.8, 12.3, 0.08, fill=C["primary"])

prs.save("output/q4_report.pptx")
```

### 由结构化内容生成完整演示文稿

```python
from pptx_designer import generate_ppt

# 结构化内容会让生成结果更可预测、更便于审查。
result = generate_ppt(
    content={
        "title": "Q4 营收报告",
        "pages": [
            {"goal": "hook", "title": "Q4 2026", "subtitle": "创纪录季度"},
            {"goal": "content", "title": "关键指标", "bullets": ["营收: ¥1.28亿", "增长: +23%"]},
        ]
    },
    style="professional",
    output="output/report.pptx",
)

# 简单描述使用包内的规划器，不需要配置 LLM 服务商。
result = generate_ppt("AI 创业融资路演", style="dark cyberpunk")
```

---

## Build 模式

所有演示文稿使用 **可组合原子** 构建 —— 简单、可预测的函数，创建形状、文字、图片和图表。

### 形状

```python
from pptx_designer.tools.shapes import rect, rrect, oval, hexagon, diamond, star5

rect(slide, left=1, top=1, width=4, height=2, fill="#3B82F6")
rrect(slide, left=1, top=3.3, width=4, height=2, fill="#2563EB")
oval(slide, left=6, top=1, width=2, height=2, fill="#10B981")
hexagon(slide, cx=9, cy=2, size=1.5, fill="#F59E0B")
```

### 文字

```python
from pptx_designer.tools.text import text, multiline, gradient_text, dramatic_text

text(slide, left=1, top=1, width=8, height=1, txt="Hello World", font_size=32, bold=True)
multiline(slide, left=1, top=2, width=8, height=3, lines=["第1行", "第2行", "第3行"], font_size=14)
gradient_text(slide, left=1, top=1, width=8, height=1, txt="渐变文字", preset="gold-shine", font_size=48)
```

### 图表

```python
from pptx_designer.tools.charts import bar_chart

bar_chart(slide, left=2, top=2, data=[("Q1", 0.85, "85%"), ("Q2", 0.92, "92%")])
```

### 图表引擎

```python
from pptx_designer.diagrams import DiagramStyle, FlowchartDiagram, Region, TimelineDiagram

style = DiagramStyle()

FlowchartDiagram(
    data={"nodes": [{"label": "发现"}, {"label": "构建"}, {"label": "审查"}]},
    style=style,
    region=Region(left=1, top=2, width=10, height=2),
).render(slide)

TimelineDiagram(
    data={"events": [{"year": "2024", "title": "发布"}, {"year": "2025", "title": "扩展"}]},
    style=style,
    region=Region(left=1, top=4.5, width=10, height=2),
).render(slide)
```

### SVG → PPTX

```python
from pptx_designer.tools.svg import svg_chart

svg = """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="360" height="160" rx="16" fill="#2563EB"/>
  <text x="200" y="112" text-anchor="middle" font-size="28"
        font-weight="bold" fill="#FFFFFF">可编辑 SVG</text>
</svg>"""

result = svg_chart(slide, svg, x=1, y=1, w=8, h=4)
print(result.shape_count, result.warnings)
```

编译器会将已支持的 SVG 子集转换成 PowerPoint 原生形状和文本。它支持常用几何图形、路径、文本/tspan、变换、渐变、`defs`/`use` 以及受限的裁剪路径流程；不承诺 filter、mask、pattern、动画、外部资源和部分 SVG paint 语义的像素级还原。生产使用时请检查 `result.warnings`。输入要求、报错处理与限制见 [SVG 指南](https://github.com/sunchaokun/pptx-designer/blob/main/docs/svg-guide.md)。

### 特效

```python
from pptx_designer.effects import text_fx, shape_fx

text_fx.apply_shadow(shape, blur=8, distance=3, color="#000000")
shape_fx.apply_3d(shape, depth=10, material="powder")
shape_fx.apply_pattern(shape, "cross", fg="#000000", bg="#FFFFFF")
```

---

## LLM 编程工作流

本库的目标是让助手编写普通 Python，而不是把版式决策隐藏在远程生成服务中。推荐流程：

1. 在代码中定义页面内容、数据和设计约束；
2. 让 LLM 组合公开的 `pptx_designer` API；
3. 像审查普通应用代码一样审查生成的 Python；
4. 运行代码、检查 `.pptx`，并将代码和测试纳入版本控制。

这形成可持续的反馈闭环：一次性的标题或数字修改可以直接在 PowerPoint 中完成；需要可重复的修改则应改动对应 Python 调用后重新构建。

### 1. 明确的函数签名

```python
def rect(slide, left, top, width, height, fill, line=None, C=None) -> Shape
def text(slide, left, top, width, height, txt, font_size=12, color="text_body", bold=False, ...) -> Shape
def kpi_card(slide, left, top, width, height, number, label, trend="", trend_up=True, C=None, ...) -> list[Shape]
```

具名参数和聚焦的辅助函数为 LLM 提供受限目标，也让代码审查更清晰。

### 2. 可组合的演示文稿原语

每个辅助函数职责单一。LLM 可以像搭积木一样组合它们，开发者仍保有每个调用的控制权：

```python
# LLM 生成的代码
page_header(slide, "标题", "副标题", C=C)
kpi_card(slide, 1, 2, 3, 1.5, "$12M", "营收", "+20%", C=C)
kpi_card(slide, 5, 2, 3, 1.5, "89%", "留存率", "+5pp", C=C)
rect(slide, 0.5, 6.8, 12.3, 0.08, fill=C["primary"])
```

### 3. 主题数据与显式覆盖

内置的配色、字体和风格数据可帮助 LLM 从协调的默认值开始；正式交付时，应固定明确选项以获得可重复的构建：

```python
from pptx_designer.renderer.theme import ThemeComposer

theme = ThemeComposer().compose(style="dark cyberpunk")
# 返回: colors, typography, decoration, layout_variant
```

### 4. 核心绘制功能无需 API Key

所有形状/文字/图表/图表/特效函数可离线使用。AI 图片生成是可选的。

### 面向 LLM 的安全提示词

在 AI 编码助手中使用 pptx-designer 时，使用此系统提示：

```
你是使用 pptx-designer 的 PPT 生成专家。

规则：
1. 只使用有文档的公开 `pptx_designer` 导入；不要臆造辅助函数或使用私有模块。
2. 创建 `Presentation()`，添加空白 slide，最后使用 `prs.save(path)` 保存。
3. 位置和尺寸使用具名参数；坐标单位为英寸。
4. 颜色放在 `C` 字典中，或选择明确的 theme。
5. 优先使用原生形状、文字、图表和图示；编译 SVG 后检查 `SVGResult.warnings`。
6. 必须生成可运行 Python 文件；PPT 未被打开或渲染检查前，不得声称页面已经正确。

可用模块：
- pptx_designer.tools.shapes: rect, rrect, oval, hexagon, diamond, star5, triangle, arrow
- pptx_designer.tools.text: text, multiline, gradient_text, dramatic_text, vertical_text
- pptx_designer.tools.charts: bar_chart, comparison_bars
- pptx_designer.tools.cards: kpi_card, highlight_cards, code_block, section_divider, hero_slide
- pptx_designer.tools.layout: page_header, top_bar, page_number
- pptx_designer.data: PALETTES (192 种配色), TYPOGRAPHY (74 种字体), STYLES (84 种风格)
```

---

## 风格系统

库内含配色、字体和风格预设数据。自然语言选风格适合探索；需要可重复构建时应使用明确值：

```python
from pptx_designer.renderer.theme import ThemeComposer

# 自然语言
theme = ThemeComposer().compose(style="warm fintech")

# 精确控制
theme = ThemeComposer().compose(
    palette="cyber-neon",
    fonts="tech-mono",
    decoration="neon-glow",
    layout="sidebar-left",
)
```

### 内置设计数据

| 数据库 | 数量 | 访问方式 |
|--------|------:|----------|
| 配色方案 | 192 | `from pptx_designer.data import PALETTES` |
| 字体对 | 74 | `from pptx_designer.data import TYPOGRAPHY` |
| 风格预设 | 84 | `from pptx_designer.data import STYLES` |

内置主题原子（ThemeComposer 用）：

| 原子 | 数量 | 示例 |
|------|------:|------|
| 硬编码配色 | 30 | ocean-blue, cyber-neon, golden-luxury |
| 硬编码字体 | 15 | modern-sans, tech-mono, elegant-serif |
| 装饰 | 10 | accent-bar, neon-glow, brush-stroke |
| 布局 | 12 | standard, sidebar-left, grid-2x2 |

---

## 模板与企业工具

包内还包含面向模板和品牌工作流的项目扫描、提案等工具。这些 API 是可选项；代码优先的 Build 模式仍是共同基础。

```python
from pptx_designer.enterprise import ProjectScanner, ProposalGenerator

# 扫描项目资产
scanner = ProjectScanner()
assets = scanner.scan("./my-project")

# 生成风格提案
proposals = ProposalGenerator().generate(
    query="Q4 业务回顾",
    template=assets.template_path,
)

# 用确认的风格生成
from pptx_designer import generate_ppt
result = generate_ppt(
    content=assets.content_raw,
    template=assets.template_path,
    confirmed_proposal="A",
)
```

---

## 配置

### 可选 API Key（仅用于 AI 图片功能）

| 变量 | 提供商 | 说明 |
|------|--------|------|
| `ARK_API_KEY` | Seedream（字节跳动） | 图片生成 |
| `OPENAI_API_KEY` | OpenAI | GPT Image / DALL-E |
| `GEMINI_API_KEY` | Google | Gemini 图片 |
| `DASHSCOPE_API_KEY` | 阿里巴巴 | 通义万相 |
| `UNSPLASH_ACCESS_KEY` | Unsplash | 素材搜索 |
| `PEXELS_API_KEY` | Pexels | 素材搜索 |

---

## 开发

```bash
git clone https://github.com/sunchaokun/pptx-designer.git
cd pptx-designer
pip install -e ".[dev]"

python -m pytest tests/ -q
python -m ruff check src/pptx_designer/compiler tests/test_compiler tests/test_svg_tools.py tests/test_svg_compiler_integration.py
```

## 文档

- [快速开始](https://github.com/sunchaokun/pptx-designer/blob/main/docs/getting-started.md)
- [API 参考](https://github.com/sunchaokun/pptx-designer/blob/main/docs/api-reference.md)
- [LLM 编写手册](https://github.com/sunchaokun/pptx-designer/blob/main/docs/llm-authoring-guide.md)
- [SVG 编译器指南](https://github.com/sunchaokun/pptx-designer/blob/main/docs/svg-guide.md)
- [更新日志](https://github.com/sunchaokun/pptx-designer/blob/main/CHANGELOG.md)

## 高级案例

[examples/](https://github.com/sunchaokun/pptx-designer/tree/main/examples) 提供三个完整、可编辑的四页高级案例：奢侈品香氛画册、时装编辑册与建筑愿景书。每个案例均包含构建代码、原创视觉资源和生成的 `.pptx` 文件。

---

## 许可证

MIT 许可证 —— 详见 [LICENSE](LICENSE)。
