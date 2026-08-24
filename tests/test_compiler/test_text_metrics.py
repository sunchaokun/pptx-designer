"""Regression tests for SVG text measurement and point-size conversion."""

from __future__ import annotations

from pptx_designer.compiler._text import _measure_text


def test_missing_pillow_font_uses_size_aware_estimator():
    metrics = _measure_text("A" * 20, 32.0, "DefinitelyMissingFont", 8.0)

    # Pillow's fixed default font used to produce a sub-inch measurement here.
    assert metrics.width_inches > 5.5
    assert metrics.height_inches > 0.4
