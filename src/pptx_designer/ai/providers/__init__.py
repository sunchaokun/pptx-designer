"""AI providers — image generation adapters."""

from pptx_designer.ai.providers.seedream import SeedreamProvider
from pptx_designer.ai.providers.gpt_image import GPTImageProvider
from pptx_designer.ai.providers.dalle import DallEProvider
from pptx_designer.ai.providers.gemini import GeminiProvider
from pptx_designer.ai.providers.wanx import WanxProvider
from pptx_designer.ai.providers.kimi import KimiProvider

__all__ = [
    "SeedreamProvider",
    "GPTImageProvider",
    "DallEProvider",
    "GeminiProvider",
    "WanxProvider",
    "KimiProvider",
]
