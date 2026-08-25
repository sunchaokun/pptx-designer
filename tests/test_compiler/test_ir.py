"""Tests for the incremental, read-only SVG intermediate representation."""

from __future__ import annotations

from pptx_designer.compiler import build_svg_ir, sanitize


def test_ir_preserves_tree_order_computed_css_and_source_index():
    root = sanitize(
        """<svg viewBox="0 0 10 10">
        <style>.accent { fill: #4472C4; }</style>
        <g id="group"><rect id="box" class="accent" width="10" height="10"/></g>
        </svg>"""
    )

    document = build_svg_ir(root)

    assert [node.tag for node in document.nodes] == ["svg", "g", "rect"]
    assert document.nodes[0].child_indices == (1,)
    assert document.nodes[1].parent_index == 0
    assert document.nodes_for_id("box")[0].get("fill") == "#4472C4"
    assert document.nodes_for_id("group")[0].child_indices == (2,)


def test_ir_identifies_features_without_mutable_xml_state():
    root = sanitize(
        """<svg viewBox="0 0 10 10">
        <defs><filter id="blur"/></defs>
        <rect id="target" width="10" height="10" fill="url(#paint)" clip-path="url(#clip)"/>
        </svg>"""
    )

    document = build_svg_ir(root)
    target = document.nodes_for_id("target")[0]

    assert {"filter", "raster_fallback_candidate", "paint_server", "clipPath"} <= document.features
    assert target.get("fill") == "url(#paint)"
    assert isinstance(target.attributes, tuple)


def test_ir_source_index_keeps_preorder_for_repeated_ids():
    root = sanitize('<svg viewBox="0 0 10 10"><g id="same"><rect id="same"/></g></svg>')

    document = build_svg_ir(root)

    assert [node.index for node in document.nodes_for_id("same")] == [1, 2]


def test_ir_marks_group_opacity_for_raster_fallback():
    root = sanitize('<svg viewBox="0 0 10 10"><g id="faded" opacity="0.5"><rect/></g></svg>')

    document = build_svg_ir(root)

    assert "group_opacity" in document.nodes_for_id("faded")[0].features
