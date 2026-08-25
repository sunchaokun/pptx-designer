"""A four-page deconstructed couture editorial, built only with pptx_designer.

The deck deliberately avoids the usual title-and-image template. Images set
atmosphere; every headline, mark, annotation, colour field and rule remains a
native, editable PowerPoint object.

Run: python examples/couture_editorial_deck.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image, gradient_mask_image
from pptx_designer.tools.shapes import donut, oval, rect, shape
from pptx_designer.tools.text import multiline, text, text_shadow


ROOT = Path(__file__).parent
EDITORIAL = ROOT / "assets" / "couture-editorial.png"
LOOK = ROOT / "assets" / "couture-look.png"
ATELIER = ROOT / "assets" / "couture-atelier.png"
MATERIAL = ROOT / "assets" / "couture-material.png"
SALON = ROOT / "assets" / "couture-salon.png"

C = {
    "ink": "#14110F", "paper": "#F4EFE6", "chalk": "#E3D8C8",
    "oxide": "#A0442F", "wine": "#5E1E1B", "gold": "#C49A5A",
    "smoke": "#716B65", "white": "#FFFFFF",
}
SERIF = "Bodoni 72"
SANS = "Arial"


def _slide(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _rule(slide, x: float, y: float, w: float, color: str = "ink", h: float = 0.028) -> None:
    rect(slide, x, y, w, h, color, C=C)


def add_cover(prs: Presentation) -> None:
    """Manifesto cover: giant type collides with a single editorial image."""
    slide = _slide(prs)
    rect(slide, 0, 0, 13.333, 7.5, "paper", C=C)
    rect(slide, 0, 0, 0.22, 7.5, "oxide", C=C)
    cover_image(slide, 5.35, 0, 7.983, 7.5, str(EDITORIAL))
    gradient_mask_image(slide, 4.55, 0, 2.1, 7.5, bg_color=C["paper"],
                        direction="left", alpha_start=100, alpha_end=0)
    text(slide, 1.05, 0.86, 2.15, 0.18, "ATELIER NOTES / 01", font_size=7,
         color="oxide", bold=True, font_name=SANS, C=C)
    text(slide, 1.05, 0.60, 3.6, 0.22, "THE WHITE STUDY", font_size=9,
         color="oxide", bold=True, font_name=SANS, C=C)
    _rule(slide, 1.05, 1.12, 3.35, "ink")
    text_shadow(slide, 0.92, 1.30, 8.25, 1.34, "COUTURE", font_size=68,
                color=C["ink"], alpha_pct=12, blur_pt=3, distance_pt=2,
                bold=True, font_name=SERIF, C=C)
    text(slide, 1.00, 2.41, 6.65, 1.24, "IN\nMOTION", font_size=66,
         color="ink", bold=True, font_name=SERIF, C=C)
    text(slide, 1.08, 4.30, 3.56, 0.74, "A study of volume,\nweight and the hand.",
         font_size=17, color="wine", font_name=SERIF, C=C)
    _rule(slide, 1.08, 5.35, 2.60, "oxide", 0.055)
    multiline(slide, 1.08, 5.62, 3.92, 0.60,
              ["PARIS / SPRING–SUMMER 2027", "PRIVATE EDITORIAL EDITION"],
              font_size=8, color="smoke", bold=True, font_name=SANS, C=C)
    oval(slide, 11.63, 0.62, 0.84, 0.84, "oxide", C=C)
    text(slide, 11.63, 0.85, 0.84, 0.22, "01", font_size=13, color="paper",
         bold=True, align="center", font_name=SANS, C=C)
    text(slide, 11.08, 6.76, 1.80, 0.35, "NOT A DRESS.\nA GESTURE.", font_size=8,
         color="paper", bold=True, align="right", font_name=SANS, C=C)


def add_silhouette(prs: Presentation) -> None:
    """Deconstruction page: editorial slices and annotations, not a photo caption."""
    slide = _slide(prs)
    rect(slide, 0, 0, 13.333, 7.5, "ink", C=C)
    text(slide, 0.60, 0.58, 5.6, 0.70, "THE BODY\nIS THE PATTERN.", font_size=34,
         color="paper", bold=True, font_name=SERIF, C=C)
    text(slide, 9.92, 0.66, 2.72, 0.24, "02 / SILHOUETTE STUDY", font_size=8,
         color="gold", bold=True, align="right", font_name=SANS, C=C)
    _rule(slide, 0.60, 1.64, 12.12, "gold")
    cover_image(slide, 0.60, 2.10, 3.12, 4.58, str(LOOK))
    cover_image(slide, 4.03, 2.10, 4.95, 4.58, str(EDITORIAL))
    cover_image(slide, 9.29, 2.10, 3.43, 4.58, str(ATELIER))
    rect(slide, 3.50, 2.10, 0.20, 4.58, "oxide", C=C)
    rect(slide, 8.75, 2.10, 0.20, 4.58, "paper", C=C)
    disk = donut(slide, 7.78, 4.85, 1.26, "gold", C=C)
    disk.rotation = 18
    text(slide, 7.24, 4.66, 1.10, 0.40, "CUT", font_size=18, color="ink",
         bold=True, align="center", font_name=SANS, C=C)
    text(slide, 7.20, 5.10, 1.16, 0.22, "ON THE BIAS", font_size=6,
         color="ink", bold=True, align="center", font_name=SANS, C=C)
    rect(slide, 0.92, 5.98, 2.50, 0.43, "paper", C=C)
    text(slide, 1.08, 6.10, 2.15, 0.16, "01 / SHOULDER LINE", font_size=7,
         color="ink", bold=True, font_name=SANS, C=C)
    rect(slide, 9.58, 2.38, 2.83, 0.43, "oxide", C=C)
    text(slide, 9.76, 2.50, 2.34, 0.16, "02 / RELEASED VOLUME", font_size=7,
         color="paper", bold=True, font_name=SANS, C=C)
    text(slide, 9.58, 6.92, 2.83, 0.18, "HAND-CUT / HAND-FINISHED", font_size=7,
         color="paper", bold=True, align="right", font_name=SANS, C=C)


def add_material_index(prs: Presentation) -> None:
    """Graphic material index with circular marks and annotations as a visual system."""
    slide = _slide(prs)
    rect(slide, 0, 0, 13.333, 7.5, "chalk", C=C)
    cover_image(slide, 0, 0, 7.85, 7.5, str(MATERIAL))
    gradient_mask_image(slide, 6.35, 0, 1.85, 7.5, bg_color=C["chalk"],
                        direction="left", alpha_start=100, alpha_end=0)
    text(slide, 0.55, 0.72, 2.40, 0.20, "03 / MATERIAL INDEX", font_size=8,
         color="paper", bold=True, font_name=SANS, C=C)
    ring = donut(slide, 8.94, 2.18, 2.15, "oxide", C=C)
    ring.rotation = -24
    oval(slide, 8.43, 1.67, 1.02, 1.02, "paper", C=C)
    text(slide, 8.54, 1.97, 0.80, 0.24, "03", font_size=12, color="oxide",
         bold=True, align="center", font_name=SANS, C=C)
    text(slide, 8.13, 3.58, 4.54, 0.78, "LIGHT NEEDS\nTEXTURE.", font_size=31,
         color="ink", bold=True, font_name=SERIF, C=C)
    _rule(slide, 8.18, 4.83, 3.80, "oxide", 0.055)
    marks = [("ORGANZA", "AIR / RESISTANCE", "oxide"),
             ("SATIN", "REFLECTION / WEIGHT", "wine"),
             ("PEARL", "GRAIN / LIGHT", "gold")]
    y = 5.22
    for index, (name, note, colour) in enumerate(marks, start=1):
        oval(slide, 8.20, y + 0.02, 0.18, 0.18, colour, C=C)
        text(slide, 8.56, y, 1.62, 0.22, f"{index:02d}  {name}", font_size=9,
             color="ink", bold=True, font_name=SANS, C=C)
        text(slide, 10.62, y + 0.02, 1.90, 0.18, note, font_size=7,
             color="smoke", bold=True, align="right", font_name=SANS, C=C)
        y += 0.48


def add_salon_poster(prs: Presentation) -> None:
    """Poster finale: oversized outlined typography sits behind the salon image."""
    slide = _slide(prs)
    rect(slide, 0, 0, 13.333, 7.5, "paper", C=C)
    cover_image(slide, 2.25, 1.28, 8.88, 5.45, str(SALON))
    text(slide, 0.38, 0.24, 12.55, 0.82, "UNFINISHED", font_size=45,
         color="oxide", bold=True, align="center", font_name=SERIF, C=C)
    rect(slide, 0.58, 1.96, 2.56, 3.78, "ink", C=C)
    text(slide, 0.90, 2.34, 1.93, 0.28, "THE FINAL\nFITTING", font_size=17,
         color="paper", bold=True, font_name=SANS, C=C)
    _rule(slide, 0.90, 3.14, 1.58, "gold", 0.052)
    multiline(slide, 0.90, 3.56, 1.88, 0.88, ["A garment is", "never still."],
              font_size=14, color="chalk", font_name=SERIF, C=C)
    text(slide, 0.90, 5.15, 1.82, 0.22, "PARIS / 19:30", font_size=8,
         color="gold", bold=True, font_name=SANS, C=C)
    strip = shape(slide, "PARALLELOGRAM", 8.67, 5.64, 3.82, 0.56, "oxide", C=C)
    strip.rotation = -8
    label = text(slide, 8.85, 5.82, 3.44, 0.18, "PRIVATE SALON / SEPTEMBER 2027",
                 font_size=8, color="paper", bold=True, align="center", font_name=SANS, C=C)
    label.rotation = -8
    text(slide, 11.26, 1.48, 1.55, 0.36, "EDITION 01\nCOUTURE / MOTION", font_size=7,
         color="oxide", bold=True, align="right", font_name=SANS, C=C)
    text(slide, 2.26, 6.92, 8.82, 0.20, "THE WHITE STUDY — A COUTURE EDITORIAL", font_size=8,
         color="smoke", bold=True, align="center", font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_silhouette(prs)
    add_material_index(prs)
    add_salon_poster(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
