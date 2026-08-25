"""Offline regression tests for deterministic image-processing effects."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from pptx_designer.effects.image_processor import (
    apply_gradient_mask,
    apply_grayscale,
    apply_scatter,
    compose_images,
    grade_image_to_palette,
)


def _source_image(path: Path) -> Path:
    image = Image.new("RGB", (24, 16), (220, 40, 20))
    image.save(path)
    return path


def test_palette_grade_and_grayscale_preserve_openable_dimensions(tmp_path):
    source = _source_image(tmp_path / "source.png")

    graded = Path(grade_image_to_palette(str(source), "#0044CC", alpha=0.5))
    grayscale = Path(apply_grayscale(str(source)))

    assert graded.exists()
    assert grayscale.exists()
    assert Image.open(graded).size == (24, 16)

    pixel = Image.open(grayscale).convert("RGB").getpixel((0, 0))
    assert pixel[0] == pixel[1] == pixel[2]


def test_gradient_mask_and_scatter_create_cached_outputs(tmp_path):
    source = _source_image(tmp_path / "source.png")

    masked = Path(apply_gradient_mask(str(source), direction="bottom", color="#000000", end_opacity=1.0))
    scatter_one = Path(apply_scatter(str(source), count=8, seed=7))
    scatter_two = Path(apply_scatter(str(source), count=8, seed=7))

    assert Image.open(masked).size == (24, 16)
    assert scatter_one == scatter_two
    assert Image.open(scatter_one).size == (24, 16)


def test_compose_images_preserves_opaque_canvas_for_semi_transparent_overlay(tmp_path):
    source = _source_image(tmp_path / "source.png")
    blue = Image.new("RGBA", (4, 4), (0, 0, 255, 255))

    result = compose_images(
        [
            {"image": str(source), "position": (0, 0)},
            {"image": blue, "position": (20, 12), "opacity": 0.5},
        ],
        width=24,
        height=16,
        bg_color="#000000",
    )

    assert result.size == (24, 16)
    assert result.getpixel((0, 0))[:3] == (220, 40, 20)
    blended = result.getpixel((21, 13))
    assert blended[2] > 0 and blended[3] == 255


def test_compose_images_clips_layers_outside_the_canvas():
    red = Image.new("RGBA", (4, 4), (255, 0, 0, 255))

    result = compose_images([{"image": red, "position": (-2, -2)}], width=2, height=2, bg_color="#000000")

    assert result.size == (2, 2)
    assert result.getpixel((0, 0)) == (255, 0, 0, 255)
