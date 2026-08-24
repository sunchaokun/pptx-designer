"""An original four-page luxury fragrance atlas built only with pptx_designer.

The deck treats the perfume as a collectible object: scent journey, materials,
ritual and travel-ready presentation. All type and graphic details are native,
editable PowerPoint objects.

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
    """A quiet product passport, deliberately unlike the architecture cover."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "cream", C=C)
    rect(slide, 0.52, 0.46, 12.30, 0.08, "wine", C=C)
    cover_image(slide, 0.78, 0.85, 11.74, 3.62, str(HERO))
    text(slide, 0.76, 5.02, 5.54, 0.38, "AURELIA NOCTURNE", font_size=16,
         color="ink", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.76, 5.42, 6.20, 0.76, ["A perfume atlas for the", "last light of the day."], font_size=21,
              color="wine", font_name=SERIF, C=C)
    text(slide, 9.14, 5.08, 3.18, 0.24, "EXTRAIT DE PARFUM", font_size=9,
         color="wine", bold=True, font_name=SANS, C=C)
    multiline(slide, 9.14, 5.48, 3.22, 0.78,
              ["Collected in motion.", "Remembered on skin."],
              font_size=14, color="ink", font_name=SERIF, C=C)
    text(slide, 0.78, 6.88, 11.42, 0.24,
         "50 ML     /     BERGAMOT — IRIS — SMOKED TEA — CEDAR     /     AUTUMN 2026",
         font_size=8, color="muted", bold=True, font_name=SANS, C=C)


def add_material_atlas(prs: Presentation) -> None:
    """Ingredient landscape and provenance markers, inspired by an atlas not a brochure."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(NOTES))
    rect(slide, 0, 0, 13.333, 0.76, "ink", C=C)
    text(slide, 0.62, 0.24, 3.1, 0.25, "01 / MATERIAL ATLAS", font_size=9,
         color="gold", bold=True, font_name=SANS, C=C)
    text(slide, 8.40, 0.20, 4.30, 0.29, "CALABRIA — GRASSE — KASHMIR", font_size=9,
         color="rose", bold=True, align="right", font_name=SANS, C=C)
    rect(slide, 0.54, 4.98, 12.26, 1.58, "cream", C=C)
    text(slide, 0.84, 5.28, 3.44, 0.28, "THE ROUTE OF THE SCENT", font_size=10,
         color="wine", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.82, 5.62, 5.70, 0.76, ["Four materials. One", "late-afternoon memory."], font_size=20,
              color="ink", font_name=SERIF, C=C)
    origins = [("01", "BERGAMOT", "Calabria / light"), ("02", "IRIS", "Florence / powder"),
               ("03", "TEA", "Fujian / smoke"), ("04", "CEDAR", "Kashmir / grain")]
    for index, (number, name, origin) in enumerate(origins):
        x = 7.02 + index * 1.38
        oval(slide, x, 5.32, 0.34, 0.34, "wine", C=C)
        text(slide, x + 0.48, 5.25, 0.74, 0.22, number, font_size=8,
             color="wine", bold=True, font_name=SANS, C=C)
        text(slide, x, 5.80, 1.18, 0.26, name, font_size=9,
             color="ink", bold=True, font_name=SANS, C=C)
        text(slide, x, 6.13, 1.16, 0.22, origin, font_size=8,
             color="muted", font_name=SANS, C=C)
    text(slide, 0.62, 6.94, 11.70, 0.22,
         "AURELIA / THE PERFUME ATLAS / A STUDY OF ORIGIN, EXTRACTION AND MEMORY", font_size=8,
         color="cream", bold=True, font_name=SANS, C=C)


def add_ritual(prs: Presentation) -> None:
    """An immersive encounter page with a horizontal, film-like caption system."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(RITUAL))
    rect(slide, 0.56, 0.50, 12.20, 0.58, "cream", C=C)
    text(slide, 0.86, 0.67, 2.82, 0.24, "02 / ON THE SKIN", font_size=9,
         color="wine", bold=True, font_name=SANS, C=C)
    text(slide, 8.50, 0.65, 3.92, 0.24, "THE RITUAL IS PRIVATE.", font_size=9,
         color="wine", bold=True, align="right", font_name=SANS, C=C)
    rect(slide, 0, 5.82, 13.333, 1.68, "wine", C=C)
    text(slide, 0.72, 6.06, 5.70, 0.44, "A gesture, not a performance.", font_size=21,
         color="cream", font_name=SERIF, C=C)
    multiline(slide, 7.16, 6.02, 4.72, 0.88,
              ["At close range, the fragrance turns warm.", "On fabric, it becomes a private address."],
              font_size=13, color="rose", font_name=SERIF, C=C)
    rect(slide, 12.08, 6.10, 0.16, 0.82, "gold", C=C)


def add_object(prs: Presentation) -> None:
    """A collectible-object finale, informed by travel cases rather than sales cards."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "ink", C=C)
    cover_image(slide, 0.58, 0.52, 12.20, 4.56, str(OBJECT))
    rect(slide, 0.58, 4.58, 12.20, 0.50, "cream", C=C)
    text(slide, 0.84, 4.70, 11.55, 0.27,
         "THE OBJECT / DARK GLASS — MATTE CASE — GOLD EDGE — DESIGNED TO TRAVEL", font_size=8,
         color="wine", bold=True, font_name=SANS, C=C)
    text(slide, 0.62, 5.62, 3.35, 0.24, "03 / TO KEEP", font_size=9,
         color="gold", bold=True, font_name=SANS, C=C)
    text(slide, 0.58, 6.02, 7.48, 0.52, "An object for the return journey.", font_size=25,
         color="cream", font_name=SERIF, C=C)
    text(slide, 9.02, 5.98, 3.28, 0.24, "50 ML / REFILLABLE", font_size=9,
         color="gold", bold=True, align="right", font_name=SANS, C=C)
    text(slide, 9.03, 6.42, 3.30, 0.24, "MAISON AURELIA / NOCTURNE", font_size=9,
         color="rose", bold=True, align="right", font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_material_atlas(prs)
    add_ritual(prs)
    add_object(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
