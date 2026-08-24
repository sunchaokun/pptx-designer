# Advanced examples

These examples are complete, editable PowerPoint decks—not screenshots or
synthetic API fragments. Each script uses the public `pptx_designer` API and
generates the adjacent `.pptx` file.

| Case | Source | Output | What it demonstrates |
|---|---|---|---|
| Executive business review | [advanced_business_review.py](advanced_business_review.py) | [advanced_business_review.pptx](advanced_business_review.pptx) | Cover, agenda, KPI cards, editable bar chart, flow diagram, and decision page. |
| Product strategy roadmap | [advanced_product_strategy.py](advanced_product_strategy.py) | [advanced_product_strategy.pptx](advanced_product_strategy.pptx) | Cover, strategy narrative, component cards, timeline, and outcome scorecard. |
| SVG architecture review | [advanced_svg_architecture.py](advanced_svg_architecture.py) | [advanced_svg_architecture.pptx](advanced_svg_architecture.pptx) | Cover, agenda, an SVG architecture diagram compiled into native PPT objects, and architecture principles. |

## Run an example

From the repository root:

```bash
python examples/advanced_business_review.py
python examples/advanced_product_strategy.py
python examples/advanced_svg_architecture.py
```

Each script overwrites only its own adjacent `.pptx` output. The decks use
16:9 pages and native PowerPoint shapes/text wherever the selected component
supports them.

## Evaluation checklist

Open an output deck in PowerPoint or LibreOffice and verify that:

1. Every deck has four pages: cover, agenda, core content, and decision/summary.
2. Titles, labels, KPI values, and diagram nodes can be selected and edited.
3. The core-content page has no accidental clipping, overlap, or off-slide objects.
4. The SVG architecture deck contains editable shapes and text rather than a
   single embedded screenshot.

For automated structural verification, each deck is also reopened during the
repository's example validation process to confirm its page and shape counts.
