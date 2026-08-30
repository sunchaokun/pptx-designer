"""CLI for rendered PNG visual regression baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pptx_designer.qa.visual_baseline import compare, create


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("create", "compare"))
    parser.add_argument("rendered", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    result = create(args.rendered, args.baseline) if args.command == "create" else compare(args.rendered, args.baseline, args.threshold)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] in {"created", "pass"} else 1)


if __name__ == "__main__":
    main()
