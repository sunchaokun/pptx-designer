"""Core planning, rendering, and BuildSpec contracts."""

from pptx_designer.core.content import ContentGenerator, PageContent
from pptx_designer.core.decider import DesignDecider, PageDesign
from pptx_designer.core.pipeline import Presentation
from pptx_designer.core.planner import PagePlan, StoryPlan, StoryPlanner

from .build_spec import render_build_spec

__all__ = [
    "Presentation",
    "StoryPlanner",
    "StoryPlan",
    "PagePlan",
    "DesignDecider",
    "PageDesign",
    "ContentGenerator",
    "PageContent",
    "render_build_spec",
]
