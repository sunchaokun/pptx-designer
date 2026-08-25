"""Professional page renderer — high-quality slide generation."""

from __future__ import annotations

from typing import Any


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _darken(hex_color: str, amount: int = 20) -> str:
    """Darken a hex color."""
    r, g, b = _hex_to_rgb(hex_color)
    r = max(0, r - amount)
    g = max(0, g - amount)
    b = max(0, b - amount)
    return f"#{r:02X}{g:02X}{b:02X}"


def _lighten(hex_color: str, amount: int = 20) -> str:
    """Lighten a hex color."""
    r, g, b = _hex_to_rgb(hex_color)
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02X}{g:02X}{b:02X}"


def render_professional_page(
    slide: Any,
    goal: str,
    title: str,
    subtitle: str,
    bullets: list[str],
    C: dict,
    page_index: int,
    total_pages: int,
) -> None:
    """Render a professional-quality page."""
    from pptx_designer.tools.shapes import rect
    from pptx_designer.tools.text import text

    # Get colors with defaults
    primary = C.get("primary", "#3B82F6")
    accent = C.get("accent", "#8B5CF6")
    bg_dark = C.get("background", "#0F172A")
    bg_card = C.get("card", "#1E293B")
    text_dark = C.get("text_dark", "#F8FAFC")
    text_body = C.get("text_body", "#CBD5E1")
    text_muted = C.get("text_muted", "#64748B")

    # ── Dark background for all slides ────────────────────────────
    rect(slide, 0, 0, 13.333, 7.5, bg_dark)

    if goal == "hook":
        _render_hero(slide, title, subtitle, primary, accent, text_dark, text_body)
    elif goal == "problem":
        _render_problem(slide, title, bullets, primary, accent, text_dark, text_body, bg_card)
    elif goal == "solution":
        _render_solution(slide, title, bullets, primary, accent, text_dark, text_body, bg_card)
    elif goal == "features":
        _render_features(slide, title, bullets, primary, accent, text_dark, text_body, bg_card)
    elif goal == "data":
        _render_data(slide, title, bullets, primary, accent, text_dark, text_body, bg_card)
    elif goal == "code":
        _render_code(slide, title, bullets, primary, accent, text_dark, text_body, bg_card)
    else:
        _render_content(slide, title, bullets, primary, accent, text_dark, text_body, bg_card)

    # ── Page number ───────────────────────────────────────────────
    if page_index > 0:
        text(
            slide, 12.0, 7.0, 1.0, 0.3, f"{page_index + 1}/{total_pages}", font_size=10, color=text_muted, align="right"
        )


def _render_hero(
    slide: Any, title: str, subtitle: str, primary: str, accent: str, text_dark: str, text_body: str
) -> None:
    """Render hero/title slide."""
    from pptx_designer.tools.shapes import oval, rect
    from pptx_designer.tools.text import text

    # Decorative circles
    oval(slide, 9.5, -1.0, 5.0, 5.0, _darken(primary, 30))
    oval(slide, 10.5, 0.5, 3.5, 3.5, primary)
    oval(slide, -1.5, 5.0, 4.0, 4.0, _darken(accent, 40))

    # Accent line
    rect(slide, 1.0, 2.8, 1.5, 0.06, accent)

    # Title
    text(slide, 1.0, 3.0, 8.0, 1.2, title, font_size=48, bold=True, color=text_dark)

    # Subtitle
    if subtitle:
        text(slide, 1.0, 4.3, 8.0, 0.6, subtitle, font_size=20, color=text_body)


def _render_problem(
    slide: Any, title: str, bullets: list[str], primary: str, accent: str, text_dark: str, text_body: str, bg_card: str
) -> None:
    """Render problem slide with visual impact."""
    from pptx_designer.tools.shapes import oval, rect, rrect
    from pptx_designer.tools.text import text

    # Section label
    text(slide, 1.0, 0.5, 3.0, 0.3, "PROBLEM", font_size=12, bold=True, color=accent)

    # Title
    text(slide, 1.0, 0.9, 11.0, 0.8, title, font_size=36, bold=True, color=text_dark)

    # Divider
    rect(slide, 1.0, 1.8, 2.0, 0.04, accent)

    # Problem cards
    if bullets:
        card_width = min(3.5, 10.5 / len(bullets[:3]))
        for j, bullet in enumerate(bullets[:3]):
            x = 1.0 + j * (card_width + 0.4)
            # Card background
            rrect(slide, x, 2.3, card_width, 3.5, bg_card)
            # Icon circle
            oval(slide, x + card_width / 2 - 0.4, 2.6, 0.8, 0.8, _darken(accent, 20))
            text(
                slide,
                x + card_width / 2 - 0.3,
                2.7,
                0.6,
                0.6,
                str(j + 1),
                font_size=24,
                bold=True,
                color="#FFFFFF",
                align="center",
            )
            # Problem text
            text(slide, x + 0.2, 3.6, card_width - 0.4, 1.8, bullet, font_size=14, color=text_body, align="center")


def _render_solution(
    slide: Any, title: str, bullets: list[str], primary: str, accent: str, text_dark: str, text_body: str, bg_card: str
) -> None:
    """Render solution slide."""
    from pptx_designer.tools.shapes import oval, rect
    from pptx_designer.tools.text import text

    # Section label
    text(slide, 1.0, 0.5, 3.0, 0.3, "SOLUTION", font_size=12, bold=True, color="#22C55E")

    # Title
    text(slide, 1.0, 0.9, 11.0, 0.8, title, font_size=36, bold=True, color=text_dark)

    # Divider
    rect(slide, 1.0, 1.8, 2.0, 0.04, "#22C55E")

    # Solution items with checkmarks
    if bullets:
        y = 2.3
        for bullet in bullets[:4]:
            # Checkmark circle
            oval(slide, 1.0, y, 0.5, 0.5, "#22C55E")
            text(slide, 1.05, y + 0.05, 0.4, 0.4, "✓", font_size=18, bold=True, color="#FFFFFF", align="center")
            # Text
            text(slide, 1.8, y + 0.05, 10.0, 0.4, bullet, font_size=16, color=text_dark)
            # Subtle line
            rect(slide, 1.8, y + 0.55, 10.0, 0.01, _darken(bg_card, 10))
            y += 0.7


def _render_features(
    slide: Any, title: str, bullets: list[str], primary: str, accent: str, text_dark: str, text_body: str, bg_card: str
) -> None:
    """Render features with gradient cards."""
    from pptx_designer.tools.shapes import oval, rect, rrect
    from pptx_designer.tools.text import text

    # Section label
    text(slide, 1.0, 0.5, 3.0, 0.3, "FEATURES", font_size=12, bold=True, color=primary)

    # Title
    text(slide, 1.0, 0.9, 11.0, 0.8, title, font_size=36, bold=True, color=text_dark)

    # Divider
    rect(slide, 1.0, 1.8, 2.0, 0.04, primary)

    # Feature cards with gradient
    if bullets:
        cards = bullets[:3]
        card_width = min(3.5, 10.5 / len(cards))
        colors = [primary, accent, "#22C55E"]

        for j, (bullet, color) in enumerate(zip(cards, colors, strict=True)):
            x = 1.0 + j * (card_width + 0.4)
            # Card with gradient effect
            rrect(slide, x, 2.3, card_width, 3.8, _darken(color, 40))
            # Top accent bar
            rect(slide, x, 2.3, card_width, 0.08, color)
            # Icon placeholder
            oval(slide, x + card_width / 2 - 0.5, 2.8, 1.0, 1.0, color)
            text(slide, x + card_width / 2 - 0.4, 2.9, 0.8, 0.8, "★", font_size=32, color="#FFFFFF", align="center")
            # Feature text
            text(slide, x + 0.3, 4.1, card_width - 0.6, 1.5, bullet, font_size=14, color=text_body, align="center")


def _render_data(
    slide: Any, title: str, bullets: list[str], primary: str, accent: str, text_dark: str, text_body: str, bg_card: str
) -> None:
    """Render data/metrics with KPI cards."""
    from pptx_designer.tools.shapes import rect, rrect
    from pptx_designer.tools.text import text

    # Section label
    text(slide, 1.0, 0.5, 3.0, 0.3, "METRICS", font_size=12, bold=True, color="#F59E0B")

    # Title
    text(slide, 1.0, 0.9, 11.0, 0.8, title, font_size=36, bold=True, color=text_dark)

    # Divider
    rect(slide, 1.0, 1.8, 2.0, 0.04, "#F59E0B")

    # Parse KPI data
    if bullets:
        kpi_data = []
        for bullet in bullets:
            if ": " in bullet:
                parts = bullet.split(": ", 1)
                kpi_data.append((parts[1], parts[0]))
            else:
                kpi_data.append((bullet, ""))

        if len(kpi_data) <= 4:
            card_width = min(2.8, 10.0 / len(kpi_data))
            gap = 0.4
            total_width = len(kpi_data) * card_width + (len(kpi_data) - 1) * gap
            start_x = (13.333 - total_width) / 2

            colors = [primary, accent, "#22C55E", "#F59E0B"]
            for j, (value, label) in enumerate(kpi_data):
                x = start_x + j * (card_width + gap)
                color = colors[j % len(colors)]
                # KPI card
                rrect(slide, x, 2.5, card_width, 3.0, bg_card)
                # Top accent
                rect(slide, x, 2.5, card_width, 0.06, color)
                # Value
                text(slide, x, 3.0, card_width, 0.8, value, font_size=36, bold=True, color=color, align="center")
                # Label
                text(slide, x, 4.0, card_width, 0.4, label, font_size=12, color=text_body, align="center")


def _render_code(
    slide: Any, title: str, bullets: list[str], primary: str, accent: str, text_dark: str, text_body: str, bg_card: str
) -> None:
    """Render code slide."""
    from pptx_designer.tools.shapes import rrect
    from pptx_designer.tools.text import text

    # Section label
    text(slide, 1.0, 0.5, 3.0, 0.3, "CODE", font_size=12, bold=True, color="#22C55E")

    # Title
    text(slide, 1.0, 0.9, 11.0, 0.8, title, font_size=36, bold=True, color=text_dark)

    # Code block background
    rrect(slide, 1.0, 2.0, 11.0, 4.5, "#0D1117")

    # Language badge
    rrect(slide, 1.2, 2.2, 1.0, 0.3, primary)
    text(slide, 1.25, 2.22, 0.9, 0.25, "Python", font_size=10, bold=True, color="#FFFFFF", align="center")

    # Code lines
    if bullets:
        y = 2.7
        for line in bullets[:8]:
            text(slide, 1.5, y, 10.0, 0.25, line, font_size=12, color="#E6EDF3", font_name="Consolas")
            y += 0.35


def _render_content(
    slide: Any, title: str, bullets: list[str], primary: str, accent: str, text_dark: str, text_body: str, bg_card: str
) -> None:
    """Render generic content slide."""
    from pptx_designer.tools.shapes import rect, rrect
    from pptx_designer.tools.text import text

    # Title
    text(slide, 1.0, 0.5, 11.0, 0.8, title, font_size=36, bold=True, color=text_dark)

    # Divider
    rect(slide, 1.0, 1.4, 2.0, 0.04, primary)

    # Content with cards
    if bullets:
        y = 1.8
        for bullet in bullets[:5]:
            # Card
            rrect(slide, 1.0, y, 11.0, 0.8, bg_card)
            # Accent dot
            from pptx_designer.tools.shapes import oval

            oval(slide, 1.3, y + 0.25, 0.3, 0.3, primary)
            # Text
            text(slide, 1.8, y + 0.15, 10.0, 0.5, bullet, font_size=15, color=text_body)
            y += 1.0
