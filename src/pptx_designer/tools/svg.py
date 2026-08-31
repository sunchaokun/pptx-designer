"""SVG tools — high-level helpers for LLM-generated SVG diagrams.

Usage::

    from pptx_designer.tools.svg import svg_chart

    svg = '<svg viewBox="0 0 400 300"><circle cx="200" cy="150" r="100" fill="#4472C4"/></svg>'
    result = svg_chart(slide, svg, x=1, y=1, w=8, h=6)
    print(result.shape_count)  # number of PPTX shapes created
"""

from __future__ import annotations

import logging
from typing import Any

from pptx_designer.compiler import SVGCompileError, SVGCompiler, SVGResult
from pptx_designer.renderer.theme_context import resolve_color_context

logger = logging.getLogger(__name__)


def svg_chart(
    slide: Any,
    svg_text: str,
    x: float = 0.5,
    y: float = 1.5,
    w: float = 9.0,
    h: float = 5.5,
    C: dict | None = None,
    text_style: dict[str, dict] | None = None,
    group_opacity: str = "strict",
    layout: dict | None = None,
) -> SVGResult:
    """Compile SVG markup to native editable PPTX shapes on *slide*.

    Parameters
    ----------
    slide:
        A python-pptx ``Slide`` object.
    svg_text:
        SVG markup string. Must include a ``viewBox`` or explicit ``width``/
        ``height`` attributes.
    x, y, w, h:
        Target rectangle in **inches** on the slide.
    C:
        Optional colour/font context dictionary.  Keys like ``primary``,
        ``secondary``, ``text_dark`` are passed through to the SVG
        compiler for gradient/colour resolution.
    text_style:
        Optional explicit styles keyed by SVG ``class``.  Each style may set
        ``font_size`` in PowerPoint points, ``color``, ``font_name``, and
        ``bold``.  Matching styles bypass automatic canvas-based font scaling.
    group_opacity:
        ``"strict"`` (default) rejects SVG group opacity because native OOXML
        cannot reproduce compositing exactly. ``"distribute"`` pushes group
        opacity to child elements for editable, renderer-safe diagrams.
    layout:
        Optional layout contract. Use ``safe_margin`` in SVG units, ``zones``
        keyed by text class as ``(x, y, width, height)``, and
        ``text_collision`` as ``"warning"`` or ``"error"``.

    Returns
    -------
    SVGResult
        Compilation result with ``shape_count``, ``warnings``, and
        ``features``.

    Raises
    ------
    SVGCompileError
        If the SVG is malformed or contains unsupported elements.
    """
    if not svg_text or not svg_text.strip():
        return SVGResult(shape_count=0, warnings=["empty svg_text"])

    # SVG is a public Build Mode helper too: inherit the nearest slide or
    # presentation theme, while allowing an explicit partial C override.
    color_context = resolve_color_context(slide, C)
    compiler = SVGCompiler(C=color_context, text_style=text_style, group_opacity=group_opacity, layout=layout)
    try:
        result = compiler.compile(svg_text, slide, (x, y, w, h))
    except SVGCompileError:
        raise
    except Exception as exc:
        raise SVGCompileError(str(exc)) from exc

    if result.warnings:
        for w_msg in result.warnings:
            logger.warning("svg_chart: %s", w_msg)

    return result
