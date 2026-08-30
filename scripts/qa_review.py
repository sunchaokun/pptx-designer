"""Run the offline PPTX QA gate and optional rendered PNG baseline check.

Examples:
    python scripts/qa_review.py deck.pptx --expected-slides 6
    python scripts/qa_review.py deck.pptx --render-dir rendered --baseline-dir baseline
    python scripts/qa_review.py deck.pptx --render-dir rendered --baseline-dir baseline --update-baseline
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from pptx_designer.qa import run_structural_qa
from pptx_designer.qa.visual_baseline import compare, create


def _render(pptx: Path, output: Path, renderer: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(renderer),
        "-InFile",
        str(pptx),
        "-OutDir",
        str(output),
    ]
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--expected-slides", type=int)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--baseline-dir", type=Path)
    parser.add_argument("--renderer", type=Path, default=Path(r"C:\Users\Administrator\.agents\skills\ppt-design-skill\scripts\render_pptx.ps1"))
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    report = {"structural": run_structural_qa(args.pptx, expected_slides=args.expected_slides).to_dict()}
    if args.render_dir:
        if not args.renderer.exists():
            parser.error(f"renderer not found: {args.renderer}")
        _render(args.pptx, args.render_dir, args.renderer)
        if args.baseline_dir:
            if args.update_baseline or not args.baseline_dir.exists():
                report["visual"] = create(args.render_dir, args.baseline_dir)
            else:
                report["visual"] = compare(args.render_dir, args.baseline_dir, args.threshold)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    structural_ok = report["structural"]["status"] != "fail"
    visual_ok = report.get("visual", {}).get("status", "pass") == "pass"
    raise SystemExit(0 if structural_ok and visual_ok else 1)


if __name__ == "__main__":
    main()
