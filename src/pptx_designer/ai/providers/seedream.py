"""Seedream (ByteDance Volcengine) image generation provider."""


class SeedreamProvider:
    """Stub for Seedream image generation."""

    PROVIDER_NAME = "seedream"
    DEFAULT_MODEL = "doubao-seedream-4-5-251128"
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

    def __init__(self, api_key: str, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.model = model or self.DEFAULT_MODEL

    def generate(self, prompt: str, width: int, height: int) -> str | None:
        raise NotImplementedError("Implement Seedream generation logic")
