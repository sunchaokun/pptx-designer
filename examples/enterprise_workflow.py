"""Enterprise workflow example: Template-based brand-compliant generation."""

from pptx_designer import extract_design_context, merge_vi_design_context
from pptx_designer.enterprise import ProjectScanner, ProposalGenerator


def merge_template_and_brand(
    template_path: str, brand_override: dict, page_override: dict | None = None
) -> dict:
    """Compose VI inputs without allowing later contexts to change template locks."""
    template_context = extract_design_context(template_path)
    return merge_vi_design_context(template_context, brand_override, page_override)


def main():
    # Method 1: Generate with proposal flow
    # Step 1: Generate style proposals
    proposals = ProposalGenerator().generate(
        query="Q4 business review presentation",
        style="professional",
        output_dir="output/proposals",
    )

    print("Generated proposals:")
    for p in proposals:
        print(f"  {p['id']}: {p['description']}")

    # Step 2: User picks a proposal (e.g., "A")
    # result = generate_ppt(
    #     "Q4 business review",
    #     confirmed_proposal="A",
    #     materials_dir="./my-project",
    # )

    # Method 2: Scan project directory for assets
    scanner = ProjectScanner()
    assets = scanner.scan("./my-project")

    print("\nProject assets found:")
    print(f"  Template: {assets.template_path}")
    print(f"  Logo: {assets.logo_path}")
    print(f"  Brand spec: {assets.brand_raw is not None}")
    print(f"  Content: {assets.content_raw is not None}")
    print(f"  Images: {len(assets.image_pool)}")

    # Method 3: compose a reviewed VI context. Do not use the compatibility
    # merge_design_context() here: it is intentionally last-writer-wins.
    # vi_context = merge_template_and_brand(
    #     assets.template_path,
    #     {"colors": {"primary": "#115E32"}},
    #     {"locks": []},  # Cannot clear template locks.
    # )
    # print(vi_context["diagnostics"]["conflicts"])


if __name__ == "__main__":
    main()
