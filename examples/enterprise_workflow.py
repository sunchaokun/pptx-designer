"""Enterprise workflow example: Template-based brand-compliant generation."""

from pptx_designer import generate_ppt
from pptx_designer.enterprise import ProjectScanner, ProposalGenerator


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

    print(f"\nProject assets found:")
    print(f"  Template: {assets.template_path}")
    print(f"  Logo: {assets.logo_path}")
    print(f"  Brand spec: {assets.brand_raw is not None}")
    print(f"  Content: {assets.content_raw is not None}")
    print(f"  Images: {len(assets.image_pool)}")


if __name__ == "__main__":
    main()
