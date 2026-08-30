"""Versioned design context and preflight rules for VI Build Mode.

This module deliberately owns no rendering primitives.  It normalizes the
shared theme/template contract and gives Build Mode a single, auditable place
to validate assets, archetypes, slots, and template locks before a page is
assembled with public helpers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

DESIGN_CONTEXT_SCHEMA_VERSION = "1.0"

_DEFAULT_CONTEXT: dict[str, Any] = {
    "schema_version": DESIGN_CONTEXT_SCHEMA_VERSION,
    "source": {"kind": "theme", "warnings": []},
    "colors": {},
    "semantic_roles": {},
    "typography": {},
    "decoration": {},
    "layout_variant": {},
    "dark_mode": False,
    "assets": {
        "logo": {},
        "references": [],
        "image_grammar": {
            "required": False,
            "subjects": [],
            "treatment": {},
            "crop": {},
            "min_area_ratio": None,
            "safe_zones": [],
            "reuse_policy": "allow",
        },
    },
    "components": {},
    "archetypes": [],
    "content_slots": [],
    "locks": [],
    "acceptance": {"must_coverage": [], "thresholds": {}},
    "diagnostics": {"warnings": [], "unknown_fields": []},
}


def _merge_defaults(value: Any, default: Any) -> Any:
    if isinstance(default, Mapping):
        result = deepcopy(dict(default))
        if isinstance(value, Mapping):
            for key, item in value.items():
                result[key] = _merge_defaults(item, default.get(key))
        return result
    return deepcopy(value) if value is not None else deepcopy(default)


def normalize_design_context(context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return the single serializable design-context representation.

    Existing resolved themes are valid inputs.  The function deliberately
    preserves unknown top-level keys so an older or newer producer can round
    trip information while diagnostics make such fields inspectable.
    """
    raw = dict(context or {})
    normalized = _merge_defaults(raw, _DEFAULT_CONTEXT)
    normalized["schema_version"] = str(raw.get("schema_version", DESIGN_CONTEXT_SCHEMA_VERSION))

    known_keys = set(_DEFAULT_CONTEXT) | {"name", "atoms", "text_effect_preset", "image_effect"}
    unknown = sorted(key for key in raw if key not in known_keys)
    diagnostics = normalized["diagnostics"]
    diagnostics["unknown_fields"] = sorted(set(diagnostics.get("unknown_fields", [])) | set(unknown))
    return normalized


def _merge_context_values(base: Any, override: Any) -> Any:
    if isinstance(base, Mapping) and isinstance(override, Mapping):
        merged = deepcopy(dict(base))
        for key, value in override.items():
            merged[key] = _merge_context_values(merged[key], value) if key in merged else deepcopy(value)
        return merged
    return deepcopy(override)


def merge_design_context(*contexts: Mapping[str, Any] | None) -> dict[str, Any]:
    """Merge producer output and a reviewed contract into one context.

    Later mappings win per field. Lists are intentionally replaced rather than
    appended so an approved slot/lock contract is unambiguous and repeatable.
    """
    merged: dict[str, Any] = {}
    for context in contexts:
        if context is not None:
            merged = _merge_context_values(merged, context)
    return normalize_design_context(merged)


def design_context_from_brand_spec(brand_spec: Any) -> dict[str, Any]:
    """Adapt the legacy ``BrandSpec`` object into the canonical context."""
    colors = dict(getattr(brand_spec, "colors", None) or {})
    fonts = dict(getattr(brand_spec, "fonts", None) or {})
    primary = colors.get("primary") or colors.get("accent", "#1D78FA")
    ink = colors.get("foreground") or colors.get("text_dark", "#111827")
    context = {
        "source": {"kind": "merged", "brand_source": getattr(brand_spec, "source", "none")},
        "colors": colors,
        "semantic_roles": {
            "background": colors.get("background", "#FFFFFF"),
            "surface": colors.get("surface", colors.get("background", "#FFFFFF")),
            "ink": ink,
            "primary": primary,
            "data-series-1": primary,
            "accent": colors.get("accent", primary),
        },
        "typography": fonts,
        "dark_mode": bool(getattr(brand_spec, "dark_mode", False)),
        "assets": {"logo": getattr(brand_spec, "logo", None) or {}},
    }
    return normalize_design_context(context)


class VIBuildSession:
    """Validate template-derived constraints before Build Mode renders a page.

    A session is presentation-scoped by construction: callers create one from
    a normalized context and provide the assets available to this particular
    deck.  It never silently downgrades a required visual asset to a color box.
    """

    def __init__(self, design_context: Mapping[str, Any], *, assets: Mapping[str, Any] | None = None):
        self.context = normalize_design_context(design_context)
        self.assets = dict(assets or {})

    def validate_overrides(
        self,
        overrides: Mapping[str, Any] | None,
        *,
        allow_template_override: bool = False,
    ) -> dict[str, Any]:
        """Reject writes to template-locked properties unless explicitly allowed."""
        lock_modes = {
            str(lock.get("field")): str(lock.get("mode", ""))
            for lock in self.context["locks"]
            if isinstance(lock, Mapping) and lock.get("field")
        }
        report = []
        for field in dict(overrides or {}):
            mode = lock_modes.get(field)
            if mode == "template-locked" and not allow_template_override:
                raise PermissionError(f"{field} is template-locked")
            report.append(
                {
                    "field": field,
                    "status": "approved_override" if mode == "template-locked" else "applied",
                }
            )
        return {"overrides": report}

    def plan_page(
        self,
        archetype_id: str,
        *,
        components: Sequence[str] | None = None,
        slot_values: Mapping[str, str] | None = None,
        overrides: Mapping[str, Any] | None = None,
        allow_template_override: bool = False,
    ) -> dict[str, Any]:
        """Return an auditable preflight result for a new template-derived page."""
        archetype = self._get_archetype(archetype_id)
        override_report = self.validate_overrides(
            overrides, allow_template_override=allow_template_override
        )
        component_report = self._validate_components(archetype, components or [])
        slot_bindings = self._bind_slots(slot_values or {})
        asset_plan = self._plan_assets(archetype, components or [])
        acceptance = self._evaluate_acceptance(asset_plan, component_report)
        if asset_plan["missing"]:
            status = "NEEDS_ASSET"
        elif asset_plan["violations"]:
            status = "NEEDS_REVISION"
        else:
            status = "READY"

        return {
            "status": status,
            "archetype": {"id": archetype_id, "reference_slide": archetype.get("reference_slide")},
            "asset_plan": asset_plan,
            "components": component_report,
            "slot_bindings": slot_bindings,
            "overrides": override_report["overrides"],
            "acceptance": acceptance,
        }

    def render_page(
        self,
        prs: Any,
        archetype_id: str,
        *,
        components: Sequence[str] | None = None,
        slot_values: Mapping[str, str] | None = None,
        overrides: Mapping[str, Any] | None = None,
        allow_template_override: bool = False,
    ) -> dict[str, Any]:
        """Create a new editable page only after its VI preflight is ready.

        The method intentionally handles only standardized component kinds.
        It is a Build consumer, not a second layout engine: callers select an
        extracted archetype and pass the component IDs that it allows.
        """
        result = self.plan_page(
            archetype_id,
            components=components,
            slot_values=slot_values,
            overrides=overrides,
            allow_template_override=allow_template_override,
        )
        if result["status"] != "READY":
            result["slide"] = None
            result["design_application"] = {
                "applied_to": [],
                "not_applied": ["page_not_created"],
                "blocked": result["asset_plan"]["missing"] + result["asset_plan"]["violations"],
            }
            return result

        from pptx_designer.renderer.theme_context import set_slide_theme
        from pptx_designer.tools.images import cover_image
        from pptx_designer.tools.shapes import rect
        from pptx_designer.tools.text import text

        slide = prs.slides.add_slide(self._blank_layout(prs))
        set_slide_theme(slide, self.context)
        applied_to: list[str] = []
        for component_id in components or []:
            component = self.context["components"][component_id]
            bounds = self._component_bounds(component, component_id)
            if component.get("kind") == "photo_panel":
                image_path = self._asset_path(self.assets["supporting_photo"])
                cover_image(slide, **bounds, image_path=image_path)
            elif component.get("kind") in {"color_panel", "rule"}:
                rect(slide, **bounds, fill=component["fill"])
            else:
                raise ValueError(f"unsupported VI component kind: {component.get('kind')}")
            applied_to.append(component_id)

        for slot_id, value in (slot_values or {}).items():
            slot = self._slot(slot_id)
            bounds = slot.get("bounds")
            if not isinstance(bounds, Mapping):
                raise ValueError(f"content slot {slot_id} has no render bounds")
            text(
                slide,
                bounds["left"],
                bounds["top"],
                bounds["width"],
                bounds["height"],
                str(value),
                font_size=slot.get("font_size", 18),
                bold=bool(slot.get("bold", False)),
                color=slot.get("color", "text_dark"),
                align=slot.get("align", "left"),
            )
            applied_to.append(slot_id)

        result["slide"] = slide
        result["design_application"] = {"applied_to": applied_to, "not_applied": [], "blocked": []}
        return result

    def _get_archetype(self, archetype_id: str) -> Mapping[str, Any]:
        for archetype in self.context["archetypes"]:
            if isinstance(archetype, Mapping) and archetype.get("id") == archetype_id:
                return archetype
        raise ValueError(f"unknown archetype: {archetype_id}")

    def _validate_components(
        self, archetype: Mapping[str, Any], components: Sequence[str]
    ) -> list[dict[str, str]]:
        permitted = set(archetype.get("permitted_components", []))
        known = set(self.context["components"])
        report = []
        for component in components:
            if component not in known:
                raise ValueError(f"unknown component: {component}")
            if permitted and component not in permitted:
                raise ValueError(f"component is not permitted by archetype: {component}")
            report.append({"id": component, "status": "applied"})
        return report

    def _bind_slots(self, slot_values: Mapping[str, str]) -> list[dict[str, str]]:
        slots = {
            str(slot.get("id")): slot
            for slot in self.context["content_slots"]
            if isinstance(slot, Mapping) and slot.get("id")
        }
        bindings = []
        for slot_id, value in slot_values.items():
            slot = slots.get(slot_id)
            if slot is None:
                raise ValueError(f"unknown content slot: {slot_id}")
            max_chars = slot.get("max_chars")
            if max_chars is not None and len(str(value)) > int(max_chars):
                raise ValueError(f"content slot {slot_id} exceeds max_chars={max_chars}")
            bindings.append({"id": slot_id, "status": "bound"})
        return bindings

    def _slot(self, slot_id: str) -> Mapping[str, Any]:
        for slot in self.context["content_slots"]:
            if isinstance(slot, Mapping) and slot.get("id") == slot_id:
                return slot
        raise ValueError(f"unknown content slot: {slot_id}")

    @staticmethod
    def _component_bounds(component: Mapping[str, Any], component_id: str) -> dict[str, float]:
        bounds = component.get("bounds")
        if not isinstance(bounds, Mapping):
            raise ValueError(f"component {component_id} has no bounds")
        required = ("left", "top", "width", "height")
        if any(field not in bounds for field in required):
            raise ValueError(f"component {component_id} has incomplete bounds")
        return {field: float(bounds[field]) for field in required}

    @staticmethod
    def _asset_path(asset: Any) -> str:
        if isinstance(asset, Mapping):
            asset = asset.get("path") or asset.get("url")
        if not isinstance(asset, str):
            raise ValueError("VI asset must provide a path or URL")
        return asset

    @staticmethod
    def _blank_layout(prs: Any) -> Any:
        """Use a template's blank layout when present, else its first layout."""
        for layout in prs.slide_layouts:
            if not layout.placeholders:
                return layout
        return prs.slide_layouts[0]

    def _plan_assets(self, archetype: Mapping[str, Any], component_ids: Sequence[str]) -> dict[str, Any]:
        image_grammar = self.context["assets"]["image_grammar"]
        required = list(archetype.get("required_assets", []))
        if image_grammar.get("required") and not required:
            required.append("supporting_photo")

        resolved: dict[str, Any] = {}
        missing: list[str] = []
        for asset_id in required:
            asset = self.assets.get(asset_id)
            if self._asset_is_available(asset):
                resolved[asset_id] = asset
            else:
                missing.append(asset_id)
        violations: list[str] = []
        minimum_area = image_grammar.get("min_area_ratio")
        if minimum_area is not None and required:
            media_area = self._photo_area_ratio(component_ids)
            if media_area < float(minimum_area):
                violations.append("media_area_ratio")
        else:
            media_area = None
        return {
            "required": required,
            "resolved": resolved,
            "missing": missing,
            "media_area_ratio": media_area,
            "violations": violations,
        }

    def _photo_area_ratio(self, component_ids: Sequence[str]) -> float:
        canvas_area = 13.333 * 7.5
        media_area = 0.0
        for component_id in component_ids:
            component = self.context["components"].get(component_id, {})
            if component.get("kind") != "photo_panel":
                continue
            bounds = component.get("bounds", {})
            try:
                media_area += float(bounds["width"]) * float(bounds["height"])
            except (KeyError, TypeError, ValueError):
                continue
        return round(media_area / canvas_area, 4) if canvas_area else 0.0

    @staticmethod
    def _asset_is_available(asset: Any) -> bool:
        if isinstance(asset, Mapping):
            asset = asset.get("path") or asset.get("url")
        if not isinstance(asset, str) or not asset:
            return False
        return Path(asset).is_file()

    def _evaluate_acceptance(
        self, asset_plan: Mapping[str, Any], components: Sequence[Mapping[str, str]]
    ) -> dict[str, list[str]]:
        passed: list[str] = []
        blocked: list[str] = []
        for requirement in self.context["acceptance"]["must_coverage"]:
            if requirement == "image_present":
                target = passed if not asset_plan["missing"] else blocked
            elif requirement == "component_applied":
                target = passed if components else blocked
            elif requirement == "media_area":
                target = passed if "media_area_ratio" not in asset_plan["violations"] else blocked
            else:
                target = blocked
            target.append(str(requirement))
        return {"passed": passed, "blocked": blocked}


__all__ = [
    "DESIGN_CONTEXT_SCHEMA_VERSION",
    "VIBuildSession",
    "design_context_from_brand_spec",
    "merge_design_context",
    "normalize_design_context",
]
