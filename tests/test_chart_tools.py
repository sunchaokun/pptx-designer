"""Regression tests for chart helpers and image compositing."""

from PIL import Image

from pptx_designer.effects.image_processor import compose_images
from pptx_designer.tools.charts import bar_chart, comparison_bars, donut_chart


def test_chart_helpers_add_editable_shapes(slide):
    """The shape-based chart helpers must render labels without NameError."""
    bar_chart(slide, 2, 1, [("Revenue", 0.75, "$12M")])
    comparison_bars(slide, 2, 2, [("Revenue", "10", "12", 0.5, 0.75)])
    donut_chart(slide, 4, 5, 0.8, 0.4, [("Core", "100%", "#3B82F6")])

    assert len(slide.shapes) > 0


def test_compose_images_applies_each_layers_own_opacity():
    """Opacity callbacks must bind the current layer rather than the final loop value."""
    red = Image.new("RGBA", (1, 1), (255, 0, 0, 255))
    transparent_blue = Image.new("RGBA", (1, 1), (0, 0, 255, 255))

    result = compose_images(
        [
            {"image": red, "opacity": 1.0},
            {"image": transparent_blue, "opacity": 0.0},
        ],
        width=1,
        height=1,
    )

    assert result.getpixel((0, 0)) == (255, 0, 0, 255)
