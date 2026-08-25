# Changelog

All notable user-facing changes are recorded here. This project follows a pre-release versioning scheme before the first stable `1.0.0` release.

## 1.0.0b3 — 2026-08-25

### Examples

- Reworked the four-page couture editorial example as a deconstructed fashion lookbook, with distinct manifesto, silhouette-study, material-index, and salon-poster layouts.
- Kept all editorial copy, typography, colour fields, labels, and geometric accents as native, editable PowerPoint objects; photography remains an atmosphere layer only.
- Added visual rendering verification to the example revision workflow using LibreOffice PDF/PNG output.

## 1.0.0-beta.2 — 2026-08-24

### SVG compiler

- Added structured compilation diagnostics through `SVGResult` / `SVGRenderReport`, including generated shapes, warnings, features, metrics, IR snapshot, and runtime source-to-output references.
- Added CSS materialization support and SVG IR snapshots for analysis and regression testing.
- Added input limits for SVG size, node count, path command count, and tree depth.
- Improved text sizing fallback and tspan font-size handling; group opacity now fails safely instead of silently producing an incorrect native rendering.
- Kept `pptx_designer.tools.svg.svg_chart()` as the high-level, editable SVG entry point.

### Documentation

- Documented the supported SVG subset, error handling, diagnostics, and safety limits.
- Recorded the reserved P3 direction: editability-first approximation by default, with raster output only as an explicit or last-resort fallback.

## 1.0.0-beta.1

- Initial beta release.
