# 快速开始

> 适用版本：`1.0.0b7`；要求 Python 3.10+。

## 安装

```bash
pip install pptx-designer
```

## 生成第一份演示文稿

```python
from pptx_designer import generate_ppt

result = generate_ppt("My first presentation", style="professional")
print(result["output_path"])
```

## Build 模式

需要逐项控制形状、文字和位置时，直接使用 Build 模式：

```python
from pptx_designer.tools.shapes import rect
from pptx_designer.tools.text import text
from pptx_designer.core.pipeline import Presentation

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

text(slide, 1, 1, 8, 1, "Hello World", font_size=32, bold=True)
rect(slide, 1, 2.5, 8, 0.1, fill="#3B82F6")

prs.save("output/hello.pptx")
```

所有坐标单位均为英寸。`Presentation()` 默认创建 16:9 画布（13.333 × 7.5 英寸）。

## 在页面中加入可编辑 SVG

```python
from pptx_designer import svg_chart

svg = '''<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="36" fill="#2563EB"/>
  <text x="105" y="58" font-size="24" fill="#172554">Hello SVG</text>
</svg>'''

result = svg_chart(slide, svg, x=1, y=3, w=8, h=3)
if result.warnings:
    print("SVG warnings:", result.warnings)
```

这是推荐公共入口；`from pptx_designer.tools import svg_chart` 和旧路径 `from pptx_designer.tools.svg import svg_chart` 仍兼容。不要把 SVG 编译器视为浏览器：它优先保留 PowerPoint 可编辑对象，而不承诺所有 SVG 特效的像素级等价。请在交付前检查 warning，并阅读 [SVG 编译器指南](svg-guide.md)。

## 下一步

- [API Reference](api-reference.md)
- [SVG 编译器指南](svg-guide.md)
- [文档索引](README.md)
