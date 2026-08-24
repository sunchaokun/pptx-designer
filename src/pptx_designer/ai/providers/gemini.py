"""Gemini (Google) image generation provider."""


class GeminiProvider:
    """Stub for Gemini image generation."""

    PROVIDER_NAME = "gemini"
    DEFAULT_MODEL = "gemini-2.5-flash-image"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.model = model or self.DEFAULT_MODEL

    def generate(self, prompt: str, width: int, height: int) -> str | None:
        raise NotImplementedError("Implement Gemini generation logic")
