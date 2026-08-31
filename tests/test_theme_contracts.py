"""Regression coverage for resolved themes and protected VI composition."""

from __future__ import annotations

import pytest

from pptx_designer import Presentation, generate_ppt, validate_resolved_theme
from pptx_designer.enterprise.vi_context import (
    merge_design_context,
    merge_vi_design_context,
    normalize_design_context,
)
from pptx_designer.renderer.theme import ThemeComposer


def _resolved_theme() -> dict:
    return ThemeComposer().compose(style="warm-elegant", seed=17)


def test_generate_ppt_rejects_a_partial_theme_before_rendering(tmp_path):
    raw_lock = {"colors": {"primary": "#112233"}, "typography": {"heading": "Arial"}}

    with pytest.raises(ValueError, match="complete resolved theme.*missing fields"):
        generate_ppt(content={"pages": []}, theme=raw_lock, output=str(tmp_path / "invalid.pptx"))


def test_validate_resolved_theme_accepts_theme_composer_output():
    validate_resolved_theme(_resolved_theme())


def test_validate_resolved_theme_rejects_a_shallow_but_incomplete_mapping():
    theme = _resolved_theme()
    theme["semantic_roles"] = {}

    with pytest.raises(ValueError, match="missing semantic roles"):
        validate_resolved_theme(theme)


def test_validate_resolved_theme_rejects_invalid_semantic_role_color_before_rendering():
    theme = _resolved_theme()
    theme["semantic_roles"]["background"] = 123

    with pytest.raises(ValueError, match="invalid semantic role colors: background"):
        validate_resolved_theme(theme)


def test_supplied_theme_reports_ignored_discovery_arguments(tmp_path):
    locked = _resolved_theme()

    with pytest.warns(UserWarning, match="theme-discovery arguments were ignored"):
        result = generate_ppt(
            content={"pages": []},
            theme=locked,
            style="dark-tech",
            palette="cyber-neon",
            style_seed=99,
            output=str(tmp_path / "locked.pptx"),
        )

    assert result["theme_context"] == locked
    assert result["theme_application"]["ignored_arguments"] == {
        "style": "dark-tech",
        "palette": "cyber-neon",
        "style_seed": 99,
    }


def test_strict_build_theme_rejects_partial_theme_but_keeps_vi_context_compatible():
    raw_lock = {"colors": {"primary": "#112233"}, "typography": {"heading": "Arial"}}

    with pytest.raises(ValueError, match="complete resolved theme"):
        Presentation(theme=raw_lock, strict_theme=True)

    assert Presentation(theme=raw_lock)
    assert Presentation(theme=_resolved_theme(), strict_theme=True)


def test_normalization_marks_declared_but_incomplete_theme_without_marking_vi_context():
    incomplete = normalize_design_context({"source": {"kind": "theme"}, "colors": {}})
    vi_context = normalize_design_context({"source": {"kind": "template"}, "locks": []})

    assert "name" in incomplete["diagnostics"]["incomplete_theme_context"]
    assert vi_context["diagnostics"]["incomplete_theme_context"] == []


def test_protected_vi_merge_preserves_template_values_and_locks():
    template = {
        "colors": {"primary": "#111111", "accent": "#222222"},
        "typography": {"heading": "Brand Heading", "body": "Brand Body"},
        "assets": {"logo": {"path": "brand.svg"}},
        "visual_grammar": {"safe_area": {"left": 1.0, "right": 1.0}},
        "locks": [
            {"field": "colors.primary", "mode": "template-locked"},
            {"field": "typography.heading", "mode": "template-locked"},
            {"field": "assets.logo", "mode": "template-locked"},
            {"field": "visual_grammar.safe_area", "mode": "template-locked"},
        ],
    }
    override = {
        "colors": {"primary": "#999999", "accent": "#AAAAAA"},
        "typography": {"heading": "Other Heading", "body": "Other Body"},
        "assets": {"logo": {"path": "other.svg"}},
        "visual_grammar": {"safe_area": {"left": 0.0}},
        "locks": [],
    }

    merged = merge_vi_design_context(template, override)

    assert merged["colors"] == {"primary": "#111111", "accent": "#AAAAAA"}
    assert merged["typography"] == {"heading": "Brand Heading", "body": "Other Body"}
    assert merged["assets"]["logo"] == {"path": "brand.svg"}
    assert merged["visual_grammar"]["safe_area"] == {"left": 1.0, "right": 1.0}
    assert len(merged["locks"]) == 4
    assert {item["path"] for item in merged["diagnostics"]["conflicts"]} == {
        "colors.primary",
        "typography.heading",
        "assets.logo",
        "visual_grammar.safe_area",
    }


def test_protected_vi_merge_rejects_parent_replacement_that_erases_a_locked_child():
    template = {
        "colors": {"primary": "#111111", "accent": "#222222"},
        "locks": [{"field": "colors.primary", "mode": "template-locked"}],
    }

    merged = merge_vi_design_context(template, {"colors": "not-a-color-map"})

    assert merged["colors"] == template["colors"]
    assert merged["diagnostics"]["conflicts"] == [
        {
            "path": "colors",
            "locked_by": "colors.primary",
            "base_value": template["colors"],
            "attempted_value": "not-a-color-map",
            "action": "rejected_to_preserve_locked_descendant",
        }
    ]


def test_generic_context_merge_remains_last_writer_wins():
    merged = merge_design_context(
        {"colors": {"primary": "#111111"}, "locks": [{"field": "colors.primary"}]},
        {"colors": {"primary": "#999999"}, "locks": []},
    )

    assert merged["colors"]["primary"] == "#999999"
    assert merged["locks"] == []
