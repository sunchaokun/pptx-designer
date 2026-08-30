# Visual review

## Render record

- PPTX: `output/template-vi-context-validation.pptx`
- PDF: `render-context/template-vi-context-validation.pdf`
- PNG directory: `render-context/`

## Gate 1 — visual effect

- First visual read: botanical editorial cover page, not a generic theme-colored slide.
- Visual anchor and composition: sage leaves fill the page; the centre-left remains intentionally dark for copy.
- Hierarchy, density, and whitespace: small eyebrow, large title, two thin rules, then a restrained subtitle.
- Direction consistency: new page matches the supplied cover's full-bleed plant photography, white type, and calm Nordic palette.

Result: PASS

## Gate 2 — requirements and defects

| Requirement / slide | Status | Evidence | Cause | Action |
|---|---|---|---|---|
| Preserve source cover / slide 1 | PASS | `render-context/slide01.png` visually matches the template reference | N/A | None |
| New VI page / slide 6 | PASS | `render-context/slide06.png` has botanical full bleed, centred white type and two rules | N/A | None |
| Required image enforcement | PASS | Preflight test returns `NEEDS_ASSET`; no slide is appended | N/A | None |
| Structural delivery | PASS | 6 slides, 41 shapes, 90.2% editable, no fatal/warning QA findings | N/A | None |

## Revision history

| Revision | Change | Failure level | Result |
|---|---|---|---|
| 1 | Added unified context, photo asset and cover archetype components | Visual system | Passed initial render except subtitle/rule collision |
| 2 | Moved subtitle below the inherited lower rule | Local composition | PASS |
