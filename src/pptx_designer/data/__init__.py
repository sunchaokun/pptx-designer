"""
Design Knowledge Base — 40,000+ style combinations.

This module provides access to the complete design knowledge base:
- 192 color schemes (PALETTES)
- 74 font pairs (TYPOGRAPHY)
- 84 style presets (STYLES)

Usage:
    from pptx_designer.data import PALETTES, TYPOGRAPHY, STYLES

    # List all available options
    print(list(PALETTES.keys()))      # 192 palette names
    print(list(TYPOGRAPHY.keys()))    # 74 font pair names
    print(list(STYLES.keys()))        # 84 style preset names

    # Use a palette
    C = PALETTES["cyber-neon"]
    # Returns: {"primary": "#0D0D0D", "secondary": "#FF00FF", ...}

    # Use a font pair
    fonts = TYPOGRAPHY["modern-professional"]
    # Returns: {"heading": "Poppins", "body": "Open Sans", ...}

    # Use a style preset
    style = STYLES["minimalism-swiss-style"]
    # Returns: {"keywords": "Clean, simple, ...", "best_for": "...", ...}
"""

from pptx_designer.data.colors import PALETTES
from pptx_designer.data.typography import TYPOGRAPHY
from pptx_designer.data.styles import STYLES

__all__ = ["PALETTES", "TYPOGRAPHY", "STYLES"]
