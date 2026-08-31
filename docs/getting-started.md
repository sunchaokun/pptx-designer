# 快速开始

> 适用版本：`1.0.0b10`；要求 Python 3.10+。

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

需要逐项控制形状、文字和位置时，直接使用 Build 模式。建议先解析并锁定主题，
使公共 helper 自动继承颜色和字体；不要为每个 helper 重复传入手写的 `C` 字典。
Build 不会由
`content_type` 自动选择页面结构：页面目标、信息层级、内容关系和每个原子的精确
几何都由调用方明确决定。

```python
from pptx_designer import Presentation
from pptx_designer.renderer.theme import ThemeComposer
from pptx_designer.tools.shapes import rect
from pptx_designer.tools.text import text

theme = ThemeComposer().compose(style="professional", seed=17)
prs = Presentation(theme=theme, strict_theme=True)
slide = prs.slides.add_slide(prs.slide_layouts[6])

text(slide, left=1, top=1, width=8, height=1, txt="Hello World", font_size=32, bold=True)
rect(slide, left=1, top=2.5, width=8, height=0.1, fill="primary")

prs.save("output/hello.pptx")
```

所有坐标单位均为英寸。`Presentation()` 默认创建 16:9 画布（13.333 × 7.5 英寸）。
将已解析 theme 传给 `Presentation(theme=theme)` 后，公共 helper 会继承当前文稿的
颜色和字体；需要特殊处理时，显式的 `C`、颜色、字体等参数优先。模板驱动的 VI
内容页请使用 Build 原子计划与 `VITemplateAdapter.compile_atomic()`，不要使用旧的
archetype 路径；完整交付和 QA 流程见 [LLM 编写手册](llm-authoring-guide.md)。

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
