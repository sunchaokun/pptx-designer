"""AI image generation — 5 engines + stock search."""

from pptx_designer.ai.fetcher import ImageFetcher


def fetch_image(
    keywords: str,
    *,
    mode: str = "auto",
    emotion: str = "",
    goal: str = "",
    width: int = 1920,
    height: int = 1080,
    **config,
) -> dict[str, str | None]:
    """Fetch or generate one image and return its path plus safe metadata."""
    fetcher = ImageFetcher(mode=mode, **config)
    path = fetcher.fetch(keywords, emotion=emotion, goal=goal, width=width, height=height)
    return {
        "path": path,
        "mode": mode,
        "provider": fetcher.llm_provider or None,
        "model": fetcher.llm_model or None,
        "detected_from": fetcher._detected_from or None,
    }

__all__ = [
    "ImageFetcher",
    "fetch_image",
]
