"""A four-page couture dossier built only with pptx_designer.

It uses distinct images for silhouette, atelier work, material study and salon
presentation. All copy, rules and information panels remain editable.

Run: python examples/couture_editorial_deck.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.shapes import oval, rect
from pptx_designer.tools.text import multiline, text


ROOT = Path(__file__).parent
LOOK = ROOT / "assets" / "couture-look.png"
ATELIER = ROOT / "assets" / "couture-atelier.png"
MATERIAL = ROOT / "assets" / "couture-material.png"
SALON = ROOT / "assets" / "couture-salon.png"
C = {
    "black": "#171310",
    "paper": "#F6F0E8",
    "sand": "#C89A70",
    "rust": "#9C4E35",
    "stone": "#9D9289",
    "champagne": "#E3D1BA",
    "white": "#FFFFFF",
}
SERIF = "Georgia"
SANS = "Arial"


def add_cover(prs: Presentation) -> None:
    """A composed collection plate, not a conventional text/image split cover."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "paper", C=C)
    rect(slide, 0.52, 0.48, 12.28, 0.08, "black", C=C)
    cover_image(slide, 0.76, 0.92, 11.82, 4.58, str(LOOK))
    rect(slide, 10.35, 0.92, 2.23, 0.54, "black", C=C)
    text(slide, 10.63, 1.07, 1.72, 0.24, "ATELIER EDITION", font_size=9,
         color="paper", bold=True, align="center", font_name=SANS, C=C)
    text(slide, 0.76, 5.94, 5.20, 0.38, "ATELIER MERIDIAN", font_size=17,
         color="black", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.74, 6.31, 6.28, 0.84,
              ["Sculpted light,", "held in fabric."],
              font_size=24, color="rust", font_name=SERIF, C=C)
    text(slide, 8.44, 6.10, 3.84, 0.24, "SPRING / SUMMER 2027", font_size=9,
         color="rust", bold=True, align="right", font_name=SANS, C=C)
    multiline(slide, 8.44, 6.40, 3.84, 0.66,
              ["A study of drape, restraint,", "and the precision of the hand."],
              font_size=13, color="black", align="right", font_name=SERIF, C=C)


def add_atelier(prs: Presentation) -> None:
    """Craft becomes the evidence of value: no generic silhouette page."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "black", C=C)
    cover_image(slide, 0.56, 0.58, 12.20, 3.84, str(ATELIER))
    rect(slide, 0.56, 3.88, 12.20, 0.54, "paper", C=C)
    text(slide, 0.84, 4.03, 11.54, 0.24,
         "HAND-FOLDED ORGANZA / TEMPORARY STITCH / FINAL SILHOUETTE", font_size=9,
         color="rust", bold=True, font_name=SANS, C=C)
    text(slide, 0.64, 4.96, 2.94, 0.24, "01 / THE HAND", font_size=9,
         color="sand", bold=True, font_name=SANS, C=C)
    text(slide, 0.58, 5.36, 6.90, 0.54, "Construction is the ornament.", font_size=26,
         color="paper", font_name=SERIF, C=C)
    multiline(slide, 8.04, 5.23, 4.06, 0.92,
              ["Each fold is pinned before it is trusted.",
               "The final line is discovered, not drawn."],
              font_size=14, color="champagne", font_name=SERIF, C=C)
    rect(slide, 0.62, 6.72, 11.72, 0.06, "rust", C=C)


def add_material(prs: Presentation) -> None:
    """Material study with factual labels rather than decorative colour swatches."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(MATERIAL))
    rect(slide, 0.54, 0.52, 5.04, 1.36, "paper", C=C)
    text(slide, 0.82, 0.77, 3.70, 0.24, "02 / MATERIAL STUDY", font_size=9,
         color="rust", bold=True, font_name=SANS, C=C)
    text(slide, 0.80, 1.10, 4.18, 0.42, "Texture carries the light.", font_size=18,
         color="black", font_name=SERIF, C=C)
    rect(slide, 0, 5.66, 13.333, 1.84, "black", C=C)
    materials = [("01", "ORGANZA", "translucent structure"), ("02", "SATIN", "weight and reflection"),
                 ("03", "PEARL", "a point of brightness")]
    for index, (number, name, detail) in enumerate(materials):
        x = 0.76 + index * 4.08
        oval(slide, x, 6.16, 0.42, 0.42, "sand", C=C)
        text(slide, x + 0.60, 6.07, 2.16, 0.24, f"{number}  {name}", font_size=10,
             color="paper", bold=True, font_name=SANS, C=C)
        text(slide, x + 0.60, 6.40, 2.72, 0.28, detail, font_size=11,
             color="champagne", font_name=SERIF, C=C)


def add_salon(prs: Presentation) -> None:
    """An exhibition-like finale; event details remain secondary to the garment."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(SALON))
    rect(slide, 0.56, 0.52, 12.22, 0.58, "paper", C=C)
    text(slide, 0.84, 0.69, 3.42, 0.24, "03 / SALON AFTER DARK", font_size=9,
         color="rust", bold=True, font_name=SANS, C=C)
    text(slide, 8.18, 0.69, 4.14, 0.24, "PARIS / SEPTEMBER 2027", font_size=9,
         color="rust", bold=True, align="right", font_name=SANS, C=C)
    rect(slide, 0.58, 5.76, 8.08, 1.18, "black", C=C)
    text(slide, 0.88, 6.04, 7.38, 0.46, "The collection waits for its first witness.", font_size=21,
         color="paper", font_name=SERIF, C=C)
    text(slide, 9.24, 6.06, 3.04, 0.24, "PRIVATE PRESENTATION", font_size=9,
         color="paper", bold=True, align="right", font_name=SANS, C=C)
    text(slide, 9.24, 6.48, 3.04, 0.24, "19:30 / BY APPOINTMENT", font_size=9,
         color="champagne", align="right", font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_atelier(prs)
    add_material(prs)
    add_salon(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
