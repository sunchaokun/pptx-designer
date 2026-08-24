"""SVG diagrams example: Complex diagrams via SVG compiler."""

from pptx_designer.tools.svg import svg_chart
from pptx_designer.tools.cards import page_header
from pptx_designer.core.pipeline import Presentation


def main():
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    page_header(slide, "Architecture Overview", "System Design", C={})

    # Architecture diagram as SVG
    svg = """
    <svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
        <!-- Background -->
        <rect x="0" y="0" width="800" height="400" rx="12" fill="#f8fafc"/>

        <!-- Client Layer -->
        <rect x="50" y="30" width="150" height="60" rx="8" fill="#3b82f6"/>
        <text x="125" y="65" text-anchor="middle" fill="white" font-size="14" font-weight="bold">Web Client</text>

        <rect x="250" y="30" width="150" height="60" rx="8" fill="#3b82f6"/>
        <text x="325" y="65" text-anchor="middle" fill="white" font-size="14" font-weight="bold">Mobile App</text>

        <!-- API Layer -->
        <rect x="150" y="130" width="200" height="60" rx="8" fill="#10b981"/>
        <text x="250" y="165" text-anchor="middle" fill="white" font-size="14" font-weight="bold">API Gateway</text>

        <!-- Services -->
        <rect x="50" y="230" width="120" height="60" rx="8" fill="#f59e0b"/>
        <text x="110" y="265" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Auth Service</text>

        <rect x="200" y="230" width="120" height="60" rx="8" fill="#f59e0b"/>
        <text x="260" y="265" text-anchor="middle" fill="white" font-size="12" font-weight="bold">Core API</text>

        <rect x="350" y="230" width="120" height="60" rx="8" fill="#f59e0b"/>
        <text x="410" y="265" text-anchor="middle" fill="white" font-size="12" font-weight="bold">ML Pipeline</text>

        <!-- Database -->
        <rect x="200" y="330" width="200" height="50" rx="8" fill="#8b5cf6"/>
        <text x="300" y="360" text-anchor="middle" fill="white" font-size="14" font-weight="bold">PostgreSQL</text>

        <!-- Connectors -->
        <line x1="125" y1="90" x2="250" y2="130" stroke="#94a3b8" stroke-width="2"/>
        <line x1="325" y1="90" x2="250" y2="130" stroke="#94a3b8" stroke-width="2"/>
        <line x1="200" y1="190" x2="110" y2="230" stroke="#94a3b8" stroke-width="2"/>
        <line x1="250" y1="190" x2="260" y2="230" stroke="#94a3b8" stroke-width="2"/>
        <line x1="300" y1="190" x2="410" y2="230" stroke="#94a3b8" stroke-width="2"/>
        <line x1="260" y1="290" x2="300" y2="330" stroke="#94a3b8" stroke-width="2"/>
    </svg>
    """

    svg_chart(slide, svg, x=0.5, y=1.5, w=12, h=6)

    prs.save("output/svg_diagram.pptx")
    print("Saved: output/svg_diagram.pptx")


if __name__ == "__main__":
    main()
