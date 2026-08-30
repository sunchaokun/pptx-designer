"""Offline, deterministic checks for PPTX delivery reliability.

This module deliberately avoids subjective visual scoring.  It checks whether
the file can be reopened, whether content stays inside the slide, whether
text is plausibly readable, and whether the deck remains natively editable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


@dataclass
class QAIssue:
    slide: int | None
    kind: str
    severity: str
    message: str


@dataclass
class StructuralQAReport:
    status: str
    fatal: list[QAIssue] = field(default_factory=list)
    warnings: list[QAIssue] = field(default_factory=list)
    slide_count: int = 0
    shape_count: int = 0
    editable_ratio: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StructuralQA:
    """Run deterministic delivery checks against a PowerPoint file."""

    def __init__(self, *, min_font_size_pt: float = 9.0, edge_tolerance_in: float = 0.02) -> None:
        self.min_font_size_pt = min_font_size_pt
        self.edge_tolerance_in = edge_tolerance_in

    def check(self, path: str | Path, *, expected_slides: int | None = None) -> StructuralQAReport:
        report = StructuralQAReport(status="pass")
        try:
            prs = Presentation(str(path))
        except Exception as exc:  # pragma: no cover - exact parser errors vary by python-pptx version
            report.status = "fail"
            report.fatal.append(QAIssue(None, "unreadable_file", "fatal", f"Cannot reopen PPTX: {exc}"))
            return report

        report.slide_count = len(prs.slides)
        if expected_slides is not None and report.slide_count != expected_slides:
            report.fatal.append(
                QAIssue(None, "slide_count", "fatal", f"Expected {expected_slides} slides, found {report.slide_count}")
            )

        slide_w = prs.slide_width / 914400.0
        slide_h = prs.slide_height / 914400.0
        total = editable = 0
        for slide_no, slide in enumerate(prs.slides, start=1):
            for shape_no, shape in enumerate(slide.shapes, start=1):
                total += 1
                if shape.shape_type not in {MSO_SHAPE_TYPE.GROUP, MSO_SHAPE_TYPE.PICTURE}:
                    editable += 1
                self._check_bounds(report, slide_no, shape_no, shape, slide_w, slide_h)
                self._check_text(report, slide_no, shape_no, shape)
        report.shape_count = total
        report.editable_ratio = editable / total if total else 1.0
        if total and report.editable_ratio < 0.8:
            report.warnings.append(
                QAIssue(None, "editable_ratio", "warning", f"Native editable shape ratio is {report.editable_ratio:.2f}")
            )
        if report.fatal:
            report.status = "fail"
        elif report.warnings:
            report.status = "pass_with_warnings"
        return report

    def _check_bounds(self, report, slide_no, shape_no, shape, slide_w, slide_h) -> None:
        x = shape.left / 914400.0
        y = shape.top / 914400.0
        w = shape.width / 914400.0
        h = shape.height / 914400.0
        if x < -self.edge_tolerance_in or y < -self.edge_tolerance_in or x + w > slide_w + self.edge_tolerance_in or y + h > slide_h + self.edge_tolerance_in:
            report.fatal.append(
                QAIssue(slide_no, "out_of_bounds", "fatal", f"Shape {shape_no} exceeds slide bounds: ({x:.2f},{y:.2f},{w:.2f},{h:.2f})")
            )

    def _check_text(self, report, slide_no, shape_no, shape) -> None:
        if not getattr(shape, "has_text_frame", False):
            return
        text = shape.text.strip()
        if not text:
            return
        sizes = [run.font.size.pt for paragraph in shape.text_frame.paragraphs for run in paragraph.runs if run.font.size]
        if sizes and min(sizes) < self.min_font_size_pt:
            report.warnings.append(
                QAIssue(slide_no, "small_text", "warning", f"Shape {shape_no} contains {min(sizes):g}pt text")
            )
        lines = max(text.count("\n") + 1, len(shape.text_frame.paragraphs))
        if sizes and shape.height / 914400.0 < lines * min(sizes) * 1.15 / 72.0:
            report.warnings.append(QAIssue(slide_no, "text_box_height", "warning", f"Shape {shape_no} may clip {lines} text lines"))


def run_structural_qa(path: str | Path, *, expected_slides: int | None = None, **kwargs) -> StructuralQAReport:
    return StructuralQA(**kwargs).check(path, expected_slides=expected_slides)
