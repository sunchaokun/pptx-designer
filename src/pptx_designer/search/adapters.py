"""Search adapters — bridge to design knowledge base.

Provides search functions for colors, typography, and styles.
"""

from __future__ import annotations

from typing import Any


def is_available() -> bool:
    """Check if search adapters are available."""
    return True


def search_color(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search color palettes by query.

    Args:
        query: Search query (e.g., "technology blue gradient")
        top_k: Number of results to return

    Returns:
        List of matching color palettes
    """
    from pptx_designer.data.colors import PALETTES

    results = []
    query_lower = query.lower()
    for name, palette in PALETTES.items():
        if query_lower in name.lower():
            results.append({"name": name, **palette})
        if len(results) >= top_k:
            break
    return results


def search_typography(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search font pairs by query.

    Args:
        query: Search query (e.g., "modern sans-serif")
        top_k: Number of results to return

    Returns:
        List of matching font pairs
    """
    from pptx_designer.data.typography import TYPOGRAPHY

    results = []
    query_lower = query.lower()
    for name, fonts in TYPOGRAPHY.items():
        if query_lower in name.lower():
            results.append({"name": name, **fonts})
        if len(results) >= top_k:
            break
    return results


def search_style(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search style presets by query.

    Args:
        query: Search query (e.g., "minimalist clean")
        top_k: Number of results to return

    Returns:
        List of matching style presets
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
