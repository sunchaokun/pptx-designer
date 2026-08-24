"""Regression tests for optional image-service configuration."""

from pptx_designer.ai.fetcher import ImageFetcher


def test_auto_detect_is_safe_without_optional_host_adapter(monkeypatch):
    """Standalone installs must not require a host-specific adapter module."""
    monkeypatch.delenv("PPT_IMAGE_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("PPT_IMAGE_LLM_API_KEY", raising=False)
    fetcher = ImageFetcher(mode="auto", auto_detect=True)
    assert fetcher.mode == "auto"
