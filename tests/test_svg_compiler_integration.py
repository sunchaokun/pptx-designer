"""SVG compiler integration tests — covers the main compilation path."""

from __future__ import annotations

import pytest
from pptx import Presentation
from pptx.util import Inches

from pptx_designer.compiler import SVGCompiler, SVGCompileError, SVGResult


def _slide():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    layout = prs.slide_layouts[6]  # blank
    return prs.slides.add_slide(layout)


class TestBasicShapes:
    def test_circle(self):
        svg = '<svg viewBox="0 0 400 300"><circle cx="200" cy="150" r="100" fill="#4472C4"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert isinstance(result, SVGResult)
        assert result.shape_count >= 1

    def test_rect(self):
        svg = '<svg viewBox="0 0 400 300"><rect x="50" y="50" width="300" height="200" fill="#E74C3C"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1

    def test_ellipse(self):
        svg = '<svg viewBox="0 0 400 300"><ellipse cx="200" cy="150" rx="150" ry="100" fill="#2ECC71"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1

    def test_polygon(self):
        svg = '<svg viewBox="0 0 400 300"><polygon points="200,30 370,280 30,280" fill="#F39C12"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1

    def test_line(self):
        svg = '<svg viewBox="0 0 400 300"><line x1="50" y1="50" x2="350" y2="250" stroke="#333" stroke-width="3"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1


class TestPath:
    def test_simple_path(self):
        svg = '<svg viewBox="0 0 400 300"><path d="M100,100 L300,100 L200,250 Z" fill="#9B59B6"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1

    def test_curved_path(self):
        svg = '<svg viewBox="0 0 400 300"><path d="M100,200 C150,50 250,50 300,200" fill="none" stroke="#1ABC9C" stroke-width="4"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1


class TestText:
    def test_simple_text(self):
        svg = '<svg viewBox="0 0 400 300"><text x="200" y="150" text-anchor="middle" font-size="24" fill="#333">Hello</text></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1

    def test_tspan(self):
        svg = '<svg viewBox="0 0 400 300"><text x="100" y="100"><tspan font-size="18" fill="#E74C3C">Line 1</tspan><tspan x="100" dy="30" font-size="14" fill="#333">Line 2</tspan></text></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1


class TestGradients:
    def test_linear_gradient(self):
        svg = '''<svg viewBox="0 0 400 300">
            <defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stop-color="#4472C4"/><stop offset="1" stop-color="#2E75B6"/>
            </linearGradient></defs>
            <rect x="50" y="50" width="300" height="200" fill="url(#g1)"/>
        </svg>'''
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1

    def test_radial_gradient(self):
        svg = '''<svg viewBox="0 0 400 300">
            <defs><radialGradient id="g2" cx="50%" cy="50%" r="50%">
                <stop offset="0" stop-color="#FFF"/><stop offset="1" stop-color="#4472C4"/>
            </radialGradient></defs>
            <circle cx="200" cy="150" r="120" fill="url(#g2)"/>
        </svg>'''
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1


class TestTransform:
    def test_translate(self):
        svg = '<svg viewBox="0 0 400 300"><g transform="translate(100,50)"><rect x="0" y="0" width="200" height="150" fill="#3498DB"/></g></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1

    def test_scale(self):
        svg = '<svg viewBox="0 0 400 300"><g transform="scale(2)"><rect x="10" y="10" width="50" height="40" fill="#E74C3C"/></g></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1


class TestClipPath:
    def test_clip_path(self):
        svg = '''<svg viewBox="0 0 400 300">
            <defs><clipPath id="cp"><rect x="50" y="50" width="200" height="200"/></clipPath></defs>
            <rect x="0" y="0" width="400" height="300" fill="#4472C4" clip-path="url(#cp)"/>
        </svg>'''
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert result.shape_count >= 1


class TestUnsupported:
    def test_image_warning(self):
        svg = '<svg viewBox="0 0 400 300"><image href="photo.jpg" width="400" height="300"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6))
        assert any("image" in w.lower() or "unsupported" in w.lower() for w in result.warnings)


class TestScalingModes:
    def test_contain(self):
        svg = '<svg viewBox="0 0 400 300"><rect x="0" y="0" width="400" height="300" fill="#4472C4"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6), scaling="contain")
        assert result.shape_count >= 1

    def test_cover(self):
        svg = '<svg viewBox="0 0 400 300"><rect x="0" y="0" width="400" height="300" fill="#4472C4"/></svg>'
        result = SVGCompiler().compile(svg, _slide(), (1, 1, 8, 6), scaling="cover")
        assert result.shape_count >= 1


class TestErrors:
    def test_empty_svg(self):
        with pytest.raises(SVGCompileError):
            SVGCompiler().compile("", _slide(), (1, 1, 8, 6))

    def test_invalid_svg(self):
        with pytest.raises(SVGCompileError):
            SVGCompiler().compile("not svg at all", _slide(), (1, 1, 8, 6))


class TestCompatShim:
    """Verify the old import path still works via the compatibility shim."""

    def test_import_from_renderer_svg_compiler(self):
        from pptx_designer.renderer.svg_compiler import SVGCompiler as OldSVGCompiler
        from pptx_designer.renderer.svg_compiler import SVGResult as OldSVGResult
        assert OldSVGCompiler is SVGCompiler
        assert OldSVGResult is SVGResult
