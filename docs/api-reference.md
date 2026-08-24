# API 参考

> 适用版本：`1.0.0-beta.2`。此页仅列出稳定且已存在的公共入口；具体 SVG 支持范围见 [SVG 编译器指南](svg-guide.md)。

## Top-Level Functions

### `generate_ppt`

Generate a complete PowerPoint presentation from a text description.

```python
from pptx_designer import generate_ppt

result = generate_ppt(
    query: str,                    # Natural language description
    *,
    style: str | None = None,      # Design style (e.g., "dark cyberpunk")
    palette: str | None = None,    # Exact color palette name
    fonts: str | None = None,      # Exact font pair name
    decoration: str | None = None, # Decoration style
    layout: str | None = None,     # Layout variant
    mood: str | None = None,       # Mood category
    slides: int = 6,               # Number of slides
    output: str | None = None,     # Output file path
    fetch_images: bool = False,    # Enable AI image generation
    image_mode: str = "auto",      # Image mode
    llm_provider: str | None = None,
    llm_api_key: str | None = None,
) -> dict:
    """Returns dict with keys: output_path, slide_count, shapes_count."""
```

### `fetch_image`

Generate or search for an image.

```python
from pptx_designer import fetch_image

result = fetch_image(
    keywords: str,                 # Search/generation prompt
    *,
    mode: str = "auto",           # placeholder|search|generate|enhance|auto
    llm_provider: str | None = None,
    llm_api_key: str | None = None,
    width: int = 1920,
    height: int = 1080,
) -> dict:
    """Returns dict with keys: path, mode, provider, keywords."""
```

### `extract_design_dna`

Extract design analysis from an existing .pptx file.

```python
from pptx_designer import extract_design_dna

dna = extract_design_dna(pptx_path: str) -> dict
```

---

## Tools

### `pptx_designer.tools.shapes`

Shape creation functions.

| Function | Description |
|----------|-------------|
| `rect(slide, left, top, width, height, *, fill, ...)` | Rectangle |
| `rounded_rect(slide, left, top, width, height, *, fill, radius, ...)` | Rounded rectangle |
| `oval(slide, left, top, width, height, *, fill, ...)` | Oval |
| `hexagon(slide, cx, cy, size, *, fill, ...)` | Hexagon |
| `diamond(slide, cx, cy, size, *, fill, ...)` | Diamond |
| `star(slide, cx, cy, radius, *, points, fill, ...)` | Star |
| `triangle(slide, left, top, width, height, *, fill, ...)` | Triangle |
| `arrow(slide, left, top, width, height, *, fill, ...)` | Arrow |
| `chevron(slide, left, top, width, height, *, fill, ...)` | Chevron |
| `cloud(slide, left, top, width, height, *, fill, ...)` | Cloud |
| `heart(slide, cx, cy, size, *, fill, ...)` | Heart |

### `pptx_designer.tools.text`

Text functions.

| Function | Description |
|----------|-------------|
| `text(slide, left, top, width, height, txt, *, font_size, color, bold, align)` | Single-line text |
| `multiline(slide, left, top, width, height, lines, *, font_size, color)` | Multi-line text |
| `gradient_text(slide, left, top, width, height, txt, *, preset, font_size)` | Gradient text |
| `dramatic_text(slide, left, top, width, height, big, small, ...)` | Size-contrast text |
| `vertical_text(slide, left, top, width, height, txt, ...)` | Vertical CJK text |

### `pptx_designer.tools.images`

Image functions.

| Function | Description |
|----------|-------------|
| `cover_image(slide, left, top, width, height, image_path)` | Cover-fit image |
| `circle_image(slide, cx, cy, radius, image_path, ...)` | Circle-clipped image |
| `ai_image(slide, left, top, width, height, keywords, ...)` | AI generate + place |
| `duotone_image(slide, left, top, width, height, image_path, ...)` | Duotone effect |

### `pptx_designer.tools.charts`

Chart functions.

| Function | Description |
|----------|-------------|
| `bar_chart(slide, left, top, data, ...)` | Horizontal bar chart |
| `donut_chart(slide, cx, cy, radius, sectors, ...)` | Donut/pie chart |
| `native_chart(slide, left, top, width, height, chart_type, ...)` | Native PPT chart |

---

## Diagrams

```python
from pptx_designer.diagrams import flowchart, timeline, swot, matrix, cycle, funnel

flowchart.render(slide, steps, region, style)
timeline.render(slide, events, region, style)
swot.render(slide, data, region, style)
```

---

## Effects

```python
from pptx_designer.effects import text_fx, shape_fx, animation

# Text effects
text_fx.apply_gradient(run, stops)
text_fx.apply_shadow(shape, blur=8)
text_fx.apply_glow(shape, color="#FF0000")

# Shape effects
shape_fx.apply_gradient(shape, "#FF0000", "#0000FF")
shape_fx.apply_3d(shape, depth=10)
shape_fx.apply_pattern(shape, "cross", fg="#000", bg="#FFF")

# Animation
animation.add_transition(slide, "morph")
animation.add_entrance(slide, shape_id, "fade_in")
```

---

## Compiler

```python
from pptx_designer.compiler import SVGCompileError, SVGCompiler

compiler = SVGCompiler()
result = compiler.compile(
    svg_text,
    slide,
    rect=(1.0, 1.0, 8.0, 4.0),  # x, y, width, height; inches
)

print(result.shape_count)
print(result.warnings)
print(result.features)
```

For the convenient Build-mode wrapper:

```python
from pptx_designer.tools.svg import svg_chart

result = svg_chart(slide, svg_text, x=1.0, y=1.0, w=8.0, h=4.0)
```

`SVGResult` includes `shape_count`, `shapes`, `native_shapes`, `warnings`, `errors`, `features`, `feature_levels`, `source_to_output`, `metrics`, and `compile_ms`. Invalid SVG or a configured safety limit raises `SVGCompileError`; unsupported individual elements may instead be skipped with a warning. Production callers should handle both paths.
