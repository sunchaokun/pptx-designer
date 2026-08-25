"""CLI entry point for pptx-designer."""


def main():
    """Run the CLI without importing its module during package initialization."""
    from pptx_designer.cli.main import main as _main

    return _main()


__all__ = ["main"]
