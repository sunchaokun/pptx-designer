"""Slide search adapter — layout and typography search."""

from __future__ import annotations

from typing import Any


def layout_for_goal(goal: str) -> dict[str, Any]:
    """Get layout for a slide goal.

    Args:
        goal: Slide goal (e.g., "hook", "content", "cta")

    Returns:
        Layout configuration dict
    """
    layouts = {
        "hook": {"layout": "hero-image", "sidebar": False},
        "content": {"layout": "standard", "sidebar": True},
        "features": {"layout": "grid-2x2", "sidebar": False},
        "data": {"layout": "chart-focus", "sidebar": False},
        "code": {"layout": "sidebar-left", "sidebar": True},
        "cta": {"layout": "hero-image", "sidebar": False},
    }
    return layouts.get(goal, layouts["content"])


def typography_for_slide(goal: str) -> str:
    """Get typography preset for a slide goal.

    Args:
        goal: Slide goal

    Returns:
        Typography preset name
    """
    presets = {
        "hook": "mckinsey",
        "content": "professional",
        "features": "professional",
        "data": "professional",
        "code": "cyberpunk",
        "cta": "mckinsey",
    }
    return presets.get(goal, "professional")


def color_for_emotion(emotion: str) -> str:
    """Get color palette for an emotion.

    Args:
        emotion: Emotion keyword

    Returns:
        Color palette name
    """
    palettes = {
        "professional": "ocean-blue",
        "tech": "cyber-neon",
        "warm": "warm-sunset",
        "elegant": "golden-luxury",
        "creative": "vibrant-pop",
    }
    return palettes.get(emotion, "ocean-blue")


def background_config(goal: str) -> dict[str, Any]:
    """Get background configuration for a slide goal.

    Args:
        goal: Slide goal

    Returns:
        Background config dict
    """
    configs = {
        "hook": {"type": "image", "overlay": True},
        "content": {"type": "solid", "color": "#FFFFFF"},
        "features": {"type": "gradient", "direction": "top"},
        "data": {"type": "solid", "color": "#F8FAFC"},
        "code": {"type": "solid", "color": "#1E1E1E"},
        "cta": {"type": "gradient", "direction": "center"},
    }
    return configs.get(goal, configs["content"])


def full_bleed(goal: str) -> bool:
    """Check if a slide should use full-bleed layout.

    Args:
        goal: Slide goal

    Returns:
        True if full-bleed
    """
    return goal in ("hook", "cta")


def pattern_break(goal: str) -> bool:
    """Check if a slide should break the visual pattern.

    Args:
        goal: Slide goal

    Returns:
        True if should break pattern
    """
    return goal in ("section", "data")
