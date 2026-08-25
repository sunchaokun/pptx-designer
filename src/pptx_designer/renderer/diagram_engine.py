"""Diagram engine — registry-based diagram rendering."""

from __future__ import annotations

from typing import Any


class DiagramEngine:
    """Registry-based diagram renderer."""

    def __init__(self):
        self._registry = {}

    def register(self, name: str, renderer: Any) -> None:
        """Register a diagram renderer."""
        self._registry[name] = renderer

    def render(self, slide: Any, diagram_type: str, data: dict, region: Any, style: Any = None) -> None:
        """Render a diagram."""
        renderer = self._registry.get(diagram_type)
        if renderer:
            renderer.render(slide, data, region, style)
