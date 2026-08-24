"""Data charts example: Native PowerPoint charts with brand colors."""

from pptx_designer.tools.charts import bar_chart, donut_chart, native_chart
from pptx_designer.tools.cards import page_header
from pptx_designer.core.pipeline import Presentation


def main():
    C = {
        "primary": "#3B82F6",
        "accent": "#10B981",
        "text_dark": "#1F2937",
        "background": "#FFFFFF",
    }

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    page_header(slide, "Revenue by Quarter", "2026 Financial Summary", C=C)

    # Horizontal bar chart
    bar_data = [
        ("Q1", "85%", 8500000),
        ("Q2", "92%", 9200000),
        ("Q3", "78%", 7800000),
        ("Q4", "100%", 10000000),
    ]
    bar_chart(slide, 0.5, 2.0, bar_data, max_width=6.0, C=C)

    # Donut chart
    sectors = [
        ("Enterprise", "45%", C["primary"]),
        ("SMB", "30%", C["accent"]),
        ("Consumer", "15%", "#F59E0B"),
        ("Other", "10%", "#9CA3AF"),
    ]
    donut_chart(slide, cx=10, cy=3.5, radius=1.8, inner_radius=0.9, sectors=sectors, C=C)

    prs.save("output/data_charts.pptx")
    print("Saved: output/data_charts.pptx")


if __name__ == "__main__":
    main()
