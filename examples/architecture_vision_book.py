"""A four-page architecture concept book built only with pptx_designer.

The imagery is intentionally a single visual anchor. Every caption, title,
rule and colour field remains a native, editable PowerPoint object.

Run: python examples/architecture_vision_book.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.shapes import oval, rect
from pptx_designer.tools.text import multiline, text


ROOT = Path(__file__).parent
PAVILION = ROOT / "assets" / "monumental-pavilion.png"
DUSK = ROOT / "assets" / "architecture-dusk.png"
INTERIOR = ROOT / "assets" / "architecture-interior.png"
DETAIL = ROOT / "assets" / "architecture-detail.png"
AERIAL = ROOT / "assets" / "architecture-aerial.png"
C = {
    "ultramarine": "#123B7A",
    "electric": "#1769E0",
    "paper": "#F4F0E8",
    "ink": "#101F37",
    "signal": "#DF3E32",
    "mist": "#DDEBFF",
    "white": "#FFFFFF",
}
SERIF = "Georgia"
SANS = "Arial"


def add_cover(prs: Presentation) -> None:
    """A typographic cover: image, title and label overlap rather than split."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "paper", C=C)
    cover_image(slide, 1.35, 0.52, 11.25, 5.62, str(AERIAL))
    rect(slide, 0.56, 0.52, 0.22, 5.62, "signal", C=C)
    rect(slide, 8.78, 0.52, 3.82, 0.65, "ultramarine", C=C)
    text(slide, 9.06, 0.77, 3.12, 0.16, "PACIFIC CULTURAL DISTRICT  /  2027",
         font_size=8, color="white", bold=True, font_name=SANS, C=C)
    text(slide, 0.62, 5.42, 7.6, 0.66, "HORIZON", font_size=52,
         color="ink", bold=True, font_name=SERIF, C=C)
    text(slide, 6.38, 5.42, 5.9, 0.66, "COMMONS", font_size=52,
         color="signal", bold=True, font_name=SERIF, C=C)
    text(slide, 0.64, 6.38, 3.2, 0.16, "A CIVIC PAVILION / CONCEPT BOOK", font_size=9,
         color="signal", bold=True, font_name=SANS, C=C)
    multiline(slide, 8.20, 6.26, 4.15, 0.54,
              ["A generous threshold between", "climate, culture and pause."],
              font_size=13, color="ultramarine", font_name=SERIF, C=C)
    text(slide, 0.64, 7.04, 11.8, 0.14,
         "STUDIO HORIZON     /     SITE 07     /     PACIFIC COAST", font_size=8,
         color="ink", bold=True, font_name=SANS, C=C)


def add_proposition(prs: Presentation) -> None:
    """A poster-like proposition page, with the image treated as a material sample."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "ultramarine", C=C)
    cover_image(slide, 3.05, 0.55, 7.28, 5.82, str(INTERIOR))
    rect(slide, 3.05, 5.75, 7.28, 0.62, "paper", C=C)
    text(slide, 3.33, 5.97, 6.65, 0.15, "THE ROOF IS A CLIMATE DEVICE, NOT AN OBJECT.",
         font_size=9, color="ultramarine", bold=True, font_name=SANS, C=C)
    text(slide, 0.58, 0.62, 2.0, 0.16, "01 / PROPOSITION", font_size=9,
         color="mist", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.55, 1.34, 2.14, 3.35, ["SHADE", "IS", "CIVIC."], font_size=39,
              color="white", bold=True, font_name=SERIF, C=C)
    multiline(slide, 10.78, 1.20, 1.92, 1.95,
              ["The canopy gives the", "public room its", "temperature, scale", "and reason to stay."],
              font_size=13, color="mist", font_name=SERIF, C=C)
    oval(slide, 10.98, 4.40, 1.05, 1.05, "signal", C=C)
    text(slide, 0.58, 6.84, 11.5, 0.16,
         "2,800 M²     /     WATER + SHADE + GATHERING     /     OPEN TO THE HORIZON",
         font_size=8, color="mist", bold=True, font_name=SANS, C=C)


def add_sequence(prs: Presentation) -> None:
    """A paced editorial sequence; not a conventional three-card layout."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "paper", C=C)
    text(slide, 0.62, 0.54, 2.1, 0.16, "02 / ARRIVAL SEQUENCE", font_size=9,
         color="signal", bold=True, font_name=SANS, C=C)
    text(slide, 0.56, 1.06, 12.0, 0.62, "A place unfolds in three pauses.", font_size=38,
         color="ink", bold=True, font_name=SERIF, C=C)
    steps = [
        ("I", "APPROACH", "The long edge slows the city before the building begins."),
        ("II", "CROSSING", "A cool shadow makes the act of arrival feel deliberate."),
        ("III", "RETURN", "Water sends the sky back into the room as a quiet civic ritual."),
    ]
    for index, (roman, title, detail) in enumerate(steps):
        top = 2.18 + index * 1.40
        text(slide, 0.68, top, 0.78, 0.46, roman, font_size=24,
             color="signal", bold=True, font_name=SERIF, C=C)
        rect(slide, 1.68, top + 0.20, 2.35 + index * 1.45, 0.07, "electric", C=C)
        text(slide, 4.74, top, 2.10, 0.26, title, font_size=16,
             color="ultramarine", bold=True, font_name=SANS, C=C)
        text(slide, 7.28, top - 0.02, 4.85, 0.46, detail, font_size=13,
             color="ink", font_name=SERIF, C=C)
    cover_image(slide, 9.45, 5.95, 2.78, 0.92, str(DETAIL))
    rect(slide, 0.62, 6.94, 12.08, 0.07, "signal", C=C)


def add_finale(prs: Presentation) -> None:
    """A closing spread with a full-bleed image interrupted by a paper manifesto."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(DUSK))
    rect(slide, 0.58, 0.55, 5.20, 5.72, "paper", C=C)
    rect(slide, 0.58, 0.55, 5.20, 0.15, "signal", C=C)
    text(slide, 0.90, 0.95, 3.7, 0.16, "03 / THE INVITATION", font_size=9,
         color="signal", bold=True, font_name=SANS, C=C)
    multiline(slide, 0.86, 1.70, 4.25, 0.90, ["MAKE ROOM", "FOR RETURN."], font_size=38,
              color="ink", bold=True, font_name=SERIF, C=C)
    multiline(slide, 0.92, 3.55, 4.08, 0.95,
              ["The strongest civic gesture is not spectacle.",
               "It is giving people a reason to pause, return, and belong."],
              font_size=15, color="ultramarine", font_name=SERIF, C=C)
    text(slide, 0.92, 5.52, 3.9, 0.16, "STUDIO HORIZON  /  ARCHITECTURE + PUBLIC LIFE",
         font_size=8, color="ink", bold=True, font_name=SANS, C=C)
    rect(slide, 6.45, 6.62, 6.28, 0.34, "ultramarine", C=C)
    text(slide, 6.70, 6.73, 5.75, 0.13, "PACIFIC CULTURAL DISTRICT  /  CONCEPT BOOK  /  2027",
         font_size=8, color="white", bold=True, font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_proposition(prs)
    add_sequence(prs)
    add_finale(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
