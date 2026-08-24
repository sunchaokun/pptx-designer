"""A four-page luxury fragrance lookbook built only with pptx_designer.

The campaign uses distinct editorial images for hero, ingredients, ritual and
object study. Typography, panels and all supporting information are editable.

Run: python examples/luxury_fragrance_lookbook.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.shapes import oval, rect
from pptx_designer.tools.text import multiline, text


ROOT = Path(__file__).parent
HERO = ROOT / "assets" / "fragrance-hero.png"
NOTES = ROOT / "assets" / "fragrance-notes.png"
RITUAL = ROOT / "assets" / "fragrance-ritual.png"
OBJECT = ROOT / "assets" / "fragrance-object.png"
C = {
    "ink": "#17080D",
    "wine": "#4A0E1D",
    "cream": "#F7F0E9",
    "gold": "#C9A66B",
    "rose": "#E5C9BF",
    "muted": "#9E7B83",
    "white": "#FFFFFF",
}
SERIF = "Georgia"
SANS = "Arial"


def add_cover(prs: Presentation) -> None:
    """A cover where large type physically enters the product image."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "cream", C=C)
    cover_image(slide, 0.78, 0.45, 11.80, 5.38, str(HERO))
    rect(slide, 0.40, 0.45, 0.16, 5.38, "gold", C=C)
    rect(slide, 8.65, 0.45, 3.93, 0.54, "ink", C=C)
    text(slide, 8.98, 0.58, 3.15, 0.26, "MAISON AURELIA  /  N° 07", font_size=9,
         color="gold", bold=True, font_name=SANS, C=C)
    text(slide, 0.72, 5.25, 7.95, 0.98, "THE RITUAL", font_size=54,
         color="ink", bold=True, font_name=SERIF, C=C)
    text(slide, 6.56, 5.25, 5.75, 0.98, "OF LIGHT", font_size=54,
         color="wine", bold=True, font_name=SERIF, C=C)
    text(slide, 0.76, 6.36, 3.75, 0.24, "EXTRAIT DE PARFUM / 50 ML", font_size=9,
         color="wine", bold=True, font_name=SANS, C=C)
    multiline(slide, 8.10, 6.22, 4.15, 0.62,
              ["A composition for the hour", "between dusk and silence."],
              font_size=14, color="ink", font_name=SERIF, C=C)
    text(slide, 0.76, 7.00, 11.50, 0.22,
         "AUTUMN / WINTER 2026     /     PARIS — NEW YORK — TOKYO", font_size=8,
         color="muted", bold=True, font_name=SANS, C=C)


def add_composition(prs: Presentation) -> None:
    """A sensory index: image as a band, native typography as the scent map."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "ink", C=C)
    cover_image(slide, 0.56, 0.55, 12.22, 3.18, str(NOTES))
    rect(slide, 0.56, 3.20, 12.22, 0.53, "cream", C=C)
    text(slide, 0.82, 3.34, 11.50, 0.26,
         "BERGAMOT PEEL  /  SMOKED TEA  /  IRIS  /  CEDAR SHAVINGS", font_size=9,
         color="wine", bold=True, font_name=SANS, C=C)
    text(slide, 0.62, 4.18, 3.00, 0.24, "01 / COMPOSITION", font_size=9,
         color="gold", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.58, 4.60, 7.10, 1.34, ["A scent with", "a slow pulse."], font_size=39,
              color="cream", bold=True, font_name=SERIF, C=C)
    multiline(slide, 8.32, 4.73, 3.92, 1.20,
              ["Citrus wakes first. Then iris moves through", "the dark, until tea and cedar stay on skin."],
              font_size=15, color="rose", font_name=SERIF, C=C)
    for index, (number, note) in enumerate((("01", "OPEN"), ("02", "HEART"), ("03", "TRAIL"))):
        x = 0.66 + index * 2.08
        oval(slide, x, 6.40, 0.42, 0.42, "gold", C=C)
        text(slide, x + 0.55, 6.37, 1.22, 0.24, f"{number}  {note}", font_size=9,
             color="cream", bold=True, font_name=SANS, C=C)
    text(slide, 8.34, 6.50, 3.78, 0.22, "THE PERFUME DEVELOPS IN LAYERS.", font_size=8,
         color="gold", bold=True, font_name=SANS, C=C)


def add_ritual(prs: Presentation) -> None:
    """A cinematic usage page with a compact editorial caption system."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(RITUAL))
    rect(slide, 0.52, 0.48, 3.50, 0.60, "cream", C=C)
    text(slide, 0.80, 0.64, 2.98, 0.26, "02 / THE GESTURE", font_size=9,
         color="wine", bold=True, font_name=SANS, C=C)
    rect(slide, 0.52, 5.10, 7.26, 1.62, "ink", C=C)
    multiline(slide, 0.82, 5.24, 6.55, 1.08, ["ONE SPRAY.", "ONE DELIBERATE PAUSE."], font_size=29,
              color="cream", bold=True, font_name=SERIF, C=C)
    text(slide, 0.84, 6.26, 6.10, 0.30,
         "The formula is made to be noticed only at close range.", font_size=12,
         color="rose", font_name=SERIF, C=C)
    rect(slide, 10.90, 6.32, 1.75, 0.52, "cream", C=C)
    text(slide, 11.12, 6.45, 1.30, 0.24, "AT DUSK", font_size=8,
         color="wine", bold=True, align="center", font_name=SANS, C=C)


def add_object(prs: Presentation) -> None:
    """A calm closing product study rather than another campaign background."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "cream", C=C)
    cover_image(slide, 2.34, 0.48, 10.38, 5.92, str(OBJECT))
    rect(slide, 0.56, 0.48, 0.18, 5.92, "wine", C=C)
    text(slide, 0.74, 0.72, 1.28, 0.24, "03 / OBJECT", font_size=9,
         color="wine", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.70, 1.30, 2.55, 1.42, ["A bottle", "kept close."], font_size=32,
              color="ink", bold=True, font_name=SERIF, C=C)
    multiline(slide, 0.76, 3.55, 1.90, 1.18,
              ["Dark glass.", "A single gold edge.", "Nothing added."],
              font_size=14, color="wine", font_name=SERIF, C=C)
    text(slide, 2.38, 6.72, 9.65, 0.22,
         "MAISON AURELIA  /  N° 07  /  EXTRAIT DE PARFUM  /  AVAILABLE OCTOBER 2026",
         font_size=8, color="wine", bold=True, font_name=SANS, C=C)
    rect(slide, 0.56, 6.72, 1.28, 0.22, "gold", C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_composition(prs)
    add_ritual(prs)
    add_object(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
