<div align="center">

# pptx-designer

**A code-first Python library for editable PowerPoint generation in LLM coding workflows**

[![PyPI version](https://img.shields.io/pypi/v/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![Python](https://img.shields.io/pypi/pyversions/pptx-designer.svg)](https://pypi.org/project/pptx-designer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Turn reviewed Python code into editable `.pptx` files with composable presentation primitives, design data, and native PowerPoint objects.

[Installation](#installation) · [Quick Start](#quick-start) · [Build Mode](#build-mode) · [LLM Authoring Guide](https://github.com/sunchaokun/pptx-designer/blob/main/docs/llm-authoring-guide.md) · [Documentation](https://github.com/sunchaokun/pptx-designer/tree/main/docs)

</div>

---

## Why pptx-designer?

More software is now written with an LLM in the loop. That makes the generated **code**—rather than an opaque prompt result—the useful unit of review, versioning, testing, and iteration. `pptx-designer` is a standard Python package built for that workflow: an assistant can compose explicit function calls, and a developer can inspect, modify, test, and rerun the same file.

It is deliberately not a presentation SaaS or a prompt-to-image black box. The output is a `.pptx` built from PowerPoint-native objects whenever the chosen component can express them.

| Design choice | What it means in practice |
|---|---|
| **Code is the source of truth** | Layout, wording, colours, and data live in Python and can be reviewed in Git. |
| **LLM-friendly public APIs** | Small, named, composable helpers reduce ambiguity when code is generated or edited by an assistant. |
| **Deterministic build path** | The same inputs, package version, fonts, and runtime produce a repeatable build target. |
| **Editable by default** | Shapes, text, diagrams, and supported SVG elements are emitted as native PPT objects where possible. |
| **Progressive control** | Start with `generate_ppt()`; move to Build mode when a slide needs exact composition. |
| **Optional AI services** | Core layout and drawing do not require an API key; image generation/search is opt-in. |

### Scope and honest boundaries

`pptx-designer` adds a higher-level, presentation-oriented layer on top of `python-pptx`; it does not replace PowerPoint's rendering engine or implement every presentation/SVG feature. Native editability and visual fidelity depend on the component and target Office environment. The SVG compiler intentionally supports an editable subset, not browser-complete SVG. Treat generated PPTX files as build artifacts: open them in the target application and review important slides before delivery.

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

### A code-first slide

When an AI coding assistant generates PPT code, it produces:

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

page_header(slide, "Q4 Revenue Report", "Financial Summary", C=C)
kpi_card(slide, 1.0, 2.0, 3.5, 1.5, "$12.8M", "Revenue", "+23%", C=C)
kpi_card(slide, 5.0, 2.0, 3.5, 1.5, "89%", "Retention", "+5pp", C=C)
rect(slide, 0.5, 6.8, 12.3, 0.08, fill=C["primary"])

prs.save("output/q4_report.pptx")
```

### A generated deck from structured content

```python
from pptx_designer import generate_ppt

# Structured content makes the generated deck predictable and reviewable.
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

# A simple query uses the package's built-in planner; no LLM provider is required.
result = generate_ppt("AI startup pitch deck", style="dark cyberpunk")
```

### Pick a distinct style instead of relying on the default

When `style` is omitted, the planner may choose similar themes for similar
requests. Ask the library for deterministic, topic-aware presets, then pass one
choice back into `generate_ppt()` explicitly:

```python
from pptx_designer import generate_ppt, recommend_styles

options = recommend_styles("AI technology platform")
# AI/technology -> dark-tech, neon, sci
chosen = options[0]

result = generate_ppt(
    "AI technology platform",
    style=chosen["style"],
    # Optional atom overrides. Use `layout` in Python; the CLI accepts
    # `--layout-variant` for the same setting.
    decoration=chosen["decoration"],
    layout=chosen["layout"],
    style_seed=17,
    output="output/ai-platform.pptx",
)

print(result["theme_atoms"])  # Persist the actual palette/font/decor/layout selected.
```

`style_seed` makes automatic atom selection reproducible. Explicit `palette`,
`fonts`, `decoration`, `layout`, and `mood` values take precedence over a preset.
The current professional renderer applies the palette to slide rendering;
decoration and layout atoms are returned and reserved for renderer-level layout
composition, rather than promising a visual rearrangement they do not yet make.

---

## Build Mode

All presentations are built using **composable atoms** — simple, predictable functions that create shapes, text, images, and charts.

### Exact-composition contract

Build Mode is not a fixed-layout generator. The author (or Build Planner)
decides the page goal, information hierarchy, content relationships, and the
exact composition. Every atom has explicit bounds; its recipe may also set
font, fill, line, data, and `z_index`. The renderer executes those instructions
as editable PowerPoint objects instead of selecting a layout from a content
type.

For a reusable component, a `BuildSpec` references `component_id`. For
atomic production work, it carries an inline `recipe`; that inline recipe takes
priority and preserves the authored geometry. A resolved theme can be attached
to the presentation or one slide, so public helpers inherit colors and fonts;
explicit helper values still override the inherited context.

When building against a VI template, this remains true: Build owns content
composition; the VI adapter only supplies visual grammar, tokens, reviewed
fixed layers, capacity, and safe/forbidden-zone constraints. It never chooses
a content archetype from `content_type` or `variant_id`.

### Shapes

```python
from pptx_designer.tools.shapes import rect, rrect, oval, hexagon, diamond, star5

rect(slide, left=1, top=1, width=4, height=2, fill="#3B82F6")
rrect(slide, left=1, top=3.3, width=4, height=2, fill="#2563EB")
oval(slide, left=6, top=1, width=2, height=2, fill="#10B981")
hexagon(slide, cx=9, cy=2, size=1.5, fill="#F59E0B")
```

### Text

```python
from pptx_designer.tools.text import text, multiline, gradient_text, dramatic_text

text(slide, left=1, top=1, width=8, height=1, txt="Hello World", font_size=32, bold=True)
multiline(slide, left=1, top=2, width=8, height=3, lines=["Line 1", "Line 2", "Line 3"], font_size=14)
gradient_text(slide, left=1, top=1, width=8, height=1, txt="Gradient", preset="gold-shine", font_size=48)
```

### Charts

```python
from pptx_designer.tools.charts import bar_chart

bar_chart(slide, left=2, top=2, data=[("Q1", 0.85, "85%"), ("Q2", 0.92, "92%")])
```

### Diagrams

```python
from pptx_designer.diagrams import DiagramStyle, FlowchartDiagram, Region, TimelineDiagram

region = Region(left=1, top=2, width=10, height=5)
style = DiagramStyle()

FlowchartDiagram(
    data={"nodes": [{"label": "Discover"}, {"label": "Build"}, {"label": "Review"}]},
    style=style,
    region=Region(left=1, top=2, width=10, height=2),
).render(slide)

TimelineDiagram(
    data={"events": [{"year": "2024", "title": "Launch"}, {"year": "2025", "title": "Scale"}]},
    style=style,
    region=Region(left=1, top=4.5, width=10, height=2),
).render(slide)
```

### SVG → PPTX

```python
from pptx_designer import svg_chart

svg = """<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="20" width="360" height="160" rx="16" fill="#2563EB"/>
  <text x="200" y="112" text-anchor="middle" font-size="28"
        font-weight="bold" fill="#FFFFFF">Editable SVG</text>
</svg>"""

result = svg_chart(slide, svg, x=1, y=1, w=8, h=4)
print(result.shape_count, result.warnings)
```

`from pptx_designer import svg_chart` is the recommended public import. `from pptx_designer.tools import svg_chart` and the legacy `from pptx_designer.tools.svg import svg_chart` remain valid. The function returns `SVGResult`; inspect `shape_count`, `warnings`, and `errors` before delivery.

The compiler creates native PowerPoint shapes and text for its supported SVG subset. It supports common geometry, paths, text/tspan, transforms, gradients, `defs`/`use`, and a constrained clipping path workflow. Filters, masks, patterns, animations, external resources, and some SVG paint semantics are not full-fidelity features. Always inspect `result.warnings` for a production SVG. See the [SVG guide](https://github.com/sunchaokun/pptx-designer/blob/main/docs/svg-guide.md) for supported input, error handling, and limits.

### Effects

```python
from pptx_designer.effects import text_fx, shape_fx

text_fx.apply_shadow(shape, blur=8, distance=3, color="#000000")
shape_fx.apply_3d(shape, depth=10, material="powder")
shape_fx.apply_pattern(shape, "cross", fg="#000000", bg="#FFFFFF")
```

---

## LLM coding workflow

The library is designed for an assistant to write ordinary Python—not to hide layout decisions behind a remote generation service. A reliable workflow is:

1. Define slide content, data, and design constraints in code.
2. Ask the LLM to compose public `pptx_designer` APIs.
3. Review the generated Python as normal application code.
4. Run it, inspect the `.pptx`, and keep the code and tests in version control.

This creates a practical feedback loop: a user can edit a title or value in PowerPoint for a one-off change, or edit the keyed Python call and rebuild when the change should be reproducible.

### 1. Explicit function signatures

```python
def rect(slide, left, top, width, height, fill, line=None, C=None) -> Shape
def text(slide, left, top, width, height, txt, font_size=12, color="text_body", bold=False, ...) -> Shape
def kpi_card(slide, left, top, width, height, number, label, trend="", trend_up=True, C=None, ...) -> list[Shape]
```

Named arguments and focused helpers give an LLM a constrained target and give reviewers readable code.

### 2. Composable presentation primitives

Each helper has a narrow responsibility. An LLM can combine them like building blocks, while a developer retains control over every call:

```python
# LLM generates this code
page_header(slide, "Title", "Subtitle", C=C)
kpi_card(slide, 1, 2, 3, 1.5, "$12M", "Revenue", "+20%", C=C)
kpi_card(slide, 5, 2, 3, 1.5, "89%", "Retention", "+5pp", C=C)
rect(slide, 0.5, 6.8, 12.3, 0.08, fill=C["primary"])
```

### 3. Theme data and explicit overrides

The built-in palette, typography, and style data help an assistant begin from coherent defaults. For production work, pin explicit choices when visual consistency matters:

```python
from pptx_designer.renderer.theme import ThemeComposer

theme = ThemeComposer().compose(style="dark cyberpunk")
# Returns: colors, typography, decoration, layout_variant
```

### 4. No API keys for core drawing features

All shape/text/chart/diagram/effect functions work offline. AI image generation is optional.

### Prompting an LLM safely

When using pptx-designer with AI coding assistants, use this system prompt:

```
You are a PPT generation expert using pptx-designer.

Rules:
1. Use only documented public `pptx_designer` imports; do not invent helpers or private modules.
2. Create a `Presentation()`, add a blank slide, and save the result with `prs.save(path)`.
3. Use named arguments for positions and dimensions. Coordinates are inches.
4. Keep colours in a `C` dictionary or select an explicit theme.
5. Prefer native shapes, text, charts, and diagrams. Check `SVGResult.warnings` after compiling SVG.
6. Generate a runnable Python file and do not claim the PPT is correct until it has been opened or rendered for review.

Available modules:
- pptx_designer.tools.shapes: rect, rrect, oval, hexagon, diamond, star5, triangle, arrow
- pptx_designer.tools.text: text, multiline, gradient_text, dramatic_text, vertical_text
- pptx_designer.tools.charts: bar_chart, comparison_bars
- pptx_designer.tools.cards: kpi_card, highlight_cards, code_block, section_divider, hero_slide
- pptx_designer.tools.layout: page_header, top_bar, page_number
- pptx_designer.data: PALETTES (192 colors), TYPOGRAPHY (74 fonts), STYLES (84 presets)
```

---

## Style system

The library ships palette, typography, and style-preset data. Natural-language style selection is a convenience for exploration; explicit values are more appropriate for a reproducible build:

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

### Built-in design data

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

## Template and enterprise utilities

The package also includes project-scanning and proposal utilities for template- and brand-led workflows. These APIs are optional: the code-first Build mode remains the common foundation.

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

### Image generation and `.env`

Put a `.env` beside your own `build.py` / project files (or in one of its
parent directories), then keep it out of Git. Do **not** put credentials in
the installed `pptx_designer` package directory: upgrades and virtual
environments will replace it.

[`.env.example`](.env.example) is the checked-in reference file. Copy it to
your own project root, then replace only the provider you plan to use:

```powershell
Copy-Item .env.example .env
```

```bash
cp .env.example .env
```

The package reads the nearest `.env` from the working directory upward.
Process environment variables take precedence over values in `.env`.

```dotenv
# .env in your presentation project
PPT_IMAGE_LLM_PROVIDER=gpt-image
OPENAI_API_KEY=your-api-key
# OPENAI_IMAGE_MODEL=gpt-image-1
```

Test the configuration without writing image-request code yourself:

```powershell
pptx-designer image "editorial fragrance bottle on black stone" --image-mode auto -v
```

`auto` resolves sources in this order:

1. A `host_image_generator` supplied by an Agent host.
2. Explicit Python arguments or CLI options.
3. Project `.env` and process environment variables.
4. An Agent provider configuration that explicitly references an environment key.
5. Stock-image search, then no image / the calling layout's placeholder.

When `PPT_IMAGE_LLM_PROVIDER` is omitted, `auto` selects a provider from one
configured provider key (`OPENAI_API_KEY`, `ARK_API_KEY`, `GEMINI_API_KEY`,
`DASHSCOPE_API_KEY`, or `MOONSHOT_API_KEY`).

```python
from pptx_designer import fetch_image

asset = fetch_image(
    "editorial fragrance bottle on black stone",
    mode="auto",
    goal="hook",
)
print(asset["path"])  # local file path, or None when every source declines
```

Agent hosts can also inject a `host_image_generator` callback. This is the
safe bridge for a host-owned image tool (such as an Agent image-generation
capability) when no image API is configured: the callback must return a local
image file path, which `pptx-designer` then places in the slide. The library
does not attempt to invoke Agent tools or login credentials by itself. This
hook is for Agent/Skill implementers, not ordinary `build.py` users:

```python
from pptx_designer import fetch_image

def generate_with_host_tool(*, keywords, emotion, goal, width, height):
    # The Agent host calls its own image tool and returns the saved local path.
    return "C:/project/assets/generated/hero.png"

asset = fetch_image(
    "quiet modern architecture at dawn",
    mode="auto",
    host_image_generator=generate_with_host_tool,
)
```

A Codex provider entry is considered only when it references an environment
key. Login/session tokens are never treated as image API keys, and the
provider's ordinary text model is never treated as an image model. Set an
explicit `image_model` in the Agent configuration when a non-default image
model is required.

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

- [Getting started](https://github.com/sunchaokun/pptx-designer/blob/main/docs/getting-started.md)
- [API reference](https://github.com/sunchaokun/pptx-designer/blob/main/docs/api-reference.md)
- [LLM authoring guide](https://github.com/sunchaokun/pptx-designer/blob/main/docs/llm-authoring-guide.md)
- [SVG compiler guide](https://github.com/sunchaokun/pptx-designer/blob/main/docs/svg-guide.md)
- [Changelog](https://github.com/sunchaokun/pptx-designer/blob/main/CHANGELOG.md)

## Advanced examples

Explore complete four-page, editable decks in [examples/](https://github.com/sunchaokun/pptx-designer/tree/main/examples): a luxury fragrance lookbook, a couture editorial deck, and an architecture vision book. Every example includes the build script, original image assets, and its generated `.pptx` output.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
