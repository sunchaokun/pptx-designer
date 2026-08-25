"""Enterprise subpackage — template-driven PPT generation."""

from pptx_designer.enterprise.brand import BrandSpec
from pptx_designer.enterprise.scanner import ProjectScanner, ProjectAsset
from pptx_designer.enterprise.content_parser import parse_readme, load_enterprise_content, infer_component_category
from pptx_designer.enterprise.image_matcher import match_images, assign_images_by_size, auto_generate_image_prompts, classify_image_size
from pptx_designer.enterprise.proposal_generator import ProposalGenerator
from pptx_designer.enterprise.template_analyzer import TemplateAnalyzer
from pptx_designer.enterprise.slide_extractor import SlideExtractor
from pptx_designer.enterprise.delivery_gate import DeliveryGate, QualityReport, CheckItem
from pptx_designer.enterprise.version_manager import next_version, write_meta, read_meta
from pptx_designer.enterprise.design_dna_extractor import DesignDNAExtractor, DesignDNA, SlideDNA, TextZone, PagePlan, extract_design_dna

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
    "extract_design_dna",
]

