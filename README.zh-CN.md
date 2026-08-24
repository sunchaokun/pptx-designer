<div align="center">

# pptx-designer

**为 LLM 设计的 Python PPT 生成库**

[![PyPI version](https://img.shields.io/pypi/v/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![Python](https://img.shields.io/pypi/pyversions/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

用可组合的原子函数构建像素级精确、完全可编辑的 `.pptx` —— 专为 AI 编码助手设计。

[安装](#安装) · [快速开始](#快速开始) · [Build 模式](#build-模式) · [LLM 集成](#llm-集成)

</div>

---

## 为什么选择 pptx-designer？

pptx-designer 为 **LLM 时代** 而生。当 AI 编码助手生成 Python 代码来创建演示文稿时，它需要：

- **清晰、可组合的 API** —— 而不是黑盒魔法
- **确定性输出** —— 相同代码，相同结果
- **完全可编辑** —— 每个形状、每段文字、每张图表
- **核心功能无需 LLM** —— 可离线使用

| 能力 | 原生 python-pptx | SaaS AI 工具 | **pptx-designer** |
|---|---|---|---|
| **LLM 友好 API** | 底层（坐标） | 黑盒 | **90+ 可组合原子** |
| **确定性** | 是 | 否（随机） | **是** |
| **可编辑输出** | 是 | 有时 | **始终可编辑** |
| **设计系统** | 无 | 私有 | **40,000+ 内置组合** |
| **SVG → PPTX** | 否 | 否 | **SVG 编译器**（常用形状/路径/渐变） |
| **图表** | 手动拼形状 | 有限 | **10 种原生引擎** |
| **品牌合规** | 手动 | 部分 | **企业 VI 模式** |
| **价格** | 免费 | ¥70-140/月 | **免费（MIT）** |

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

### 为 LLM 设计

当 AI 编码助手生成 PPT 代码时，输出如下：

```python
from pptx_designer.tools.shapes import rect, rounded_rect
from pptx_designer.tools.text import text, multiline
from pptx_designer.tools.cards import page_header, kpi_card
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

### 为人类开发者

```python
from pptx_designer import generate_ppt

# generate_ppt 内部使用 Build 模式
# 提供结构化内容可获得最佳效果
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

# 或提供简单描述（LLM 会展开为结构化内容）
result = generate_ppt("AI 创业融资路演", style="dark cyberpunk")
```

---

## Build 模式

所有演示文稿使用 **可组合原子** 构建 —— 简单、可预测的函数，创建形状、文字、图片和图表。

### 形状

```python
from pptx_designer.tools.shapes import rect, rounded_rect, oval, hexagon, diamond, star

rect(slide, x=1, y=1, w=4, h=2, fill="#3B82F6")
rounded_rect(slide, x=1, y=1, w=4, h=2, fill="#3B82F6", radius="lg")
oval(slide, cx=3, cy=2, size=1.5, fill="#10B981")
hexagon(slide, cx=6, cy=2, size=1.5, fill="#F59E0B")
```

### 文字

```python
from pptx_designer.tools.text import text, multiline, gradient_text, dramatic_text

text(slide, x=1, y=1, w=8, h=1, "Hello World", font_size=32, bold=True)
multiline(slide, x=1, y=2, w=8, h=3, ["第1行", "第2行", "第3行"], font_size=14)
gradient_text(slide, x=1, y=1, w=8, h=1, "渐变文字", preset="gold-shine", font_size=48)
```

### 图表

```python
from pptx_designer.tools.charts import bar_chart, donut_chart, native_chart

bar_chart(slide, x=1, y=2, data=[("Q1", "85%", 8500000), ("Q2", "92%", 9200000)])
donut_chart(slide, cx=8, cy=3, radius=1.5, sectors=[("A", "40%", "#3B82F6"), ("B", "60%", "#10B981")])
```

### 图表引擎

```python
from pptx_designer.diagrams import flowchart, timeline, swot, matrix

flowchart.render(slide, steps=["步骤1", "步骤2", "步骤3"], region=region, style=style)
timeline.render(slide, events=[("2024", "发布"), ("2025", "扩展")], region=region, style=style)
```

### SVG → PPTX

```python
from pptx_designer.tools.svg import svg_chart

svg_chart(slide, svg_text="<svg>...</svg>", x=1, y=1, w=8, h=6)
```

### 特效

```python
from pptx_designer.effects import text_fx, shape_fx

text_fx.apply_shadow(shape, blur=8, distance=3, color="#000000")
shape_fx.apply_3d(shape, depth=10, material="powder")
shape_fx.apply_pattern(shape, "cross", fg="#000000", bg="#FFFFFF")
```

---

## LLM 集成

pptx-designer 专为 AI 编码助手设计。以下是它有效的原因：

### 1. 清晰的函数签名

```python
def rect(slide, left, top, width, height, *, fill, line=None, C=None) -> Shape
def text(slide, left, top, width, height, txt, *, font_size=12, color="text_body", bold=False) -> Shape
def kpi_card(slide, left, top, width, height, number, label, trend="", *, C=None) -> Shape
```

LLM 可以理解并生成这些函数调用，无需猜测。

### 2. 可组合原子

每个函数只做一件事。LLM 像搭积木一样组合它们：

```python
# LLM 生成的代码
page_header(slide, "标题", "副标题", C=C)
kpi_card(slide, 1, 2, 3, 1.5, "$12M", "营收", "+20%", C=C)
kpi_card(slide, 5, 2, 3, 1.5, "89%", "留存率", "+5pp", C=C)
rect(slide, 0.5, 6.8, 12.3, 0.08, fill=C["primary"])
```

### 3. 确定性输出

相同代码始终生成相同 PPT。无随机性，无变异。

### 4. 40,000+ 风格预设

LLM 可用自然语言选择风格：

```python
from pptx_designer.renderer.theme import ThemeComposer

theme = ThemeComposer().compose(style="dark cyberpunk")
# 返回: colors, typography, decoration, layout_variant
```

### 5. 核心功能无需 API Key

所有形状/文字/图表/图表/特效函数可离线使用。AI 图片生成是可选的。

### 给 LLM 的系统提示

在 AI 编码助手中使用 pptx-designer 时，使用此系统提示：

```
你是使用 pptx-designer 的 PPT 生成专家。

关键规则：
1. 始终从 pptx_designer.tools.* 导入形状、文字、图表
2. 使用 C 字典管理颜色（primary, accent, text_dark, text_body, background）
3. 使用 PALETTES 字典获取预定义配色：from pptx_designer.data import PALETTES
4. 每个内容页使用 page_header()
5. 指标用 kpi_card()，数据用 bar_chart()
6. 最后用 prs.save(path) 保存

可用模块：
- pptx_designer.tools.shapes: rect, rounded_rect, oval, hexagon, diamond, star, triangle, arrow
- pptx_designer.tools.text: text, multiline, gradient_text, dramatic_text, vertical_text
- pptx_designer.tools.charts: bar_chart, donut_chart, native_chart, comparison_bars
- pptx_designer.tools.cards: kpi_card, highlight_cards, code_block, section_divider, hero_slide
- pptx_designer.data: PALETTES (192 种配色), TYPOGRAPHY (74 种字体), STYLES (84 种风格)
```

---

## 风格系统

40,000+ 组合来自离散原子：

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

### 设计知识库

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

## 企业模式（VI Build）

基于模板的品牌合规生成：

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
python -m ruff check src/
```

---

## 许可证

MIT 许可证 —— 详见 [LICENSE](LICENSE)。
