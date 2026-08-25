"""Regression tests for image-service configuration and public entry points."""

import os

from pptx_designer.ai import fetch_image
from pptx_designer.ai.fetcher import ImageFetcher
from pptx_designer.utils.env import load_project_dotenv

_IMAGE_ENV = (
    "PPT_IMAGE_LLM_PROVIDER", "PPT_IMAGE_LLM_API_KEY", "PPT_IMAGE_LLM_BASE_URL",
    "PPT_IMAGE_LLM_MODEL", "OPENAI_API_KEY", "ARK_API_KEY", "GEMINI_API_KEY",
    "DASHSCOPE_API_KEY", "MOONSHOT_API_KEY", "UNSPLASH_ACCESS_KEY", "PEXELS_API_KEY",
)


def _clear_image_env(monkeypatch):
    for name in _IMAGE_ENV:
        monkeypatch.delenv(name, raising=False)


def test_auto_detect_is_safe_without_optional_host_adapter(monkeypatch):
    """Standalone installs must work without a configured host provider."""
    _clear_image_env(monkeypatch)
    fetcher = ImageFetcher(mode="auto", auto_detect=True)
    assert fetcher.mode == "auto"
    assert fetcher.llm_provider == ""


def test_provider_key_selects_provider_without_generic_setting(monkeypatch):
    _clear_image_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    fetcher = ImageFetcher(mode="auto", auto_detect=True)

    assert fetcher.llm_provider == "gpt-image"
    assert fetcher.llm_api_key == "test-key"
    assert fetcher._detected_from == "environment:OPENAI_API_KEY"


def test_explicit_provider_alias_and_arguments_win(monkeypatch):
    _clear_image_env(monkeypatch)
    monkeypatch.setenv("ARK_API_KEY", "environment-key")

    fetcher = ImageFetcher(llm_provider="openai", llm_api_key="argument-key")

    assert fetcher.llm_provider == "gpt-image"
    assert fetcher.llm_api_key == "argument-key"


def test_nearest_project_dotenv_loads_without_overwriting_environment(monkeypatch, tmp_path):
    _clear_image_env(monkeypatch)
    project = tmp_path / "project"
    nested = project / "slides" / "build"
    nested.mkdir(parents=True)
    (project / ".env").write_text(
        "OPENAI_API_KEY=from-dotenv\nPPT_IMAGE_LLM_PROVIDER=gpt-image\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(nested)
    monkeypatch.setenv("OPENAI_API_KEY", "from-environment")

    assert load_project_dotenv() == project / ".env"
    assert os.environ["OPENAI_API_KEY"] == "from-environment"
    fetcher = ImageFetcher()
    assert fetcher.llm_provider == "gpt-image"
    assert fetcher.llm_api_key == "from-environment"


def test_public_fetch_image_returns_safe_metadata(monkeypatch, tmp_path):
    _clear_image_env(monkeypatch)
    result = fetch_image("test image", mode="placeholder", image_cache_dir=str(tmp_path))

    assert result["path"] is None
    assert result["mode"] == "placeholder"
    assert "api_key" not in result


def test_host_image_generator_is_the_no_key_auto_fallback(monkeypatch, tmp_path):
    _clear_image_env(monkeypatch)
    image_path = tmp_path / "generated.png"
    image_path.write_bytes(b"host generated image")
    seen = {}

    def generate_from_host(**kwargs):
        seen.update(kwargs)
        return str(image_path)

    fetcher = ImageFetcher(mode="auto", host_image_generator=generate_from_host)
    assert fetcher.fetch("a premium fragrance bottle", goal="hook") == str(image_path)
    assert seen["keywords"] == "a premium fragrance bottle"
    assert seen["goal"] == "hook"
    assert fetcher._detected_from == "host-image-generator"


def test_codex_provider_entry_is_used_only_with_an_environment_key(monkeypatch, tmp_path):
    _clear_image_env(monkeypatch)
    codex_home = tmp_path / "codex"
    codex_home.mkdir()
    (codex_home / "config.toml").write_text(
        "model_provider = 'company-openai'\n"
        "model = 'gpt-5.3-codex'\n"
        "[model_providers.company-openai]\n"
        "env_key = 'COMPANY_OPENAI_KEY'\n"
        "base_url = 'https://images.example.test/v1'\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("COMPANY_OPENAI_KEY", "agent-provider-key")

    # Unknown provider ids intentionally do not infer an image API protocol.
    assert ImageFetcher(auto_detect=True).llm_provider == ""

    (codex_home / "config.toml").write_text(
        "model_provider = 'openai'\n"
        "model = 'gpt-5.3-codex'\n"
        "[model_providers.openai]\n"
        "env_key = 'COMPANY_OPENAI_KEY'\n"
        "base_url = 'https://images.example.test/v1'\n",
        encoding="utf-8",
    )
    fetcher = ImageFetcher(auto_detect=True)
    assert fetcher.llm_provider == "gpt-image"
    assert fetcher.llm_api_key == "agent-provider-key"
    assert fetcher.llm_base_url == "https://images.example.test/v1"
    assert fetcher.llm_model == ""

    (codex_home / "config.toml").write_text(
        "model_provider = 'openai'\n"
        "model = 'gpt-5.3-codex'\n"
        "image_model = 'gpt-image-1'\n"
        "[model_providers.openai]\n"
        "env_key = 'COMPANY_OPENAI_KEY'\n"
        "base_url = 'https://images.example.test/v1'\n",
        encoding="utf-8",
    )
    fetcher = ImageFetcher(auto_detect=True)
    assert fetcher.llm_model == "gpt-image-1"
    assert fetcher._detected_from == "codex:openai"
