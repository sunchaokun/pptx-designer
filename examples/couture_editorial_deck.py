"""A four-page couture editorial deck built only with pptx_designer.

Run: python examples/couture_editorial_deck.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.shapes import rect, rrect
from pptx_designer.tools.text import multiline, text


ROOT = Path(__file__).parent
COUTURE = ROOT / "assets" / "couture-editorial.png"
C = {"black": "#171310", "paper": "#F6F0E8", "sand": "#C89A70", "rust": "#9C4E35", "stone": "#9D9289"}
SERIF = "Georgia"
SANS = "Arial"


def add_cover(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(COUTURE))
    rect(slide, 0, 0, 13.333, 0.14, "black", C=C)
    rect(slide, 0, 0, 4.35, 7.5, "paper", C=C)
    text(slide, 0.68, 0.78, 2.7, 0.18, "ATELIER  /  2026", font_size=10, color="rust", bold=True, font_name=SANS, C=C)
    text(slide, 0.65, 2.05, 3.3, 1.20, "Stillness\nin motion", font_size=39, color="black", bold=True, font_name=SERIF, C=C)
    text(slide, 0.68, 3.78, 2.95, 0.62, "A couture study in sculpted fabric, sun, and silence.", font_size=15,
         color="rust", font_name=SERIF, C=C)
    text(slide, 0.68, 6.48, 3.0, 0.16, "PRIVATE COLLECTION  /  SS 2027", font_size=9, color="stone", bold=True, font_name=SANS, C=C)


def add_story(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "paper", C=C)
    cover_image(slide, 0.75, 0.70, 5.25, 6.05, str(COUTURE))
    rect(slide, 6.42, 0.70, 0.04, 6.05, "sand", C=C)
    text(slide, 7.05, 0.88, 3.8, 0.18, "01  /  THE SILHOUETTE", font_size=10, color="rust", bold=True, font_name=SANS, C=C)
    text(slide, 7.00, 1.55, 5.15, 1.15, "The line\ncomes first.", font_size=39, color="black", bold=True, font_name=SERIF, C=C)
    multiline(slide, 7.05, 3.22, 4.65, 1.10,
              ["Every volume is reduced until gesture becomes architecture.", "The body is not dressed. It is framed."],
              font_size=15, color="rust", font_name=SERIF, C=C)
    rrect(slide, 7.05, 5.35, 4.75, 0.80, "black", C=C)
    text(slide, 7.35, 5.64, 4.1, 0.16, "CUT  /  FALL  /  LIGHT", font_size=10, color="paper", bold=True, font_name=SANS, C=C)


def add_palette(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "black", C=C)
    text(slide, 0.72, 0.75, 2.7, 0.18, "02  /  THE PALETTE", font_size=10, color="sand", bold=True, font_name=SANS, C=C)
    text(slide, 0.68, 1.35, 6.3, 0.55, "Warm neutrals,\nprecise emotion.", font_size=36, color="paper", bold=True, font_name=SERIF, C=C)
    colors = [("PORCELAIN", "#F6F0E8"), ("SAND", "#C89A70"), ("OXIDE", "#9C4E35"), ("OBSIDIAN", "#171310")]
    for index, (name, color) in enumerate(colors):
        x = 0.78 + index * 3.03
        rect(slide, x, 3.40, 2.54, 1.55, color, C=C)
        text(slide, x, 5.22, 2.54, 0.16, name, font_size=10, color="paper", bold=True, font_name=SANS, C=C)
    cover_image(slide, 8.25, 5.80, 4.25, 1.00, str(COUTURE))
    text(slide, 0.78, 6.15, 5.9, 0.22, "A collection designed to be remembered as a single image.", font_size=14, color="#D9C9BC", font_name=SERIF, C=C)


def add_invitation(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(COUTURE))
    rect(slide, 0, 0, 13.333, 7.5, "#171310", C=C)
    # The black overlay is intentionally interrupted by the editorial image panel.
    cover_image(slide, 7.10, 0, 6.233, 7.5, str(COUTURE))
    text(slide, 0.78, 1.25, 5.25, 0.18, "THE PRIVATE VIEW", font_size=10, color="sand", bold=True, font_name=SANS, C=C)
    text(slide, 0.72, 2.05, 5.3, 1.20, "Spring / Summer\n2027", font_size=39, color="paper", bold=True, font_name=SERIF, C=C)
    text(slide, 0.78, 4.05, 4.95, 0.52, "Palais de Tokyo\nParis  •  18 September  •  19:30", font_size=15, color="#D9C9BC", font_name=SERIF, C=C)
    rrect(slide, 0.78, 5.72, 2.45, 0.52, "sand", C=C)
    text(slide, 1.02, 5.88, 1.95, 0.14, "BY INVITATION ONLY", font_size=9, color="black", bold=True, align="center", font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_story(prs)
    add_palette(prs)
    add_invitation(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
