"""Shape utilities — helper functions for shape manipulation."""

from __future__ import annotations

from typing import Any


def group_shapes(slide: Any, shape_indices: list[int]) -> Any:
    """Group shapes on a slide.

    Args:
        slide: Slide object
        shape_indices: List of shape indices to group

    Returns:
        GroupShape or None
    """
    if not shape_indices:
        return None

    try:
        from pptx.oxml.ns import qn
        from lxml import etree

        # Get the slide's shape tree
        sp_tree = slide.shapes._spTree

        # Create group shape element
        grpSp = etree.SubElement(sp_tree, qn('p:grpSp'))

        # Get the first shape to determine grouping bounds
        first_shape = slide.shapes[shape_indices[0]]
        grpSpPr = etree.SubElement(grpSp, qn('p:grpSpPr'))

        # Set group bounds (simplified - use first shape's position)
        x = first_shape.left
        y = first_shape.top
        cx = first_shape.width
        cy = first_shape.height

        # Add transform
        xfrm = etree.SubElement(grpSpPr, qn('a:xfrm'))
        off = etree.SubElement(xfrm, qn('a:off'))
        off.set('x', str(x))
        off.set('y', str(y))
        ext = etree.SubElement(xfrm, qn('a:ext'))
        ext.set('cx', str(cx))
        ext.set('cy', str(cy))
        ch = etree.SubElement(xfrm, qn('a:ch'))
        ch.set('x', str(x))
        ch.set('y', str(y))
        chExt = etree.SubElement(xfrm, qn('a:chExt'))
        chExt.set('cx', str(cx))
        chExt.set('cy', str(cy))

        return grpSp
    except Exception:
        return None
