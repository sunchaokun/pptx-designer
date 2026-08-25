"""Basic tests for pptx-designer package."""

from pptx_designer.core.pipeline import Presentation
from pptx_designer.data import PALETTES, STYLES, TYPOGRAPHY
from pptx_designer.tools.cards import highlight_cards, kpi_card
from pptx_designer.tools.layout import page_header, top_bar
from pptx_designer.tools.shapes import hexagon, oval, rect
from pptx_designer.tools.text import multiline, text


class TestPackageImport:
    """Test package imports."""

    def test_version(self):
        import pptx_designer

        assert pptx_designer.__version__ == "1.0.0b5"

    def test_palletes_count(self):
        assert len(PALETTES) == 192

    def test_typography_count(self):
        assert len(TYPOGRAPHY) == 74

    def test_styles_count(self):
        assert len(STYLES) == 84


class TestPresentation:
    """Test Presentation creation."""

    def test_create_presentation(self):
        prs = Presentation()
        assert prs is not None
        assert prs.slide_width == 12192000  # 13.333 inches
        assert prs.slide_height == 6858000  # 7.5 inches

    def test_add_slide(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        assert slide is not None


class TestShapes:
    """Test shape functions."""

    def test_rect(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shape = rect(slide, 1, 1, 4, 2, fill="#3B82F6")
        assert shape is not None

    def test_oval(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shape = oval(slide, 3, 2, 1.5, 1.5, fill="#10B981")
        assert shape is not None

    def test_hexagon(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shape = hexagon(slide, 6, 2, 1.5, fill="#F59E0B")
        assert shape is not None


class TestText:
    """Test text functions."""

    def test_text(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shape = text(slide, 1, 1, 8, 1, "Hello World", font_size=32)
        assert shape is not None

    def test_multiline(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shape = multiline(slide, 1, 2, 8, 3, ["Line 1", "Line 2", "Line 3"])
        assert shape is not None


class TestCards:
    """Test card functions."""

    def test_kpi_card(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shapes = kpi_card(slide, 1, 2, 3, 1.5, "$12M", "Revenue", "+20%")
        assert len(shapes) > 0

    def test_highlight_cards(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cards = [
            ("Title 1", "Description 1", "#3B82F6"),
            ("Title 2", "Description 2", "#10B981"),
        ]
        shapes = highlight_cards(slide, 1, 2, cards)
        assert len(shapes) > 0


class TestLayout:
    """Test layout functions."""

    def test_page_header(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        page_header(slide, "Title", "Subtitle")
        assert len(slide.shapes) > 0

    def test_top_bar(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        top_bar(slide, "#3B82F6")
        assert len(slide.shapes) > 0


class TestData:
    """Test data module."""

    def test_palette_access(self):
        palette = PALETTES.get("saas-general")
        assert palette is not None
        assert "primary" in palette
        assert palette["primary"].startswith("#")

    def test_typography_access(self):
        fonts = TYPOGRAPHY.get("modern-professional")
        assert fonts is not None
        assert "heading" in fonts
        assert "body" in fonts

    def test_style_access(self):
        style = STYLES.get("minimalism-swiss-style")
        assert style is not None
        assert "keywords" in style


class TestSearch:
    """Test search adapters."""

    def test_search_color(self):
        from pptx_designer.search import adapters

        results = adapters.search_color("tech", top_k=3)
        assert len(results) > 0
        assert "primary" in results[0]

    def test_search_typography(self):
        from pptx_designer.search import adapters

        results = adapters.search_typography("modern", top_k=3)
        assert len(results) > 0
        assert "heading" in results[0]
