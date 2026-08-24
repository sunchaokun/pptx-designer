"""Wanx (Alibaba DashScope) image generation provider."""


class WanxProvider:
    """Stub for Wanx image generation."""

    PROVIDER_NAME = "wanx"
    DEFAULT_MODEL = "wanx-v1"
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

    def __init__(self, api_key: str, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.model = model or self.DEFAULT_MODEL

    def generate(self, prompt: str, width: int, height: int) -> str | None:
        raise NotImplementedError("Implement Wanx generation logic")
