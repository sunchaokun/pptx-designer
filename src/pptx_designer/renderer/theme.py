"""Theme Composer — infinite design combinations from composable atoms.

When ui-ux-pro-max is available, delegates color/typography/style search
to its rich CSV databases (192 palettes, 74 font pairs, 84 styles).
Falls back to the hardcoded atoms below when the package is absent.

Design atoms (fallback):
  - ColorPalette: 25+ curated palettes (mood + industry based)
  - FontPair: 20+ heading+body font combinations
  - DecorationStyle: 10+ visual decoration patterns
  - LayoutVariant: 8+ structural layout modifications
  - Mood: emotional tone that biases all atom selections

Usage:
  composer = ThemeComposer()
  theme = composer.compose("minimalist fintech pitch with warm tones")
  theme = composer.compose(style="dark-tech")  # preset still works
  theme = composer.compose(palette="ocean-depth", fonts="serif-editorial", decoration="accent-bar", layout="sidebar-nav")
"""

from __future__ import annotations

import random
import re
from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from pptx_designer.search.adapters import (
    is_available as _ux_available,
)
from pptx_designer.search.adapters import (
    search_color as _ux_search_color,
)
from pptx_designer.search.adapters import (
    search_style as _ux_search_style,
)
from pptx_designer.search.adapters import (
    search_typography as _ux_search_typography,
)


def _package_version() -> str:
    try:
        return version("pptx-designer")
    except PackageNotFoundError:
        return "unknown"


_RESOLVED_THEME_FIELDS = {
    "name": str,
    "atoms": Mapping,
    "colors": Mapping,
    "semantic_roles": Mapping,
    "typography": Mapping,
    "decoration": Mapping,
    "layout_variant": Mapping,
    "source": Mapping,
}
_HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\Z")


def _is_hex_color(value: Any) -> bool:
    return isinstance(value, str) and bool(_HEX_COLOR.fullmatch(value))


def validate_resolved_theme(theme: Mapping[str, Any]) -> None:
    """Validate the complete theme contract consumed by FreeStyle rendering.

    ``ThemeComposer.compose()`` returns this contract.  Template and VI design
    contexts are deliberately *not* validated here: they may be partial and
    belong to Build Mode rather than the FreeStyle renderer.

    Raises:
        ValueError: If *theme* is not a complete resolved theme.
    """
    if not isinstance(theme, Mapping):
        raise ValueError("theme must be a resolved theme mapping from ThemeComposer.compose()")

    missing = sorted(field for field in _RESOLVED_THEME_FIELDS if field not in theme)
    invalid = sorted(
        field
        for field, expected_type in _RESOLVED_THEME_FIELDS.items()
        if field in theme
        and (
            not isinstance(theme[field], expected_type)
            or (expected_type is str and not theme[field].strip())
        )
    )
    atoms = theme.get("atoms")
    if isinstance(atoms, Mapping):
        missing_atoms = sorted(
            field for field in ("palette", "fonts", "decoration", "layout", "moods") if field not in atoms
        )
    else:
        missing_atoms = []
    invalid_atoms = []
    if isinstance(atoms, Mapping):
        invalid_atoms = [
            field
            for field in ("palette", "fonts", "decoration", "layout")
            if field in atoms and (not isinstance(atoms[field], str) or not atoms[field].strip())
        ]
        if "moods" in atoms and (
            not isinstance(atoms["moods"], list)
            or not atoms["moods"]
            or any(not isinstance(mood, str) or not mood.strip() for mood in atoms["moods"])
        ):
            invalid_atoms.append("moods")

    roles = theme.get("semantic_roles")
    if isinstance(roles, Mapping):
        missing_roles = sorted(
            field
            for field in (
                "background",
                "surface",
                "ink",
                "muted",
                "accent",
                "accent-secondary",
                "success",
                "warning",
                "danger",
                "border",
                "data-series-1",
                "data-series-2",
            )
            if field not in roles
        )
    else:
        missing_roles = []
    invalid_roles = []
    if isinstance(roles, Mapping):
        invalid_roles = [field for field, value in roles.items() if not _is_hex_color(value)]

    typography = theme.get("typography")
    if isinstance(typography, Mapping):
        missing_typography = sorted(field for field in ("heading", "body") if field not in typography)
    else:
        missing_typography = []
    invalid_typography = []
    if isinstance(typography, Mapping):
        invalid_typography = [
            field
            for field in ("heading", "body")
            if field in typography and (not isinstance(typography[field], str) or not typography[field].strip())
        ]

    colors = theme.get("colors")
    invalid_colors = []
    if isinstance(colors, Mapping):
        if not colors:
            invalid_colors.append("<empty>")
        invalid_colors.extend(field for field, value in colors.items() if not _is_hex_color(value))

    source = theme.get("source")
    if isinstance(source, Mapping):
        missing_source = sorted(field for field in ("requested", "resolved") if field not in source)
        invalid_source = sorted(
            field
            for field in ("requested", "resolved")
            if field in source and not isinstance(source[field], Mapping)
        )
    else:
        missing_source = []
        invalid_source = []

    if (
        missing
        or invalid
        or missing_atoms
        or invalid_atoms
        or missing_roles
        or invalid_roles
        or missing_typography
        or invalid_typography
        or invalid_colors
        or missing_source
        or invalid_source
    ):
        details: list[str] = []
        if missing:
            details.append("missing fields: " + ", ".join(missing))
        if invalid:
            details.append("invalid fields: " + ", ".join(invalid))
        if missing_atoms:
            details.append("missing atoms: " + ", ".join(missing_atoms))
        if invalid_atoms:
            details.append("invalid atoms: " + ", ".join(invalid_atoms))
        if missing_roles:
            details.append("missing semantic roles: " + ", ".join(missing_roles))
        if invalid_roles:
            details.append("invalid semantic role colors: " + ", ".join(sorted(invalid_roles)))
        if missing_typography:
            details.append("missing typography fields: " + ", ".join(missing_typography))
        if invalid_typography:
            details.append("invalid typography fields: " + ", ".join(invalid_typography))
        if invalid_colors:
            details.append("invalid colors: " + ", ".join(sorted(invalid_colors)))
        if missing_source:
            details.append("missing source fields: " + ", ".join(missing_source))
        if invalid_source:
            details.append("invalid source fields: " + ", ".join(invalid_source))
        raise ValueError(
            "theme must be a complete resolved theme from ThemeComposer.compose(); " + "; ".join(details)
        )

# ============================================================
# COLOR PALETTES — 25 curated palettes
# ============================================================

COLOR_PALETTES: dict[str, dict[str, str]] = {
    "ocean-blue": {
        "primary": "#1E5AB8",
        "on-primary": "#FFFFFF",
        "secondary": "#64748B",
        "accent": "#0096C7",
        "background": "#FFFFFF",
        "foreground": "#0A1E3D",
        "muted": "#F0F4F8",
        "muted-foreground": "#6B7B8D",
        "border": "#DEE5EF",
        "destructive": "#EF4444",
    },
    "midnight-navy": {
        "primary": "#1E3A5F",
        "on-primary": "#FFFFFF",
        "secondary": "#8A9BB5",
        "accent": "#E8A838",
        "background": "#0A1E3D",
        "foreground": "#F0F4F8",
        "muted": "#1A2E4A",
        "muted-foreground": "#8A9BB5",
        "border": "#2A3E5A",
        "destructive": "#FF6B6B",
    },
    "cyber-neon": {
        "primary": "#6366F1",
        "on-primary": "#FFFFFF",
        "secondary": "#94A3B8",
        "accent": "#22D3EE",
        "background": "#060B18",
        "foreground": "#F8FAFC",
        "muted": "#0D152A",
        "muted-foreground": "#64748B",
        "border": "#1A2A4A",
        "destructive": "#FF0080",
    },
    "neon-gradient": {
        "primary": "#8B5CF6",
        "on-primary": "#FFFFFF",
        "secondary": "#A09CB0",
        "accent": "#FF2D87",
        "background": "#120C1E",
        "foreground": "#F8FAFC",
        "muted": "#1E1435",
        "muted-foreground": "#A09CB0",
        "border": "#2A1E4A",
        "destructive": "#FF4444",
    },
    "golden-luxury": {
        "primary": "#C99A4E",
        "on-primary": "#FFFFFF",
        "secondary": "#9A8C7E",
        "accent": "#D4A853",
        "background": "#FAF3E8",
        "foreground": "#2C2C2C",
        "muted": "#FEF3C7",
        "muted-foreground": "#9A8C7E",
        "border": "#E7E5E4",
        "destructive": "#DC2626",
    },
    "rose-gold": {
        "primary": "#B76E79",
        "on-primary": "#FFFFFF",
        "secondary": "#8B7E74",
        "accent": "#E8B4B8",
        "background": "#FFF5F5",
        "foreground": "#3D2C2C",
        "muted": "#FDE8E8",
        "muted-foreground": "#A89898",
        "border": "#E8D5D5",
        "destructive": "#DC2626",
    },
    "forest-green": {
        "primary": "#1B5E20",
        "on-primary": "#FFFFFF",
        "secondary": "#6B8E6B",
        "accent": "#4CAF50",
        "background": "#F5F7F0",
        "foreground": "#0D3B11",
        "muted": "#E8F0E5",
        "muted-foreground": "#6B8E6B",
        "border": "#C8DCC5",
        "destructive": "#DC2626",
    },
    "sage-calm": {
        "primary": "#5B7553",
        "on-primary": "#FFFFFF",
        "secondary": "#8B9E84",
        "accent": "#8BC38A",
        "background": "#F4F7F1",
        "foreground": "#2D3B28",
        "muted": "#E5EDE2",
        "muted-foreground": "#8B9E84",
        "border": "#D0DCCE",
        "destructive": "#DC2626",
    },
    "sunset-warm": {
        "primary": "#D97706",
        "on-primary": "#FFFFFF",
        "secondary": "#92400E",
        "accent": "#F59E0B",
        "background": "#FFFBEB",
        "foreground": "#1C1917",
        "muted": "#FEF3C7",
        "muted-foreground": "#A8A29E",
        "border": "#E7E5E4",
        "destructive": "#DC2626",
    },
    "terracotta": {
        "primary": "#C4704B",
        "on-primary": "#FFFFFF",
        "secondary": "#8B6B5E",
        "accent": "#E8926C",
        "background": "#FBF5F0",
        "foreground": "#3D2B1F",
        "muted": "#F0E0D5",
        "muted-foreground": "#9B8B7E",
        "border": "#DDD0C5",
        "destructive": "#DC2626",
    },
    "cherry-red": {
        "primary": "#DC2626",
        "on-primary": "#FFFFFF",
        "secondary": "#991B1B",
        "accent": "#F87171",
        "background": "#FEF2F2",
        "foreground": "#1C1917",
        "muted": "#FEE2E2",
        "muted-foreground": "#B91C1C",
        "border": "#FECACA",
        "destructive": "#991B1B",
    },
    "royal-purple": {
        "primary": "#7C3AED",
        "on-primary": "#FFFFFF",
        "secondary": "#6D28D9",
        "accent": "#A78BFA",
        "background": "#F5F3FF",
        "foreground": "#1E1B4B",
        "muted": "#EDE9FE",
        "muted-foreground": "#8B5CF6",
        "border": "#DDD6FE",
        "destructive": "#EF4444",
    },
    "arctic-frost": {
        "primary": "#0EA5E9",
        "on-primary": "#FFFFFF",
        "secondary": "#0284C7",
        "accent": "#38BDF8",
        "background": "#F0F9FF",
        "foreground": "#0C4A6E",
        "muted": "#E0F2FE",
        "muted-foreground": "#0369A1",
        "border": "#BAE6FD",
        "destructive": "#EF4444",
    },
    "slate-minimal": {
        "primary": "#475569",
        "on-primary": "#FFFFFF",
        "secondary": "#64748B",
        "accent": "#94A3B8",
        "background": "#F8FAFC",
        "foreground": "#0F172A",
        "muted": "#F1F5F9",
        "muted-foreground": "#94A3B8",
        "border": "#E2E8F0",
        "destructive": "#EF4444",
    },
    "charcoal-bold": {
        "primary": "#1F2937",
        "on-primary": "#FFFFFF",
        "secondary": "#4B5563",
        "accent": "#F97316",
        "background": "#111827",
        "foreground": "#F9FAFB",
        "muted": "#1F2937",
        "muted-foreground": "#6B7280",
        "border": "#374151",
        "destructive": "#EF4444",
    },
    "coral-energy": {
        "primary": "#F97316",
        "on-primary": "#FFFFFF",
        "secondary": "#EA580C",
        "accent": "#FB923C",
        "background": "#FFF7ED",
        "foreground": "#431407",
        "muted": "#FFEDD5",
        "muted-foreground": "#C2410C",
        "border": "#FED7AA",
        "destructive": "#DC2626",
    },
    "teal-fresh": {
        "primary": "#0D9488",
        "on-primary": "#FFFFFF",
        "secondary": "#0F766E",
        "accent": "#2DD4BF",
        "background": "#F0FDFA",
        "foreground": "#134E4A",
        "muted": "#CCFBF1",
        "muted-foreground": "#14B8A6",
        "border": "#99F6E4",
        "destructive": "#EF4444",
    },
    "indigo-deep": {
        "primary": "#4338CA",
        "on-primary": "#FFFFFF",
        "secondary": "#3730A3",
        "accent": "#6366F1",
        "background": "#EEF2FF",
        "foreground": "#1E1B4B",
        "muted": "#E0E7FF",
        "muted-foreground": "#4F46E5",
        "border": "#C7D2FE",
        "destructive": "#EF4444",
    },
    "copper-industrial": {
        "primary": "#B87333",
        "on-primary": "#FFFFFF",
        "secondary": "#8B5E3C",
        "accent": "#D4956A",
        "background": "#2D2D2D",
        "foreground": "#E8E0D8",
        "muted": "#3D3D3D",
        "muted-foreground": "#9B8B7E",
        "border": "#4D4D4D",
        "destructive": "#FF6B6B",
    },
    "monochrome": {
        "primary": "#18181B",
        "on-primary": "#FFFFFF",
        "secondary": "#3F3F46",
        "accent": "#A1A1AA",
        "background": "#FAFAFA",
        "foreground": "#09090B",
        "muted": "#F4F4F5",
        "muted-foreground": "#71717A",
        "border": "#E4E4E7",
        "destructive": "#DC2626",
    },
    "monochrome-dark": {
        "primary": "#D4D4D8",
        "on-primary": "#18181B",
        "secondary": "#A1A1AA",
        "accent": "#F4F4F5",
        "background": "#09090B",
        "foreground": "#FAFAFA",
        "muted": "#18181B",
        "muted-foreground": "#71717A",
        "border": "#27272A",
        "destructive": "#EF4444",
    },
    "lavender-dream": {
        "primary": "#8B5CF6",
        "on-primary": "#FFFFFF",
        "secondary": "#7C3AED",
        "accent": "#C4B5FD",
        "background": "#FAF5FF",
        "foreground": "#3B0764",
        "muted": "#F3E8FF",
        "muted-foreground": "#9333EA",
        "border": "#E9D5FF",
        "destructive": "#EF4444",
    },
    "mint-fresh": {
        "primary": "#10B981",
        "on-primary": "#FFFFFF",
        "secondary": "#059669",
        "accent": "#34D399",
        "background": "#ECFDF5",
        "foreground": "#064E3B",
        "muted": "#D1FAE5",
        "muted-foreground": "#6B7280",
        "border": "#A7F3D0",
        "destructive": "#DC2626",
    },
    "wine-burgundy": {
        "primary": "#7F1D1D",
        "on-primary": "#FFFFFF",
        "secondary": "#991B1B",
        "accent": "#B91C1C",
        "background": "#1C1010",
        "foreground": "#FEF2F2",
        "muted": "#2D1A1A",
        "muted-foreground": "#9B7A7A",
        "border": "#3D2A2A",
        "destructive": "#EF4444",
    },
    "sky-bright": {
        "primary": "#0284C7",
        "on-primary": "#FFFFFF",
        "secondary": "#0369A1",
        "accent": "#38BDF8",
        "background": "#F0F9FF",
        "foreground": "#0C4A6E",
        "muted": "#E0F2FE",
        "muted-foreground": "#0EA5E9",
        "border": "#BAE6FD",
        "destructive": "#EF4444",
    },
    "ink-wash": {
        "primary": "#2C2C2C",
        "on-primary": "#F5F0E8",
        "secondary": "#8B7355",
        "accent": "#C41E3A",
        "background": "#F5F0E8",
        "foreground": "#1A1A1A",
        "muted": "#EDE6D6",
        "muted-foreground": "#8B7355",
        "border": "#D4C5A0",
        "destructive": "#C41E3A",
    },
    "ink-wash-dark": {
        "primary": "#F5F0E8",
        "on-primary": "#2C2C2C",
        "secondary": "#8B7355",
        "accent": "#C41E3A",
        "background": "#1A1A1A",
        "foreground": "#F5F0E8",
        "muted": "#2D2D2D",
        "muted-foreground": "#8B7355",
        "border": "#3D3D3D",
        "destructive": "#C41E3A",
    },
    "cyber-neon-pro": {
        "primary": "#8B5CF6",
        "on-primary": "#FFFFFF",
        "secondary": "#64748B",
        "accent": "#22D3EE",
        "background": "#0A0A1A",
        "foreground": "#F8FAFC",
        "muted": "#1A1A3A",
        "muted-foreground": "#6366F1",
        "border": "#2A2A5A",
        "destructive": "#FF0080",
    },
    "sci-paper": {
        "primary": "#1E3A5F",
        "on-primary": "#FFFFFF",
        "secondary": "#64748B",
        "accent": "#E8A838",
        "background": "#FFFFFF",
        "foreground": "#1A1A1A",
        "muted": "#F0F4F8",
        "muted-foreground": "#6B7B8D",
        "border": "#DEE5EF",
        "destructive": "#DC2626",
    },
    "zen-minimal": {
        "primary": "#5B7553",
        "on-primary": "#FFFFFF",
        "secondary": "#8B9E84",
        "accent": "#C99A4E",
        "background": "#FAFAF5",
        "foreground": "#2D3B28",
        "muted": "#E5EDE2",
        "muted-foreground": "#8B9E84",
        "border": "#D0DCCE",
        "destructive": "#DC2626",
    },
}

# ============================================================
# FONT PAIRS — 20 curated heading+body combinations
# ============================================================

FONT_PAIRS: dict[str, dict[str, str]] = {
    "modern-sans": {"heading": "Inter", "body": "Inter"},
    "geometric-sans": {"heading": "Space Grotesk", "body": "Inter"},
    "bold-sans": {"heading": "Poppins", "body": "Inter"},
    "clean-corporate": {"heading": "Calibri", "body": "Calibri"},
    "serif-editorial": {"heading": "Georgia", "body": "Georgia"},
    "elegant-serif": {"heading": "Playfair Display", "body": "Inter"},
    "literary-serif": {"heading": "Lora", "body": "Inter"},
    "tech-mono": {"heading": "Consolas", "body": "Consolas"},
    "mono-clean": {"heading": "Consolas", "body": "Inter"},
    "swiss-style": {"heading": "Arial", "body": "Arial"},
    "humanist-sans": {"heading": "Segoe UI", "body": "Segoe UI"},
    "friendly-round": {"heading": "Nunito", "body": "Inter"},
    "sharp-modern": {"heading": "Montserrat", "body": "Inter"},
    "classic-formal": {"heading": "Times New Roman", "body": "Times New Roman"},
    "contrast-mix": {"heading": "Playfair Display", "body": "Calibri"},
    "tech-contrast": {"heading": "Space Grotesk", "body": "Consolas"},
    "warm-mix": {"heading": "Georgia", "body": "Calibri"},
    "startup-mix": {"heading": "Poppins", "body": "Segoe UI"},
    "minimal-mix": {"heading": "Inter", "body": "Calibri"},
    "editorial-mix": {"heading": "Georgia", "body": "Segoe UI"},
    "ink-wash-serif": {"heading": "STKaiti", "body": "FangSong"},
    "chinese-calligraphy": {"heading": "STXingkai", "body": "SimSun"},
    "chinese-classical": {"heading": "LiSu", "body": "FangSong"},
    "sci-serif": {"heading": "Georgia", "body": "Times New Roman"},
    "tech-display": {"heading": "Orbitron", "body": "JetBrains Mono"},
}

# ============================================================
# DECORATION STYLES — 10 visual decoration patterns
# ============================================================

DECORATION_STYLES: dict[str, dict[str, Any]] = {
    "accent-bar": {
        "name": "Accent Bar",
        "left_accent": True,
        "title_underline": True,
        "card_top_bar": True,
        "description": "Clean accent bars and underlines",
    },
    "neon-lines": {
        "name": "Neon Lines",
        "left_accent": True,
        "title_underline": True,
        "card_top_bar": True,
        "top_line": True,
        "bottom_line": True,
        "description": "Glowing neon accent lines",
    },
    "gold-trim": {
        "name": "Gold Trim",
        "left_accent": True,
        "title_underline": True,
        "card_top_bar": True,
        "top_line": True,
        "bottom_line": True,
        "description": "Elegant gold decorative lines",
    },
    "minimal-dots": {
        "name": "Minimal Dots",
        "left_accent": False,
        "title_underline": False,
        "card_top_bar": False,
        "bullet_style": "circle",
        "description": "Subtle dot bullets, no lines",
    },
    "diamond-bullets": {
        "name": "Diamond Bullets",
        "left_accent": False,
        "title_underline": True,
        "card_top_bar": True,
        "bullet_style": "diamond",
        "description": "Diamond-shaped bullet points",
    },
    "gradient-bar": {
        "name": "Gradient Bar",
        "left_accent": True,
        "title_underline": True,
        "card_top_bar": True,
        "gradient_accent": True,
        "description": "Gradient-colored accent bars",
    },
    "circle-accent": {
        "name": "Circle Accent",
        "left_accent": False,
        "title_underline": False,
        "card_top_bar": False,
        "circle_decoration": True,
        "description": "Circle decorative elements",
    },
    "sidebar-nav": {
        "name": "Sidebar Navigation",
        "left_accent": True,
        "title_underline": True,
        "card_top_bar": True,
        "sidebar": True,
        "description": "Left sidebar with section info",
    },
    "no-decoration": {
        "name": "No Decoration",
        "left_accent": False,
        "title_underline": False,
        "card_top_bar": False,
        "description": "Clean, no decorative elements",
    },
    "full-bleed-overlay": {
        "name": "Full Bleed Overlay",
        "left_accent": False,
        "title_underline": False,
        "card_top_bar": False,
        "dark_overlay": True,
        "description": "Full-bleed image with dark overlay",
    },
    "brush-stroke": {
        "name": "Brush Stroke",
        "left_accent": True,
        "title_underline": True,
        "brush_divider": True,
        "description": "Ink brush stroke decorative elements",
    },
    "seal-stamp": {
        "name": "Seal Stamp",
        "left_accent": False,
        "title_underline": False,
        "seal_decoration": True,
        "description": "Traditional Chinese seal stamp accents",
    },
    "neon-glow": {
        "name": "Neon Glow",
        "left_accent": True,
        "title_underline": True,
        "card_top_bar": True,
        "bottom_line": True,
        "neon_accent": True,
        "description": "Glowing neon accent lines and borders",
    },
    "sci-grid": {
        "name": "Science Grid",
        "left_accent": True,
        "title_underline": True,
        "grid_background": True,
        "description": "Subtle grid background for scientific presentations",
    },
    "glass-panel": {
        "name": "Glass Panel",
        "left_accent": False,
        "title_underline": False,
        "glass_card": True,
        "description": "Frosted glass card-style panels",
    },
}

# ============================================================
# LAYOUT VARIANTS — 8 structural modifications
# ============================================================

LAYOUT_VARIANTS: dict[str, dict[str, Any]] = {
    "standard": {
        "name": "Standard",
        "content_margin_left": 0.9,
        "content_margin_right": 0.9,
        "title_alignment": "left",
        "card_style": "rounded",
        "description": "Standard left-aligned layout",
    },
    "centered": {
        "name": "Centered",
        "content_margin_left": 2.0,
        "content_margin_right": 2.0,
        "title_alignment": "center",
        "card_style": "rounded",
        "description": "Centered editorial layout",
    },
    "sidebar-left": {
        "name": "Left Sidebar",
        "sidebar_width": 3.5,
        "sidebar_side": "left",
        "content_margin_left": 4.2,
        "content_margin_right": 0.9,
        "title_alignment": "left",
        "card_style": "rounded",
        "description": "Left sidebar with section info",
    },
    "sidebar-right": {
        "name": "Right Sidebar",
        "sidebar_width": 3.5,
        "sidebar_side": "right",
        "content_margin_left": 0.9,
        "content_margin_right": 4.5,
        "title_alignment": "left",
        "card_style": "rounded",
        "description": "Right sidebar for stats/quotes",
    },
    "wide-cards": {
        "name": "Wide Cards",
        "content_margin_left": 0.6,
        "content_margin_right": 0.6,
        "title_alignment": "left",
        "card_style": "wide",
        "card_gap": 0.3,
        "description": "Wide card-based layout",
    },
    "grid-2x2": {
        "name": "2x2 Grid",
        "content_margin_left": 0.8,
        "content_margin_right": 0.8,
        "title_alignment": "left",
        "card_style": "grid",
        "grid_rows": 2,
        "grid_cols": 2,
        "description": "2x2 grid of metric cards",
    },
    "asymmetric": {
        "name": "Asymmetric",
        "content_margin_left": 0.8,
        "content_margin_right": 0.8,
        "title_alignment": "left",
        "card_style": "staggered",
        "description": "Asymmetric staggered layout",
    },
    "full-width": {
        "name": "Full Width",
        "content_margin_left": 0.5,
        "content_margin_right": 0.5,
        "title_alignment": "left",
        "card_style": "flat",
        "description": "Full-width edge-to-edge layout",
    },
    "scroll": {
        "name": "Scroll",
        "content_margin_left": 2.5,
        "content_margin_right": 2.5,
        "title_alignment": "center",
        "card_style": "scroll",
        "description": "Central scroll/panel layout with wide margins",
    },
    "ink-wash": {
        "name": "Ink Wash",
        "content_margin_left": 1.5,
        "content_margin_right": 3.5,
        "title_alignment": "left",
        "card_style": "minimal",
        "vertical_text_area": True,
        "description": "Left content + right vertical text column",
    },
    "sci-dense": {
        "name": "Science Dense",
        "content_margin_left": 0.6,
        "content_margin_right": 0.6,
        "title_alignment": "left",
        "card_style": "flat",
        "dense_mode": True,
        "description": "High-density layout for scientific papers",
    },
    "hero-image": {
        "name": "Hero Image",
        "content_margin_left": 0.0,
        "content_margin_right": 0.0,
        "title_alignment": "center",
        "card_style": "overlay",
        "description": "Full-bleed hero image with text overlay",
    },
}

# ============================================================
# MOOD KEYWORDS — natural language → atom selection hints
# ============================================================

_MOOD_PALETTE_MAP: dict[str, list[str]] = {
    "professional": ["ocean-blue", "midnight-navy", "slate-minimal", "arctic-frost"],
    "corporate": ["ocean-blue", "midnight-navy", "indigo-deep", "charcoal-bold"],
    "tech": ["cyber-neon", "neon-gradient", "charcoal-bold", "monochrome-dark"],
    "dark": ["cyber-neon", "neon-gradient", "charcoal-bold", "monochrome-dark", "copper-industrial", "wine-burgundy"],
    "warm": ["golden-luxury", "sunset-warm", "terracotta", "coral-energy", "rose-gold"],
    "elegant": ["golden-luxury", "rose-gold", "lavender-dream", "wine-burgundy"],
    "luxury": ["golden-luxury", "rose-gold", "wine-burgundy", "copper-industrial"],
    "vibrant": ["neon-gradient", "coral-energy", "cherry-red", "royal-purple"],
    "startup": ["neon-gradient", "royal-purple", "coral-energy", "arctic-frost"],
    "nature": ["forest-green", "sage-calm", "mint-fresh", "teal-fresh"],
    "calm": ["sage-calm", "arctic-frost", "sky-bright", "lavender-dream"],
    "minimal": ["slate-minimal", "monochrome", "arctic-frost", "ocean-blue"],
    "bold": ["cherry-red", "coral-energy", "charcoal-bold", "cyber-neon"],
    "fresh": ["mint-fresh", "teal-fresh", "arctic-frost", "sky-bright"],
    "industrial": ["copper-industrial", "charcoal-bold", "monochrome-dark", "terracotta"],
    "fintech": ["ocean-blue", "midnight-navy", "forest-green", "indigo-deep"],
    "health": ["mint-fresh", "teal-fresh", "sage-calm", "sky-bright"],
    "education": ["ocean-blue", "indigo-deep", "teal-fresh", "slate-minimal"],
    "creative": ["neon-gradient", "royal-purple", "lavender-dream", "coral-energy"],
    "sustainability": ["forest-green", "sage-calm", "mint-fresh", "teal-fresh"],
    "international": ["ocean-blue", "midnight-navy", "slate-minimal", "indigo-deep"],
    "cream": ["golden-luxury", "sunset-warm", "terracotta", "rose-gold"],
    "frosted": ["arctic-frost", "sky-bright", "lavender-dream", "slate-minimal"],
    "mckinsey": ["ocean-blue", "midnight-navy", "slate-minimal", "indigo-deep"],
    "consulting": ["ocean-blue", "midnight-navy", "slate-minimal", "indigo-deep"],
    "pastel": ["lavender-dream", "mint-fresh", "sky-bright", "rose-gold"],
    "retro": ["terracotta", "sunset-warm", "golden-luxury", "copper-industrial"],
    "government": ["ocean-blue", "midnight-navy", "slate-minimal", "charcoal-bold"],
    "legal": ["ocean-blue", "midnight-navy", "charcoal-bold", "slate-minimal"],
    "pharma": ["mint-fresh", "teal-fresh", "sky-bright", "arctic-frost"],
    "realestate": ["golden-luxury", "terracotta", "sunset-warm", "copper-industrial"],
    "automotive": ["charcoal-bold", "monochrome-dark", "copper-industrial", "midnight-navy"],
    "aviation": ["sky-bright", "ocean-blue", "arctic-frost", "midnight-navy"],
    "energy": ["forest-green", "copper-industrial", "charcoal-bold", "sunset-warm"],
    "telecom": ["cyber-neon", "ocean-blue", "midnight-navy", "neon-gradient"],
    "logistics": ["copper-industrial", "charcoal-bold", "slate-minimal", "monochrome"],
    "ink-wash": ["ink-wash", "ink-wash-dark", "zen-minimal"],
    "chinese-traditional": ["ink-wash", "ink-wash-dark", "zen-minimal"],
    "zen": ["zen-minimal", "ink-wash", "sage-calm"],
    "sci": ["sci-paper", "ocean-blue", "midnight-navy"],
    "neon": ["cyber-neon-pro", "cyber-neon", "neon-gradient"],
}

_MOOD_FONT_MAP: dict[str, list[str]] = {
    "professional": ["modern-sans", "clean-corporate", "swiss-style"],
    "corporate": ["clean-corporate", "modern-sans", "swiss-style"],
    "tech": ["tech-mono", "mono-clean", "geometric-sans"],
    "dark": ["tech-mono", "mono-clean", "geometric-sans"],
    "warm": ["serif-editorial", "warm-mix", "elegant-serif"],
    "elegant": ["elegant-serif", "serif-editorial", "literary-serif"],
    "luxury": ["elegant-serif", "serif-editorial", "contrast-mix"],
    "vibrant": ["bold-sans", "startup-mix", "sharp-modern"],
    "startup": ["bold-sans", "startup-mix", "humanist-sans"],
    "nature": ["literary-serif", "warm-mix", "humanist-sans"],
    "calm": ["humanist-sans", "minimal-mix", "literary-serif"],
    "minimal": ["modern-sans", "minimal-mix", "swiss-style"],
    "bold": ["bold-sans", "sharp-modern", "geometric-sans"],
    "fresh": ["humanist-sans", "friendly-round", "modern-sans"],
    "industrial": ["tech-contrast", "mono-clean", "swiss-style"],
    "fintech": ["clean-corporate", "modern-sans", "swiss-style"],
    "health": ["humanist-sans", "friendly-round", "modern-sans"],
    "education": ["clean-corporate", "editorial-mix", "modern-sans"],
    "creative": ["contrast-mix", "sharp-modern", "friendly-round"],
    "sustainability": ["humanist-sans", "warm-mix", "literary-serif"],
    "international": ["clean-corporate", "modern-sans", "swiss-style"],
    "cream": ["serif-editorial", "warm-mix", "elegant-serif"],
    "frosted": ["modern-sans", "minimal-mix", "humanist-sans"],
    "mckinsey": ["clean-corporate", "swiss-style", "modern-sans"],
    "consulting": ["clean-corporate", "swiss-style", "modern-sans"],
    "pastel": ["humanist-sans", "friendly-round", "warm-mix"],
    "retro": ["serif-editorial", "literary-serif", "warm-mix"],
    "government": ["clean-corporate", "swiss-style", "modern-sans"],
    "legal": ["serif-editorial", "clean-corporate", "elegant-serif"],
    "pharma": ["clean-corporate", "humanist-sans", "modern-sans"],
    "realestate": ["serif-editorial", "elegant-serif", "clean-corporate"],
    "automotive": ["tech-contrast", "geometric-sans", "bold-sans"],
    "aviation": ["modern-sans", "clean-corporate", "swiss-style"],
    "energy": ["clean-corporate", "modern-sans", "tech-contrast"],
    "telecom": ["tech-mono", "modern-sans", "geometric-sans"],
    "logistics": ["modern-sans", "clean-corporate", "mono-clean"],
    "ink-wash": ["ink-wash-serif", "chinese-calligraphy", "chinese-classical"],
    "chinese-traditional": ["ink-wash-serif", "chinese-classical", "literary-serif"],
    "zen": ["ink-wash-serif", "literary-serif", "humanist-sans"],
    "sci": ["sci-serif", "clean-corporate", "modern-sans"],
    "neon": ["tech-display", "tech-mono", "geometric-sans"],
}

_MOOD_DECORATION_MAP: dict[str, list[str]] = {
    "professional": ["accent-bar", "sidebar-nav"],
    "corporate": ["accent-bar", "sidebar-nav", "gradient-bar"],
    "tech": ["neon-lines", "no-decoration"],
    "dark": ["neon-lines", "full-bleed-overlay", "no-decoration"],
    "warm": ["gold-trim", "diamond-bullets"],
    "elegant": ["gold-trim", "diamond-bullets", "circle-accent"],
    "luxury": ["gold-trim", "circle-accent"],
    "vibrant": ["gradient-bar", "neon-lines"],
    "startup": ["gradient-bar", "accent-bar"],
    "nature": ["circle-accent", "minimal-dots"],
    "calm": ["minimal-dots", "no-decoration", "circle-accent"],
    "minimal": ["no-decoration", "minimal-dots"],
    "bold": ["accent-bar", "gradient-bar"],
    "fresh": ["circle-accent", "accent-bar"],
    "industrial": ["accent-bar", "no-decoration"],
    "fintech": ["accent-bar", "sidebar-nav"],
    "health": ["circle-accent", "accent-bar"],
    "education": ["accent-bar", "minimal-dots"],
    "creative": ["gradient-bar", "circle-accent"],
    "sustainability": ["circle-accent", "minimal-dots"],
    "international": ["accent-bar", "sidebar-nav", "gradient-bar"],
    "cream": ["gold-trim", "diamond-bullets", "circle-accent"],
    "frosted": ["no-decoration", "minimal-dots", "circle-accent"],
    "mckinsey": ["accent-bar", "sidebar-nav"],
    "consulting": ["accent-bar", "sidebar-nav", "gradient-bar"],
    "pastel": ["circle-accent", "minimal-dots", "no-decoration"],
    "retro": ["diamond-bullets", "gold-trim", "accent-bar"],
    "government": ["accent-bar", "sidebar-nav", "no-decoration"],
    "legal": ["accent-bar", "sidebar-nav", "no-decoration"],
    "pharma": ["accent-bar", "circle-accent", "minimal-dots"],
    "realestate": ["gold-trim", "accent-bar", "circle-accent"],
    "automotive": ["accent-bar", "gradient-bar", "no-decoration"],
    "aviation": ["accent-bar", "minimal-dots", "no-decoration"],
    "energy": ["accent-bar", "sidebar-nav", "gradient-bar"],
    "telecom": ["neon-lines", "gradient-bar", "accent-bar"],
    "logistics": ["accent-bar", "sidebar-nav", "no-decoration"],
    "ink-wash": ["brush-stroke", "seal-stamp", "no-decoration"],
    "chinese-traditional": ["brush-stroke", "seal-stamp", "gold-trim"],
    "zen": ["no-decoration", "minimal-dots", "brush-stroke"],
    "sci": ["sci-grid", "accent-bar", "no-decoration"],
    "neon": ["neon-glow", "neon-lines", "no-decoration"],
}

_MOOD_LAYOUT_MAP: dict[str, list[str]] = {
    "professional": ["sidebar-left", "grid-2x2", "standard"],
    "corporate": ["sidebar-left", "standard", "grid-2x2"],
    "tech": ["wide-cards", "standard", "full-width"],
    "dark": ["wide-cards", "full-width", "standard"],
    "warm": ["centered", "standard", "sidebar-right"],
    "elegant": ["centered", "standard", "sidebar-right"],
    "luxury": ["centered", "sidebar-right"],
    "vibrant": ["wide-cards", "grid-2x2", "asymmetric"],
    "startup": ["grid-2x2", "wide-cards", "asymmetric"],
    "nature": ["standard", "sidebar-left", "grid-2x2"],
    "calm": ["standard", "centered", "sidebar-left"],
    "minimal": ["standard", "centered", "full-width"],
    "bold": ["full-width", "asymmetric", "wide-cards"],
    "fresh": ["grid-2x2", "standard", "wide-cards"],
    "industrial": ["full-width", "standard", "sidebar-left"],
    "fintech": ["sidebar-left", "grid-2x2", "standard"],
    "health": ["grid-2x2", "standard", "sidebar-left"],
    "education": ["standard", "sidebar-left", "grid-2x2"],
    "creative": ["asymmetric", "wide-cards", "centered"],
    "sustainability": ["grid-2x2", "sidebar-left", "standard"],
    "international": ["sidebar-left", "standard", "grid-2x2"],
    "cream": ["centered", "standard", "sidebar-right"],
    "frosted": ["standard", "centered", "full-width"],
    "mckinsey": ["sidebar-left", "standard", "grid-2x2"],
    "consulting": ["sidebar-left", "standard", "grid-2x2"],
    "pastel": ["centered", "standard", "grid-2x2"],
    "retro": ["centered", "standard", "sidebar-right"],
    "government": ["sidebar-left", "standard", "grid-2x2"],
    "legal": ["sidebar-left", "standard", "grid-2x2"],
    "pharma": ["grid-2x2", "standard", "sidebar-left"],
    "realestate": ["grid-2x2", "standard", "sidebar-left"],
    "automotive": ["full-width", "standard", "wide-cards"],
    "aviation": ["standard", "sidebar-left", "grid-2x2"],
    "energy": ["sidebar-left", "grid-2x2", "standard"],
    "telecom": ["wide-cards", "standard", "grid-2x2"],
    "logistics": ["sidebar-left", "standard", "grid-2x2"],
    "ink-wash": ["ink-wash", "scroll", "centered"],
    "chinese-traditional": ["ink-wash", "scroll", "centered"],
    "zen": ["centered", "standard", "ink-wash"],
    "sci": ["sci-dense", "sidebar-left", "grid-2x2"],
    "neon": ["wide-cards", "full-width", "hero-image"],
}

_MOOD_TEXT_EFFECT_MAP: dict[str, list[str | None]] = {
    "professional": [None, "steel"],
    "corporate": [None, "steel"],
    "tech": ["cyber-cyan", "blue-deep"],
    "dark": ["purple-neon", "cyber-cyan"],
    "warm": ["gold-shine", "sunset"],
    "elegant": ["rose-gold", "gold-shine"],
    "luxury": ["gold-shine", "rose-gold"],
    "vibrant": ["sunset", "emerald"],
    "startup": ["blue-deep", "cyber-cyan"],
    "nature": ["emerald", None],
    "calm": [None, "emerald"],
    "minimal": [None],
    "bold": ["sunset", "seal-red"],
    "fresh": ["emerald", "cyber-cyan"],
    "industrial": ["steel", None],
    "fintech": ["blue-deep", "steel"],
    "health": ["emerald", None],
    "education": ["blue-deep", None],
    "creative": ["purple-neon", "sunset"],
    "sustainability": ["emerald", None],
    "international": ["blue-deep", None],
    "cream": ["gold-shine", "rose-gold"],
    "frosted": ["steel", None],
    "mckinsey": ["blue-deep", None],
    "consulting": ["blue-deep", None],
    "pastel": ["rose-gold", None],
    "retro": ["gold-shine", "ink-wash"],
    "government": ["steel", None],
    "legal": ["steel", None],
    "pharma": ["emerald", None],
    "realestate": ["gold-shine", None],
    "automotive": ["steel", "cyber-cyan"],
    "aviation": ["blue-deep", None],
    "energy": ["emerald", "sunset"],
    "telecom": ["cyber-cyan", "purple-neon"],
    "logistics": ["steel", None],
    "ink-wash": ["ink-wash", None],
    "chinese-traditional": ["ink-wash", "seal-red"],
    "zen": [None],
    "sci": ["blue-deep", None],
    "neon": ["purple-neon", "cyber-cyan"],
}

_MOOD_IMAGE_EFFECT_MAP: dict[str, list[str | None]] = {
    "professional": [None, "soft_edge"],
    "corporate": [None, "soft_edge"],
    "tech": ["duotone", None],
    "dark": ["duotone", None],
    "warm": ["sepia", "soft_edge"],
    "elegant": ["soft_edge", None],
    "luxury": ["soft_edge", None],
    "vibrant": [None],
    "startup": [None],
    "nature": ["soft_edge", None],
    "calm": ["soft_edge", None],
    "minimal": [None],
    "bold": [None],
    "fresh": [None],
    "industrial": [None],
    "fintech": [None],
    "health": [None],
    "education": [None],
    "creative": [None],
    "sustainability": ["soft_edge", None],
    "international": [None],
    "cream": ["sepia", None],
    "frosted": ["soft_edge", None],
    "mckinsey": [None],
    "consulting": [None],
    "pastel": [None],
    "retro": ["sepia", "grayscale"],
    "government": [None],
    "legal": [None],
    "pharma": [None],
    "realestate": [None],
    "automotive": [None],
    "aviation": [None],
    "energy": [None],
    "telecom": ["duotone", None],
    "logistics": [None],
    "ink-wash": ["ink_wash", "grayscale"],
    "chinese-traditional": ["ink_wash", "grayscale"],
    "zen": ["soft_edge", None],
    "sci": [None],
    "neon": ["duotone", None],
}

# Preset theme → atom mapping (backward compatible)
_PRESET_ATOM_MAP: dict[str, dict[str, str]] = {
    "professional": {
        "palette": "midnight-navy",
        "fonts": "clean-corporate",
        "decoration": "accent-bar",
        "layout": "sidebar-left",
    },
    "dark-tech": {"palette": "cyber-neon", "fonts": "tech-mono", "decoration": "neon-lines", "layout": "wide-cards"},
    "warm-elegant": {
        "palette": "golden-luxury",
        "fonts": "serif-editorial",
        "decoration": "gold-trim",
        "layout": "centered",
    },
    "vibrant-startup": {
        "palette": "neon-gradient",
        "fonts": "bold-sans",
        "decoration": "gradient-bar",
        "layout": "grid-2x2",
    },
    "nature-calm": {
        "palette": "forest-green",
        "fonts": "humanist-sans",
        "decoration": "circle-accent",
        "layout": "sidebar-left",
    },
    "ink-wash": {"palette": "ink-wash", "fonts": "ink-wash-serif", "decoration": "brush-stroke", "layout": "ink-wash"},
    "chinese-traditional": {
        "palette": "ink-wash",
        "fonts": "chinese-calligraphy",
        "decoration": "seal-stamp",
        "layout": "ink-wash",
    },
    "zen": {"palette": "zen-minimal", "fonts": "ink-wash-serif", "decoration": "no-decoration", "layout": "centered"},
    "sci": {"palette": "sci-paper", "fonts": "sci-serif", "decoration": "sci-grid", "layout": "sci-dense"},
    "neon": {"palette": "cyber-neon-pro", "fonts": "tech-display", "decoration": "neon-glow", "layout": "wide-cards"},
}

_MOOD_PRESET_RECOMMENDATIONS: dict[str, tuple[str, ...]] = {
    "tech": ("dark-tech", "neon", "sci"),
    "dark": ("dark-tech", "neon", "professional"),
    "elegant": ("warm-elegant", "zen", "chinese-traditional"),
    "luxury": ("warm-elegant", "zen", "professional"),
    "vibrant": ("vibrant-startup", "neon", "dark-tech"),
    "nature": ("nature-calm", "zen", "warm-elegant"),
    "ink-wash": ("ink-wash", "chinese-traditional", "zen"),
    "sci": ("sci", "dark-tech", "professional"),
}

_DEFAULT_PRESET_RECOMMENDATIONS = ("professional", "vibrant-startup", "warm-elegant")


class ThemeComposer:
    """Compose infinite theme combinations from design atoms.

    When ui-ux-pro-max is available, uses its search engine to find
    product-specific colors, typography, and styles from the CSV databases.
    Falls back to the hardcoded atoms above when the package is absent.
    """

    def compose(
        self,
        style: str | None = None,
        palette: str | None = None,
        fonts: str | None = None,
        decoration: str | None = None,
        layout: str | None = None,
        mood: str | None = None,
        seed: int | None = None,
        query: str | None = None,
        text_effect_preset: str | None = None,
        image_effect: str | None = None,
    ) -> dict[str, Any]:
        requested = {
            "style": style,
            "palette": palette,
            "fonts": fonts,
            "decoration": decoration,
            "layout": layout,
            "mood": mood,
            "seed": seed,
            "query": query,
            "text_effect_preset": text_effect_preset,
            "image_effect": image_effect,
        }
        if style and style in _PRESET_ATOM_MAP:
            atoms = _PRESET_ATOM_MAP[style]
            palette = palette or atoms.get("palette")
            fonts = fonts or atoms.get("fonts")
            decoration = decoration or atoms.get("decoration")
            layout = layout or atoms.get("layout")

        detected_moods = self._detect_moods(style or "") if style else []
        if mood:
            detected_moods = [mood] + detected_moods
        if not detected_moods:
            detected_moods = ["professional"]

        rng = random.Random(seed) if seed is not None else random.Random()

        ux_colors = None
        ux_typo = None
        ux_style_name = ""
        ux_style_effects = ""
        ux_anti_patterns = ""

        search_query = query or style or " ".join(detected_moods[:2])

        if _ux_available() and not palette and not fonts:
            ux_colors = self._ux_find_colors(search_query, detected_moods, rng)
            ux_typo = self._ux_find_typography(search_query, detected_moods, rng)
            ux_style_info = self._ux_find_style(search_query, detected_moods)
            if ux_style_info:
                ux_style_name = ux_style_info.get("name", "")
                ux_style_effects = ux_style_info.get("effects", "")
                ux_anti_patterns = ux_style_info.get("anti_patterns", "")

        fallbacks: list[dict[str, str]] = []
        if ux_colors:
            colors = ux_colors
            resolved_palette = "external"
        else:
            p = palette or self._pick_from_mood(detected_moods, _MOOD_PALETTE_MAP, rng)
            resolved_palette = p if p in COLOR_PALETTES else "ocean-blue"
            if resolved_palette != p:
                fallbacks.append({"field": "palette", "requested": str(p), "used": resolved_palette})
            colors = dict(COLOR_PALETTES[resolved_palette])

        if ux_typo:
            typo = ux_typo
            resolved_fonts = "external"
        else:
            f = fonts or self._pick_from_mood(detected_moods, _MOOD_FONT_MAP, rng)
            resolved_fonts = f if f in FONT_PAIRS else "modern-sans"
            if resolved_fonts != f:
                fallbacks.append({"field": "fonts", "requested": str(f), "used": resolved_fonts})
            typo = dict(FONT_PAIRS[resolved_fonts])

        d = decoration or self._pick_from_mood(detected_moods, _MOOD_DECORATION_MAP, rng)
        lay_atom = layout or self._pick_from_mood(detected_moods, _MOOD_LAYOUT_MAP, rng)

        resolved_decoration = d if d in DECORATION_STYLES else "accent-bar"
        if resolved_decoration != d:
            fallbacks.append({"field": "decoration", "requested": str(d), "used": resolved_decoration})
        resolved_layout = lay_atom if lay_atom in LAYOUT_VARIANTS else "standard"
        if resolved_layout != lay_atom:
            fallbacks.append({"field": "layout", "requested": str(lay_atom), "used": resolved_layout})
        deco = dict(DECORATION_STYLES[resolved_decoration])
        lay = dict(LAYOUT_VARIANTS[resolved_layout])

        te = text_effect_preset or self._pick_effect_from_mood(detected_moods, _MOOD_TEXT_EFFECT_MAP, rng)
        ie = image_effect or self._pick_effect_from_mood(detected_moods, _MOOD_IMAGE_EFFECT_MAP, rng)

        dark_mode = self._is_dark(colors)

        # Keep the existing flat color dictionary for backward compatibility,
        # while exposing a stable semantic vocabulary for downstream renderers.
        semantic_roles = {
            "background": colors.get("background", "#FFFFFF"),
            "surface": colors.get("card", colors.get("muted", "#F5F5F5")),
            "ink": colors.get("foreground", colors.get("text_dark", "#111827")),
            "muted": colors.get("muted-foreground", colors.get("text_muted", "#6B7280")),
            "accent": colors.get("accent", colors.get("primary", "#1D78FA")),
            "accent-secondary": colors.get("secondary", colors.get("primary", "#1D78FA")),
            # A palette may deliberately avoid conventional green/orange.
            # Preserve that visual language when it has no dedicated semantic
            # status colors instead of injecting fixed renderer colors.
            "success": colors.get("success", colors.get("accent", colors.get("primary", "#1D78FA"))),
            "warning": colors.get("warning", colors.get("secondary", colors.get("accent", "#8B5CF6"))),
            "danger": colors.get("destructive", "#EF4444"),
            "border": colors.get("border", "#E5E7EB"),
            "data-series-1": colors.get("primary", "#1D78FA"),
            "data-series-2": colors.get("accent", "#8B5CF6"),
        }

        result = {
            "name": f"{ux_style_name or style or 'custom'}+{resolved_decoration}+{resolved_layout}",
            "colors": colors,
            "typography": typo,
            "dark_mode": dark_mode,
            "decoration": deco,
            "layout_variant": lay,
            "text_effect_preset": te,
            "image_effect": ie,
            "semantic_roles": semantic_roles,
            "source": {
                "requested": requested,
                "resolved": {
                    "style": style,
                    "palette": resolved_palette,
                    "fonts": resolved_fonts,
                    "decoration": resolved_decoration,
                    "layout": resolved_layout,
                    "mood": detected_moods,
                },
                "seed": seed,
                "resolver": "external" if ux_colors or ux_typo else "local",
                "package_version": _package_version(),
                "fallbacks": fallbacks,
                "warnings": [],
            },
            "atoms": {
                "palette": resolved_palette,
                "fonts": resolved_fonts,
                "decoration": resolved_decoration,
                "layout": resolved_layout,
                "moods": detected_moods,
            },
        }

        if ux_style_effects:
            result["style_effects"] = ux_style_effects
        if ux_anti_patterns:
            result["anti_patterns"] = ux_anti_patterns
        if ux_style_name:
            result["style_name"] = ux_style_name

        return result

    def recommend_styles(self, query: str = "", top_k: int = 3) -> list[dict[str, str]]:
        """Return distinct, directly usable preset recommendations for a topic.

        Results contain a ``style`` key suitable for :func:`generate_ppt` plus
        the exact atoms it expands to.  This gives an LLM explicit choices
        rather than relying on the generic ``professional`` fallback.
        """
        if top_k < 1:
            return []

        candidates: list[str] = []
        for mood in self._detect_moods(query):
            candidates.extend(_MOOD_PRESET_RECOMMENDATIONS.get(mood, ()))
        candidates.extend(_DEFAULT_PRESET_RECOMMENDATIONS)

        selected: list[dict[str, str]] = []
        seen: set[str] = set()
        for style in candidates:
            if style in seen:
                continue
            seen.add(style)
            selected.append({"style": style, **_PRESET_ATOM_MAP[style]})
            if len(selected) == top_k:
                break
        return selected

    def _ux_find_colors(self, query: str, moods: list[str], rng: random.Random) -> dict[str, str] | None:
        try:
            results = _ux_search_color(query, 3)
            if not results:
                for mood in moods:
                    results = _ux_search_color(mood, 2)
                    if results:
                        break
            if results:
                best = results[0]
                mapped = {}
                _KEY_MAP = {
                    "Primary": "primary",
                    "On Primary": "on-primary",
                    "Secondary": "secondary",
                    "On Secondary": "on-secondary",
                    "Accent": "accent",
                    "On Accent": "on-accent",
                    "Background": "background",
                    "Foreground": "foreground",
                    "Card": "card",
                    "Card Foreground": "card-foreground",
                    "Muted": "muted",
                    "Muted Foreground": "muted-foreground",
                    "Border": "border",
                    "Destructive": "destructive",
                    "On Destructive": "on-destructive",
                    "Ring": "ring",
                }
                for csv_key, our_key in _KEY_MAP.items():
                    val = best.get(csv_key, "")
                    if val:
                        mapped[our_key] = val
                if mapped.get("primary"):
                    return mapped
        except Exception:
            pass
        return None

    def _ux_find_typography(self, query: str, moods: list[str], rng: random.Random) -> dict[str, str] | None:
        try:
            results = _ux_search_typography(query, 3)
            if not results:
                for mood in moods:
                    results = _ux_search_typography(mood, 2)
                    if results:
                        break
            if results:
                best = results[0]
                heading = best.get("Heading Font", "")
                body = best.get("Body Font", "")
                if heading or body:
                    return {
                        "heading": heading or "Inter",
                        "body": body or "Inter",
                        "mood": best.get("Mood/Style Keywords", ""),
                        "best_for": best.get("Best For", ""),
                    }
        except Exception:
            pass
        return None

    def _ux_find_style(self, query: str, moods: list[str]) -> dict[str, str] | None:
        try:
            results = _ux_search_style(query, 3)
            if not results:
                for mood in moods:
                    results = _ux_search_style(mood, 2)
                    if results:
                        break
            if results:
                best = results[0]
                return {
                    "name": best.get("Style Category", ""),
                    "effects": best.get("Effects & Animation", ""),
                    "keywords": best.get("Keywords", ""),
                    "best_for": best.get("Best For", ""),
                    "dark_mode": best.get("Dark Mode ✓", ""),
                    "light_mode": best.get("Light Mode ✓", ""),
                }
        except Exception:
            pass
        return None

    def _detect_moods(self, text: str) -> list[str]:
        text_lower = " " + text.lower() + " "
        moods = []
        mood_words = {
            "professional": ["professional", "corporate", "business", "formal", "专业", "企业", "商务", "正式"],
            "tech": [
                "tech",
                "technology",
                "software",
                "developer",
                "engineering",
                "技术",
                "科技",
                "软件",
                "开发",
                "工程",
                "人工智能",
                "智能",
            ],
            "dark": ["dark", "cyberpunk", "noir", "shadow"],
            "warm": ["warm", "cozy", "inviting", "friendly"],
            "elegant": ["elegant", "refined", "sophisticated", "graceful", "优雅", "精致", "高级", "雅致"],
            "luxury": ["luxury", "premium", "exclusive", "opulent", "奢侈", "奢华", "高定", "高端", "精品"],
            "vibrant": ["vibrant", "energetic", "dynamic", "bold"],
            "startup": ["startup", "launch", "founder"],
            "nature": ["nature", "organic", "natural", "earthy"],
            "calm": ["calm", "serene", "peaceful", "tranquil"],
            "minimal": ["minimal", "minimalist", "clean", "simple"],
            "bold": ["bold", "daring", "fearless", "strong"],
            "fresh": ["fresh", "modern", "new", "innovative"],
            "industrial": ["industrial", "manufacturing", "factory"],
            "fintech": ["fintech", "finance", "banking", "trading"],
            "health": ["health", "medical", "healthcare", "wellness"],
            "education": ["education", "learning", "academic", "university"],
            "sustainability": ["sustainability", "sustainable", "esg"],
            "creative": ["creative", "design", "artistic"],
            "international": ["international", "global", "multinational", "cross-border"],
            "cream": ["cream", "ivory", "beige", "off-white"],
            "frosted": ["frosted", "frost", "glassmorphism", "glassmorphic", "translucent"],
            "mckinsey": ["mckinsey"],
            "consulting": [
                "consulting",
                "consultant",
                "bcg",
                "bain",
                "deloitte",
                "accenture",
                "pwc",
                "kpmg",
                "strategy&",
            ],
            "pastel": ["pastel", "soft-toned", "light-toned", "candy-colored"],
            "retro": ["retro", "vintage", "nostalgic", "throwback", "mid-century"],
            "government": ["government", "gov", "public-sector", "civic", "municipal", "federal"],
            "legal": ["legal", "law", "lawfirm", "attorney", "compliance", "regulatory"],
            "pharma": ["pharma", "pharmaceutical", "biotech", "biopharma", "clinical", "drug"],
            "realestate": ["real estate", "realestate", "property", "housing", "mortgage", "reit"],
            "automotive": ["automotive", "auto", "car", "vehicle", "motor"],
            "aviation": ["aviation", "aerospace", "airline", "aircraft", "flight"],
            "energy": ["energy", "oil", "gas", "petroleum", "renewable", "solar", "wind", "power-generation"],
            "telecom": ["telecom", "telecommunication", "5g", "broadband", "wireless", "carrier"],
            "logistics": ["logistics", "supply-chain", "shipping", "freight", "warehouse", "fulfillment"],
            "ink-wash": ["ink-wash", "ink wash", "水墨", "国风", "古典", "毛笔", "山水", "写意", "宣纸"],
            "chinese-traditional": [
                "chinese-traditional",
                "chinese traditional",
                "国风",
                "古典",
                "传统",
                "中式",
                "古风",
            ],
            "zen": ["zen", "wabi-sabi", "禅意", "侘寂", "极简东方", "和风"],
            "sci": ["sci", "science", "scientific", "科研", "学术", "论文", "期刊"],
            "neon": ["neon", "霓虹", "赛博", "cyberpunk", "发光"],
        }
        for mood, words in mood_words.items():
            if any(self._keyword_matches(text_lower, word) for word in words) and mood not in moods:
                moods.append(mood)

        industry_hints = {
            "investor": "fintech",
            "pitch": "startup",
            "fundrais": "startup",
            "saas": "tech",
            "ai ": "tech",
            " ml ": "tech",
            "cloud": "tech",
            "luxury": "luxury",
            "brand": "elegant",
            "consult": "consulting",
            "mckinsey": "mckinsey",
            "pharma": "pharma",
            "biotech": "pharma",
            "regul": "legal",
            "compliance": "legal",
            "supply chain": "logistics",
            "shipping": "logistics",
            "水墨": "ink-wash",
            "国风": "ink-wash",
            "古典": "ink-wash",
            "禅意": "zen",
            "侘寂": "zen",
            "科研": "sci",
            "学术": "sci",
            "论文": "sci",
            "霓虹": "neon",
            "赛博": "neon",
        }
        for hint, mood in industry_hints.items():
            if hint in text_lower and mood not in moods:
                moods.append(mood)
        return moods

    @staticmethod
    def _keyword_matches(text: str, keyword: str) -> bool:
        """Match word-delimited Latin keywords and substring-oriented CJK terms."""
        if any("\u4e00" <= char <= "\u9fff" for char in keyword):
            return keyword in text
        return f" {keyword} " in text

    def _pick_from_mood(self, moods: list[str], mood_map: dict, rng: random.Random) -> str:
        for mood in moods:
            options = mood_map.get(mood, [])
            if options:
                return rng.choice(options)
        all_options = [v for v in mood_map.values() if v]
        if all_options:
            chosen_list = rng.choice(all_options)
            if chosen_list:
                return rng.choice(chosen_list)
        if mood_map:
            return list(mood_map.keys())[0]
        return "standard"

    def _pick_effect_from_mood(self, moods: list[str], mood_map: dict, rng: random.Random) -> str | None:
        for mood in moods:
            options = mood_map.get(mood, [])
            non_none = [o for o in options if o is not None]
            if non_none:
                return rng.choice(non_none)
        return None

    def _is_dark(self, colors: dict[str, str]) -> bool:
        bg = colors.get("background", "#FFFFFF")
        r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    @staticmethod
    def available_palettes() -> list[str]:
        return list(COLOR_PALETTES.keys())

    @staticmethod
    def available_fonts() -> list[str]:
        return list(FONT_PAIRS.keys())

    @staticmethod
    def available_decorations() -> list[str]:
        return list(DECORATION_STYLES.keys())

    @staticmethod
    def available_layouts() -> list[str]:
        return list(LAYOUT_VARIANTS.keys())

    @staticmethod
    def available_presets() -> list[str]:
        return list(_PRESET_ATOM_MAP.keys())

    @staticmethod
    def combination_count() -> int:
        return len(COLOR_PALETTES) * len(FONT_PAIRS) * len(DECORATION_STYLES) * len(LAYOUT_VARIANTS)


def recommend_styles(query: str = "", top_k: int = 3) -> list[dict[str, str]]:
    """Return preset choices suitable for ``generate_ppt(style=...)``.

    This module-level helper avoids requiring callers to instantiate
    :class:`ThemeComposer` just to obtain deterministic style suggestions.
    """
    return ThemeComposer().recommend_styles(query=query, top_k=top_k)
