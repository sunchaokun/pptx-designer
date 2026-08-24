"""GPT Image (OpenAI) image generation provider."""


class GPTImageProvider:
    """Stub for GPT Image generation."""

    PROVIDER_NAME = "gpt-image"
    DEFAULT_MODEL = "gpt-image-1"
    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.model = model or self.DEFAULT_MODEL

    def generate(self, prompt: str, width: int, height: int) -> str | None:
        raise NotImplementedError("Implement GPT Image generation logic")
