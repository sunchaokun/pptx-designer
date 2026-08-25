"""Visual effects — shape-level effects (gradient, shadow, 3D, pattern).

This module provides backward-compatible imports for the effects module.
For new code, use pptx_designer.effects.shape_effects directly.
"""

from __future__ import annotations

# Re-export from the actual implementation
from pptx_designer.effects.shape_effects import (
    apply_3d,
    apply_bevel,
    apply_frosted_glass,
    apply_glow,
    apply_gradient,
    apply_pattern_fill,
    apply_shadow,
    apply_soft_edge,
)

__all__ = [
    "apply_gradient",
    "apply_shadow",
    "apply_glow",
    "apply_soft_edge",
    "apply_3d",
    "apply_bevel",
    "apply_pattern_fill",
    "apply_frosted_glass",
]
