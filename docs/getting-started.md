# Getting Started

## Installation

```bash
pip install pptx-designer
```

## First Presentation

```python
from pptx_designer import generate_ppt

result = generate_ppt("My first presentation", style="professional")
print(result["output_path"])
```

## Build Mode

For pixel-perfect control:

```python
from pptx_designer.tools.shapes import rect
from pptx_designer.tools.text import text
from pptx_designer.core.pipeline import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

text(slide, 1, 1, 8, 1, "Hello World", font_size=32, bold=True)
rect(slide, 1, 2.5, 8, 0.1, fill="#3B82F6")

prs.save("hello.pptx")
```

## Next Steps

- [API Reference](api-reference.md)
- [Build Mode Guide](guides/build-mode.md)
- [Diagrams Guide](guides/diagrams.md)
- [Enterprise Mode](guides/enterprise.md)
