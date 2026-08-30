# Acceptance contract

| ID | Level | Requirement | Expected evidence in rendered output | Status |
|---|---|---|---|---|
| R1 | MUST | Preserve supplied framework pages | Rendered slides 1–5 remain visually unchanged | PASS |
| R2 | MUST | Use the template's photographic grammar on a new page | Slide 6 uses a full-bleed botanical image rather than a color-only substitute | PASS |
| R3 | MUST | Preserve the cover archetype | Slide 6 has centered white editorial type and the two inherited horizontal rules | PASS |
| R4 | MUST | Require an image for a photo archetype | Build preflight returns `NEEDS_ASSET` and creates no page when `supporting_photo` is missing | PASS |
| R5 | MUST | Keep delivery editable and structurally valid | Structural QA has no fatal/warning defects; text/rules remain native objects | PASS |

Rules:

- Do not rewrite a MUST requirement merely to fit an output.
- Every MUST requires visible evidence in the rendered pages.
- Record `PASS`, `NEEDS_REVISION`, or `BLOCKED` with evidence.
