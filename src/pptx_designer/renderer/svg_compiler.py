"""SVG compiler — compatibility shim.

This module now forwards to the real implementation in
``pptx_designer.compiler``. New code should import from there directly::

    from pptx_designer.compiler import SVGCompiler, SVGCompileError, SVGResult
"""

from __future__ import annotations

from typing import Any

from pptx_designer.compiler import SVGCompileError, SVGCompiler, SVGResult  # noqa: F401

__all__ = ["SVGCompileError", "SVGCompiler", "SVGResult"]
