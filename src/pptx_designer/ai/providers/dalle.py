"""DALL-E 3 (OpenAI) image generation provider."""


class DallEProvider:
    """Stub for DALL-E 3 generation."""

    PROVIDER_NAME = "dalle"
    DEFAULT_MODEL = "dall-e-3"
    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.model = model or self.DEFAULT_MODEL

    def generate(self, prompt: str, width: int, height: int) -> str | None:
        raise NotImplementedError("Implement DALL-E generation logic")
