"""Enterprise subpackage — template-driven PPT generation."""

from pptx_designer.enterprise.brand import BrandSpec
from pptx_designer.enterprise.content_parser import infer_component_category, load_enterprise_content, parse_readme
from pptx_designer.enterprise.delivery_gate import CheckItem, DeliveryGate, QualityReport
from pptx_designer.enterprise.design_dna_extractor import (
    DesignDNA,
    DesignDNAExtractor,
    PagePlan,
    SlideDNA,
    TextZone,
    extract_design_context,
    extract_design_dna,
)
from pptx_designer.enterprise.image_matcher import (
    assign_images_by_size,
    auto_generate_image_prompts,
    classify_image_size,
    match_images,
)
from pptx_designer.enterprise.proposal_generator import ProposalGenerator
from pptx_designer.enterprise.scanner import ProjectAsset, ProjectScanner
from pptx_designer.enterprise.slide_extractor import SlideExtractor
from pptx_designer.enterprise.template_analyzer import TemplateAnalyzer
from pptx_designer.enterprise.version_manager import next_version, read_meta, write_meta
from pptx_designer.enterprise.vi_context import (
    VIBuildSession,
    design_context_from_brand_spec,
    normalize_design_context,
)

__all__ = [
    "BrandSpec",
    "ProjectScanner",
    "ProjectAsset",
    "parse_readme",
    "load_enterprise_content",
    "infer_component_category",
    "match_images",
    "assign_images_by_size",
    "auto_generate_image_prompts",
    "classify_image_size",
    "ProposalGenerator",
    "TemplateAnalyzer",
    "SlideExtractor",
    "DeliveryGate",
    "QualityReport",
    "CheckItem",
    "next_version",
    "write_meta",
    "read_meta",
    "DesignDNAExtractor",
    "DesignDNA",
    "SlideDNA",
    "TextZone",
    "PagePlan",
    "extract_design_context",
    "extract_design_dna",
    "VIBuildSession",
    "design_context_from_brand_spec",
    "normalize_design_context",
]
