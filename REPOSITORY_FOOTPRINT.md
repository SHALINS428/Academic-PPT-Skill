# Repository Footprint

This file explains which bundled assets are intentionally kept in the public repository and which items are intentionally excluded.

## Current Bundled Areas

Approximate source footprint:

- `skill/academic-ppt/assets`: about 627 KB
- `skill/academic-ppt/scripts`: about 323 KB
- `skill/academic-ppt/references`: about 41 KB

These are modest sizes for a self-contained skill repository, so the current approach favors offline reproducibility over aggressive fragmentation.

## Intentionally Kept In The Repository

### 1. `assets/reference-layouts/`

Kept because:

- the repository needs local layout shells to build editable PPTX output reproducibly
- these files are part of the visible behavior of the skill
- removing them would make the public repository incomplete

### 2. `assets/reference-charts/`

Kept because:

- they provide reusable local chart and process shells
- they support the template-driven generation path without network access

### 3. `scripts/vendor_source_to_md/`

Kept because:

- the normalization workflow depends on them directly
- requiring users to fetch them separately would make setup more fragile

## Explicitly Excluded From The Repository

The following are not part of the public source tree and should stay excluded:

- `node_modules/`
- `tmp/`
- generated `.pptx`
- rendered preview caches
- validation temp folders
- Python bytecode caches

## Slimming Decisions Made

- removed local `tmp/` outputs
- removed `node_modules/`
- removed `__pycache__/`
- added ignore rules so generated artifacts do not re-enter the repository accidentally

## Possible Future Splits

These are optional future refactors, not urgent cleanup items:

1. Move institution-specific layout packs into separate optional bundles.
2. Split example outputs into a dedicated `examples` branch if many large previews accumulate.
3. Publish vendor converters as a separately versioned helper package if reuse expands beyond this skill.

## Maintainer Guidance

Before adding any new bundled asset set, ask two questions:

1. Is it required for offline reproducibility?
2. Is it part of the default user-facing behavior of the skill?

If both answers are no, prefer documentation over bundling.
