"""A four-page couture editorial study built only with pptx_designer.

This intentionally uses four distinct editorial structures: contact sheet,
manifesto, material plate and salon poster. Supporting copy is editable.

Run: python examples/couture_editorial_deck.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.shapes import rect
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


def add_contact_sheet(prs: Presentation) -> None:
    """Cover: asymmetrical editorial contact sheet, not a hero-image cover."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "paper", C=C)
    cover_image(slide, 0.56, 0.55, 6.18, 5.92, str(LOOK))
    cover_image(slide, 7.04, 0.55, 5.72, 2.32, str(MATERIAL))
    cover_image(slide, 7.04, 3.16, 5.72, 1.82, str(ATELIER))
    rect(slide, 7.04, 5.25, 5.72, 1.22, "black", C=C)
    text(slide, 7.34, 5.52, 4.98, 0.40, "THE WHITE STUDY", font_size=18,
         color="paper", bold=True, font_name=SANS, C=C)
    text(slide, 7.35, 6.05, 4.90, 0.24, "COUTURE / SPRING–SUMMER 2027", font_size=9,
         color="champagne", bold=True, font_name=SANS, C=C)
    text(slide, 0.58, 6.79, 3.72, 0.24, "SILHOUETTE / HAND / MATERIAL", font_size=9,
         color="rust", bold=True, font_name=SANS, C=C)
    text(slide, 7.04, 6.82, 5.62, 0.24,
         "AN EDITORIAL RECORD OF HOW A DRESS COMES INTO BEING", font_size=8,
         color="stone", bold=True, align="right", font_name=SANS, C=C)


def add_manifesto(prs: Presentation) -> None:
    """Page two: typographic manifesto above a narrow atelier evidence strip."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "black", C=C)
    text(slide, 0.64, 0.62, 2.80, 0.24, "I / THE HAND", font_size=9,
         color="sand", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.58, 1.34, 9.20, 2.38,
              ["FORM IS A DECISION", "MADE BY HAND."],
              font_size=48, color="paper", bold=True, font_name=SERIF, C=C)
    multiline(slide, 9.72, 1.58, 2.58, 1.62,
              ["No seam is merely", "functional. It guides", "the body through light."],
              font_size=14, color="champagne", font_name=SERIF, C=C)
    cover_image(slide, 0.58, 4.56, 12.18, 2.10, str(ATELIER))
    rect(slide, 0.58, 6.17, 12.18, 0.49, "paper", C=C)
    text(slide, 0.88, 6.29, 11.52, 0.25,
         "PIN / FOLD / RELEASE / REPEAT — THE GARMENT IS FOUND THROUGH ITS MAKING", font_size=8,
         color="rust", bold=True, font_name=SANS, C=C)


def add_material_plate(prs: Presentation) -> None:
    """Page three: near-silent full-frame material plate with side annotations."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(MATERIAL))
    rect(slide, 0.52, 0.52, 2.84, 6.46, "paper", C=C)
    text(slide, 0.82, 0.84, 2.14, 0.24, "II / MATERIAL", font_size=9,
         color="rust", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.78, 1.38, 2.12, 1.48,
              ["Light", "needs", "texture."],
              font_size=30, color="black", bold=True, font_name=SERIF, C=C)
    rect(slide, 0.82, 3.34, 1.92, 0.06, "sand", C=C)
    multiline(slide, 0.82, 3.76, 1.92, 1.18,
              ["Organza", "Satin", "Pearl"],
              font_size=14, color="rust", font_name=SANS, C=C)
    multiline(slide, 0.82, 5.42, 1.92, 0.92,
              ["Structure", "Reflection", "Brightness"],
              font_size=11, color="stone", font_name=SERIF, C=C)
    text(slide, 0.82, 6.62, 1.92, 0.22, "A MATERIAL PLATE", font_size=8,
         color="rust", bold=True, font_name=SANS, C=C)


def add_salon_poster(prs: Presentation) -> None:
    """Page four: a restrained exhibition poster, letting the salon carry the drama."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(SALON))
    rect(slide, 0.56, 0.54, 4.20, 5.78, "paper", C=C)
    text(slide, 0.86, 0.86, 3.48, 0.24, "III / AFTER DARK", font_size=9,
         color="rust", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.82, 1.50, 3.34, 1.58,
              ["A room", "for the", "first look."],
              font_size=31, color="black", bold=True, font_name=SERIF, C=C)
    multiline(slide, 0.88, 3.78, 3.24, 0.88,
              ["The dress stands still.", "Everything around it changes."],
              font_size=14, color="rust", font_name=SERIF, C=C)
    rect(slide, 0.86, 5.22, 3.32, 0.06, "sand", C=C)
    multiline(slide, 0.86, 5.54, 3.20, 0.52,
              ["PRIVATE SALON / PARIS", "SEPTEMBER 2027 / 19:30"],
              font_size=8, color="black", bold=True, font_name=SANS, C=C)
    text(slide, 5.30, 6.82, 7.14, 0.24,
         "THE WHITE STUDY / COUTURE EDITORIAL", font_size=8,
         color="paper", bold=True, align="right", font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_contact_sheet(prs)
    add_manifesto(prs)
    add_material_plate(prs)
    add_salon_poster(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
