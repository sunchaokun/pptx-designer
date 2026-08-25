"""Design DNA extractor — extract design patterns from PPT files."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TextZone:
    """Text zone in a slide."""

    text: str = ""
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    font_size: float = 12
    font_name: str = ""
    color: str = ""


@dataclass
class SlideDNA:
    """Design DNA for a single slide."""

    slide_index: int = 0
    title: str = ""
    text_zones: list[TextZone] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    shapes: list[dict] = field(default_factory=list)


@dataclass
class DesignDNA:
    """Design DNA for a presentation."""

    title: str = ""
    slides: list[SlideDNA] = field(default_factory=list)
    colors: dict[str, str] = field(default_factory=dict)
    fonts: dict[str, str] = field(default_factory=dict)
    brand_spec: Any = None


@dataclass
class PagePlan:
    """Page plan for rendering."""

    page_type: str = "content"
    title: str = ""
    subtitle: str = ""
    bullets: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)


class DesignDNAExtractor:
    """Extracts design DNA from PPT files."""

    def __init__(self):
        pass

    def extract(self, pptx_path: str) -> DesignDNA:
        """Extract design DNA from a PPTX file.

        Args:
            pptx_path: Path to .pptx file

        Returns:
            DesignDNA
        """
        from pptx import Presentation

        dna = DesignDNA()

        try:
            prs = Presentation(pptx_path)

            for i, slide in enumerate(prs.slides):
                slide_dna = SlideDNA(slide_index=i)

                for shape in slide.shapes:
                    if shape.has_text_frame:
                        text = shape.text_frame.text.strip()
                        if text:
                            zone = TextZone(
                                text=text,
                                x=shape.left / 914400,  # EMU to inches
                                y=shape.top / 914400,
                                width=shape.width / 914400,
                                height=shape.height / 914400,
                            )
                            slide_dna.text_zones.append(zone)

                            if not dna.title and shape.shape_type == 13:
                                dna.title = text

                dna.slides.append(slide_dna)

        except Exception:
            pass

        return dna


def extract_design_dna(pptx_path: str) -> dict[str, Any]:
    """Extract design DNA as a JSON-serializable dictionary."""
    return asdict(DesignDNAExtractor().extract(pptx_path))
