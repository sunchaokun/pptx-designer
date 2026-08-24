"""Convert CSV design databases to Python modules.

Usage:
    python scripts/csv_to_python.py

Reads data/*.csv and generates data/*.py files.
Run this after editing CSV files to update the Python modules.
"""

import csv
import re
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to a valid Python variable name."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text


def convert_colors(data_dir: Path, output_dir: Path):
    """Convert colors.csv to colors.py."""
    csv_path = data_dir / "colors.csv"
    py_path = output_dir / "colors.py"

    palettes = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = slugify(row.get("Product Type", f"palette-{row['No']}"))
            palette = {
                "primary": row.get("Primary", "#000000"),
                "on-primary": row.get("On Primary", "#FFFFFF"),
                "secondary": row.get("Secondary", "#666666"),
                "on-secondary": row.get("On Secondary", "#FFFFFF"),
                "accent": row.get("Accent", "#0066CC"),
                "on-accent": row.get("On Accent", "#FFFFFF"),
                "background": row.get("Background", "#FFFFFF"),
                "foreground": row.get("Foreground", "#000000"),
                "card": row.get("Card", "#FFFFFF"),
                "card-foreground": row.get("Card Foreground", "#000000"),
                "muted": row.get("Muted", "#E5E5E5"),
                "muted-foreground": row.get("Muted Foreground", "#737373"),
                "border": row.get("Border", "#E5E5E5"),
                "destructive": row.get("Destructive", "#DC2626"),
                "on-destructive": row.get("On Destructive", "#FFFFFF"),
                "ring": row.get("Ring", "#0066CC"),
                "notes": row.get("Notes", ""),
            }
            palettes.append((name, palette))

    with open(py_path, "w", encoding="utf-8") as f:
        f.write('"""192 color schemes — the design knowledge base.\n\n')
        f.write("Generated from colors.csv. Do not edit manually.\n")
        f.write("Run: python scripts/csv_to_python.py to regenerate.\n\n")
        f.write("Usage:\n")
        f.write("    from pptx_designer.data.colors import PALETTES\n")
        f.write('    C = PALETTES["saas-general"]\n')
        f.write('"""\n\n\n')
        f.write("PALETTES: dict[str, dict[str, str]] = {\n")

        for name, palette in palettes:
            f.write(f'    "{name}": {{\n')
            for key, value in palette.items():
                if key == "notes":
                    f.write(f'        "{key}": {repr(value)},\n')
                else:
                    f.write(f'        "{key}": "{value}",\n')
            f.write("    },\n")

        f.write("}\n")

    print(f"Generated {py_path} ({len(palettes)} palettes)")


def convert_typography(data_dir: Path, output_dir: Path):
    """Convert typography.csv to typography.py."""
    csv_path = data_dir / "typography.csv"
    py_path = output_dir / "typography.py"

    fonts = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = slugify(row.get("Font Pairing Name", f"font-{row['No']}"))
            font_pair = {
                "heading": row.get("Heading Font", "Arial"),
                "body": row.get("Body Font", "Arial"),
                "category": row.get("Category", ""),
                "mood": row.get("Mood/Style Keywords", ""),
                "best_for": row.get("Best For", ""),
                "notes": row.get("Notes", ""),
            }
            fonts.append((name, font_pair))

    with open(py_path, "w", encoding="utf-8") as f:
        f.write('"""74 font pairs — the typography knowledge base.\n\n')
        f.write("Generated from typography.csv. Do not edit manually.\n")
        f.write("Run: python scripts/csv_to_python.py to regenerate.\n\n")
        f.write("Usage:\n")
        f.write("    from pptx_designer.data.typography import TYPOGRAPHY\n")
        f.write('    fonts = TYPOGRAPHY["modern-professional"]\n')
        f.write('    heading_font = fonts["heading"]  # "Poppins"\n')
        f.write('"""\n\n\n')
        f.write("TYPOGRAPHY: dict[str, dict[str, str]] = {\n")

        for name, font_pair in fonts:
            f.write(f'    "{name}": {{\n')
            for key, value in font_pair.items():
                f.write(f'        "{key}": {repr(value)},\n')
            f.write("    },\n")

        f.write("}\n")

    print(f"Generated {py_path} ({len(fonts)} font pairs)")


def convert_styles(data_dir: Path, output_dir: Path):
    """Convert styles.csv to styles.py."""
    csv_path = data_dir / "styles.csv"
    py_path = output_dir / "styles.py"

    styles = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = slugify(row.get("Style Category", f"style-{row['No']}"))
            style = {
                "category": row.get("Style Category", ""),
                "type": row.get("Type", ""),
                "keywords": row.get("Keywords", ""),
                "primary_colors": row.get("Primary Colors", ""),
                "secondary_colors": row.get("Secondary Colors", ""),
                "best_for": row.get("Best For", ""),
                "do_not_use_for": row.get("Do Not Use For", ""),
                "light_mode": row.get("Light Mode ✓", ""),
                "dark_mode": row.get("Dark Mode ✓", ""),
                "performance": row.get("Performance", ""),
                "accessibility": row.get("Accessibility", ""),
                "complexity": row.get("Complexity", ""),
                "ai_prompt_keywords": row.get("AI Prompt Keywords", ""),
            }
            styles.append((name, style))

    with open(py_path, "w", encoding="utf-8") as f:
        f.write('"""84 style presets — the style knowledge base.\n\n')
        f.write("Generated from styles.csv. Do not edit manually.\n")
        f.write("Run: python scripts/csv_to_python.py to regenerate.\n\n")
        f.write("Usage:\n")
        f.write("    from pptx_designer.data.styles import STYLES\n")
        f.write('    style = STYLES["minimalism-swiss-style"]\n')
        f.write('    keywords = style["keywords"]\n')
        f.write('"""\n\n\n')
        f.write("STYLES: dict[str, dict[str, str]] = {\n")

        for name, style in styles:
            f.write(f'    "{name}": {{\n')
            for key, value in style.items():
                f.write(f'        "{key}": {repr(value)},\n')
            f.write("    },\n")

        f.write("}\n")

    print(f"Generated {py_path} ({len(styles)} styles)")


def main():
    # Find project root (parent of scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "src" / "pptx_designer" / "data"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return

    print(f"Converting CSV files in {data_dir}...")

    convert_colors(data_dir, data_dir)
    convert_typography(data_dir, data_dir)
    convert_styles(data_dir, data_dir)

    print("\nDone! Python modules generated.")
    print("Import with: from pptx_designer.data import PALETTES, TYPOGRAPHY, STYLES")


if __name__ == "__main__":
    main()
