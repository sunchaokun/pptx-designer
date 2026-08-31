# API 参考

> 适用版本：`1.0.0b10`。此页仅列出稳定且已存在的公共入口；具体 SVG 支持范围见 [SVG 编译器指南](svg-guide.md)。

## Top-Level Functions

### `generate_ppt`

Generate a complete PowerPoint presentation from a text description.

```python
from pptx_designer import generate_ppt

def generate_ppt(
    query: str = "",               # Natural language description
    *,
    content: dict | None = None,   # Structured FreeStyle page plan
    style: str | None = None,      # Design style (e.g., "dark cyberpunk")
    palette: str | None = None,    # Exact color palette name
    fonts: str | None = None,      # Exact font pair name
    decoration: str | None = None, # Decoration style
    layout: str | None = None,     # Layout variant
    layout_variant: str | None = None, # Alias for layout
    mood: str | None = None,       # Mood category
    style_seed: int | None = None, # Local theme-selection seed
    theme: dict | None = None,     # Complete ThemeComposer-resolved theme
    template: str | None = None,   # Optional source template
    slides: int | None = None,     # Number of slides for query mode
    output: str = "output.pptx",  # Output file path
    **kwargs,
) -> dict:
    ...
```

`query` and `content` are FreeStyle inputs; `content` is a structured page
plan, not Build Mode. Passing a previously resolved `theme` prevents a second
theme-discovery step and supports reproducible delivery generation. The value
must be a complete result from `ThemeComposer.compose()`; partial template/VI
contexts are rejected with `ValueError`. When `theme` is supplied, `style`,
`palette`, `fonts`, `decoration`, `layout`, `layout_variant`, `mood`, and
`style_seed` are ignored and reported through `UserWarning` plus
`theme_application.ignored_arguments`.

Use `validate_resolved_theme(theme)` to validate a Theme Lock before passing it
across process or storage boundaries:

```python
from pptx_designer import validate_resolved_theme

validate_resolved_theme(theme)  # raises ValueError for an incomplete or invalid theme
```

### `Presentation`, `set_presentation_theme`, and `set_slide_theme`

Build Mode can attach a resolved theme once, then use existing helpers without
repeating `C` and `typo` on every call.

```python
from pptx_designer import Presentation, set_presentation_theme, set_slide_theme
from pptx_designer.renderer.theme import ThemeComposer

theme = ThemeComposer().compose(style="warm-elegant", seed=17)
prs = Presentation(theme=theme, strict_theme=True)
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Optional slide-only override. Explicit helper and element values still win.
set_slide_theme(slide, ThemeComposer().compose(style="dark-tech", seed=17))
```

Presentation-level inheritance is scoped to that presentation. Existing calls
with explicit `C`, `typo`, `font_name`, and colors remain compatible and have
higher priority than inherited defaults.

`strict_theme=False` is the default so partial template/VI design contexts
remain valid for Build Mode. Set `strict_theme=True` when the `theme` argument
is intended to be a complete FreeStyle Theme Lock.

### `render_build_spec`

`render_build_spec()` is the Build Core executor for a prepared component
`BuildSpec`. It does not infer page structure. A component can reference a
reusable `component_id`, or carry an inline `recipe`; the inline recipe is used
when present, so Build can keep exact bounds, font choices, data, and z-order.

```python
from pptx_designer import Presentation
from pptx_designer.core import render_build_spec

prs = Presentation()
spec = {
    "kind": "BuildSpec",
    "render_strategy": "components",
    "components": [{
        "atom_id": "headline",
        "z_index": 10,
        "recipe": {
            "kind": "text",
            "bounds": {"left": 0.8, "top": 0.8, "width": 8.0, "height": 0.7},
            "font_name": "Aptos Display", "font_size": 30, "bold": True,
            "color": "text_dark",
        },
        "data": "Build-owned composition",
    }],
}
slide = render_build_spec(spec, prs, context={})
```

The executor creates editable native objects in ascending `z_index` order. If
`fixed_base` is present, copying template artwork requires an explicitly
reviewed `reference_slide` and `fixed_shape_indices`; Build Core does not clone
an entire template slide implicitly.

### `fetch_image`

Generate or search for an image.

```python
from pptx_designer import fetch_image

def fetch_image(
    keywords: str,                 # Search/generation prompt
    *,
    mode: str = "auto",           # placeholder|search|generate|enhance|auto
    emotion: str = "",
    goal: str = "",
    width: int = 1920,
    height: int = 1080,
    **config,
) -> dict[str, str | None]:
    ...
```

### `extract_design_dna`

Extract design analysis from an existing .pptx file.

```python
from pptx_designer import extract_design_dna

dna = extract_design_dna("template.pptx")
```

### Production VI Build: `extract_design_context`, `VITemplateAdapter`, and `VIBuildDelivery`

VI Build uses the same versioned design-context dictionary as Build Mode theme
inheritance. `extract_design_context()` provides deterministic evidence from a
16:9 template: direct colors, fonts, image references, photo/color-panel
components, fixed visual layers, and a template fingerprint. It does not guess
unknown text boxes as writable slots. It is visual evidence, not a content
planner.

```python
from pptx_designer import Presentation, extract_design_context, merge_vi_design_context
from pptx_designer.enterprise import VIBuildDelivery, VITemplateAdapter

context = extract_design_context("template.pptx")
# Confirm framework pages and only the text objects that may be rebound.
context["framework_pages"] = [{
    "id": "cover", "role": "cover", "reference_slide": 1,
    "text_contract": {"strict": True},
}]
context["content_slots"] = [{
    "id": "cover.title", "page_role": "cover",
    "target": {"shape_index": 3},
    "text_style": {"font_size": 32},
}]

prs = Presentation("template.pptx", theme=context)
adapter = VITemplateAdapter(context)
delivery = VIBuildDelivery(prs, adapter)

# Framework page: rebind only confirmed text.
delivery.add(adapter.compile(
    page_role="cover", content={"slots": {"cover.title": "Spring collection"}},
))

# Content page: Build owns content relations, components and exact geometry.
delivery.add(adapter.compile_atomic(
    page_role="content",
    atomic_build_plan={
        "content_model": {"relations": [{"id": "journey", "type": "sequence"}]},
        "atoms": [
            {"id": "headline", "kind": "text", "geometry": {"left": 0.8, "top": 0.8, "width": 7, "height": 0.7}, "style": {"font_size": 30, "bold": True, "color": "text_dark"}, "data": "A Build-owned page"},
        ],
        "relation_bindings": [{"relation_id": "journey", "atom_ids": ["headline"]}],
    },
))
report = delivery.finalize("output.pptx", sample_texts=["template placeholder"])
assert report.status == "pass"
```

When adding a brand, resolved theme, or page-level context to template evidence,
use `merge_vi_design_context(template_context, *overrides)`, not the generic
`merge_design_context()`. The VI entry preserves template-locked paths and
reports rejected writes in `diagnostics.conflicts`; the generic merge remains
last-writer-wins for compatibility.

`compile(page_role="content")` and `VIBuildSession` archetype planning do not
create production content pages. Use `compile_atomic()` only. `VIBuildDelivery`
removes the template source slides by identity during `finalize`, checks page
provenance and template-text leaks, and makes a source page impossible to ship
by accident. With `text_contract.strict`, every non-empty framework text object
must be replaced, explicitly cleared, or explicitly preserved.

### `svg_chart`

Compile a supported SVG subset into editable native PowerPoint objects.

```python
from pptx_designer import svg_chart

result = svg_chart(slide, svg_text, x=1.0, y=1.0, w=8.0, h=4.0, C=None)
```

`x`, `y`, `w`, and `h` are inches. The function returns `SVGResult`; inspect
`shape_count`, `warnings`, and `errors`. `from pptx_designer.tools import
svg_chart` and `from pptx_designer.tools.svg import svg_chart` remain compatible
imports.

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

For direct compiler control, use `SVGCompiler`. For normal Build-mode use,
prefer the public wrapper above:

```python
from pptx_designer import svg_chart

result = svg_chart(slide, svg_text, x=1.0, y=1.0, w=8.0, h=4.0)
```

`SVGResult` includes `shape_count`, `shapes`, `native_shapes`, `warnings`, `errors`, `features`, `feature_levels`, `source_to_output`, `metrics`, and `compile_ms`. Invalid SVG or a configured safety limit raises `SVGCompileError`; unsupported individual elements may instead be skipped with a warning. Production callers should handle both paths.
