"""Core pipeline — 4-stage PPT generation."""

from pptx_designer.core.content import ContentGenerator, PageContent
from pptx_designer.core.decider import DesignDecider, PageDesign
from pptx_designer.core.pipeline import Presentation
from pptx_designer.core.planner import PagePlan, StoryPlan, StoryPlanner

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
