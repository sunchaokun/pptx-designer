"""Chart builder — native PowerPoint chart creation."""

from __future__ import annotations

from typing import Any

from pptx.chart.data import ChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches


def _rgb(value: str):
    return RGBColor.from_string(value.lstrip("#"))


class ChartBuilder:
    """Creates native PowerPoint charts."""

    def __init__(self, brand_colors: dict | None = None):
        self._colors = brand_colors or {}

    def build(
        self,
        slide: Any,
        config: dict,
        position: dict,
        brand_colors: dict | None = None,
        brand_fonts: dict | None = None,
    ) -> Any:
        """Build a native editable PowerPoint chart from the public config."""
        chart_type = config.get("type", config.get("chart_type", "bar"))
        type_map = {
            "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "bar_stacked": XL_CHART_TYPE.COLUMN_STACKED,
            "bar_100": XL_CHART_TYPE.COLUMN_STACKED_100,
            "bar_horizontal": XL_CHART_TYPE.BAR_CLUSTERED,
            "bar_horizontal_stacked": XL_CHART_TYPE.BAR_STACKED,
            "bar_horizontal_100": XL_CHART_TYPE.BAR_STACKED_100,
            "line": XL_CHART_TYPE.LINE,
            "line_markers": XL_CHART_TYPE.LINE_MARKERS,
            "line_stacked": XL_CHART_TYPE.LINE_STACKED,
            "line_stacked_100": XL_CHART_TYPE.LINE_STACKED_100,
            "pie": XL_CHART_TYPE.PIE,
            "pie_exploded": XL_CHART_TYPE.PIE_EXPLODED,
            "doughnut": XL_CHART_TYPE.DOUGHNUT,
            "doughnut_exploded": XL_CHART_TYPE.DOUGHNUT_EXPLODED,
            "area": XL_CHART_TYPE.AREA,
            "area_stacked": XL_CHART_TYPE.AREA_STACKED,
            "area_stacked_100": XL_CHART_TYPE.AREA_STACKED_100,
            "radar": XL_CHART_TYPE.RADAR,
            "radar_markers": XL_CHART_TYPE.RADAR_MARKERS,
            "scatter": XL_CHART_TYPE.XY_SCATTER,
            "scatter_lines": XL_CHART_TYPE.XY_SCATTER_LINES,
            "scatter_smooth": XL_CHART_TYPE.XY_SCATTER_SMOOTH,
        }
        if chart_type not in type_map:
            raise ValueError(f"Unsupported native chart type: {chart_type!r}")

        categories = config.get("categories") or []
        series = config.get("series") or []
        if chart_type.startswith("scatter"):
            data = XyChartData()
            for item in series:
                xy_series = data.add_series(item.get("name", "Data"))
                for point in item.get("values", []):
                    if len(point) < 2:
                        raise ValueError(f"Scatter series points require [x, y] values: {point!r}")
                    xy_series.add_data_point(point[0], point[1])
        else:
            data = ChartData()
            data.categories = categories
            for item in series:
                data.add_series(item.get("name", "Data"), item.get("values", []))

        p = dict(position)
        chart = slide.shapes.add_chart(
            type_map[chart_type],
            Inches(p["x"]),
            Inches(p["y"]),
            Inches(p["width"]),
            Inches(p["height"]),
            data,
        ).chart
        style = config.get("style") or {}
        chart.chart_style = style.get("chart_style", 2)
        chart.has_legend = bool(style.get("show_legend", False))
        if chart.has_legend and style.get("legend_position"):
            from pptx.enum.chart import XL_LEGEND_POSITION

            legend_map = {
                "right": XL_LEGEND_POSITION.RIGHT,
                "left": XL_LEGEND_POSITION.LEFT,
                "top": XL_LEGEND_POSITION.TOP,
                "bottom": XL_LEGEND_POSITION.BOTTOM,
            }
            chart.legend.position = legend_map.get(style["legend_position"], XL_LEGEND_POSITION.RIGHT)
        if chart_type.startswith("doughnut") or chart_type.startswith("pie"):
            plot = chart.plots[0]
            colors = style.get("color_scheme") or list((brand_colors or self._colors).values())
            if colors:
                for idx, point in enumerate(plot.series[0].points):
                    point.format.fill.solid()
                    point.format.fill.fore_color.rgb = _rgb(colors[idx % len(colors)])
            if style.get("show_labels"):
                plot.has_data_labels = True
                labels = plot.data_labels
                labels.show_category_name = bool(style.get("show_category_name", True))
                labels.show_percentage = bool(style.get("show_percentage", True))
                labels.show_value = bool(style.get("show_value", False))
        return chart

    def add_bar_chart(
        self, slide: Any, left: float, top: float, width: float, height: float, categories: list, series: list, **kwargs
    ) -> Any:
        """Add bar chart."""
        pass

    def add_line_chart(
        self, slide: Any, left: float, top: float, width: float, height: float, categories: list, series: list, **kwargs
    ) -> Any:
        """Add line chart."""
        pass

    def add_pie_chart(
        self, slide: Any, left: float, top: float, width: float, height: float, categories: list, values: list, **kwargs
    ) -> Any:
        """Add pie chart."""
        pass
