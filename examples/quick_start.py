"""Build mode example: LLM generates this code to create a presentation."""

from pptx_designer.tools.shapes import rect, rounded_rect
from pptx_designer.tools.text import text, multiline
from pptx_designer.tools.cards import page_header, kpi_card, highlight_cards, code_block
from pptx_designer.tools.images import cover_image
from pptx_designer.tools.layout import top_bar, page_number
from pptx_designer.core.pipeline import Presentation


def main():
    # Color scheme (LLM selects based on style)
    C = {
        "primary": "#1D78FA",
        "accent": "#FF6B35",
        "text_dark": "#1A1A1A",
        "text_body": "#4A4A4A",
        "text_muted": "#9CA3AF",
        "background": "#FFFFFF",
    }

    prs = Presentation()

    # === Slide 1: Title ===
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    top_bar(slide, C["primary"])
    text(slide, 0.5, 1.5, 12, 1.5, "Q4 Revenue Report", font_size=44, bold=True, color="text_dark", C=C)
    text(slide, 0.5, 3.2, 12, 0.8, "Financial Summary — October to December 2026", font_size=18, color="text_body", C=C)
    rect(slide, 0.5, 4.5, 2, 0.08, fill=C["accent"])

    # === Slide 2: Key Metrics ===
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    page_header(slide, "Key Metrics", "Quarterly Performance", C=C)

    kpi_card(slide, 1.0, 2.0, 3.5, 1.5, "$12.8M", "Revenue", "+23%", C=C)
    kpi_card(slide, 5.0, 2.0, 3.5, 1.5, "89%", "Retention", "+5pp", C=C)
    kpi_card(slide, 9.0, 2.0, 3.5, 1.5, "4.2x", "ROI", "+0.8x", C=C)

    # === Slide 3: Highlights ===
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    page_header(slide, "Highlights", "What Went Well", C=C)

    highlight_cards(slide, 1.0, 2.0, [
        ("Enterprise Wins", "Closed 3 Fortune 500 deals", C["primary"]),
        ("Product Launch", "New analytics dashboard live", C["accent"]),
        ("Team Growth", "Engineering headcount +40%", "#10B981"),
    ], total_width=11, C=C)

    # === Slide 4: Code Snippet ===
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    page_header(slide, "Technical Achievement", "API Performance", C=C)

    code_block(slide, 1.0, 2.0, 10, 3.5, [
        "# Before optimization",
        "response_time = 245ms  # p99",
        "",
        "# After optimization",
        "response_time = 42ms   # p99",
        "# 5.8x improvement",
    ], language="python", C=C)

    # Save
    prs.save("output/build_mode_example.pptx")
    print("Saved: output/build_mode_example.pptx")


if __name__ == "__main__":
    main()
