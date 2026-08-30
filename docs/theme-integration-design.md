# Theme Integration Upgrade — Development Design

Status: proposed for implementation on `codex/theme-integration-upgrade`  
Scope: `pptx-designer` theme resolution, FreeStyle rendering, Build Mode defaults, diagnostics, and QA

## 1. Decision summary

`pptx-designer` will treat a resolved theme as a complete visual context rather
than a palette dictionary.  The library will reliably apply that context to
text, surfaces, semantic colors, charts, decorations, layout preferences, and
image/text effects where those effects are appropriate.

The upgrade must not turn themes into page templates or a second page DSL.
The LLM remains responsible for audience, narrative, page goal, composition,
focal point, information density, and the combination of public helpers.

The central contract is:

```text
ThemeComposer / explicit resolved theme
    -> normalized theme context
    -> presentation and optional slide context
    -> FreeStyle renderer or Build Mode helper
    -> editable PPTX
    -> PPTX -> PDF -> PNG acceptance review
```

## 2. Goals and non-goals

### Goals

1. A theme must visibly affect more than the palette: typography, surfaces,
   hierarchy, decoration, chart treatment, and image treatment must have a
   defined consumption path.
2. The same resolved theme must produce reproducible visual tokens when used
   with the same library version, content, renderer path, and seed.
3. `generate_ppt(query=...)` and `generate_ppt(content=...)` must use one
   FreeStyle theme-application path.  `content` is structured FreeStyle input,
   not Build Mode.
4. Build Mode must inherit presentation-level defaults without requiring an
   LLM to repeat `C` and `typo` on every helper call.
5. Explicit local values must keep their existing priority.
6. Important text, shapes, native charts, diagrams, and image containers must
   remain editable in the generated PPTX.
7. Each generation must expose enough diagnostics to explain the resolved
   theme, applied fields, fallbacks, and omissions.

### Non-goals

- No theme-specific cover/data/process/closing templates.
- No fixed required API combination per page type.
- No new page DSL or wrapper layer for every existing helper.
- No visual-effect quota and no default shadow/outline/gradient escalation.
- No attempt to make the library decide the page narrative or composition.
- No rasterized full-slide layer in place of editable content.
- No one-pass rewrite of every public helper.

## 3. Terms and generation modes

| Term | Meaning |
|---|---|
| Theme discovery | Query/style selection that proposes or resolves visual atoms. |
| Resolved theme | The locked, serializable combination of colors, typography, decoration, layout, effects, semantic roles, and source data. |
| Theme context | The normalized resolved theme made available to renderers and helpers. |
| Theme Lock | Task-level LLM design record: visual thesis, rules, page guidance, forbidden patterns, and a resolved theme. It is not a fixed page template. |
| FreeStyle | `generate_ppt(query=...)` or `generate_ppt(content=...)`; the renderer determines an editable draft from a page plan. |
| Build Mode | Direct use of `Presentation()` and public helpers for exact element placement. |
| VI Build Mode | Build Mode that preserves a supplied template and extracted Design DNA. |

## 4. Acceptance contract

The following conditions are implementation requirements.

| ID | Requirement | Priority | Evidence |
|---|---|---:|---|
| T-01 | Changing a locked theme changes editable output beyond a single color. | MUST | PPTX object inspection and PNG A/B review. |
| T-02 | Heading/body/CJK typography reaches editable text. | MUST | PPTX run font inspection; rendered PNG check. |
| T-03 | Theme fields have a consumer or an explicit `not_applied` diagnostic. | MUST | `theme_application` report. |
| T-04 | Renderer does not overwrite a theme with fixed background, green, orange, code, or font defaults. | MUST | semantic-role tests; A/B deck. |
| T-05 | Explicit element/helper values override slide and presentation defaults. | MUST | unit tests. |
| T-06 | Existing `C=None`, `typo=None`, and explicit `C`/`typo` calls remain valid. | MUST | compatibility tests. |
| T-07 | Same resolved theme can be rerun without re-querying an external style service. | MUST | deterministic regression test. |
| T-08 | Theme context improves deck coherence without forcing repeated layouts. | SHOULD | cross-page PNG review. |
| T-09 | Theme Lock guidance affects page decisions through the LLM workflow, not a page template. | SHOULD | task review record. |

## 5. Canonical theme context

### 5.1 Public representation

`ThemeComposer.compose()` remains backward compatible and returns a `dict`.
That dictionary is the serializable public representation of a resolved theme.
The implementation may use typed internal structures, but callers must not be
required to instantiate a new class to use themes.

Minimum schema:

```python
theme = {
    "name": "warm-elegant+gold-trim+centered",
    "colors": {...},                  # existing palette-compatible keys
    "typography": {...},              # heading, body, mono, cjk fallback
    "semantic_roles": {...},          # normalized role -> color
    "decoration": {...},
    "layout_variant": {...},
    "text_effect_preset": "...",
    "image_effect": "...",
    "dark_mode": False,
    "atoms": {...},
    "source": {...},
}
```

The current dictionary fields remain supported.  New consumers must use the
normalized context and not infer theme semantics from palette names.

### 5.2 Semantic roles

The initial required roles are:

```text
background, surface, ink, muted, border,
accent, accent-secondary,
success, warning, danger,
data-series-1, data-series-2
```

The normalization layer supplies sensible legacy defaults only when a palette
does not expose a role.  Page renderers and helpers must request a role; they
must not use hard-coded hex values for visual meaning.

The following legacy aliases remain resolvable during migration:

| Legacy key | Canonical role |
|---|---|
| `foreground`, `text_dark` | `ink` |
| `muted-foreground`, `text_muted` | `muted` |
| `card`, `card_bg`, `muted` | `surface` |
| `destructive` | `danger` |
| `primary` | `data-series-1` / primary accent use case |
| `accent` | `accent` / `data-series-2` |

### 5.3 Typography

The normalized typography contract must expose:

```text
heading, body, mono, cjk_fallback,
heading_size_scale, body_size_scale, caption_size_scale
```

Only the font family and CJK fallback are P0.  Size scales remain optional
until all high-frequency helpers can use them without changing legacy layout.
When an explicit `font_name` is passed to an element, it overrides the context.

### 5.4 Source and reproducibility

`source` must record:

```yaml
requested:       # original style/query/atom arguments
resolved:        # exact atoms and final values selected
seed:
resolver:        # local, external, explicit-theme
package_version:
fallbacks: []
warnings: []
```

External query lookup is allowed for discovery, but delivery generation must
accept a previously resolved theme.  Re-running a saved resolved theme must
not call external discovery again.  A seed only controls local choices; it
does not make an unrecorded external search reproducible.

## 6. API design and precedence

### 6.1 FreeStyle API

The existing arguments remain valid:

```python
generate_ppt(
    query="...",
    content=None,
    style=None,
    palette=None,
    fonts=None,
    decoration=None,
    layout=None,
    mood=None,
    style_seed=None,
)
```

One optional keyword is added:

```python
generate_ppt(..., theme: Mapping[str, Any] | None = None)
```

Rules:

1. `theme` is a previously resolved theme and wins over discovery arguments.
2. Without `theme`, compose exactly once after the planner has supplied any
   style hint; never silently compose a second random theme.
3. `query` and structured `content` share the same theme-resolution and
   application route.
4. The return value retains existing keys and adds:

```python
{
    "theme_context": {...},
    "theme_application": {
        "requested": {...},
        "resolved": {...},
        "applied_to": [],
        "not_applied": [],
        "fallbacks": [],
        "warnings": [],
    },
}
```

### 6.2 Build Mode API

The recommended public entry points are:

```python
prs = Presentation(template_path=None, theme=theme)
set_presentation_theme(prs, theme)  # equivalent post-construction form
set_slide_theme(slide, theme)       # optional local override
```

`Presentation(template_path)` continues to work unchanged.  `theme` accepts a
resolved-theme mapping, not a new page format.  The PowerPoint color-scheme
writer (`set_theme_colors`) stays available but is not itself the theme
inheritance mechanism.

High-frequency helpers keep their current public signatures.  No caller needs
to add `theme=` to each call:

```python
text(slide, ..., C=None)
kpi_card(slide, ..., C=None, typo=None)
bar_chart(slide, ..., C=None, typo=None)
```

### 6.3 Precedence

Values resolve from most to least specific:

```text
element explicit value (color/font_name/layout/image effect)
    > helper C / typo partial override
    > slide theme
    > presentation theme
    > normalized legacy default
```

Partial dictionaries merge by key.  For example, an explicit `C={"accent":
"#112233"}` only replaces `accent`; it must not remove the inherited `ink`,
`surface`, or typography values.

Theme lookup must be presentation-scoped.  It must not use module-level mutable
state, because parallel presentation builds must not contaminate one another.

## 7. Implementation architecture

### 7.1 Normalization and attachment

Add an internal theme-context module with these responsibilities:

- validate and normalize a resolved-theme mapping;
- resolve semantic colors and typography aliases;
- merge presentation/slide/helper/element values;
- attach an immutable context to a presentation and optional slide;
- collect application diagnostics.

The attachment storage may use a private presentation attribute or a
presentation-scoped weak registry.  It must not be a global mutable singleton.
The exact storage mechanism is an implementation detail; `Presentation(theme=)`
and `set_presentation_theme()` are the public boundary.

### 7.2 `ThemeComposer`

`ThemeComposer` must:

- preserve explicit atom precedence over a preset;
- provide the canonical semantic role map and source record;
- use deterministic local selection when a seed is supplied;
- record any local or external fallback;
- return actual resolved atom names whenever known;
- not claim an external/dynamic atom when a fallback was used.

It does not decide a slide layout or apply shapes.

### 7.3 FreeStyle pipeline and renderer

`generate_ppt()` resolves a theme once and attaches it to the presentation.
`professional_renderer` receives the complete normalized context rather than a
bare `C` dictionary.

Page goal controls what the page communicates.  Theme controls how it looks:

| Renderer concern | Source |
|---|---|
| background, surface, ink, dividers | semantic roles |
| labels, callouts, chart series | semantic roles |
| title/body/code/CJK font | typography |
| corner accents, rules, lines | decoration data |
| margins, alignment preference, card restraint | layout preference |
| text/image treatment | explicit applicable theme effect, otherwise diagnostics |
| page arrangement and focal point | renderer/page-plan/LLM decision |

Initial migration removes fixed dark backgrounds, green solution markers,
orange data markers, fixed code fills, fixed white text, and hard-coded
`Consolas` from the renderer.  Semantic defaults belong only in normalization.

### 7.4 Helper migration

Migration order is based on impact:

1. `tools.text` and layout headers/footers;
2. `tools.cards` and `tools.charts`;
3. high-traffic diagrams;
4. image helpers and effect helpers.

Each migrated helper resolves its defaults from the slide/presentation context,
then merges explicit `C`, `typo`, spacing, font, and color overrides.  Helpers
that do not yet consume a theme field must add a `not_applied` diagnostic rather
than silently ignore it.

### 7.5 VI Build Mode

Template Design DNA is higher priority than generic theme defaults.  Theme
Lock must label each property as one of:

```text
template-locked | template-derived | theme-adjustable
```

The initial upgrade must not change PowerPoint masters, placeholders, logos, or
brand colors unless the caller explicitly enables that behavior.

## 8. Phased delivery plan

### Phase 0 — baseline and design (complete)

- Theme application acceptance tests created.
- Current failures identified: typography does not reach editable text,
  renderer has semantic-color hard-coding, and diagnostics were incomplete.
- Theme context and initial diagnostics are saved to `master` as a baseline.

### Phase 1 — complete normalized context

Files: `renderer/theme.py`, new context module, focused tests.

- Finish source/fallback/version reporting.
- Normalize roles, aliases, typography, and effect preferences.
- Guarantee explicit theme precedence and one-resolution FreeStyle behavior.
- Add schema and reproducibility tests.

Exit: `ThemeComposer` contract is stable and serializable.

### Phase 2 — FreeStyle visual application

Files: `core/pipeline.py`, `core/professional_renderer.py`, text/layout helpers.

- Pass normalized context through `generate_ppt()`.
- Apply typography to editable FreeStyle text.
- Replace renderer color/font hard-coding with semantic roles.
- Apply safe decoration and layout preferences without template lock-in.
- Return `theme_application` diagnostics.

Exit: current theme acceptance failures pass and FreeStyle changes visibly
affect typography plus semantic visual treatment.

### Phase 3 — Build Mode inheritance

Files: `core/pipeline.py`/presentation API, new context module,
`tools.text.py`, `tools.layout.py`, `tools.cards.py`, `tools.charts.py`.

- Add `Presentation(theme=)`, `set_presentation_theme()`, and optional
  `set_slide_theme()`.
- Implement precedence and partial-override merge rules.
- Migrate high-frequency helpers.
- Preserve all existing explicit-parameter behavior.

Exit: Build Mode can create a coherent deck without repetitive `C`/`typo`.

### Phase 4 — extended consumers and VI rules

Files: diagram/image/effect helpers and enterprise/template modules as needed.

- Migrate remaining high-impact consumers.
- Record unapplied effects instead of silently dropping them.
- Introduce template-DNA precedence tests.

Exit: all theme fields have a consumer or a diagnostic record.

### Phase 5 — visual acceptance and documentation

- Render A/B decks through the approved PPTX -> PDF -> PNG path.
- Inspect individual pages and a contact sheet.
- Update public API reference, authoring guide, examples, and changelog.
- Publish an acceptance record for each MUST requirement.

Exit: all MUST requirements pass with reviewed PNG evidence.

## 9. Test plan

### Unit tests

- explicit style/palette/fonts/decoration/layout precedence;
- local seed reproducibility;
- query fallback reporting;
- semantic alias resolution;
- partial `C`/`typo` merge behavior;
- presentation, slide, helper, and element precedence;
- CJK fallback and unavailable-font fallback;
- legacy public call compatibility.

### Integration tests

Use identical structured FreeStyle content with at least these themes:

| Theme family | Required pages |
|---|---|
| dark technology | hero, content, data, process, closing |
| warm editorial / luxury | hero, content, comparison, image, closing |
| research / data | evidence, chart, diagram, caption, closing |

Verify editable text fonts, fill/line colors, charts, source diagnostics, and
PPTX reopenability.

### PNG A/B acceptance

For every test deck, fix brief, content, page count, library version, seed, and
rendering chain.  Compare:

```text
A: legacy/baseline theme path
B: complete theme context path
```

The reviewer records `PASS`, `NEEDS_REVISION`, or `BLOCKED` for each:

- theme is perceptible beyond color;
- typography and hierarchy match the resolved theme;
- surfaces, charts, and decoration are coherent but not mechanically repeated;
- page focal point, density, and whitespace still suit the page goal;
- no overflow, overlap, clipping, contrast failure, or irrelevant effect;
- important content remains editable;
- PDF and PNG agree with the PPTX.

An A/B test does not pass merely because pixel values differ.  It passes only
when visual evidence shows a stronger, coherent design without degrading
readability or domain appropriateness.

## 10. Compatibility, rollout, and rollback

### Compatibility guarantees

- Existing public helper calls remain valid.
- `C` and `typo` remain accepted.
- No theme set means predictable legacy-default behavior, never a silent random
  theme injection.
- Existing callers can adopt theme inheritance gradually.

### Rollout controls

- New context features are opt-in in Build Mode through `Presentation(theme=)`
  or `set_presentation_theme()`.
- FreeStyle applies the complete context after Phase 2 because it already owns
  the full generation path.
- Diagnostics may warn about unapplied fields during migration; warnings are
  not errors unless a MUST requirement is violated in a release gate.

### Git workflow

- `master` holds the Phase 0 baseline commit (`1f65110`).
- Development continues on `codex/theme-integration-upgrade`.
- Each phase is one or more separately testable commits.
- A failed phase is discarded by deleting or reverting only the development
  branch; the baseline remains available on `master`.

## 11. Risks and controls

| Risk | Control |
|---|---|
| Theme becomes a template | Keep page arrangement out of the theme API. |
| Theme only changes colors | Typography, semantic treatment, and PNG A/B are MUST gates. |
| Over-decoration | Effects require an applicable use case; otherwise record `not_applied`. |
| Build Mode contamination | Use presentation-scoped context; prohibit global mutable state. |
| Breaking legacy calls | Preserve signatures and test explicit overrides. |
| Query non-determinism | Persist resolved themes; report lookup source and fallback. |
| Template brand conflict | Template DNA has explicit precedence in VI Build Mode. |
| Visual regressions hidden by unit tests | Require PPTX -> PDF -> PNG inspection before final acceptance. |

## 12. Definition of done

The upgrade is complete only when:

1. all MUST acceptance requirements pass;
2. full unit and integration tests pass;
3. three cross-domain A/B decks have been rendered and individually reviewed;
4. no critical editability or rendering issue remains;
5. public API and examples document both FreeStyle and Build Mode use;
6. the final Theme Lock/PNG QA record explains why the visual result is better,
   not merely different.
