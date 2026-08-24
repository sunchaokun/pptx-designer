# Contributing to pptx-designer

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/sunchaokun/pptx-designer.git
cd pptx-designer

# Install in development mode
pip install -e ".[dev]"

# Verify installation
python -c "import pptx_designer; print(pptx_designer.__version__)"
```

## Code Style

- **Formatter/Linter**: We use [ruff](https://docs.astral.sh/ruff/) with 120 char line length
- **Type hints**: Add type hints to all public functions
- **Docstrings**: Use Google-style docstrings for public APIs

```python
def generate_ppt(
    query: str,
    *,
    style: str | None = None,
    slides: int = 6,
) -> dict[str, Any]:
    """Generate a PowerPoint presentation from a text description.

    Args:
        query: Natural language description of the presentation.
        style: Design style (e.g., "dark cyberpunk", "warm elegant").
        slides: Number of slides to generate.

    Returns:
        Dictionary with keys: output_path, slide_count, shapes_count.
    """
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -q

# Run with coverage
python -m pytest tests/ --cov=pptx_designer --cov-report=html

# Run specific test file
python -m pytest tests/test_api/test_generate.py -v
```

## Running Lint

```bash
# Check lint
python -m ruff check src/

# Auto-fix lint issues
python -m ruff check src/ --fix

# Type check
python -m mypy src/pptx_designer/
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Make** your changes with tests
4. **Run** lint and tests to ensure nothing is broken
5. **Commit** with a clear message: `git commit -m "feat: add new diagram type"`
6. **Push** to your fork: `git push origin feature/my-feature`
7. **Open** a Pull Request

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` formatting changes
- `refactor:` code refactoring
- `test:` adding tests
- `chore:` maintenance tasks

### PR Requirements

- All tests must pass
- Lint must be clean
- New features must include tests
- Documentation must be updated if API changes

## Project Structure

```
src/pptx_designer/
├── core/           4-stage pipeline
├── renderer/       Unified rendering engine
├── effects/        Text, shape, image effects
├── diagrams/       10 diagram engines
├── compiler/       SVG → PPTX compiler
├── enterprise/     Enterprise features
├── ai/             Image generation
├── tools/          Build-mode atoms
├── search/         Design knowledge search
├── utils/          Utilities
└── data/           Bundled CSV databases
```

## Adding a New Diagram Type

1. Create `src/pptx_designer/diagrams/my_diagram.py`
2. Inherit from `BaseDiagram`
3. Implement `render(slide, data, region, style)`
4. Register in `engine.py`
5. Add tests in `tests/test_diagrams/`

## Adding a New Effect

1. Choose the appropriate module (`text_fx.py`, `shape_fx.py`, or `image_fx.py`)
2. Implement the effect function
3. Add convenience wrapper in `build_helpers.py` (for backward compat)
4. Add tests

## Questions?

Open an issue at https://github.com/sunchaokun/pptx-designer/issues
