"""Create or compare rendered PNG visual regression baselines."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def _pngs(folder: Path) -> dict[str, Path]:
    return {p.name: p for p in folder.glob("*.png")}


def create(rendered: Path, baseline: Path) -> dict:
    baseline.mkdir(parents=True, exist_ok=True)
    images = _pngs(rendered)
    for name, source in images.items():
        shutil.copy2(source, baseline / name)
    return {"status": "created", "images": sorted(images)}


def compare(rendered: Path, baseline: Path, threshold: float = 0.5) -> dict:
    current, expected = _pngs(rendered), _pngs(baseline)
    missing = sorted(set(expected) - set(current))
    added = sorted(set(current) - set(expected))
    differences = []
    for name in sorted(set(current) & set(expected)):
        with Image.open(current[name]).convert("RGBA") as actual, Image.open(expected[name]).convert("RGBA") as reference:
            if actual.size != reference.size:
                differences.append({"image": name, "kind": "size", "actual": actual.size, "expected": reference.size})
                continue
            mean = sum(ImageStat.Stat(ImageChops.difference(actual, reference)).mean) / 4
            if mean > threshold:
                differences.append({"image": name, "kind": "pixel_diff", "mean": round(mean, 4)})
    return {"status": "pass" if not missing and not added and not differences else "fail", "missing": missing, "added": added, "differences": differences}
