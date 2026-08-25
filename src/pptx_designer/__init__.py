"""
pptx-designer: Python library for LLMs to generate PowerPoint presentations.

Quick start:
    from pptx_designer import generate_ppt
    result = generate_ppt("AI startup pitch deck", style="dark cyberpunk")

Build mode (pixel-perfect control):
    from pptx_designer.tools.shapes import rect
    from pptx_designer.tools.text import text
    from pptx_designer.tools.cards import kpi_card, page_header
    from pptx_designer.core.pipeline import Presentation

Available data (40,000+ style combinations):
    from pptx_designer.data import PALETTES    # 192 color schemes
    from pptx_designer.data import TYPOGRAPHY  # 74 font pairs
    from pptx_designer.data import STYLES      # 84 style presets

Shape functions:
    rect, rounded_rect, oval, hexagon, diamond, star, triangle, arrow, chevron

Text functions:
    text, multiline, gradient_text, dramatic_text, vertical_text

Chart functions:
    bar_chart, donut_chart, native_chart, comparison_bars

Component functions:
    kpi_card, highlight_cards, code_block, section_divider, hero_slide

Image functions:
    cover_image, circle_image, ai_image

Layout functions:
    page_header, top_bar, page_number

Effect functions:
    text_shadow, text_glow, shape_3d, pattern_fill

For more information, see: https://github.com/sunchaokun/pptx-designer
"""

from __future__ import annotations

__version__ = "1.0.0b3"

from pptx_designer.data import PALETTES, TYPOGRAPHY, STYLES
from pptx_designer.core.pipeline import Presentation, generate_ppt

__all__ = [
    "__version__",
    "PALETTES",
    "TYPOGRAPHY",
    "STYLES",
    "Presentation",
    "generate_ppt",
]
