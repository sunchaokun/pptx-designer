"""Content parser — parse content.json slides[] to PageContent-like dicts."""

from __future__ import annotations

import os
import re
from typing import Any


_GOAL_KEYWORDS: list[tuple[str, list[str]]] = [
    ("problem", ["problem", "pain point", "challenge"]),
    ("solution", ["solution", "approach", "how we"]),
    ("features", ["features", "capability", "what we offer"]),
    ("data", ["tech stack", "data", "metric", "kpi"]),
    ("overview", ["architecture", "overview"]),
    ("code", ["quick start", "getting started", "installation", "usage", "example"]),
    ("cta", ["contact", "get in touch", "next step"]),
    ("overview", ["overview", "agenda", "table of content"]),
]

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}

_COMPONENT_KEYWORDS: list[tuple[str, str, list[str]]] = [
    ("group", "swot", ["strength", "weakness", "opportunity", "threat", "swot"]),
    ("group", "hierarchy", ["hierarchy", "org chart", "CEO", "CTO", "CFO"]),
    ("group", "process", ["process", "step", "phase", "pipeline", "workflow"]),
    ("group", "timeline", ["timeline", "milestone", "roadmap"]),
    ("group", "cycle", ["cycle", "feedback", "loop", "iterate"]),
    ("group", "pyramid", ["pyramid", "layered"]),
    ("group", "matrix", ["matrix", "quadrant"]),
    ("chart", "bar", ["chart", "graph", "bar", "column"]),
    ("chart", "line", ["trend", "growth", "line chart"]),
    ("chart", "pie", ["distribution", "breakdown", "pie", "donut"]),
    ("chart", "radar", ["radar", "spider", "comparison"]),
]


def parse_readme(readme_path: str, project_dir: str) -> list[dict]:
    """Parse README.md into page dicts.

    Args:
        readme_path: Path to README.md
        project_dir: Project directory

    Returns:
        List of page dicts
    """
    if not os.path.exists(readme_path):
        return []

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    pages = []
    current_page = None

    for line in content.split("\n"):
        if line.startswith("# "):
            if current_page:
                pages.append(current_page)
            current_page = {
                "title": line[2:].strip(),
                "bullets": [],
                "goal": "content",
            }
        elif line.startswith("## "):
            if current_page:
                pages.append(current_page)
            current_page = {
                "title": line[3:].strip(),
                "bullets": [],
                "goal": "content",
            }
        elif line.startswith("- ") or line.startswith("* "):
            if current_page:
                current_page["bullets"].append(line[2:].strip())

    if current_page:
        pages.append(current_page)

    return pages


def load_enterprise_content(content_raw: dict, project_dir: str) -> list[dict]:
    """Parse content.json into page dicts.

    Args:
        content_raw: Parsed content.json
        project_dir: Project directory

    Returns:
        List of page dicts
    """
    pages = content_raw.get("pages", [])
    if not pages and "title" in content_raw:
        pages = [{"title": content_raw["title"], "bullets": [], "goal": "content"}]
    return pages


def infer_component_category(bullets: list[str]) -> tuple[str | None, str | None]:
    """Infer component category from bullet content.

    Args:
        bullets: List of bullet strings

    Returns:
        Tuple of (component_type, category) or (None, None)
    """
    text = " ".join(bullets).lower()

    for comp_type, category, keywords in _COMPONENT_KEYWORDS:
        if any(kw.lower() in text for kw in keywords):
            return comp_type, category

    return None, None
