"""Deterministic quality checks for generated PowerPoint files."""

from .structural import StructuralQA, StructuralQAReport, run_structural_qa
from .visual_baseline import compare, create

__all__ = ["StructuralQA", "StructuralQAReport", "compare", "create", "run_structural_qa"]
