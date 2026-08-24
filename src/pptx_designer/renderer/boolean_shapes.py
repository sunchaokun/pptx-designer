"""Boolean shapes — Shapely geometry boolean operations."""

from __future__ import annotations

from typing import Any

from pptx.oxml.ns import qn
from lxml import etree

EMU_PER_INCH = 914400

try:
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.ops import unary_union
    from shapely.validation import make_valid
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def poly_rect(x: float, y: float, w: float, h: float) -> Any:
    """Create rectangle polygon."""
    if not HAS_SHAPELY:
        return None
    return Polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def poly_circle(cx: float, cy: float, r: float, segments: int = 32) -> Any:
    """Create circle polygon."""
    if not HAS_SHAPELY:
        return None
    import math
    points = [(cx + r * math.cos(2 * math.pi * i / segments),
               cy + r * math.sin(2 * math.pi * i / segments))
              for i in range(segments)]
    return Polygon(points)


def bool_subtract(a: Any, b: Any) -> Any:
    """Subtract polygon b from a."""
    if not HAS_SHAPELY or a is None or b is None:
        return None
    return a.difference(b)


def bool_union(a: Any, b: Any) -> Any:
    """Union of two polygons."""
    if not HAS_SHAPELY or a is None or b is None:
        return None
    return a.union(b)


def bool_intersect(a: Any, b: Any) -> Any:
    """Intersection of two polygons."""
    if not HAS_SHAPELY or a is None or b is None:
        return None
    return a.intersection(b)


def _multipolygon_to_paths(geom, scale: float = 1.0) -> list[list[dict]]:
    """Convert a Shapely geometry to a list of path command lists."""
    if geom is None or not HAS_SHAPELY:
        return []

    from shapely.geometry import Polygon as ShapelyPoly

    polygons = []
    if isinstance(geom, ShapelyPoly):
        polygons = [geom]
    elif isinstance(geom, MultiPolygon):
        polygons = list(geom.geoms)
    else:
        return []

    paths = []
    for poly in polygons:
        if poly.is_empty:
            continue
        exterior = list(poly.exterior.coords)
        if len(exterior) < 3:
            continue
        path = []
        path.append({"cmd": "moveTo", "x": exterior[0][0] * scale, "y": exterior[0][1] * scale})
        for x, y in exterior[1:]:
            path.append({"cmd": "lnTo", "x": x * scale, "y": y * scale})
        path.append({"cmd": "close"})
        paths.append(path)
    return paths


def _build_custGeom_shape(slide, paths: list[list[dict]], x_in: float, y_in: float,
                           w_in: float, h_in: float, fill_color: str = "#4472C4",
                           line_color: str | None = None, alpha: int | None = None) -> Any:
    """Build a custGeom shape from path commands."""
    sp_tree = slide.shapes._spTree
    sp = etree.SubElement(sp_tree, qn("p:sp"))

    nvSpPr = etree.SubElement(sp, qn("p:nvSpPr"))
    cNvPr = etree.SubElement(nvSpPr, qn("p:cNvPr"))
    max_id = 1
    for sh in slide.shapes:
        try:
            if sh.shape_id > max_id:
                max_id = sh.shape_id
        except Exception:
            pass
    cNvPr.set("id", str(max_id + 1))
    cNvPr.set("name", "BooleanShape")
    etree.SubElement(nvSpPr, qn("p:cNvSpPr"))
    etree.SubElement(nvSpPr, qn("p:nvPr"))

    spPr = etree.SubElement(sp, qn("p:spPr"))
    xfrm = etree.SubElement(spPr, qn("a:xfrm"))
    off = etree.SubElement(xfrm, qn("a:off"))
    off.set("x", str(int(x_in * EMU_PER_INCH)))
    off.set("y", str(int(y_in * EMU_PER_INCH)))
    ext = etree.SubElement(xfrm, qn("a:ext"))
    ext.set("cx", str(int(w_in * EMU_PER_INCH)))
    ext.set("cy", str(int(h_in * EMU_PER_INCH)))

    custGeom = etree.SubElement(spPr, qn("a:custGeom"))
    etree.SubElement(custGeom, qn("a:avLst"))
    etree.SubElement(custGeom, qn("a:gdLst"))
    pathLst = etree.SubElement(custGeom, qn("a:pathLst"))

    path_w = int(w_in * EMU_PER_INCH)
    path_h = int(h_in * EMU_PER_INCH)
    off_x_emu = int(x_in * EMU_PER_INCH)
    off_y_emu = int(y_in * EMU_PER_INCH)

    for path_cmds in paths:
        path_el = etree.SubElement(pathLst, qn("a:path"))
        path_el.set("w", str(path_w))
        path_el.set("h", str(path_h))
        for cmd in path_cmds:
            if cmd["cmd"] == "moveTo":
                moveTo = etree.SubElement(path_el, qn("a:moveTo"))
                pt = etree.SubElement(moveTo, qn("a:pt"))
                pt.set("x", str(int(cmd["x"] * EMU_PER_INCH) - off_x_emu))
                pt.set("y", str(int(cmd["y"] * EMU_PER_INCH) - off_y_emu))
            elif cmd["cmd"] == "lnTo":
                lnTo = etree.SubElement(path_el, qn("a:lnTo"))
                pt = etree.SubElement(lnTo, qn("a:pt"))
                pt.set("x", str(int(cmd["x"] * EMU_PER_INCH) - off_x_emu))
                pt.set("y", str(int(cmd["y"] * EMU_PER_INCH) - off_y_emu))
            elif cmd["cmd"] == "close":
                etree.SubElement(path_el, qn("a:close"))

    solidFill = etree.SubElement(spPr, qn("a:solidFill"))
    srgb = etree.SubElement(solidFill, qn("a:srgbClr"))
    srgb.set("val", fill_color.lstrip("#"))
    if alpha is not None and 0 <= alpha <= 100:
        a_elem = etree.SubElement(srgb, qn("a:alpha"))
        a_elem.set("val", str(alpha * 1000))

    ln = etree.SubElement(spPr, qn("a:ln"))
    if line_color:
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr")).set("val", line_color.lstrip("#"))
    else:
        etree.SubElement(ln, qn("a:noFill"))

    return sp


def _boolean_to_slide(slide, geom, x_in, y_in, w_in, h_in,
                       fill_color="#4472C4", line_color=None, alpha=None):
    """Convert Shapely geometry to a PPTX shape on the slide."""
    paths = _multipolygon_to_paths(geom, scale=1.0)
    if not paths:
        return None
    return _build_custGeom_shape(slide, paths, x_in, y_in, w_in, h_in,
                                  fill_color=fill_color, line_color=line_color,
                                  alpha=alpha)


def bool_shape(geometry, slide, x, y, w, h, fill=None, line=None, C=None,
               alpha=None):
    """Convert Shapely geometry to a PPTX shape with fill/line colors."""
    if geometry is None:
        return None
    fill_hex = '#4472C4'
    if fill:
        if isinstance(fill, str):
            fill_hex = fill
        elif C and fill in C:
            fill_hex = C[fill]
    line_hex = None
    if line:
        if isinstance(line, str):
            line_hex = line
        elif C and line in C:
            line_hex = C[line]
    return _boolean_to_slide(slide, geometry, x, y, w, h,
                              fill_color=fill_hex, line_color=line_hex,
                              alpha=alpha)
