"""Read-only intermediate representation for sanitized SVG documents.

The current compiler still renders directly from the sanitized lxml tree.  The
IR deliberately mirrors that tree rather than replacing it: it provides stable
node identities, source-order information and pre-render capability analysis
for diagnostics and later backend selection.
"""
from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass(frozen=True)
class SVGIRNode:
    """A normalized SVG element captured after sanitization and CSS cascade."""

    index: int
    tag: str
    source_id: str | None
    parent_index: int | None
    child_indices: tuple[int, ...]
    attributes: tuple[tuple[str, str], ...]
    text: str | None
    features: frozenset[str]

    def get(self, name: str, default: str | None = None) -> str | None:
        """Return a normalized attribute without exposing mutable XML state."""
        for key, value in self.attributes:
            if key == name:
                return value
        return default


@dataclass(frozen=True)
class SVGIRDocument:
    """Immutable, source-ordered representation of a sanitized SVG tree."""

    nodes: tuple[SVGIRNode, ...]
    root_index: int
    source_index: tuple[tuple[str, tuple[int, ...]], ...]
    features: frozenset[str]

    def nodes_for_id(self, source_id: str) -> tuple[SVGIRNode, ...]:
        """Return all nodes bearing ``source_id`` (SVG permits duplicate ids)."""
        indices = dict(self.source_index).get(source_id, ())
        return tuple(self.nodes[index] for index in indices)


_GEOMETRY_TAGS = frozenset({
    "rect", "circle", "ellipse", "line", "polygon", "polyline", "path",
})
_DEFINITION_TAGS = frozenset({"linearGradient", "radialGradient", "clipPath", "symbol"})
_RASTER_ONLY_TAGS = frozenset({"image", "filter", "mask", "pattern", "marker"})


def _features_for(tag: str, attributes: dict[str, str]) -> frozenset[str]:
    features = {tag}
    if tag in _GEOMETRY_TAGS:
        features.add("geometry")
    if tag in _DEFINITION_TAGS:
        features.add("definitions")
    if tag in _RASTER_ONLY_TAGS:
        features.add("raster_fallback_candidate")
    if tag in {"linearGradient", "radialGradient"}:
        features.add("gradient")
    if attributes.get("clip-path"):
        features.add("clipPath")
    if attributes.get("fill-rule") == "evenodd":
        features.add("evenodd")
    if tag in {"g", "svg"} and attributes.get("opacity", "1") not in {"1", "1.0"}:
        features.add("group_opacity")
    if attributes.get("display") == "none" or attributes.get("visibility") in {"hidden", "collapse"}:
        features.add("hidden")
    if any(value.startswith("url(") for key, value in attributes.items() if key in {"fill", "stroke"}):
        features.add("paint_server")
    return frozenset(features)


def build_svg_ir(root: etree._Element) -> SVGIRDocument:
    """Build an immutable IR from a sanitized lxml SVG root.

    CSS has already been materialized into presentation attributes by the
    sanitizer, so ``attributes`` represent the computed subset consumed by the
    native renderer.  Comments and processing instructions are excluded.
    """
    nodes: list[SVGIRNode | None] = []
    source_index: dict[str, list[int]] = {}

    def visit(element: etree._Element, parent_index: int | None) -> int | None:
        if not isinstance(element.tag, str):
            return None
        index = len(nodes)
        nodes.append(None)
        attributes_dict = dict(element.attrib)
        source_id = attributes_dict.get("id")
        if source_id:
            source_index.setdefault(source_id, []).append(index)
        child_indices = tuple(
            child_index
            for child in element
            if (child_index := visit(child, index)) is not None
        )
        tag = element.tag.split("}")[-1]
        nodes[index] = SVGIRNode(
            index=index,
            tag=tag,
            source_id=source_id,
            parent_index=parent_index,
            child_indices=child_indices,
            attributes=tuple(sorted(attributes_dict.items())),
            text=element.text.strip() if element.text and element.text.strip() else None,
            features=_features_for(tag, attributes_dict),
        )
        return index

    root_index = visit(root, None)
    if root_index is None:
        raise ValueError("SVG root must be an element")
    built_nodes = tuple(node for node in nodes if node is not None)
    return SVGIRDocument(
        nodes=built_nodes,
        root_index=root_index,
        source_index=tuple((key, tuple(value)) for key, value in source_index.items()),
        features=frozenset().union(*(node.features for node in built_nodes)),
    )
