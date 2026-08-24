"""Chart builder — native PowerPoint chart creation."""

from __future__ import annotations

from typing import Any


class ChartBuilder:
    """Creates native PowerPoint charts."""

    def __init__(self, brand_colors: dict | None = None):
        self._colors = brand_colors or {}

    def add_bar_chart(self, slide: Any, left: float, top: float,
                      width: float, height: float, categories: list,
                      series: list, **kwargs) -> Any:
        """Add bar chart."""
        pass

    def add_line_chart(self, slide: Any, left: float, top: float,
                       width: float, height: float, categories: list,
                       series: list, **kwargs) -> Any:
        """Add line chart."""
        pass

    def add_pie_chart(self, slide: Any, left: float, top: float,
                      width: float, height: float, categories: list,
                      values: list, **kwargs) -> Any:
        """Add pie chart."""
        pass
