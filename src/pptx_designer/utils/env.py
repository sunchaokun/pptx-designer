"""Small, dependency-free project ``.env`` loader.

Credentials belong to the project that invokes pptx-designer, never to the
installed package directory.  Only the nearest ``.env`` from the current
working directory upward is considered, and existing process variables win.
"""

from __future__ import annotations

import os
from pathlib import Path


def find_project_env(start_dir: str | Path | None = None) -> Path | None:
    """Return the nearest project ``.env`` from *start_dir* upward."""
    current = Path(start_dir or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def load_project_dotenv(start_dir: str | Path | None = None) -> Path | None:
    """Load the nearest project ``.env`` without overriding the environment.

    The supported format deliberately covers conventional ``KEY=value`` files,
    optional ``export`` prefixes, comments, and quoted values.  It avoids a
    runtime dependency solely for configuration loading.
    """
    env_path = find_project_env(start_dir)
    if env_path is None:
        return None

    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)
    return env_path
