"""Real-template VI Build validation using the unified design context."""

from pathlib import Path

from pptx_designer import Presentation, VIBuildSession, extract_design_context
from pptx_designer.qa import run_structural_qa

TASK_DIR = Path(__file__).parent
TEMPLATE = Path(r"C:\Users\Administrator\Desktop\template.pptx")
PHOTO = TASK_DIR / "assets" / "nordic-sage-cover.png"
OUTPUT = TASK_DIR / "output" / "template-vi-context-validation.pptx"


def component_ids_for_cover(context: dict) -> list[str]:
    """Use the photo and rule grammar observed on template cover slide 1."""
    return [
        component_id
        for component_id, component in context["components"].items()
        if component.get("reference_slide") == 1 and component.get("kind") in {"photo_panel", "rule"}
    ]


context = extract_design_context(str(TEMPLATE))
# Text boxes are deliberately supplied as an explicit, reviewed contract.  The
# extractor does not guess that arbitrary source-page text may be overwritten.
context["content_slots"] = [
    {
        "id": "eyebrow",
        "max_chars": 18,
        "bounds": {"left": 4.2, "top": 2.15, "width": 4.9, "height": 0.35},
        "font_size": 15,
        "bold": True,
        "color": "#FFFFFF",
        "align": "center",
    },
    {
        "id": "page_title",
        "max_chars": 28,
        "bounds": {"left": 3.25, "top": 3.0, "width": 6.85, "height": 0.85},
        "font_size": 40,
        "bold": True,
        "color": "#FFFFFF",
        "align": "center",
    },
    {
        "id": "subtitle",
        "max_chars": 36,
        "bounds": {"left": 3.6, "top": 4.62, "width": 6.1, "height": 0.35},
        "font_size": 16,
        "color": "#FFFFFF",
        "align": "center",
    },
]

prs = Presentation(template_path=str(TEMPLATE), theme=context)
session = VIBuildSession(context, assets={"supporting_photo": str(PHOTO)})
result = session.render_page(
    prs,
    "slide-1-photo",
    components=component_ids_for_cover(context),
    slot_values={
        "eyebrow": "NORDIC BOTANICAL",
        "page_title": "Sage Garden Notes",
        "subtitle": "Asset-aware template inheritance",
    },
)
if result["status"] != "READY":
    raise RuntimeError(result)

OUTPUT.parent.mkdir(exist_ok=True)
prs.save(OUTPUT)
report = run_structural_qa(OUTPUT, expected_slides=6)
print(OUTPUT)
print(result["design_application"])
print(report.to_dict())
if report.status == "fail":
    raise SystemExit(1)
