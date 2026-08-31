"""Renderer-neutral BuildSpec executor.

Build supplies the content composition: reusable component references or
inline recipes with exact geometry, visual properties, data, and z-order.
This module renders that stable, generic vocabulary into editable PPTX objects.
When a VI template is used, its adapter supplies constraints and fixed visual
layers only; it does not choose the content composition.  Keeping this boundary
small prevents template-specific branches from leaking into Build Core.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def render_build_spec(spec: Mapping[str, Any], presentation: Any, context: Mapping[str, Any]) -> Any:
    """Render a component BuildSpec and return the newly created slide."""
    if spec.get("kind") != "BuildSpec":
        raise ValueError("renderer requires a BuildSpec")
    if spec.get("render_strategy") != "components":
        raise ValueError("Build Core only renders component BuildSpecs")

    from pptx_designer.renderer.theme_context import set_slide_theme

    slide = presentation.slides.add_slide(_blank_layout(presentation))
    for placeholder in list(slide.shapes):
        if getattr(placeholder, "is_placeholder", False):
            placeholder.element.getparent().remove(placeholder.element)
    set_slide_theme(slide, context)
    _apply_fixed_base(spec.get("fixed_base"), presentation, slide)
    components = context.get("components", {})
    for instance in spec.get("components", []):
        inline_recipe = instance.get("recipe")
        if isinstance(inline_recipe, Mapping):
            component = inline_recipe
        else:
            component_id = str(instance.get("component_id"))
            component = components.get(component_id, {})
            if not isinstance(component, Mapping):
                raise ValueError(f"unknown component recipe: {component_id}")
        _render_component(slide, component, instance.get("data"), context)
    return slide


def _render_component(slide: Any, component: Mapping[str, Any], data: Any, context: Mapping[str, Any]) -> None:
    kind = str(component.get("kind", ""))
    bounds = _bounds(component.get("bounds"), kind)
    colors = context.get("colors", {})
    if kind in {"text", "multiline_text"}:
        from pptx_designer.tools.text import multiline, text

        value = _value(data, "text", "value", default="")
        kwargs = {
            **bounds,
            "font_size": component.get("font_size", 18),
            "bold": bool(component.get("bold", False)),
            "color": component.get("color", "text_dark"),
            "align": component.get("align", "left"),
            "font_name": component.get("font_name"),
        }
        if kind == "multiline_text":
            lines = value if isinstance(value, list) else str(value).splitlines() or [""]
            multiline(slide, **kwargs, lines=lines)
        else:
            text(slide, **kwargs, txt=str(value))
        return
    if kind in {"photo_panel", "image", "image_panel"}:
        from pptx_designer.tools.images import cover_image

        cover_image(slide, **bounds, image_path=_asset_path(data))
        return
    if kind in {"color_panel", "rule", "rect", "shape"}:
        from pptx_designer.tools.shapes import rect, shape

        fill = component.get("fill", colors.get("surface", "#FFFFFF"))
        if kind == "shape" and component.get("shape_type"):
            shape(slide, component["shape_type"], **bounds, fill=fill, line=component.get("line"))
        else:
            rect(slide, **bounds, fill=fill, line=component.get("line"))
        return
    if kind == "kpi_card":
        from pptx_designer.tools.cards import kpi_card

        payload = data if isinstance(data, Mapping) else {}
        kpi_card(slide, **bounds, number=str(payload.get("number", "")), label=str(payload.get("label", "")),
                 trend=str(payload.get("trend", "")), trend_up=bool(payload.get("trend_up", True)))
        return
    if kind in {"highlight_cards", "card_group"}:
        from pptx_designer.tools.cards import highlight_cards

        cards = data if isinstance(data, list) else []
        highlight_cards(slide, bounds["left"], bounds["top"], cards,
                        total_width=bounds["width"])
        return
    if kind == "code_block":
        from pptx_designer.tools.cards import code_block

        payload = data if isinstance(data, Mapping) else {"lines": data or []}
        code_block(slide, **bounds, lines=payload.get("lines", []), language=payload.get("language", "text"))
        return
    if kind == "bar_chart":
        from pptx_designer.tools.charts import bar_chart

        payload = data if isinstance(data, Mapping) else {"data": data or {}}
        bar_chart(slide, bounds["left"], bounds["top"], payload.get("data", payload),
                  max_width=bounds["width"], bar_height=payload.get("bar_height", 0.3))
        return
    if kind == "comparison_bars":
        from pptx_designer.tools.charts import comparison_bars

        comparison_bars(slide, bounds["left"], bounds["top"], data or {}, max_width=bounds["width"])
        return
    if kind == "donut_chart":
        from pptx_designer.tools.charts import donut_chart

        payload = data if isinstance(data, Mapping) else {}
        donut_chart(slide, bounds["left"] + bounds["width"] / 2,
                    bounds["top"] + bounds["height"] / 2,
                    min(bounds["width"], bounds["height"]) / 2,
                    payload.get("inner_radius", 0.45), payload.get("sectors", []))
        return
    if kind == "native_chart":
        from pptx_designer.tools.charts import native_chart

        payload = data if isinstance(data, Mapping) else {}
        native_chart(slide, **bounds, chart_type=payload.get("chart_type", "bar"),
                     categories=payload.get("categories"), series=payload.get("series"),
                     style=payload.get("style"))
        return
    if kind in {"section_divider", "hero_slide", "cta_slide"}:
        from pptx_designer.tools.cards import cta_slide, hero_slide, section_divider

        payload = data if isinstance(data, Mapping) else {}
        if kind == "section_divider":
            section_divider(slide, payload.get("number", ""), payload.get("title", ""))
        elif kind == "hero_slide":
            hero_slide(slide, payload.get("title", ""), payload.get("subtitle", ""))
        else:
            cta_slide(slide, payload.get("title", ""), payload.get("subtitle", ""))
        return
    raise ValueError(f"unsupported BuildSpec component kind: {kind}")


def _bounds(value: Any, component: str) -> dict[str, float]:
    if not isinstance(value, Mapping) or any(key not in value for key in ("left", "top", "width", "height")):
        raise ValueError(f"component {component} has incomplete render bounds")
    return {key: float(value[key]) for key in ("left", "top", "width", "height")}


def _value(data: Any, *keys: str, default: Any = None) -> Any:
    if isinstance(data, Mapping):
        for key in keys:
            if key in data:
                return data[key]
    return data if data is not None else default


def _asset_path(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("path") or value.get("url")
    if not isinstance(value, str) or not value:
        raise ValueError("BuildSpec image component requires a path or URL")
    return value


def _blank_layout(presentation: Any) -> Any:
    for layout in presentation.slide_layouts:
        if not layout.placeholders:
            return layout
    return presentation.slide_layouts[0]


def _apply_fixed_base(fixed_base: Any, presentation: Any, target_slide: Any) -> None:
    if not isinstance(fixed_base, Mapping) or fixed_base.get("status") == "review_required":
        return
    if fixed_base.get("safe_to_clone") is False:
        raise ValueError(f"unsafe fixed base: {fixed_base.get('id', 'unknown')}")
    reference_slide = fixed_base.get("reference_slide")
    if reference_slide is None:
        return
    if "fixed_shape_indices" not in fixed_base:
        raise ValueError(
            f"fixed base {fixed_base.get('id', 'unknown')} requires explicit fixed_shape_indices"
        )
    from pptx_designer.enterprise.prototype import copy_slide_shapes

    reference_slide = int(reference_slide)
    if not 1 <= reference_slide <= len(presentation.slides):
        raise ValueError(f"fixed base reference_slide is unavailable: {reference_slide}")
    copied = copy_slide_shapes(
        presentation,
        presentation.slides[reference_slide - 1],
        target_slide,
        fixed_base.get("fixed_shape_indices"),
        exclude_indices=fixed_base.get("exclude_shape_indices"),
    )
    # Keep the result observable for delivery reports without changing the
    # caller's original context object.
    if isinstance(fixed_base, dict):
        fixed_base["applied_shape_names"] = copied


__all__ = ["render_build_spec"]
