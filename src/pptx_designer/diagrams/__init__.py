"""Diagrams package — structured diagram rendering with native Shapes."""

from pptx_designer.diagrams.base import BaseDiagram
from pptx_designer.diagrams.cycle import CycleDiagram
from pptx_designer.diagrams.diagram_style import DiagramStyle
from pptx_designer.diagrams.flowchart import FlowchartDiagram
from pptx_designer.diagrams.funnel import FunnelDiagram
from pptx_designer.diagrams.hierarchy import HierarchyDiagram
from pptx_designer.diagrams.layout_engine import Region
from pptx_designer.diagrams.matrix import MatrixDiagram
from pptx_designer.diagrams.pyramid import PyramidDiagram
from pptx_designer.diagrams.swot import SwotDiagram
from pptx_designer.diagrams.table import TableDiagram
from pptx_designer.diagrams.timeline import TimelineDiagram
from pptx_designer.diagrams.venn import VennDiagram

__all__ = [
    "BaseDiagram",
    "DiagramStyle",
    "Region",
    "FlowchartDiagram",
    "TimelineDiagram",
    "SwotDiagram",
    "MatrixDiagram",
    "TableDiagram",
    "HierarchyDiagram",
    "VennDiagram",
    "CycleDiagram",
    "FunnelDiagram",
    "PyramidDiagram",
]
