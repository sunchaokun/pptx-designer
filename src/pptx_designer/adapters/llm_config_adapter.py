"""Conservative bridge to an agent's configured model provider.

Only provider entries that name an environment variable are used.  This keeps
the library from reading OAuth/session credential files or executing host
configuration helpers, neither of which is a portable image-generation API.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

_PROVIDER_ALIASES = {
    "openai": "gpt-image",
    "gpt-image": "gpt-image",
    "gpt_image": "gpt-image",
    "dalle": "dalle",
    "dall-e": "dalle",
    "volcengine": "seedream",
    "ark": "seedream",
    "doubao": "seedream",
    "seedream": "seedream",
    "google": "gemini",
    "gemini": "gemini",
    "dashscope": "wanx",
    "aliyun": "wanx",
    "wanx": "wanx",
    "moonshot": "kimi",
    "kimi": "kimi",
}


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib

        with path.open("rb") as handle:
            value = tomllib.load(handle)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def detect_host_llm_config() -> dict[str, str] | None:
    """Read a Codex image-provider entry backed by an environment key.

    The function intentionally ignores ``auth.json`` and any session token.
    A ChatGPT/Codex login credential is not interchangeable with an image API
    key.  Standard provider variables are handled separately by ImageFetcher.
    """
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    config = _read_toml(codex_home / "config.toml")
    provider_id = str(config.get("image_model_provider") or config.get("model_provider", "")).lower()
    providers = config.get("model_providers", {})
    provider = providers.get(provider_id, {}) if isinstance(providers, dict) else {}
    if not isinstance(provider, dict):
        return None

    env_key = provider.get("env_key")
    api_key = os.environ.get(str(env_key), "") if env_key else ""
    llm_provider = _PROVIDER_ALIASES.get(provider_id, "")
    if not api_key or not llm_provider:
        return None

    result = {
        "llm_provider": llm_provider,
        "llm_api_key": api_key,
        "detected_from": f"codex:{provider_id}",
    }
    if provider.get("base_url"):
        result["llm_base_url"] = str(provider["base_url"])
    image_model = provider.get("image_model") or config.get("image_model")
    if image_model:
        result["llm_model"] = str(image_model)
    return result
