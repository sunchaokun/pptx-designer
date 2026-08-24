"""A four-page luxury fragrance lookbook built only with pptx_designer.

Run: python examples/luxury_fragrance_lookbook.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.shapes import oval, rect, rrect
from pptx_designer.tools.text import multiline, text


ROOT = Path(__file__).parent
PERFUME = ROOT / "assets" / "luxury-perfume.png"
C = {"ink": "#1C0C11", "wine": "#4A0E1D", "cream": "#F7F0E9", "gold": "#C9A66B", "muted": "#9E7B83"}
SERIF = "Georgia"
SANS = "Arial"


def add_cover(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(PERFUME))
    rect(slide, 0, 0, 5.15, 7.5, "ink", C=C)
    rect(slide, 5.15, 0, 0.055, 7.5, "gold", C=C)
    text(slide, 0.68, 0.85, 3.8, 0.20, "MAISON AURELIA  /  N° 07", font_size=10, color="gold", bold=True, font_name=SANS, C=C)
    text(slide, 0.68, 2.0, 4.0, 1.25, "The ritual\nof light", font_size=41, color="cream", bold=True, font_name=SERIF, C=C)
    text(slide, 0.72, 3.72, 3.7, 0.55, "An extrait composed for the hour between dusk and silence.",
         font_size=15, color="#E7D8CF", font_name=SERIF, C=C)
    text(slide, 0.72, 6.55, 3.8, 0.18, "AUTUMN / WINTER 2026", font_size=9, color="gold", bold=True, font_name=SANS, C=C)


def add_manifesto(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "cream", C=C)
    text(slide, 0.75, 0.62, 2.4, 0.18, "01  /  THE COMPOSITION", font_size=10, color="wine", bold=True, font_name=SANS, C=C)
    text(slide, 0.72, 1.28, 6.1, 1.25, "A fragrance\nwith a slow pulse.", font_size=38, color="ink", bold=True, font_name=SERIF, C=C)
    multiline(slide, 0.78, 3.15, 4.65, 1.25,
              ["The first note is bergamot at night.", "Then iris, smoked tea, and a trace of cedar."],
              font_size=16, color="wine", font_name=SERIF, C=C)
    cover_image(slide, 6.12, 0.72, 6.45, 5.35, str(PERFUME))
    rect(slide, 6.12, 5.78, 6.45, 0.29, "wine", C=C)
    notes = [("01", "BERGAMOT", "electric opening"), ("02", "IRIS", "powdered heart"), ("03", "CEDAR", "quiet finish")]
    for index, (number, note, detail) in enumerate(notes):
        x = 0.78 + index * 1.82
        text(slide, x, 5.50, 0.38, 0.16, number, font_size=9, color="gold", bold=True, font_name=SANS, C=C)
        text(slide, x, 5.80, 1.55, 0.20, note, font_size=11, color="ink", bold=True, font_name=SANS, C=C)
        text(slide, x, 6.10, 1.55, 0.18, detail, font_size=9, color="muted", font_name=SANS, C=C)
    text(slide, 0.78, 6.82, 11.8, 0.16, "AURELIA / EXTRACT OF PARFUM / 50 ML", font_size=8, color="wine", bold=True, font_name=SANS, C=C)


def add_ingredients(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "wine", C=C)
    text(slide, 0.76, 0.68, 2.5, 0.18, "02  /  THE MATERIALS", font_size=10, color="gold", bold=True, font_name=SANS, C=C)
    text(slide, 0.72, 1.25, 5.0, 0.95, "A study in\ncontrast.", font_size=37, color="cream", bold=True, font_name=SERIF, C=C)
    cover_image(slide, 6.45, 0.65, 5.95, 3.05, str(PERFUME))
    rrect(slide, 0.78, 3.15, 5.05, 2.30, "#64182B", C=C)
    text(slide, 1.10, 3.52, 4.15, 0.26, "FORM", font_size=11, color="gold", bold=True, font_name=SANS, C=C)
    text(slide, 1.10, 3.95, 4.15, 0.65, "Black glass.\nA single gold seam.", font_size=23, color="cream", bold=True, font_name=SERIF, C=C)
    rrect(slide, 6.45, 4.18, 5.95, 1.27, "cream", C=C)
    text(slide, 6.78, 4.48, 5.2, 0.20, "THE GESTURE", font_size=10, color="wine", bold=True, font_name=SANS, C=C)
    text(slide, 6.78, 4.82, 5.1, 0.25, "One spray. One deliberate pause.", font_size=16, color="ink", font_name=SERIF, C=C)
    for index, color in enumerate(("#D8B777", "#A64C64", "#EEE0D3", "#201017")):
        oval(slide, 0.84 + index * 1.14, 6.10, 0.64, 0.64, color, C=C)
    text(slide, 5.63, 6.31, 5.7, 0.16, "Palette: champagne / wine / porcelain / ink", font_size=9, color="#E7C8CF", font_name=SANS, C=C)


def add_campaign(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    cover_image(slide, 0, 0, 13.333, 7.5, str(PERFUME))
    rect(slide, 0, 5.45, 13.333, 2.05, "ink", C=C)
    text(slide, 0.74, 5.88, 7.7, 0.48, "The night stays with you.", font_size=31, color="cream", bold=True, font_name=SERIF, C=C)
    text(slide, 0.77, 6.55, 5.2, 0.18, "MAISON AURELIA  /  N° 07  /  AVAILABLE OCTOBER 2026", font_size=9, color="gold", bold=True, font_name=SANS, C=C)
    rrect(slide, 10.55, 5.90, 1.85, 0.52, "cream", C=C)
    text(slide, 10.74, 6.07, 1.45, 0.14, "DISCOVER", font_size=9, color="wine", bold=True, align="center", font_name=SANS, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_manifesto(prs)
    add_ingredients(prs)
    add_campaign(prs)
    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
