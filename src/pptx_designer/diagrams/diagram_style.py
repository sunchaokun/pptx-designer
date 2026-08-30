"""DiagramStyle — diagram styling system aligned with PPT theme."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiagramStyle:
    node_fill: str = "primary"
    node_border: str = "border"
    node_border_width_pt: float = 1.0
    node_corner_radius: str = "rounded"
    node_shadow: bool = True
    node_gradient: bool = True

    node_font_size_pt: int = 13
    node_font_weight: str = "normal"
    node_font_color: str = "on-primary"
    node_text_alignment: str = "center"

    connector_color: str = "muted-foreground"
    connector_width_pt: float = 1.5
    connector_style: str = "solid"
    arrow_enabled: bool = True
    arrow_size: str = "medium"

    label_font_size_pt: int = 11
    label_font_color: str = "muted-foreground"

    node_gap_inches: float = 0.3
    padding_inches: float = 0.15

    cell_header_font_size_pt: int = 16
    cell_body_font_size_pt: int = 12
    cell_header_font_weight: str = "bold"

    _color_map: dict[str, str] = field(default_factory=dict, repr=False)

    def resolve_color(self, role: str) -> str:
        if self._color_map and role in self._color_map:
            return self._color_map[role]
        fallback = {
            "primary": "#2563EB",
            "secondary": "#64748B",
            "accent": "#F97316",
            "muted": "#F1F5F9",
            "foreground": "#1A1A1A",
            "on-primary": "#FFFFFF",
            "muted-foreground": "#94A3B8",
            "border": "#E2E8F0",
            "background": "#FFFFFF",
        }
        return fallback.get(role, "#000000")

    @classmethod
    def from_theme(cls, theme: dict[str, Any], business_mode: str = "pitch") -> DiagramStyle:
        style = cls()
        colors = dict(theme.get("colors", {}))
        roles = theme.get("semantic_roles", {})
        colors.update(
            {
                "background": roles.get("background", colors.get("background", "#FFFFFF")),
                "primary": roles.get("data-series-1", colors.get("primary", "#2563EB")),
                "accent": roles.get("accent", colors.get("accent", "#F97316")),
                "secondary": roles.get("accent-secondary", colors.get("secondary", "#64748B")),
                "muted": roles.get("surface", colors.get("muted", "#F1F5F9")),
                "foreground": roles.get("ink", colors.get("foreground", "#1A1A1A")),
                "muted-foreground": roles.get("muted", colors.get("muted-foreground", "#94A3B8")),
                "border": roles.get("border", colors.get("border", "#E2E8F0")),
                "on-primary": colors.get("on-primary", "#FFFFFF"),
            }
        )
        if colors:
            style._color_map = colors

        bg = colors.get("background", "#FFFFFF")
        if _is_dark(bg):
            style.node_fill = "muted"
            style.node_font_color = "foreground"
            style.connector_color = "muted-foreground"

        if business_mode in ("education", "training"):
            style.node_font_size_pt = 12
            style.label_font_size_pt = 10
            style.node_gap_inches = 0.2
            style.node_shadow = False

        return style

    @classmethod
    def from_brand_spec(cls, brand_spec: Any) -> DiagramStyle:
        style = cls()
        if hasattr(brand_spec, "colors") and brand_spec.colors:
            style._color_map = dict(brand_spec.colors)
            bg = brand_spec.colors.get("background", "#FFFFFF")
            if _is_dark(bg):
                style.node_fill = "muted"
                style.node_font_color = "foreground"
                style.connector_color = "muted-foreground"
        if hasattr(brand_spec, "spacing") and brand_spec.spacing:
            style.node_font_size_pt = brand_spec.spacing.get("body_size_pt", 13)
            margins = brand_spec.spacing.get("margins_inches", 1.0)
            style.node_gap_inches = margins * 0.3
        return style

    def apply_density(self, density: int) -> DiagramStyle:
        density = max(1, min(10, density))
        if density <= 3:
            style = DiagramStyle(
                node_font_size_pt=16,
                label_font_size_pt=13,
                cell_header_font_size_pt=18,
                cell_body_font_size_pt=14,
                node_gap_inches=0.4,
                padding_inches=0.2,
                _color_map=self._color_map,
            )
        elif density <= 6:
            style = DiagramStyle(
                node_font_size_pt=14,
                label_font_size_pt=12,
                cell_header_font_size_pt=16,
                cell_body_font_size_pt=12,
                node_gap_inches=0.3,
                padding_inches=0.15,
                _color_map=self._color_map,
            )
        else:
            style = DiagramStyle(
                node_font_size_pt=12,
                label_font_size_pt=10,
                cell_header_font_size_pt=14,
                cell_body_font_size_pt=10,
                node_gap_inches=0.2,
                padding_inches=0.1,
                _color_map=self._color_map,
            )
        style.node_fill = self.node_fill
        style.node_font_color = self.node_font_color
        style.connector_color = self.connector_color
        return style


def _is_dark(hex_color: str) -> bool:
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (r * 0.299 + g * 0.587 + b * 0.114) < 128
    except (ValueError, IndexError):
        return False
