"""Core pipeline — 4-stage PPT generation."""

from pptx_designer.core.pipeline import Presentation
from pptx_designer.core.planner import StoryPlanner, StoryPlan, PagePlan
from pptx_designer.core.decider import DesignDecider, PageDesign
from pptx_designer.core.content import ContentGenerator, PageContent

__all__ = [
    "Presentation",
    "StoryPlanner",
    "StoryPlan",
    "PagePlan",
    "DesignDecider",
    "PageDesign",
    "ContentGenerator",
    "PageContent",
]
