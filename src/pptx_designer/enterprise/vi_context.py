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
    "atom_styles": {},
    "visual_grammar": {
        "allowed_atom_kinds": [],
        "safe_area": {},
        "forbidden_zones": [],
        "min_font_size": None,
    },
    "archetypes": [],
    "visual_families": [],
    "layout_variants": [],
    "fixed_bases": {},
    "content_slots": [],
    "media_slots": [],
    "locks": [],
    "acceptance": {"must_coverage": [], "thresholds": {}},
    "diagnostics": {"warnings": [], "unknown_fields": [], "conflicts": [], "incomplete_theme_context": []},
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
    # A mapping that declares itself as a theme should not silently look like a
    # complete FreeStyle theme after defaults have been added. Template and VI
    # contexts remain intentionally partial.
    raw_source = raw.get("source")
    is_declared_theme = isinstance(raw_source, Mapping) and raw_source.get("kind") == "theme"
    if is_declared_theme or "name" in raw or "atoms" in raw:
        required = {"name", "atoms", "colors", "semantic_roles", "typography", "source"}
        diagnostics["incomplete_theme_context"] = sorted(required - set(raw))
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


def _template_lock_fields(context: Mapping[str, Any]) -> list[str]:
    return [
        str(lock["field"])
        for lock in context.get("locks", [])
        if isinstance(lock, Mapping) and lock.get("field") and lock.get("mode") == "template-locked"
    ]


def _locked_path(path: str, lock_fields: Sequence[str]) -> str | None:
    """Return the lock affecting *path*, including locked parent paths."""
    for field in lock_fields:
        if path == field or path.startswith(f"{field}."):
            return field
    return None


def _locked_descendant(path: str, lock_fields: Sequence[str]) -> str | None:
    """Return a descendant lock that would be erased by replacing *path*."""
    prefix = f"{path}."
    return next((field for field in lock_fields if field.startswith(prefix)), None)


def _merge_vi_context_values(
    base: Any,
    override: Any,
    *,
    path: str,
    lock_fields: Sequence[str],
    conflicts: list[dict[str, Any]],
) -> Any:
    locked_by = _locked_path(path, lock_fields) if path else None
    if locked_by:
        if base != override:
            conflicts.append(
                {
                    "path": path,
                    "locked_by": locked_by,
                    "base_value": deepcopy(base),
                    "attempted_value": deepcopy(override),
                    "action": "rejected",
                }
            )
        return deepcopy(base)
    descendant_lock = _locked_descendant(path, lock_fields) if path else None
    if descendant_lock and not (isinstance(base, Mapping) and isinstance(override, Mapping)):
        if base != override:
            conflicts.append(
                {
                    "path": path,
                    "locked_by": descendant_lock,
                    "base_value": deepcopy(base),
                    "attempted_value": deepcopy(override),
                    "action": "rejected_to_preserve_locked_descendant",
                }
            )
        return deepcopy(base)
    if isinstance(base, Mapping) and isinstance(override, Mapping):
        merged = deepcopy(dict(base))
        for key, value in override.items():
            child_path = f"{path}.{key}" if path else str(key)
            merged[key] = _merge_vi_context_values(
                merged.get(key), value, path=child_path, lock_fields=lock_fields, conflicts=conflicts
            )
        return merged
    return deepcopy(override)


def _preserve_template_locks(
    template: Mapping[str, Any], overrides: Sequence[Mapping[str, Any] | None]
) -> list[Any]:
    """Union lock declarations while keeping the template declaration authoritative."""
    result = deepcopy(list(template.get("locks", [])))
    known_fields = {
        str(lock.get("field"))
        for lock in result
        if isinstance(lock, Mapping) and lock.get("field")
    }
    for context in overrides:
        if context is None:
            continue
        for lock in context.get("locks", []):
            if not isinstance(lock, Mapping) or not lock.get("field"):
                continue
            field = str(lock["field"])
            if field not in known_fields:
                result.append(deepcopy(lock))
                known_fields.add(field)
    return result


def merge_vi_design_context(
    template_context: Mapping[str, Any], *overrides: Mapping[str, Any] | None
) -> dict[str, Any]:
    """Merge VI contexts without allowing later inputs to alter template locks.

    Unlike :func:`merge_design_context`, this is the policy boundary for
    template/brand/theme/page composition. Later contexts still win for
    unlocked values; rejected writes are retained as serializable diagnostics.
    """
    lock_fields = _template_lock_fields(template_context)
    conflicts: list[dict[str, Any]] = []
    merged: Any = deepcopy(dict(template_context))
    for override in overrides:
        if override is None:
            continue
        values = {key: value for key, value in override.items() if key != "locks"}
        merged = _merge_vi_context_values(
            merged, values, path="", lock_fields=lock_fields, conflicts=conflicts
        )
    merged["locks"] = _preserve_template_locks(template_context, overrides)
    normalized = normalize_design_context(merged)
    normalized["diagnostics"]["conflicts"] = conflicts
    return normalized


def validate_variant_sequence(plans: Sequence[Mapping[str, Any]]) -> list[str]:
    """Return deterministic layout-diversity violations for a deck sequence."""
    violations: list[str] = []
    previous = None
    for index, plan in enumerate(plans, start=1):
        if plan.get("page_role") != "content":
            previous = None
            continue
        variant = plan.get("variant_id")
        if variant and variant == previous:
            violations.append(f"adjacent_variant_repeat:page-{index}:{variant}")
        previous = variant
    return violations


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

    def plan(
        self,
        *,
        page_role: str,
        page_goal: str = "",
        content: Mapping[str, Any] | None = None,
        previous_variants: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Select a safe archetype and produce a renderer-ready page plan.

        This is intentionally deterministic.  A planner may select only an
        explicitly reviewed archetype; it never invents geometry or silently
        falls back from a content component page to a full prototype copy.
        """
        content = dict(content or {})
        if page_role == "content":
            return {
                "status": "NEEDS_REVISION",
                "page_role": page_role,
                "page_goal": page_goal,
                "diagnostics": {"blocked": ["content_pages_require_atomic_build_plan"]},
            }
        previous = set(previous_variants or ())
        candidates = [
            item for item in self.context["archetypes"]
            if isinstance(item, Mapping)
            and (not item.get("page_role") or item.get("page_role") == page_role)
        ]
        if previous:
            unused = [item for item in candidates if item.get("variant_id") not in previous]
            if unused:
                candidates = unused
            elif previous_variants:
                # Once a family has been fully consumed, avoid an immediate
                # repeat of the last variant.  This is the same deterministic
                # rotation rule used by the VI adapter.
                last = previous_variants[-1]
                candidates = [item for item in candidates if item.get("variant_id") != last] or candidates
        if not candidates:
            return {
                "status": "NEEDS_REVISION",
                "page_role": page_role,
                "page_goal": page_goal,
                "diagnostics": {"blocked": ["no_safe_archetype"]},
            }
        archetype = candidates[0]
        component_ids = list(content.get("components", archetype.get("default_components", [])))
        slot_values = dict(content.get("slots", {}))
        media_values = dict(content.get("media", {}))
        preflight = self.plan_page(
            str(archetype["id"]),
            components=component_ids,
            slot_values=slot_values,
            media_values=media_values,
        )
        return {
            "status": preflight["status"],
            "page_role": page_role,
            "page_goal": page_goal,
            "reference_slide": archetype.get("reference_slide"),
            "archetype_id": archetype["id"],
            "family_id": archetype.get("family_id"),
            "variant_id": archetype.get("variant_id"),
            "base_id": archetype.get("base_id"),
            "components": component_ids,
            "text_instances": slot_values,
            "media_instances": media_values,
            "preflight": preflight,
            "diagnostics": {"blocked": preflight.get("asset_plan", {}).get("missing", [])},
        }

    def render(self, plan: Mapping[str, Any], presentation: Any) -> dict[str, Any]:
        """Render a plan produced by :meth:`plan` through the existing API."""
        if plan.get("status") != "READY":
            return {**dict(plan), "slide": None}
        return self.render_page(
            presentation,
            str(plan["archetype_id"]),
            components=plan.get("components", []),
            slot_values=plan.get("text_instances", {}),
            media_values=plan.get("media_instances", {}),
        )

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
        media_values: Mapping[str, Any] | None = None,
        overrides: Mapping[str, Any] | None = None,
        allow_template_override: bool = False,
    ) -> dict[str, Any]:
        """Return an auditable preflight result for a new template-derived page."""
        archetype = self._get_archetype(archetype_id)
        if archetype.get("page_role") == "content":
            return {
                "status": "NEEDS_REVISION",
                "archetype": {"id": archetype_id, "reference_slide": archetype.get("reference_slide")},
                "asset_plan": {"missing": [], "violations": []},
                "media_plan": {"missing": []},
                "diagnostics": {"blocked": ["content_pages_require_atomic_build_plan"]},
            }
        override_report = self.validate_overrides(
            overrides, allow_template_override=allow_template_override
        )
        component_report = self._validate_components(archetype, components or [])
        layout_violations = self._validate_layout(components or [], slot_values or {})
        slot_bindings = self._bind_slots(slot_values or {})
        media_plan = self._bind_media_slots(media_values or {})
        asset_plan = self._plan_assets(archetype, components or [])
        acceptance = self._evaluate_acceptance(asset_plan, component_report)
        if asset_plan["missing"] or media_plan["missing"]:
            status = "NEEDS_ASSET"
        elif asset_plan["violations"] or layout_violations:
            status = "NEEDS_REVISION"
        else:
            status = "READY"

        return {
            "status": status,
            "archetype": {
                "id": archetype_id,
                "reference_slide": archetype.get("reference_slide"),
                "render_strategy": archetype.get("render_strategy", "components"),
            },
            "asset_plan": asset_plan,
            "components": component_report,
            "layout": {"violations": layout_violations},
            "slot_bindings": slot_bindings,
            "media_bindings": media_plan["bindings"],
            "media_plan": media_plan,
            "overrides": override_report["overrides"],
            "acceptance": acceptance,
            "fixed_base": self._fixed_base(archetype),
        }

    def render_page(
        self,
        prs: Any,
        archetype_id: str,
        *,
        components: Sequence[str] | None = None,
        slot_values: Mapping[str, str] | None = None,
        media_values: Mapping[str, Any] | None = None,
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
            media_values=media_values,
            overrides=overrides,
            allow_template_override=allow_template_override,
        )
        archetype = self._get_archetype(archetype_id)
        if archetype.get("page_role") == "content" and archetype.get("render_strategy", "components") == "prototype":
            result["status"] = "NEEDS_REVISION"
            result["diagnostics"] = {"blocked": ["content_pages_require_atomic_build_plan"]}
            result["slide"] = None
            return result
        if result["status"] != "READY":
            result["slide"] = None
            result["design_application"] = {
                "applied_to": [],
                "not_applied": ["page_not_created"],
                "blocked": result["asset_plan"]["missing"]
                + result["media_plan"]["missing"]
                + result["asset_plan"]["violations"],
            }
            return result

        render_strategy = archetype.get("render_strategy", "components")
        if render_strategy == "prototype":
            from pptx_designer.enterprise.prototype import clone_slide_prototype

            reference_slide = int(archetype.get("reference_slide", 0))
            if not 1 <= reference_slide <= len(prs.slides):
                raise ValueError(f"prototype reference_slide is unavailable: {reference_slide}")
            slide = clone_slide_prototype(prs, prs.slides[reference_slide - 1])
            applied_to: list[str] = [f"prototype:slide-{reference_slide}"] + list(components or [])
        elif render_strategy == "components":
            from pptx_designer.core.build_spec import render_build_spec

            instances = []
            for component_id in components or []:
                component = self.context["components"][component_id]
                data = None
                if component.get("kind") == "photo_panel":
                    data = self.assets.get("supporting_photo")
                instances.append({"component_id": component_id, "data": data})
            slide = render_build_spec(
                {
                    "kind": "BuildSpec",
                    "render_strategy": "components",
                    "components": instances,
                    "fixed_base": self._fixed_base(archetype),
                },
                prs,
                self.context,
            )
            applied_to = list(components or [])
        else:
            raise ValueError(f"unsupported VI render strategy: {render_strategy}")

        for slot_id, value in (slot_values or {}).items():
            slot = self._slot(slot_id)
            if render_strategy == "prototype":
                self._bind_prototype_text(slide, slot_id, slot, str(value))
            else:
                from pptx_designer.tools.text import text

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

        for slot_id, asset in (media_values or {}).items():
            slot = self._media_slot(slot_id)
            if render_strategy != "prototype":
                raise ValueError("media slots require the prototype render strategy")
            image_path = self._asset_path(asset)
            mode = str(slot.get("mode", "replace"))
            if mode == "replace":
                self._bind_prototype_image(slide, slot_id, slot, image_path)
            elif mode == "insert":
                from pptx_designer.tools.images import cover_image

                bounds = self._media_slot_bounds(slot, slot_id)
                picture = cover_image(slide, **bounds, image_path=image_path)
                if slot.get("z_order") == "back":
                    self._send_shape_to_back(slide, picture)
            else:
                raise ValueError(f"unsupported prototype media slot mode: {mode}")
            applied_to.append(slot_id)

        result["slide"] = slide
        result["design_application"] = {"applied_to": applied_to, "not_applied": [], "blocked": []}
        return result

    def _get_archetype(self, archetype_id: str) -> Mapping[str, Any]:
        for archetype in self.context["archetypes"]:
            if isinstance(archetype, Mapping) and archetype.get("id") == archetype_id:
                return archetype
        raise ValueError(f"unknown archetype: {archetype_id}")

    def _fixed_base(self, archetype: Mapping[str, Any]) -> dict[str, Any] | None:
        """Return the reviewed fixed-base recipe for a content archetype."""
        if archetype.get("page_role") != "content" or not archetype.get("base_id"):
            return None
        base_id = str(archetype["base_id"])
        base = self.context.get("fixed_bases", {}).get(base_id)
        if not isinstance(base, Mapping):
            return {"id": base_id, "status": "review_required"}
        if not base.get("safe_to_clone", False):
            raise ValueError(f"unsafe fixed base: {base_id}")
        if "reference_slide" in base and "fixed_shape_indices" not in base:
            raise ValueError(
                f"fixed base {base_id} requires explicit fixed_shape_indices"
            )
        return {
            "id": base_id,
            "safe_to_clone": True,
            "reference_slide": base.get("reference_slide"),
            "fixed_shape_indices": list(base.get("fixed_shape_indices", [])) or None,
            "exclude_shape_indices": list(base.get("exclude_shape_indices", [])) or None,
            "fixed_objects": list(base.get("fixed_objects", [])),
            "removed_objects": list(base.get("removed_objects", [])),
            "unsupported_objects": list(base.get("unsupported_objects", [])),
        }

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

    def _validate_layout(
        self, component_ids: Sequence[str], slot_values: Mapping[str, Any]
    ) -> list[str]:
        """Reject accidental component/text collisions before rendering."""
        violations: list[str] = []
        boxes: list[tuple[str, Mapping[str, Any]]] = []
        for component_id in component_ids:
            component = self.context["components"].get(component_id, {})
            bounds = component.get("bounds")
            if isinstance(bounds, Mapping):
                boxes.append((component_id, bounds))
                if any(float(bounds.get(key, 0)) < 0 for key in ("left", "top", "width", "height")):
                    violations.append(f"negative_geometry:{component_id}")
                if float(bounds.get("left", 0)) + float(bounds.get("width", 0)) > 13.333 or float(bounds.get("top", 0)) + float(bounds.get("height", 0)) > 7.5:
                    violations.append(f"out_of_bounds:{component_id}")
        for index, (first_id, first) in enumerate(boxes):
            for second_id, second in boxes[index + 1:]:
                if self._intersection_ratio(first, second) > 0:
                    first_component = self.context["components"].get(first_id, {})
                    second_component = self.context["components"].get(second_id, {})
                    if not first_component.get("allow_overlap") and not second_component.get("allow_overlap"):
                        violations.append(f"component_overlap:{first_id}:{second_id}")
        # Text over a photo can be intentional in editorial templates.  The
        # renderer/visual QA decides whether its contrast and z-order are safe;
        # the planner only rejects unambiguous component-component collisions.
        return sorted(set(violations))

    @staticmethod
    def _intersection_ratio(first: Mapping[str, Any], second: Mapping[str, Any]) -> float:
        try:
            ax, ay, aw, ah = (float(first[key]) for key in ("left", "top", "width", "height"))
            bx, by, bw, bh = (float(second[key]) for key in ("left", "top", "width", "height"))
        except (KeyError, TypeError, ValueError):
            return 0.0
        area = max(0.0, min(ax + aw, bx + bw) - max(ax, bx)) * max(0.0, min(ay + ah, by + bh) - max(ay, by))
        return area / max(aw * ah, 0.0001)

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

    def _bind_media_slots(self, media_values: Mapping[str, Any]) -> dict[str, Any]:
        bindings: list[dict[str, str]] = []
        missing: list[str] = []
        for slot_id, asset in media_values.items():
            self._media_slot(slot_id)
            if self._asset_is_available(asset):
                bindings.append({"id": slot_id, "status": "bound"})
            else:
                bindings.append({"id": slot_id, "status": "missing_asset"})
                missing.append(slot_id)
        return {"bindings": bindings, "missing": missing}

    def _media_slot(self, slot_id: str) -> Mapping[str, Any]:
        for slot in self.context["media_slots"]:
            if isinstance(slot, Mapping) and slot.get("id") == slot_id:
                return slot
        raise ValueError(f"unknown media slot: {slot_id}")

    @staticmethod
    def _media_slot_bounds(slot: Mapping[str, Any], slot_id: str) -> dict[str, float]:
        bounds = slot.get("bounds")
        if not isinstance(bounds, Mapping):
            raise ValueError(f"prototype media slot {slot_id} has no bounds")
        required = ("left", "top", "width", "height")
        if any(field not in bounds for field in required):
            raise ValueError(f"prototype media slot {slot_id} has incomplete bounds")
        return {field: float(bounds[field]) for field in required}

    @staticmethod
    def _send_shape_to_back(slide: Any, shape: Any) -> None:
        """Place a contract-defined media layer behind copied template text."""
        element = shape.element
        parent = element.getparent()
        parent.remove(element)
        # The first two children are the group's non-visual and group
        # properties. Index 2 is consequently behind every shape layer.
        parent.insert(2, element)

    @staticmethod
    def _bind_prototype_text(slide: Any, slot_id: str, slot: Mapping[str, Any], value: str) -> None:
        """Replace a reviewed template text slot without changing its styling."""
        target = slot.get("target")
        if not isinstance(target, Mapping) or "shape_index" not in target:
            raise ValueError(f"prototype content slot {slot_id} has no target.shape_index")
        shape_index = int(target["shape_index"])
        if not 0 <= shape_index < len(slide.shapes):
            raise ValueError(f"prototype content slot {slot_id} targets an unavailable shape")
        shape = slide.shapes[shape_index]
        if not shape.has_text_frame or not shape.text_frame.paragraphs:
            raise ValueError(f"prototype content slot {slot_id} does not target a text shape")
        paragraph = shape.text_frame.paragraphs[0]
        if paragraph.runs:
            paragraph.runs[0].text = value
            for run in paragraph.runs[1:]:
                run.text = ""
        else:
            paragraph.text = value
        for extra in shape.text_frame.paragraphs[1:]:
            for run in extra.runs:
                run.text = ""

    @staticmethod
    def _bind_prototype_image(slide: Any, slot_id: str, slot: Mapping[str, Any], image_path: str) -> None:
        """Replace a prototype picture while retaining the template crop and bounds."""
        target = slot.get("target")
        if not isinstance(target, Mapping) or "shape_index" not in target:
            raise ValueError(f"prototype media slot {slot_id} has no target.shape_index")
        shape_index = int(target["shape_index"])
        if not 0 <= shape_index < len(slide.shapes):
            raise ValueError(f"prototype media slot {slot_id} targets an unavailable shape")
        shape = slide.shapes[shape_index]
        try:
            image_part, new_rid = slide.part.get_or_add_image_part(image_path)
            del image_part  # The slide relationship holds the part; keep the public result explicit.
            shape._element.blipFill.blip.rEmbed = new_rid
        except (AttributeError, TypeError):
            raise ValueError(f"prototype media slot {slot_id} does not target a picture") from None

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
    "merge_vi_design_context",
    "normalize_design_context",
    "validate_variant_sequence",
]
