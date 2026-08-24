# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-beta.1] - 2026-08-24

### Added

- **Core pipeline**: 4-stage generation (Story → Design → Content → Render)
- **PrecisionRenderer**: Unified rendering engine for Build and VI Build modes
- **40,000+ style combinations**: 25 palettes × 20 font pairs × 10 decorations × 8 layouts
- **35 mood categories**: Professional, tech, dark, warm, elegant, luxury, vibrant, startup, nature, calm, minimal, bold, fresh, industrial, fintech, and more
- **10 diagram engines**: Flowchart, Timeline, SWOT, Matrix, Cycle, Funnel, Pyramid, Hierarchy, Venn, Table
- **SVG compiler**: SVG → native editable PPTX shapes (rect, circle, path, text, gradients, transforms, clip-paths)
- **Text effects**: Gradient fill, outline, shadow, glow, 3D, vertical text, rotation, letter spacing
- **Shape effects**: 3D extrusion, bevel, 31 pattern fills, frosted glass, boolean operations
- **Image effects**: 22 artistic effects, duotone, grayscale, blur, vignette, cover-fit cropping
- **Animation & transitions**: 13 slide transitions (including morph), 11 entrance, 8 exit, 8 emphasis presets
- **Decoration library**: Brush divider, seal stamp, scroll frame, neon border, grid background, glass panel, ink splash
- **AI image generation**: 5 engines (Seedream, GPT Image, DALL-E, Gemini, Wanx) with cache-first architecture
- **Stock photo search**: Unsplash + Pexels integration
- **Enterprise mode**: Template analysis, brand compliance, content.json + README.md parsing
- **Design DNA extraction**: Zero-loss design analysis from existing .pptx files
- **Quality gates**: Three-tier QA (fatal → warning → review) with auto-fix
- **Build mode atoms**: 90+ composable functions for pixel-perfect control
- **CJK support**: 12 Chinese-English font pairings with auto-fallback
- **OKLCH color system**: Perceptual color science for tint/shade scales
- **LLM-friendly API**: Clear function signatures, composable atoms, deterministic output
- **CLI**: `pptx-designer` command
- **Bundled design knowledge**: 7 CSV databases (192 colors, 74 fonts, 84 styles, 161 anti-patterns)

### Removed

- **FreeStyle mode**: Removed (not mature enough for production use)
- All generation now goes through Build mode (pixel-perfect control)

### Changed

- Rebranded from `ppt-design-skill` (ppt_pro_max) to `pptx-designer` (pptx_designer)
- Reorganized from flat `build_helpers.py` (2,806 lines) to modular `tools/` package (11 files)
- Reorganized internal modules into 6-layer architecture (core, renderer, effects, diagrams, compiler, enterprise)
- Primary audience: LLMs (AI coding assistants)
- English-first documentation with Chinese translation

## [0.18.0] - 2026-08-01

### Added

- BuildQA three-tier QA system for Build-mode PPTs
- SVG compiler with support for common shapes, paths, text, gradients, transforms, and clip-path
- 3D shapes and pattern fills
- Animation and transition expansion (morph, 8 exit presets, 8 emphasis presets)
- Decoration library (brush divider, seal stamp, scroll, neon, grid, glass, ink splash)
- Mode integration (mood→text_effect_preset, mood→image_effect)

## [0.17.0] - 2026-07-01

### Added

- ProposalGenerator (2-3 style preview PPTs)
- generate_ppt() API with proposal/confirmed_proposal/materials_dir
- SlideExtractor for reverse-engineering existing PPTs
- SmartArt/GroupShape/OLE XML extractors
- Design Quality Upgrades (28 upgrades)

## [0.16.0] - 2026-06-01

### Added

- PrecisionRenderer unified rendering engine
- Pipeline unification (P2): all modes go through PrecisionRenderer
- Mood words expansion (35 moods)
- ContentParser README.md parsing
- Image size classification + image_prompt

## [0.15.0] - 2026-05-01

### Added

- Initial public release as `ppt-design-skill`
- FreeStyle mode (one-liner generation)
- Build mode (pixel-perfect control)
- Enterprise mode (template-driven)
- 40,000+ style combinations
- 10 diagram engines
- AI image generation (4 engines)
- Text and shape effects
- CJK font support
