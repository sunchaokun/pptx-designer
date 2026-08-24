<div align="center">

# pptx-designer

**The Python library for LLMs to generate professional PowerPoint presentations**

[![PyPI version](https://img.shields.io/pypi/v/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![Python](https://img.shields.io/pypi/pyversions/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Build pixel-perfect, fully editable `.pptx` presentations with composable atoms — designed for AI coding assistants.

[Installation](#installation) · [Quick Start](#quick-start) · [Build Mode](#build-mode) · [SVG Guide](docs/svg-guide.md) · [Documentation](docs/README.md)

</div>

---

## Why pptx-designer?

pptx-designer is built for the **LLM era**. When AI coding assistants generate Python code to create presentations, they need:

- **Clear, composable APIs** — not magic black boxes
- **Deterministic output** — same code, same result
- **Full editability** — every shape, every text, every chart
- **No LLM dependency for core features** — offline-capable

| Capability | Raw python-pptx | SaaS AI tools | **pptx-designer** |
|---|---|---|---|
| **LLM-friendly API** | Low-level (coordinates) | Black box | **90+ composable atoms** |
| **Deterministic** | Yes | No (varies) | **Yes** |
| **Editable output** | Yes | Sometimes | **Native-first; supported SVG objects are editable** |
| **Design system** | None | Proprietary | **40,000+ built-in combos** |
| **SVG → PPTX** | No | No | **Editable SVG subset compiler** |
| **Diagrams** | Manual shapes | Limited | **10 native engines** |
| **Brand compliance** | Manual | Partial | **Enterprise VI mode** |
| **Price** | Free | $10-20/mo | **Free (MIT)** |

---

## Installation

```bash
pip install pptx-designer
```

Optional extras:

```bash
pip install pptx-designer[images]      # Stock photo search (Unsplash/Pexels)
pip install pptx-designer[ai-images]   # AI image generation (OpenAI, etc.)
```

**Requirements**: Python 3.10+

---

## Quick Start

### For LLMs

When an AI coding assistant generates PPT code, it produces:

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

page_header(slide, "Q4 Revenue Report", "Financial Summary", C=C)
kpi_card(slide, 1.0, 2.0, 3.5, 1.5, "$12.8M", "Revenue", "+23%", C=C)
kpi_card(slide, 5.0, 2.0, 3.5, 1.5, "89%", "Retention", "+5pp", C=C)
rect(slide, 0.5, 6.8, 12.3, 0.08, fill=C["primary"])

prs.save("output/q4_report.pptx")
```

### For humans

```python
from pptx_designer import generate_ppt

# generate_ppt uses Build mode internally
# Provide structured content for best results
result = generate_ppt(
    content={
        "title": "Q4 Revenue Report",
        "pages": [
            {"goal": "hook", "title": "Q4 2026", "subtitle": "Record Quarter"},
            {"goal": "content", "title": "Key Metrics", "bullets": ["Revenue: $12.8M", "Growth: +23%"]},
        ]
    },
    style="professional",
    output="output/report.pptx",
)

# Or provide a simple query (LLM will expand to structured content)
result = generate_ppt("AI startup pitch deck", style="dark cyberpunk")
```

---

## Build Mode

All presentations are built using **composable atoms** — simple, predictable functions that create shapes, text, images, and charts.

### Shapes

```python
from pptx_designer.tools.shapes import rect, rounded_rect, oval, hexagon, diamond, star

rect(slide, x=1, y=1, w=4, h=2, fill="#3B82F6")
rounded_rect(slide, x=1, y=1, w=4, h=2, fill="#3B82F6", radius="lg")
oval(slide, cx=3, cy=2, size=1.5, fill="#10B981")
hexagon(slide, cx=6, cy=2, size=1.5, fill="#F59E0B")
```

### Text

```python
from pptx_designer.tools.text import text, multiline, gradient_text, dramatic_text

text(slide, x=1, y=1, w=8, h=1, "Hello World", font_size=32, bold=True)
multiline(slide, x=1, y=2, w=8, h=3, ["Line 1", "Line 2", "Line 3"], font_size=14)
gradient_text(slide, x=1, y=1, w=8, h=1, "Gradient", preset="gold-shine", font_size=48)
```

### Charts

```python
from pptx_designer.tools.charts import bar_chart, donut_chart, native_chart

bar_chart(slide, x=1, y=2, data=[("Q1", "85%", 8500000), ("Q2", "92%", 9200000)])
donut_chart(slide, cx=8, cy=3, radius=1.5, sectors=[("A", "40%", "#3B82F6"), ("B", "60%", "#10B981")])
```

### Diagrams

```python
from pptx_designer.diagrams import flowchart, timeline, swot, matrix
from pptx_designer.renderer.layout import Region

# Define region (position and size)
region = Region(left=1, top=2, width=10, height=5)

flowchart.render(slide, steps=["Step 1", "Step 2", "Step 3"], region=region)
timeline.render(slide, events=[("2024", "Launch"), ("2025", "Scale")], region=region)
```

### SVG → PPTX

```python
from pptx_designer.tools.svg import svg_chart

svg = """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="360" height="160" rx="16" fill="#2563EB"/>
  <text x="200" y="112" text-anchor="middle" font-size="28"
        font-weight="bold" fill="#FFFFFF">Editable SVG</text>
</svg>"""

result = svg_chart(slide, svg, x=1, y=1, w=8, h=4)
print(result.shape_count, result.warnings)
```

The compiler creates native PowerPoint shapes and text for its supported SVG subset. It supports common geometry, paths, text/tspan, transforms, gradients, `defs`/`use`, and a constrained clipping path workflow. Filters, masks, patterns, animations, external resources, and some SVG paint semantics are not full-fidelity features. Always inspect `result.warnings` for a production SVG. See the [SVG guide](docs/svg-guide.md) for supported input, error handling, and limits.

### Effects

```python
from pptx_designer.effects import text_fx, shape_fx

text_fx.apply_shadow(shape, blur=8, distance=3, color="#000000")
shape_fx.apply_3d(shape, depth=10, material="powder")
shape_fx.apply_pattern(shape, "cross", fg="#000000", bg="#FFFFFF")
```

---

## LLM Integration

pptx-designer is designed for AI coding assistants. Here's why it works:

### 1. Clear function signatures

```python
def rect(slide, left, top, width, height, *, fill, line=None, C=None) -> Shape
def text(slide, left, top, width, height, txt, *, font_size=12, color="text_body", bold=False) -> Shape
def kpi_card(slide, left, top, width, height, number, label, trend="", *, C=None) -> Shape
```

LLMs can understand and generate calls to these functions without guessing.

### 2. Composable atoms

Each function does one thing well. LLMs combine them like building blocks:

```python
# LLM generates this code
page_header(slide, "Title", "Subtitle", C=C)
kpi_card(slide, 1, 2, 3, 1.5, "$12M", "Revenue", "+20%", C=C)
kpi_card(slide, 5, 2, 3, 1.5, "89%", "Retention", "+5pp", C=C)
rect(slide, 0.5, 6.8, 12.3, 0.08, fill=C["primary"])
```

### 3. Deterministic output

Same code always produces the same PPT. No randomness, no variation.

### 4. 40,000+ style presets

LLMs can select styles with natural language:

```python
from pptx_designer.renderer.theme import ThemeComposer

theme = ThemeComposer().compose(style="dark cyberpunk")
# Returns: colors, typography, decoration, layout_variant
```

### 5. No API keys for core features

All shape/text/chart/diagram/effect functions work offline. AI image generation is optional.

### System prompt for LLMs

When using pptx-designer with AI coding assistants, use this system prompt:

```
You are a PPT generation expert using pptx-designer.

Key rules:
1. Always import from pptx_designer.tools.* for shapes, text, charts
2. Use C dict for colors (primary, accent, text_dark, text_body, background)
3. Use PALETTES dict for pre-defined color schemes: from pptx_designer.data import PALETTES
4. Use page_header() for every content slide
5. Use kpi_card() for metrics, bar_chart() for data
6. Save with prs.save(path) at the end

Available modules:
- pptx_designer.tools.shapes: rect, rounded_rect, oval, hexagon, diamond, star, triangle, arrow
- pptx_designer.tools.text: text, multiline, gradient_text, dramatic_text, vertical_text
- pptx_designer.tools.charts: bar_chart, donut_chart, native_chart, comparison_bars
- pptx_designer.tools.cards: kpi_card, highlight_cards, code_block, section_divider, hero_slide
- pptx_designer.data: PALETTES (192 colors), TYPOGRAPHY (74 fonts), STYLES (84 presets)
```

---

## Style System

40,000+ combinations from discrete atoms:

```python
from pptx_designer.renderer.theme import ThemeComposer

# Natural language
theme = ThemeComposer().compose(style="warm fintech")

# Exact control
theme = ThemeComposer().compose(
    palette="cyber-neon",
    fonts="tech-mono",
    decoration="neon-glow",
    layout="sidebar-left",
)
```

### Design knowledge base

| Database | Count | Access |
|----------|------:|--------|
| Color palettes | 192 | `from pptx_designer.data import PALETTES` |
| Font pairs | 74 | `from pptx_designer.data import TYPOGRAPHY` |
| Style presets | 84 | `from pptx_designer.data import STYLES` |

Built-in theme atoms (for ThemeComposer):

| Atom | Count | Examples |
|------|------:|---------|
| Hardcoded palettes | 30 | ocean-blue, cyber-neon, golden-luxury |
| Hardcoded fonts | 15 | modern-sans, tech-mono, elegant-serif |
| Decorations | 10 | accent-bar, neon-glow, brush-stroke |
| Layouts | 12 | standard, sidebar-left, grid-2x2 |

---

## Enterprise Mode (VI Build)

Brand-compliant generation from templates:

```python
from pptx_designer.enterprise import ProjectScanner, ProposalGenerator

# Scan project for assets
scanner = ProjectScanner()
assets = scanner.scan("./my-project")

# Generate style proposals
proposals = ProposalGenerator().generate(
    query="Q4 business review",
    template=assets.template_path,
)

# Generate with confirmed style
from pptx_designer import generate_ppt
result = generate_ppt(
    content=assets.content_raw,
    template=assets.template_path,
    confirmed_proposal="A",
)
```

---

## Configuration

### Optional API keys (for AI image features only)

| Variable | Provider | Description |
|----------|----------|-------------|
| `ARK_API_KEY` | Seedream (ByteDance) | Image generation |
| `OPENAI_API_KEY` | OpenAI | GPT Image / DALL-E |
| `GEMINI_API_KEY` | Google | Gemini images |
| `DASHSCOPE_API_KEY` | Alibaba | Wanx images |
| `UNSPLASH_ACCESS_KEY` | Unsplash | Stock photos |
| `PEXELS_API_KEY` | Pexels | Stock photos |

---

## Development

```bash
git clone https://github.com/sunchaokun/pptx-designer.git
cd pptx-designer
pip install -e ".[dev]"

python -m pytest tests/ -q
python -m ruff check src/pptx_designer/compiler tests/test_compiler tests/test_svg_tools.py tests/test_svg_compiler_integration.py
```

## Documentation

- [Getting started](docs/getting-started.md)
- [API reference](docs/api-reference.md)
- [SVG compiler guide](docs/svg-guide.md)
- [Changelog](CHANGELOG.md)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
