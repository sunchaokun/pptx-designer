"""Slide utilities �?helper functions for slide manipulation."""

from __future__ import annotations

from typing import Any


def remove_slide(prs: Any, index: int) -> None:
    """Remove a slide by index.

    Args:
        prs: Presentation object
        index: Slide index to remove
    """
    slide_id = prs.slides._sldIdLst[index]
    prs.slides._sldIdLst.remove(slide_id)


