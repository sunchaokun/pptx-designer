"""Advanced example: editable SVG architecture diagram in a PowerPoint slide.

Run from the repository root:
    python examples/advanced_svg_architecture.py

The SVG is compiled with pptx_designer.tools.svg.svg_chart; it is not embedded
as a screenshot. The resulting labels and geometry are editable PPT objects.
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.tools.layout import page_header, page_number
from pptx_designer.tools.shapes import rect, rrect
from pptx_designer.tools.svg import svg_chart
from pptx_designer.tools.text import text


C = {
    "primary": "#2563EB",
    "accent": "#F97316",
    "background": "#F8FAFC",
    "text_dark": "#0F172A",
    "text_body": "#475569",
    "text_muted": "#64748B",
    "divider": "#CBD5E1",
}

ARCHITECTURE_SVG = """<svg viewBox="0 0 1200 560" xmlns="http://www.w3.org/2000/svg">
  <style>
    .lane { fill: #FFFFFF; stroke: #D0D5DD; stroke-width: 2; }
    .label { font-family: Arial; font-size: 20px; fill: #101828; font-weight: bold; }
    .note { font-family: Arial; font-size: 15px; fill: #667085; }
    .connector { stroke: #98A2B3; stroke-width: 4; }
  </style>
  <defs>
    <linearGradient id="blue" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2563EB"/><stop offset="100%" stop-color="#1D4ED8"/>
    </linearGradient>
    <linearGradient id="violet" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#8B5CF6"/><stop offset="100%" stop-color="#6D28D9"/>
    </linearGradient>
  </defs>
  <rect x="20" y="22" width="1160" height="125" rx="18" class="lane"/>
  <rect x="20" y="217" width="1160" height="125" rx="18" class="lane"/>
  <rect x="20" y="412" width="1160" height="125" rx="18" class="lane"/>
  <line x1="325" y1="147" x2="325" y2="217" class="connector"/>
  <line x1="605" y1="147" x2="605" y2="217" class="connector"/>
  <line x1="605" y1="342" x2="605" y2="412" class="connector"/>
  <rect x="110" y="75" width="210" height="48" rx="12" fill="url(#blue)"/>
  <text x="215" y="106" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold" fill="#FFFFFF">Web workspace</text>
  <rect x="390" y="75" width="210" height="48" rx="12" fill="url(#blue)"/>
  <text x="495" y="106" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold" fill="#FFFFFF">Mobile companion</text>
  <rect x="670" y="75" width="210" height="48" rx="12" fill="url(#blue)"/>
  <text x="775" y="106" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold" fill="#FFFFFF">Partner portal</text>
  <rect x="460" y="270" width="290" height="48" rx="12" fill="url(#violet)"/>
  <text x="605" y="301" text-anchor="middle" font-family="Arial" font-size="21" font-weight="bold" fill="#FFFFFF">Decision and workflow engine</text>
  <rect x="280" y="465" width="230" height="48" rx="12" fill="#0F766E"/>
  <text x="395" y="496" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold" fill="#FFFFFF">Customer data</text>
  <rect x="700" y="465" width="230" height="48" rx="12" fill="#0F766E"/>
  <text x="815" y="496" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold" fill="#FFFFFF">Integration layer</text>
</svg>"""


def add_cover(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "#0F172A", C=C)
    rect(slide, 0, 0, 13.333, 0.14, "primary", C=C)
    text(slide, 0.9, 1.55, 11.0, 0.58, "Composable Platform\nArchitecture", font_size=39, color="#FFFFFF", bold=True, C=C)
    text(slide, 0.95, 3.15, 9.0, 0.30, "A four-page technical narrative built with native PPT and editable SVG objects", font_size=16,
         color="#BFDBFE", C=C)
    text(slide, 0.95, 6.05, 4.4, 0.18, "ARCHITECTURE REVIEW  •  2026", font_size=10, color="#93C5FD", bold=True, C=C)


def add_agenda(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    page_header(slide, "Architecture review", "A decision-ready technical narrative", C=C)
    topics = [("01", "User experience", "One workflow across web, mobile, and partner surfaces"),
              ("02", "Decision engine", "A shared intelligence layer orchestrates workflow choices"),
              ("03", "Foundation", "Customer data and governed integrations create leverage")]
    for index, (number, title, description) in enumerate(topics):
        y = 1.65 + index * 1.38
        rrect(slide, 0.88, y, 11.6, 0.96, "#FFFFFF", line="divider", C=C)
        text(slide, 1.18, y + 0.24, 0.65, 0.24, number, font_size=18, color="primary", bold=True, C=C)
        text(slide, 2.1, y + 0.18, 3.2, 0.26, title, font_size=16, color="text_dark", bold=True, C=C)
        text(slide, 2.1, y + 0.53, 8.8, 0.18, description, font_size=11, color="text_body", C=C)
    page_number(slide, current=2, total=4, C=C)


def add_architecture_page(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    page_header(slide, "Composable Platform Architecture", "SVG source compiled into editable PowerPoint shapes", C=C)
    result = svg_chart(slide, ARCHITECTURE_SVG, x=0.55, y=1.45, w=12.25, h=5.72, C=C)
    if result.warnings:
        raise RuntimeError(f"Unexpected SVG warnings: {result.warnings}")
    text(slide, 0.72, 7.12, 8.0, 0.18, f"Generated {result.shape_count} editable SVG-derived objects", font_size=9,
         color="text_muted", C=C)
    page_number(slide, current=3, total=4, style="simple", C=C)


def add_principles_page(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    page_header(slide, "Architecture principles", "How the platform stays composable as it grows", C=C)
    principles = [("One experience contract", "All entry points use the same workflow semantics and identity model."),
                  ("Decision logic in one place", "Policy, routing, and recommendations do not leak into each channel."),
                  ("Governed extension points", "Integrations add capability without creating a second platform.")]
    colors = ["#2563EB", "#7C3AED", "#0F766E"]
    for index, ((title, body), color) in enumerate(zip(principles, colors)):
        x = 0.82 + index * 4.10
        rrect(slide, x, 1.85, 3.65, 3.10, "#FFFFFF", line="divider", C=C)
        rrect(slide, x + 0.28, 2.18, 0.65, 0.65, color, C=C)
        text(slide, x + 0.50, 2.39, 0.23, 0.18, str(index + 1), font_size=13, color="#FFFFFF", bold=True, align="center", C=C)
        text(slide, x + 0.28, 3.18, 2.95, 0.50, title, font_size=17, color="text_dark", bold=True, C=C)
        text(slide, x + 0.28, 3.95, 2.95, 0.58, body, font_size=11, color="text_body", C=C)
    rrect(slide, 0.82, 5.60, 11.8, 0.72, "#0F172A", C=C)
    text(slide, 1.12, 5.86, 10.9, 0.18, "Next decision: establish the shared workflow contract before scaling channel-specific features.",
         font_size=12, color="#FFFFFF", bold=True, C=C)
    page_number(slide, current=4, total=4, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_agenda(prs)
    add_architecture_page(prs)
    add_principles_page(prs)

    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
