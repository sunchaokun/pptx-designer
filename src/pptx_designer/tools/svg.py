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

logger = logging.getLogger(__name__)


def svg_chart(
    slide: Any,
    svg_text: str,
    x: float = 0.5,
    y: float = 1.5,
    w: float = 9.0,
    h: float = 5.5,
    C: dict | None = None,
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

    compiler = SVGCompiler(C=C or {})
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
