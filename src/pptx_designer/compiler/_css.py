"""Small, deterministic CSS subset for SVG style blocks.

The compiler deliberately supports only selectors common in generated SVG:
tag names, ``.class``, ``#id``, ``:root`` and comma-separated lists. It
implements cascade order, specificity, inline styles, ``!important`` and CSS
custom-property substitution without attempting to emulate a web browser.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"
SVG = f"{{{SVG_NS}}}"

_CSS_PROP_RE = re.compile(r"([\w-]+)\s*:\s*([^;]+?)(?:;|$)")
_IMPORTANT_RE = re.compile(r"\s*!important\s*$", re.IGNORECASE)
_VAR_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]+?))?\s*\)")

_SUPPORTED_PROPERTIES = frozenset(
    {
        "fill",
        "fill-opacity",
        "fill-rule",
        "stroke",
        "stroke-opacity",
        "stroke-width",
        "stroke-dasharray",
        "stroke-dashoffset",
        "stroke-linecap",
        "stroke-linejoin",
        "opacity",
        "font-size",
        "font-family",
        "font-weight",
        "font-style",
        "text-anchor",
        "dominant-baseline",
        "alignment-baseline",
        "color",
        "visibility",
        "display",
        "transform",
        "clip-path",
    }
)

# SVG group opacity is composited, not inherited; do not propagate it here.
_INHERITED = frozenset(
    {
        "fill",
        "fill-opacity",
        "fill-rule",
        "stroke",
        "stroke-opacity",
        "stroke-width",
        "stroke-dasharray",
        "stroke-dashoffset",
        "stroke-linecap",
        "stroke-linejoin",
        "font-size",
        "font-family",
        "font-weight",
        "font-style",
        "text-anchor",
        "dominant-baseline",
        "alignment-baseline",
        "color",
        "visibility",
    }
)

_Selector = str
_CSSRule = tuple[_Selector, dict[str, str]]


@dataclass(frozen=True)
class _Declaration:
    value: str
    important: bool
    specificity: int
    order: int


def _parse_css_block(text: str) -> list[_CSSRule]:
    """Return simple ``(selector, properties)`` rules for test and tooling use."""
    rules: list[_CSSRule] = []
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    for match in re.finditer(r"([^{}]+)\{([^}]*)\}", text):
        selectors_raw, declarations = match.group(1).strip(), match.group(2).strip()
        if not declarations:
            continue
        props = {
            prop_match.group(1).strip(): prop_match.group(2).strip()
            for prop_match in _CSS_PROP_RE.finditer(declarations)
            if prop_match.group(2).strip()
        }
        if not props:
            continue
        for selector in selectors_raw.split(","):
            selector = selector.strip()
            if selector:
                rules.append((selector, dict(props)))
    return rules


def _local_name(el: etree._Element) -> str:
    return el.tag.split("}")[-1] if "}" in el.tag else el.tag


def _match_selector(root: etree._Element, selector: str) -> set[etree._Element]:
    """Return matches for a supported simple selector."""
    selector = selector.strip()
    if selector == ":root":
        return {root}
    if selector.startswith("#"):
        return {el for el in root.iter() if el.get("id") == selector[1:]}
    if selector.startswith("."):
        target = selector[1:]
        return {el for el in root.iter() if target in el.get("class", "").split()}
    if any(token in selector for token in (" ", ">", "+", "~", "[", ":")):
        return set()
    return {el for el in root.iter() if _local_name(el) == selector}


def _specificity(selector: str) -> int:
    if selector.startswith("#"):
        return 100
    if selector.startswith(".") or selector == ":root":
        return 10
    return 1


def _parse_declarations(properties: dict[str, str]) -> Iterable[tuple[str, str, bool]]:
    for prop, raw_value in properties.items():
        value = raw_value.strip()
        important = bool(_IMPORTANT_RE.search(value))
        if important:
            value = _IMPORTANT_RE.sub("", value).strip()
        if prop.startswith("--") or prop in _SUPPORTED_PROPERTIES:
            yield prop, value, important


def _inline_properties(el: etree._Element) -> dict[str, str]:
    return {
        match.group(1).strip(): match.group(2).strip()
        for match in _CSS_PROP_RE.finditer(el.get("style", ""))
        if match.group(2).strip()
    }


def _set_if_wins(
    candidates: dict[etree._Element, dict[str, _Declaration]],
    el: etree._Element,
    prop: str,
    declaration: _Declaration,
) -> None:
    current = candidates.setdefault(el, {}).get(prop)
    candidate_key = (declaration.important, declaration.specificity, declaration.order)
    current_key = (current.important, current.specificity, current.order) if current else None
    if current_key is None or candidate_key >= current_key:
        candidates[el][prop] = declaration


def _apply_rules_to_tree(root: etree._Element, rules: list[_CSSRule]) -> None:
    """Materialize the CSS subset as XML attributes, then inherit properties."""
    candidates: dict[etree._Element, dict[str, _Declaration]] = {}

    # Presentation attributes are author declarations of lowest specificity.
    for el in root.iter():
        for prop in _SUPPORTED_PROPERTIES:
            value = el.get(prop)
            if value is not None:
                _set_if_wins(candidates, el, prop, _Declaration(value, False, 0, -1))

    # Stylesheet rules cascade by importance, specificity and source order.
    for order, (selector, properties) in enumerate(rules):
        specificity = _specificity(selector)
        for el in _match_selector(root, selector):
            for prop, value, important in _parse_declarations(properties):
                _set_if_wins(candidates, el, prop, _Declaration(value, important, specificity, order))

    # Inline styles have highest normal specificity and are consumed here so
    # sanitizer does not subsequently overwrite the computed attributes.
    inline_order = len(rules) + 1
    for el in root.iter():
        for prop, value, important in _parse_declarations(_inline_properties(el)):
            _set_if_wins(candidates, el, prop, _Declaration(value, important, 1000, inline_order))
        el.attrib.pop("style", None)

    custom_properties: dict[etree._Element, dict[str, str]] = {}
    for el, properties in candidates.items():
        for prop, declaration in properties.items():
            if prop.startswith("--"):
                # XML attribute names cannot start with ``--`` in lxml, so
                # custom properties stay in the computed-style side table.
                custom_properties.setdefault(el, {})[prop] = declaration.value
            else:
                el.set(prop, declaration.value)

    _inherit_and_resolve(root, {}, {}, custom_properties)


def _resolve_vars(value: str, variables: dict[str, str]) -> str:
    for _ in range(8):
        replaced = False

        def replace(match: re.Match[str]) -> str:
            nonlocal replaced
            name, fallback = match.group(1), match.group(2)
            resolved = variables.get(name, fallback)
            if resolved is None:
                return match.group(0)
            replaced = True
            return resolved.strip()

        new_value = _VAR_RE.sub(replace, value)
        if not replaced or new_value == value:
            return new_value
        value = new_value
    return value


def _inherit_and_resolve(
    el: etree._Element,
    inherited: dict[str, str],
    inherited_variables: dict[str, str],
    custom_properties: dict[etree._Element, dict[str, str]],
) -> None:
    variables = dict(inherited_variables)
    for name, value in custom_properties.get(el, {}).items():
        variables[name] = _resolve_vars(value, variables)

    current = dict(inherited)
    for prop in _INHERITED:
        value = el.get(prop)
        if value is None and prop in current:
            value = current[prop]
            el.set(prop, value)
        if value is not None:
            resolved = _resolve_vars(value, variables)
            if resolved != value:
                el.set(prop, resolved)
            current[prop] = resolved

    for prop in _SUPPORTED_PROPERTIES - _INHERITED:
        value = el.get(prop)
        if value is not None:
            resolved = _resolve_vars(value, variables)
            if resolved != value:
                el.set(prop, resolved)

    for child in el:
        if isinstance(child.tag, str):
            _inherit_and_resolve(child, current, variables, custom_properties)


def apply_css_blocks(root: etree._Element) -> None:
    """Apply safe SVG CSS style blocks and remove them from *root*."""
    style_els = root.findall(f".//{SVG}style")
    style_els.extend(root.findall(".//style"))
    rules: list[_CSSRule] = []
    for style_el in style_els:
        rules.extend(_parse_css_block(style_el.text or ""))

    _apply_rules_to_tree(root, rules)

    for style_el in style_els:
        parent = style_el.getparent()
        if parent is not None:
            parent.remove(style_el)
