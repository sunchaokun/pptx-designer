"""Brand specification for enterprise mode."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BrandSpec:
    """Brand specification for enterprise PPT generation."""

    source: str = "none"
    colors: dict[str, str] | None = None
    fonts: dict[str, str] | None = None
    spacing: dict[str, Any] | None = None
    logo: dict[str, Any] | None = None
    layout_mapping: dict[str, Any] | None = None
    template_layouts: list[Any] | None = None
    dark_mode: bool = False
    footer: dict[str, Any] | None = None
    watermark: dict[str, Any] | None = None

    @classmethod
    def from_brand_json(cls, data: dict) -> BrandSpec:
        """Create BrandSpec from brand.json data."""
        return cls(
            source="brand_json",
            colors=data.get("colors"),
            fonts=data.get("fonts"),
            spacing=data.get("spacing"),
            logo=data.get("logo"),
            footer=data.get("footer"),
            watermark=data.get("watermark"),
        )
