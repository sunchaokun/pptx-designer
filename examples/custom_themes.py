"""Theme system example: LLM selects styles with natural language."""

from pptx_designer.renderer.theme import ThemeComposer
from pptx_designer.tools.shapes import rect
from pptx_designer.tools.text import text
from pptx_designer.tools.cards import page_header, kpi_card
from pptx_designer.core.pipeline import Presentation


def main():
    # LLM picks style based on user request
    theme = ThemeComposer().compose(style="dark cyberpunk")

    C = theme["colors"]
    typo = theme["typography"]

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    page_header(slide, "Cyberpunk Dashboard", "Real-time Metrics", C=C, typo=typo)

    kpi_card(slide, 1, 2.5, 3, 1.5, "1.2M", "Requests/s", "+45%", C=C, typo=typo)
    kpi_card(slide, 4.5, 2.5, 3, 1.5, "99.9%", "Uptime", "+0.1%", C=C, typo=typo)
    kpi_card(slide, 8, 2.5, 3, 1.5, "23ms", "Latency", "-67%", C=C, typo=typo)

    prs.save("output/theme_example.pptx")
    print("Saved: output/theme_example.pptx")


if __name__ == "__main__":
    main()
