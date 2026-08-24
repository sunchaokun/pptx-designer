"""SVG tools tests — validates the high-level svg_chart helper."""

from __future__ import annotations

import pytest
from pptx import Presentation
from pptx.util import Inches

from pptx_designer.tools.svg import svg_chart
from pptx_designer.compiler import SVGCompileError


def _slide():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    layout = prs.slide_layouts[6]
    return prs.slides.add_slide(layout)


class TestSvgChart:
    def test_basic_circle(self):
        svg = '<svg viewBox="0 0 400 300"><circle cx="200" cy="150" r="100" fill="#4472C4"/></svg>'
        result = svg_chart(_slide(), svg, x=1, y=1, w=8, h=6)
        assert result.shape_count >= 1

    def test_empty_svg_returns_result(self):
        result = svg_chart(_slide(), "")
        assert result.shape_count == 0
        assert "empty svg_text" in result.warnings

    def test_with_color_context(self):
        svg = '<svg viewBox="0 0 400 300"><rect x="50" y="50" width="300" height="200" fill="#FFF"/></svg>'
        C = {"primary": "#4472C4", "text_dark": "#333"}
        result = svg_chart(_slide(), svg, C=C)
        assert result.shape_count >= 1

    def test_invalid_svg_raises(self):
        with pytest.raises(SVGCompileError):
            svg_chart(_slide(), "not svg")

    def test_svg_with_text(self):
        svg = '<svg viewBox="0 0 400 300"><text x="200" y="150" font-size="24" fill="#333">Title</text></svg>'
        result = svg_chart(_slide(), svg)
        assert result.shape_count >= 1

    def test_svg_with_gradient(self):
        svg = '''<svg viewBox="0 0 400 300">
            <defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stop-color="#4472C4"/><stop offset="1" stop-color="#2E75B6"/>
            </linearGradient></defs>
            <rect x="0" y="0" width="400" height="300" fill="url(#g1)"/>
        </svg>'''
        result = svg_chart(_slide(), svg)
        assert result.shape_count >= 1
