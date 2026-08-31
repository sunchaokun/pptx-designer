"""Production delivery boundary for template-backed VI Build decks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

from pptx_designer.enterprise.prototype import prune_unreferenced_slide_parts
from pptx_designer.qa import StructuralQAReport, run_structural_qa


class VIBuildDelivery:
    """Build a delivery deck without leaking template source pages.

    A template presentation is temporarily retained only as a read source for
    framework prototypes and fixed visual layers. ``finalize`` removes exactly
    those original slide identities, then validates the surviving delivery
    pages against the supplied BuildSpecs.
    """

    def __init__(self, presentation: Any, adapter: Any) -> None:
        self.presentation = presentation
        self.adapter = adapter
        self._template_slide_ids = {item.id for item in presentation.slides._sldIdLst}
        self._plans: list[dict[str, Any]] = []
        self._finalized = False

    @property
    def plans(self) -> list[dict[str, Any]]:
        return deepcopy(self._plans)

    def add(self, spec: Mapping[str, Any]) -> Any:
        if self._finalized:
            raise RuntimeError("cannot add a page after delivery finalization")
        plan = deepcopy(dict(spec))
        origin = plan.get("delivery_origin")
        if origin not in {"framework_rebound", "build_atomic", "build_components"}:
            raise ValueError("delivery BuildSpec has no approved page origin")
        slide = self.adapter.render(plan, self.presentation)
        self._plans.append(plan)
        return slide

    def finalize(
        self,
        path: str | Path,
        *,
        sample_texts: Sequence[str] | None = None,
        check_overlaps: bool = True,
        edge_tolerance_in: float = 0.02,
    ) -> StructuralQAReport:
        if self._finalized:
            raise RuntimeError("delivery has already been finalized")
        self._remove_template_source_slides()
        if len(self.presentation.slides) != len(self._plans):
            raise ValueError("delivery page count does not match the planned BuildSpecs")
        for page_number, plan in enumerate(self._plans, start=1):
            plan["page_number"] = page_number
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        self.presentation.save(output)
        prune_unreferenced_slide_parts(str(output))
        report = run_structural_qa(
            output,
            expected_slides=len(self._plans),
            vi_plans=self._plans,
            sample_texts=list(sample_texts or []),
            check_overlaps=check_overlaps,
            edge_tolerance_in=edge_tolerance_in,
        )
        self._finalized = True
        if report.status == "fail":
            raise ValueError("delivery QA failed")
        return report

    def _remove_template_source_slides(self) -> None:
        """Remove original template pages by immutable slide identity, not order."""
        for item in list(self.presentation.slides._sldIdLst):
            if item.id not in self._template_slide_ids:
                continue
            relationship_id = item.rId
            self.presentation.part.drop_rel(relationship_id)
            self.presentation.slides._sldIdLst.remove(item)


__all__ = ["VIBuildDelivery"]
