"""Theme mapper — design system to PPT theme mapping."""

from __future__ import annotations

# CJK font companions
CJK_COMPANIONS = {
    "Arial": "Microsoft YaHei",
    "Calibri": "Microsoft YaHei",
    "Segoe UI": "Microsoft YaHei",
    "Helvetica": "PingFang SC",
    "Times New Roman": "SimSun",
    "Georgia": "SimSun",
    "Verdana": "Microsoft YaHei",
    "Tahoma": "Microsoft YaHei",
    "Trebuchet MS": "Microsoft YaHei",
    "Consolas": "Microsoft YaHei",
}


def get_cjk_companion(latin_font: str) -> str:
    """Get CJK companion font for a Latin font.

    Args:
        latin_font: Latin font name

    Returns:
        CJK font name
    """
    return CJK_COMPANIONS.get(latin_font, "Microsoft YaHei")
