"""Presentation-scoped theme inheritance for public Build Mode helpers."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

_PRESENTATION_THEME_ATTR = "_pptx_designer_theme_context"
_SLIDE_THEME_ATTR = "_pptx_designer_slide_theme_context"


def _theme_colors(theme: Mapping[str, Any]) -> dict[str, Any]:
    colors = dict(theme.get("colors", {}))
    roles = dict(theme.get("semantic_roles", {}))
    typography = dict(theme.get("typography", {}))

    primary = roles.get("data-series-1") or colors.get("primary", "#1D78FA")
    accent = roles.get("accent") or colors.get("accent", primary)
    surface = roles.get("surface") or colors.get("card") or colors.get("muted", "#F5F5F5")
    ink = roles.get("ink") or colors.get("foreground") or colors.get("text_dark", "#111827")
    muted = roles.get("muted") or colors.get("muted-foreground") or colors.get("text_muted", "#6B7280")
    border = roles.get("border") or colors.get("border", "#E5E7EB")

    colors.update(
        {
            "background": roles.get("background") or colors.get("background", "#FFFFFF"),
            "surface": surface,
            "ink": ink,
            "muted": muted,
            "card": surface,
            "card_bg": surface,
            "bg_tint": surface,
            "text_dark": ink,
            "text_body": ink,
            "text_muted": muted,
            "border": border,
            "divider": border,
            "primary": primary,
            "accent": accent,
            "secondary": roles.get("accent-secondary") or colors.get("secondary", primary),
            "success": roles.get("success") or accent,
            "warning": roles.get("warning") or colors.get("secondary", accent),
            "destructive": roles.get("danger") or colors.get("destructive", accent),
            "on_primary": colors.get("on-primary", "#FFFFFF"),
            "font_heading": typography.get("heading", colors.get("font_heading")),
            "font_body": typography.get("body", colors.get("font_body")),
            "font_mono": typography.get("mono", typography.get("body", colors.get("font_mono"))),
            "font_cjk": typography.get("cjk_fallback", colors.get("font_cjk")),
        }
    )
    return colors


def set_presentation_theme(prs: Any, theme: Mapping[str, Any]) -> None:
    """Attach a resolved theme to one presentation without global state."""
    setattr(prs.part.package, _PRESENTATION_THEME_ATTR, deepcopy(dict(theme)))


def set_slide_theme(slide: Any, theme: Mapping[str, Any]) -> None:
    """Attach a resolved theme that overrides presentation defaults on one slide."""
    setattr(slide.part, _SLIDE_THEME_ATTR, deepcopy(dict(theme)))


def get_theme(slide: Any) -> Mapping[str, Any] | None:
    """Return the nearest theme for a slide, if one has been attached."""
    return getattr(slide.part, _SLIDE_THEME_ATTR, None) or getattr(
        slide.part.package, _PRESENTATION_THEME_ATTR, None
    )


def resolve_color_context(slide: Any, explicit: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Merge inherited colors with a helper's explicit partial ``C`` override."""
    inherited = _theme_colors(get_theme(slide)) if get_theme(slide) else {}
    inherited.update(dict(explicit or {}))
    return inherited
