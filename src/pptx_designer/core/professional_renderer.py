"""Theme-aware renderer for editable FreeStyle presentation pages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _darken(hex_color: str, amount: int = 20) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    return f"#{max(0, r - amount):02X}{max(0, g - amount):02X}{max(0, b - amount):02X}"


@dataclass(frozen=True)
class _ThemeTokens:
    """Renderer-facing view of a resolved theme mapping."""

    background: str
    surface: str
    ink: str
    muted: str
    border: str
    accent: str
    accent_secondary: str
    success: str
    warning: str
    danger: str
    data_1: str
    data_2: str
    on_primary: str
    heading_font: str | None
    body_font: str | None
    mono_font: str | None
    cjk_fallback: str | None

    @classmethod
    def from_theme(cls, theme: Mapping[str, Any]) -> _ThemeTokens:
        colors = theme.get("colors", {})
        roles = theme.get("semantic_roles", {})
        typography = theme.get("typography", {})

        def role(name: str, fallback: str) -> str:
            return roles.get(name) or fallback

        primary = colors.get("primary", "#1D78FA")
        accent = role("accent", colors.get("accent", primary))
        return cls(
            background=role("background", colors.get("background", "#FFFFFF")),
            surface=role("surface", colors.get("card", colors.get("muted", "#F5F5F5"))),
            ink=role("ink", colors.get("foreground", colors.get("text_dark", "#111827"))),
            muted=role("muted", colors.get("muted-foreground", colors.get("text_muted", "#6B7280"))),
            border=role("border", colors.get("border", "#E5E7EB")),
            accent=accent,
            accent_secondary=role("accent-secondary", colors.get("secondary", primary)),
            success=role("success", accent),
            warning=role("warning", colors.get("secondary", accent)),
            danger=role("danger", colors.get("destructive", accent)),
            data_1=role("data-series-1", primary),
            data_2=role("data-series-2", accent),
            on_primary=colors.get("on-primary", "#FFFFFF"),
            heading_font=typography.get("heading"),
            body_font=typography.get("body"),
            mono_font=typography.get("mono") or typography.get("body"),
            cjk_fallback=typography.get("cjk_fallback") or colors.get("font_cjk"),
        )

    @property
    def color_context(self) -> dict[str, str]:
        """Compatibility context used by text helpers for CJK fallback."""
        return {"font_body": self.body_font or "", "font_cjk": self.cjk_fallback or ""}


def _text(slide: Any, *args: Any, kind: str = "body", tokens: _ThemeTokens, **kwargs: Any) -> Any:
    from pptx_designer.tools.text import text

    font_name = tokens.heading_font if kind == "heading" else tokens.mono_font if kind == "mono" else tokens.body_font
    return text(slide, *args, font_name=font_name, C=tokens.color_context, **kwargs)


def render_professional_page(
    slide: Any,
    goal: str,
    title: str,
    subtitle: str,
    bullets: list[str],
    theme: Mapping[str, Any],
    page_index: int,
    total_pages: int,
) -> None:
    """Render an editable FreeStyle page from a complete resolved theme."""
    from pptx_designer.tools.shapes import rect

    tokens = _ThemeTokens.from_theme(theme)
    rect(slide, 0, 0, 13.333, 7.5, tokens.background)

    if goal == "hook":
        _render_hero(slide, title, subtitle, tokens)
    elif goal == "problem":
        _render_problem(slide, title, bullets, tokens)
    elif goal == "solution":
        _render_solution(slide, title, bullets, tokens)
    elif goal == "features":
        _render_features(slide, title, bullets, tokens)
    elif goal == "data":
        _render_data(slide, title, bullets, tokens)
    elif goal == "code":
        _render_code(slide, title, bullets, tokens)
    else:
        _render_content(slide, title, bullets, tokens)

    if page_index > 0:
        _text(
            slide,
            12.0,
            7.0,
            1.0,
            0.3,
            f"{page_index + 1}/{total_pages}",
            font_size=10,
            color=tokens.muted,
            align="right",
            tokens=tokens,
        )


def _section_header(slide: Any, label: str, title: str, color: str, tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import rect

    _text(slide, 1.0, 0.5, 3.0, 0.3, label, font_size=12, bold=True, color=color, kind="heading", tokens=tokens)
    _text(slide, 1.0, 0.9, 11.0, 0.8, title, font_size=36, bold=True, color=tokens.ink, kind="heading", tokens=tokens)
    rect(slide, 1.0, 1.8, 2.0, 0.04, color)


def _render_hero(slide: Any, title: str, subtitle: str, tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import oval, rect

    oval(slide, 9.5, -1.0, 5.0, 5.0, _darken(tokens.data_1, 30))
    oval(slide, 10.5, 0.5, 3.5, 3.5, tokens.data_1)
    oval(slide, -1.5, 5.0, 4.0, 4.0, _darken(tokens.accent, 40))
    rect(slide, 1.0, 2.8, 1.5, 0.06, tokens.accent)
    _text(slide, 1.0, 3.0, 8.0, 1.2, title, font_size=48, bold=True, color=tokens.ink, kind="heading", tokens=tokens)
    if subtitle:
        _text(slide, 1.0, 4.3, 8.0, 0.6, subtitle, font_size=20, color=tokens.muted, tokens=tokens)


def _render_problem(slide: Any, title: str, bullets: list[str], tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import oval, rrect

    _section_header(slide, "PROBLEM", title, tokens.danger, tokens)
    if not bullets:
        return
    card_width = min(3.5, 10.5 / len(bullets[:3]))
    for index, bullet in enumerate(bullets[:3]):
        x = 1.0 + index * (card_width + 0.4)
        rrect(slide, x, 2.3, card_width, 3.5, tokens.surface, line=tokens.border)
        oval(slide, x + card_width / 2 - 0.4, 2.6, 0.8, 0.8, tokens.danger)
        _text(
            slide, x + card_width / 2 - 0.3, 2.7, 0.6, 0.6, str(index + 1), font_size=24, bold=True,
            color=tokens.on_primary, align="center", kind="heading", tokens=tokens,
        )
        _text(slide, x + 0.2, 3.6, card_width - 0.4, 1.8, bullet, font_size=14, color=tokens.ink, align="center", tokens=tokens)


def _render_solution(slide: Any, title: str, bullets: list[str], tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import oval, rect

    _section_header(slide, "SOLUTION", title, tokens.success, tokens)
    y = 2.3
    for bullet in bullets[:4]:
        oval(slide, 1.0, y, 0.5, 0.5, tokens.success)
        _text(slide, 1.05, y + 0.05, 0.4, 0.4, "✓", font_size=18, bold=True, color=tokens.on_primary, align="center", tokens=tokens)
        _text(slide, 1.8, y + 0.05, 10.0, 0.4, bullet, font_size=16, color=tokens.ink, tokens=tokens)
        rect(slide, 1.8, y + 0.55, 10.0, 0.01, tokens.border)
        y += 0.7


def _render_features(slide: Any, title: str, bullets: list[str], tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import oval, rect, rrect

    _section_header(slide, "FEATURES", title, tokens.data_1, tokens)
    cards = bullets[:3]
    if not cards:
        return
    card_width = min(3.5, 10.5 / len(cards))
    colors = [tokens.data_1, tokens.data_2, tokens.accent_secondary]
    for index, (bullet, color) in enumerate(zip(cards, colors, strict=True)):
        x = 1.0 + index * (card_width + 0.4)
        rrect(slide, x, 2.3, card_width, 3.8, tokens.surface, line=tokens.border)
        rect(slide, x, 2.3, card_width, 0.08, color)
        oval(slide, x + card_width / 2 - 0.5, 2.8, 1.0, 1.0, color)
        _text(slide, x + card_width / 2 - 0.4, 2.9, 0.8, 0.8, "★", font_size=32, color=tokens.on_primary, align="center", tokens=tokens)
        _text(slide, x + 0.3, 4.1, card_width - 0.6, 1.5, bullet, font_size=14, color=tokens.ink, align="center", tokens=tokens)


def _render_data(slide: Any, title: str, bullets: list[str], tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import rect, rrect

    _section_header(slide, "METRICS", title, tokens.warning, tokens)
    kpi_data = []
    for bullet in bullets:
        if ": " in bullet:
            label, value = bullet.split(": ", 1)
            kpi_data.append((value, label))
        else:
            kpi_data.append((bullet, ""))
    if not kpi_data or len(kpi_data) > 4:
        return
    card_width = min(2.8, 10.0 / len(kpi_data))
    gap = 0.4
    total_width = len(kpi_data) * card_width + (len(kpi_data) - 1) * gap
    start_x = (13.333 - total_width) / 2
    colors = [tokens.data_1, tokens.data_2, tokens.accent_secondary, tokens.warning]
    for index, (value, label) in enumerate(kpi_data):
        x = start_x + index * (card_width + gap)
        color = colors[index % len(colors)]
        rrect(slide, x, 2.5, card_width, 3.0, tokens.surface, line=tokens.border)
        rect(slide, x, 2.5, card_width, 0.06, color)
        _text(slide, x, 3.0, card_width, 0.8, value, font_size=36, bold=True, color=color, align="center", kind="heading", tokens=tokens)
        _text(slide, x, 4.0, card_width, 0.4, label, font_size=12, color=tokens.muted, align="center", tokens=tokens)


def _render_code(slide: Any, title: str, bullets: list[str], tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import rrect

    _section_header(slide, "CODE", title, tokens.accent, tokens)
    rrect(slide, 1.0, 2.0, 11.0, 4.5, tokens.surface, line=tokens.border)
    rrect(slide, 1.2, 2.2, 1.0, 0.3, tokens.data_1)
    _text(slide, 1.25, 2.22, 0.9, 0.25, "Python", font_size=10, bold=True, color=tokens.on_primary, align="center", tokens=tokens)
    y = 2.7
    for line in bullets[:8]:
        _text(slide, 1.5, y, 10.0, 0.25, line, font_size=12, color=tokens.ink, kind="mono", tokens=tokens)
        y += 0.35


def _render_content(slide: Any, title: str, bullets: list[str], tokens: _ThemeTokens) -> None:
    from pptx_designer.tools.shapes import oval, rect, rrect

    _text(slide, 1.0, 0.5, 11.0, 0.8, title, font_size=36, bold=True, color=tokens.ink, kind="heading", tokens=tokens)
    rect(slide, 1.0, 1.4, 2.0, 0.04, tokens.data_1)
    y = 1.8
    for bullet in bullets[:5]:
        rrect(slide, 1.0, y, 11.0, 0.8, tokens.surface, line=tokens.border)
        oval(slide, 1.3, y + 0.25, 0.3, 0.3, tokens.data_1)
        _text(slide, 1.8, y + 0.15, 10.0, 0.5, bullet, font_size=15, color=tokens.ink, tokens=tokens)
        y += 1.0
