# Changelog

## 1.0.0b9 - 2026-08-31

### Theme and VI reliability

- FreeStyle now validates supplied resolved themes before rendering, including
  semantic-role and palette color values, typography, atoms, and provenance.
- Passing `theme=` alongside theme-discovery arguments now emits a `UserWarning`
  and records the ignored arguments in the rendering diagnostics.
- Added protected `merge_vi_design_context()` and migrated template analysis,
  documentation, and the enterprise example to preserve template locks and
  report rejected context overrides.
- Added `Presentation(strict_theme=True)` for callers that require a complete
  resolved theme instead of a partial Build/VI context.

### Release verification

- CI and release jobs now install the built wheel and verify both the package
  version and its `site-packages` import path before release.

## 1.0.0b8 - 2026-08-31

### Build and VI

- BuildSpec now executes Build-authored inline recipes with exact geometry,
  typography, data, and z-order; presentation and slide themes are inherited by
  public Build helpers while explicit values keep priority.
- Content-page composition is Build-owned. The VI adapter now validates visual
  grammar, fixed layers, capacity, and safety constraints through the atomic
  content contract instead of selecting a template archetype.
- Added delivery isolation and Structural QA checks for content relationships,
  provenance, template-text leaks, and reviewed fixed-base copying.

### Rendering, tests, and documentation

- Extended professional rendering, diagram/theme coverage, and SVG handling for
  namespace-free gradient and clipping definitions.
- Added atomic BuildSpec, VI boundary, delivery, QA, and theme-inheritance
  regression coverage; refreshed the README, API reference, quick start, and
  LLM authoring guidance.

## 1.0.0b7 - 2026-08-30

- 修复 SVG 文字角色字号、颜色、嵌套 transform 布局校验和透明度处理。
- 修复原生图表 builder 的 radar、scatter 类型及 PrecisionRenderer 图表调用链。
- 增加 StructuralQA、PNG 视觉基线比较和复杂 SVG 回归测试。

All notable user-facing changes are recorded here. This project follows a pre-release versioning scheme before the first stable `1.0.0` release.

## 1.0.0b5 — 2026-08-25

### Documentation

- Replaced README relative documentation, example, and changelog links with absolute GitHub URLs so they render correctly on PyPI.
- Pointed the PyPI documentation metadata to the maintained GitHub documentation index.

## 1.0.0b4 — 2026-08-25

### Image configuration

- Restored the public `fetch_image()` and `extract_design_dna()` APIs used by the CLI.
- Load the nearest project `.env` without overriding existing environment variables; added `.env.example` and documented the safe placement.
- Detect the image provider from conventional provider keys and conservatively support Codex provider entries backed by an environment key. Session credentials are never used as API keys.
- Added the safe `host_image_generator` bridge for Agent-owned image tools, and prevent ordinary Agent text models from being used as image models unless `image_model` is explicitly configured.

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
