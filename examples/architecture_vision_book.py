"""A four-page architecture vision book built only with pptx_designer.

Run: python examples/architecture_vision_book.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.shapes import oval, rect, rrect
from pptx_designer.tools.text import multiline, text


ROOT = Path(__file__).parent
PAVILION = ROOT / "assets" / "monumental-pavilion.png"
C = {"blue": "#123B7A", "cobalt": "#1967D2", "sky": "#DDEBFF", "white": "#F9FBFF", "ink": "#10213D", "red": "#D84437"}
SERIF = "Georgia"
SANS = "Arial"


def add_cover(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(PAVILION))
    rect(slide, 0, 0, 13.333, 0.15, "red", C=C)
    rrect(slide, 0.70, 0.72, 3.15, 0.46, "white", C=C)
    text(slide, 0.90, 0.87, 2.75, 0.14, "STUDIO HORIZON  /  2027", font_size=9, color="blue", bold=True, font_name=SANS, C=C)
    text(slide, 0.72, 2.00, 6.7, 1.10, "A place for\nclearer futures.", font_size=42, color="white", bold=True, font_name=SERIF, C=C)
    text(slide, 0.78, 3.70, 4.9, 0.48, "A civic pavilion imagined as a threshold between climate, culture, and calm.",
         font_size=15, color="sky", font_name=SERIF, C=C)
    rect(slide, 0, 6.90, 13.333, 0.60, "blue", C=C)
    text(slide, 0.78, 7.10, 11.8, 0.14, "CONCEPT BOOK  /  PACIFIC CULTURAL DISTRICT  /  COMPETITION ENTRY", font_size=9,
         color="white", bold=True, font_name=SANS, C=C)


def add_concept(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "white", C=C)
    text(slide, 0.72, 0.72, 2.8, 0.18, "01  /  THE CONCEPT", font_size=10, color="red", bold=True, font_name=SANS, C=C)
    text(slide, 0.68, 1.30, 5.3, 1.08, "Monumental,\nnever imposing.", font_size=39, color="ink", bold=True, font_name=SERIF, C=C)
    multiline(slide, 0.75, 3.02, 4.65, 1.08,
              ["A generous curve gives shade, frames water, and makes arrival feel ceremonial.",
               "The architecture does less so the landscape can do more."],
              font_size=15, color="blue", font_name=SERIF, C=C)
    cover_image(slide, 5.85, 0.72, 6.75, 5.90, str(PAVILION))
    rect(slide, 5.85, 6.30, 6.75, 0.32, "blue", C=C)
    text(slide, 0.78, 5.35, 3.8, 0.20, "2,800 m²  /  WATER + SHADE + GATHERING", font_size=9, color="red", bold=True, font_name=SANS, C=C)


def add_principles(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "blue", C=C)
    text(slide, 0.72, 0.72, 3.0, 0.18, "02  /  THE PRINCIPLES", font_size=10, color="sky", bold=True, font_name=SANS, C=C)
    text(slide, 0.68, 1.30, 6.0, 0.54, "Three precise gestures.", font_size=37, color="white", bold=True, font_name=SERIF, C=C)
    principles = [("01", "SHADE", "A deep canopy reduces heat and creates a public room."),
                  ("02", "REFLECTION", "Water doubles the sky and slows the pace of the site."),
                  ("03", "THRESHOLD", "A single red object marks arrival without adding noise.")]
    for index, (number, title, detail) in enumerate(principles):
        x = 0.78 + index * 4.05
        rrect(slide, x, 2.65, 3.58, 2.58, "#1B4D95", C=C)
        oval(slide, x + 0.30, 3.00, 0.55, 0.55, "red" if index == 2 else "sky", C=C)
        text(slide, x + 1.05, 3.02, 2.0, 0.18, number, font_size=9, color="sky", bold=True, font_name=SANS, C=C)
        text(slide, x + 0.30, 3.88, 2.8, 0.30, title, font_size=19, color="white", bold=True, font_name=SERIF, C=C)
        text(slide, x + 0.30, 4.35, 2.78, 0.48, detail, font_size=11, color="#DDEBFF", font_name=SANS, C=C)
    text(slide, 0.78, 6.42, 10.8, 0.18, "The proposal measures ambition by the quality of the public’s pause.", font_size=14,
         color="sky", font_name=SERIF, C=C)


def add_finale(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(PAVILION))
    rect(slide, 0, 0, 5.15, 7.5, "white", C=C)
    rect(slide, 5.15, 0, 0.06, 7.5, "red", C=C)
    text(slide, 0.70, 0.92, 3.5, 0.18, "THE INVITATION", font_size=10, color="red", bold=True, font_name=SANS, C=C)
    text(slide, 0.65, 2.05, 4.05, 1.20, "Build a place\nworth returning to.", font_size=38, color="ink", bold=True, font_name=SERIF, C=C)
    text(slide, 0.72, 4.06, 3.75, 0.52, "A pavilion that does not compete with the horizon—it clarifies it.",
         font_size=15, color="blue", font_name=SERIF, C=C)
    rrect(slide, 0.72, 5.82, 2.62, 0.50, "blue", C=C)
    text(slide, 0.98, 5.98, 2.08, 0.14, "STUDIO HORIZON", font_size=9, color="white", bold=True, align="center", font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_concept(prs)
    add_principles(prs)
    add_finale(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
