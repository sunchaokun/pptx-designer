"""UI/UX adapter — bridge to design knowledge base.

Provides search functions for design patterns, landing pages, and product types.
"""

from __future__ import annotations

from typing import Any


def is_available() -> bool:
    """Check if UI/UX adapter is available."""
    return True


def search_design(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search design patterns.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        List of matching design patterns
    """
    from pptx_designer.data.styles import STYLES

    results = []
    query_lower = query.lower()
    for name, style in STYLES.items():
        if query_lower in name.lower():
            results.append({"name": name, **style})
        if len(results) >= top_k:
            break
    return results


def search_landing(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search landing page patterns.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        List of matching landing page patterns
    """
    return search_design(query, top_k)


def get_design_system(query: str) -> dict[str, Any]:
    """Get design system for a query.

    Args:
        query: Search query

    Returns:
        Design system dict with colors, fonts, etc.
    """
    from pptx_designer.data.colors import PALETTES
    from pptx_designer.data.typography import TYPOGRAPHY

    # Simple keyword matching
    colors = {}
    fonts = {}
    query_lower = query.lower()

    for name, palette in PALETTES.items():
        if any(kw in name.lower() for kw in query_lower.split()):
            colors = palette
            break

    for name, font_pair in TYPOGRAPHY.items():
        if any(kw in name.lower() for kw in query_lower.split()):
            fonts = font_pair
            break

    return {"colors": colors, "fonts": fonts}


def search_style(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search style presets.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        List of matching styles
    """
    from pptx_designer.data.styles import STYLES

    results = []
    query_lower = query.lower()
    for name, style in STYLES.items():
        if query_lower in name.lower():
            results.append({"name": name, **style})
        if len(results) >= top_k:
            break
    return results
