"""Advanced example: an editable executive business-review slide.

Run from the repository root:
    python examples/advanced_business_review.py

The output uses only pptx_designer public APIs. Every title, card, bar, and
flow node remains editable in PowerPoint.
"""

from pathlib import Path

from pptx_designer import Presentation
from pptx_designer.diagrams import DiagramStyle, FlowchartDiagram, Region
from pptx_designer.tools.cards import kpi_card
from pptx_designer.tools.charts import bar_chart
from pptx_designer.tools.layout import page_header, page_number
from pptx_designer.tools.shapes import rect, rrect
from pptx_designer.tools.text import text


C = {
    "primary": "#155EEF",
    "accent": "#F79009",
    "background": "#F8FAFC",
    "card": "#FFFFFF",
    "text_dark": "#101828",
    "text_body": "#475467",
    "text_muted": "#667085",
    "border": "#E4E7EC",
    "divider": "#D0D5DD",
    "bg_tint": "#EAECF0",
}


def add_cover(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "#0B1F3A", C=C)
    rect(slide, 0, 0, 0.20, 7.5, "accent", C=C)
    text(slide, 0.9, 1.45, 10.8, 0.7, "Q2 Executive\nBusiness Review", font_size=38, color="#FFFFFF", bold=True, C=C)
    text(slide, 0.95, 3.10, 8.3, 0.35, "Growth quality, retention signals, and Q3 operating choices", font_size=17, color="#B9D3FF", C=C)
    rrect(slide, 0.95, 5.75, 3.2, 0.55, "#163B6D", C=C)
    text(slide, 1.18, 5.90, 2.8, 0.2, "LEADERSHIP TEAM  •  JULY 2026", font_size=9, color="#FFFFFF", bold=True, C=C)


def add_agenda(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    page_header(slide, "Today’s discussion", "A concise decision-oriented review", C=C)
    items = [("01", "Business performance", "Revenue, retention, and cycle-time signals"),
             ("02", "Growth drivers", "Which segments are creating durable expansion"),
             ("03", "Q3 operating plan", "The choices, owners, and review date")]
    for idx, (number, title, detail) in enumerate(items):
        y = 1.65 + idx * 1.5
        rrect(slide, 0.9, y, 11.5, 1.05, "card", line="border", C=C)
        text(slide, 1.2, y + 0.27, 0.7, 0.35, number, font_size=23, color="primary", bold=True, C=C)
        text(slide, 2.15, y + 0.20, 4.0, 0.3, title, font_size=18, color="text_dark", bold=True, C=C)
        text(slide, 2.15, y + 0.57, 7.5, 0.22, detail, font_size=11, color="text_body", C=C)
    page_number(slide, current=2, total=4, C=C)


def add_review_page(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    rect(slide, 0, 0, 13.333, 0.12, "primary", C=C)
    page_header(slide, "Q2 Executive Business Review", "Revenue quality improved while retention remains the operating focus", C=C)

    # KPI band
    metrics = [
        ("$12.8M", "Quarterly revenue", "+23%", True),
        ("89%", "Gross retention", "+5 pp", True),
        ("42 days", "Sales cycle", "−8 days", True),
    ]
    for index, (number, label, trend, trend_up) in enumerate(metrics):
        kpi_card(
            slide,
            left=0.7 + index * 4.05,
            top=1.45,
            width=3.65,
            height=1.45,
            number=number,
            label=label,
            trend=trend,
            trend_up=trend_up,
            C=C,
        )

    # Left insight panel
    rrect(slide, 0.7, 3.25, 6.0, 3.35, "card", line="border", C=C)
    text(slide, 1.0, 3.55, 5.4, 0.35, "Growth drivers", font_size=18, color="text_dark", bold=True, C=C)
    text(slide, 1.0, 3.95, 5.2, 0.38, "Enterprise expansion is now the largest contributor to net new ARR.",
         font_size=12, color="text_body", C=C)
    bar_chart(
        slide,
        left=1.9,
        top=4.55,
        data=[
            ("Enterprise", 0.88, "$5.6M"),
            ("Mid-market", 0.67, "$4.3M"),
            ("Self-serve", 0.43, "$2.9M"),
        ],
        max_width=3.8,
        bar_height=0.30,
        C=C,
    )
    text(slide, 1.0, 6.15, 5.1, 0.25, "Decision: add two enterprise account executives in Q3.",
         font_size=11, color="primary", bold=True, C=C)

    # Right operating plan panel
    rrect(slide, 6.95, 3.25, 5.68, 3.35, "#102A56", C=C)
    text(slide, 7.28, 3.55, 5.0, 0.35, "Q3 operating plan", font_size=18, color="#FFFFFF", bold=True, C=C)
    text(slide, 7.28, 3.95, 5.0, 0.32, "A focused sequence from insight to measurable retention impact.",
         font_size=11, color="#D0D5DD", C=C)
    plan_style = DiagramStyle(node_fill="primary", node_font_color="on-primary", node_shadow=False, node_gradient=False)
    FlowchartDiagram(
        data={"nodes": [{"label": "Onboard"}, {"label": "Adopt"}, {"label": "Renew"}]},
        style=plan_style,
        region=Region(left=7.35, top=4.55, width=4.85, height=1.05),
    ).render(slide)
    text(slide, 7.28, 6.12, 5.0, 0.25, "Owner: Chief Revenue Officer  •  Review: 30 Sep", font_size=10, color="#D0D5DD", C=C)
    page_number(slide, current=3, total=4, style="simple", C=C)


def add_decision_page(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, 13.333, 7.5, "background", C=C)
    page_header(slide, "Decision and next actions", "Convert the Q2 signals into focused Q3 execution", C=C)
    actions = [("Invest", "Add two enterprise account executives", "Owner: CRO", "#155EEF"),
               ("Protect", "Launch renewal-risk review for the top 30 accounts", "Owner: VP Customer Success", "#F79009"),
               ("Measure", "Review adoption-to-renewal conversion monthly", "Owner: RevOps", "#12B76A")]
    for idx, (tag, action, owner, color) in enumerate(actions):
        y = 1.55 + idx * 1.45
        rrect(slide, 0.85, y, 11.65, 1.04, "card", line="border", C=C)
        rrect(slide, 1.08, y + 0.25, 1.25, 0.48, color, C=C)
        text(slide, 1.24, y + 0.38, 0.95, 0.14, tag.upper(), font_size=9, color="#FFFFFF", bold=True, C=C)
        text(slide, 2.7, y + 0.24, 6.9, 0.28, action, font_size=16, color="text_dark", bold=True, C=C)
        text(slide, 2.7, y + 0.61, 5.0, 0.18, owner, font_size=10, color="text_muted", C=C)
    rrect(slide, 0.85, 6.20, 11.65, 0.55, "#0B1F3A", C=C)
    text(slide, 1.12, 6.39, 10.9, 0.16, "Decision requested today: approve headcount and the top-account retention review cadence.",
         font_size=11, color="#FFFFFF", bold=True, C=C)
    page_number(slide, current=4, total=4, C=C)


def build() -> Path:
    prs = Presentation()
    add_cover(prs)
    add_agenda(prs)
    add_review_page(prs)
    add_decision_page(prs)

    output = Path(__file__).with_suffix(".pptx")
    prs.save(output)
    return output


if __name__ == "__main__":
    print(f"Created {build()}")
