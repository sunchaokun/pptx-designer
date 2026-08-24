"""Advanced example: an editable product-strategy roadmap slide.

Run from the repository root:
    python examples/advanced_product_strategy.py
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.diagrams import DiagramStyle, Region, TimelineDiagram
from pptx_designer.tools.cards import highlight_cards
from pptx_designer.tools.layout import page_header, page_number
from pptx_designer.tools.shapes import rect, rrect
from pptx_designer.tools.text import multiline, text


C = {
    "primary": "#7F56D9",
    "accent": "#06B6D4",
    "background": "#FCFAFF",
    "card": "#FFFFFF",
    "text_dark": "#2D1B4E",
    "text_body": "#5B5570",
    "text_muted": "#7A728D",
    "border": "#E9D7FE",
    "divider": "#D9D6FE",
}


def add_cover(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "#2D1B4E", C=C)
    rect(slide, 0, 0, 13.333, 0.16, "accent", C=C)
    text(slide, 0.9, 1.55, 10.5, 0.55, "From Workflow\nto Platform", font_size=40, color="#FFFFFF", bold=True, C=C)
    text(slide, 0.95, 3.15, 7.9, 0.30, "Product strategy and delivery roadmap • H2 2026", font_size=17, color="#D9D6FE", C=C)
    rrect(slide, 0.95, 5.85, 3.1, 0.50, "#5B21B6", C=C)
    text(slide, 1.18, 6.00, 2.75, 0.16, "PRODUCT LEADERSHIP REVIEW", font_size=9, color="#FFFFFF", bold=True, C=C)


def add_agenda(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    page_header(slide, "Strategy narrative", "The path from a useful workflow to a scalable platform", C=C)
    chapters = [("01", "Where to win", "A workflow that becomes part of the team’s daily habit"),
                ("02", "What to ship", "Four connected release moments across the next two quarters"),
                ("03", "What we need", "A two-squad allocation and shared success metrics")]
    for index, (number, title, body) in enumerate(chapters):
        y = 1.70 + index * 1.38
        text(slide, 0.95, y, 0.70, 0.30, number, font_size=22, color="primary", bold=True, C=C)
        rrect(slide, 1.75, y - 0.12, 10.1, 0.90, "card", line="border", C=C)
        text(slide, 2.05, y + 0.05, 3.5, 0.24, title, font_size=16, color="text_dark", bold=True, C=C)
        text(slide, 2.05, y + 0.39, 8.7, 0.17, body, font_size=11, color="text_body", C=C)
    page_number(slide, current=2, total=4, C=C)


def add_roadmap_page(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    rect(slide, 0, 0, 13.333, 0.12, "primary", C=C)
    page_header(slide, "Product Strategy: From Workflow to Platform", "A portfolio view of the next two quarters", C=C)

    # Strategic pillars
    highlight_cards(
        slide,
        left=0.7,
        top=1.45,
        total_width=11.93,
        cards=[
            ("Win the workflow", "Make the daily team ritual faster and more reliable.", "#7F56D9"),
            ("Prove the outcome", "Connect adoption signals to executive business value.", "#06B6D4"),
            ("Scale the platform", "Open governed integrations for enterprise expansion.", "#F79009"),
        ],
        C=C,
    )

    # Roadmap band
    rrect(slide, 0.7, 3.25, 11.93, 2.15, "card", line="border", C=C)
    text(slide, 1.0, 3.55, 4.0, 0.35, "Delivery roadmap", font_size=18, color="text_dark", bold=True, C=C)
    text(slide, 1.0, 3.92, 6.2, 0.28, "Three release moments, each tied to a measurable adoption signal.",
         font_size=11, color="text_body", C=C)
    TimelineDiagram(
        data={
            "events": [
                {"year": "JUL", "title": "Guided setup"},
                {"year": "AUG", "title": "Team workspace"},
                {"year": "SEP", "title": "Admin insights"},
                {"year": "OCT", "title": "Integration hub"},
            ]
        },
        style=DiagramStyle(node_fill="primary", node_font_color="on-primary", node_shadow=False, node_gradient=False),
        region=Region(left=1.1, top=4.2, width=10.9, height=0.9),
    ).render(slide)

    # Bottom decision panel
    rrect(slide, 0.7, 5.75, 11.93, 1.05, "#2D1B4E", C=C)
    text(slide, 1.0, 6.03, 2.0, 0.25, "Leadership ask", font_size=12, color="#D9D6FE", bold=True, C=C)
    multiline(
        slide,
        left=3.0,
        top=5.93,
        width=8.9,
        height=0.55,
        lines=["Approve a two-squad allocation through October.", "Success metric: 60% of active teams complete the workflow within 14 days."],
        font_size=13,
        color="#FFFFFF",
        C=C,
    )
    page_number(slide, current=3, total=4, style="simple", C=C)


def add_scorecard_page(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    page_header(slide, "Leadership scorecard", "Measure outcomes, not just shipped features", C=C)
    goals = [("Adoption", "60%", "Active teams completing setup in 14 days", "#7F56D9"),
             ("Engagement", "3×", "Weekly workflow actions per active team", "#06B6D4"),
             ("Expansion", "25%", "Enterprise accounts enabling an integration", "#F79009")]
    for index, (label, target, description, color) in enumerate(goals):
        x = 0.85 + index * 4.08
        rrect(slide, x, 1.80, 3.65, 2.55, "card", line="border", C=C)
        rect(slide, x, 1.80, 3.65, 0.08, color, C=C)
        text(slide, x + 0.28, 2.18, 3.0, 0.22, label, font_size=13, color="text_muted", bold=True, C=C)
        text(slide, x + 0.28, 2.63, 3.0, 0.58, target, font_size=35, color="text_dark", bold=True, C=C)
        text(slide, x + 0.28, 3.48, 2.95, 0.38, description, font_size=11, color="text_body", C=C)
    rrect(slide, 0.85, 5.12, 11.8, 1.05, "#2D1B4E", C=C)
    text(slide, 1.15, 5.40, 2.0, 0.20, "Decision requested", font_size=12, color="#D9D6FE", bold=True, C=C)
    text(slide, 3.25, 5.37, 8.7, 0.25, "Approve a two-squad allocation through October, then review the scorecard monthly.",
         font_size=14, color="#FFFFFF", bold=True, C=C)
    page_number(slide, current=4, total=4, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_agenda(prs)
    add_roadmap_page(prs)
    add_scorecard_page(prs)

    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
