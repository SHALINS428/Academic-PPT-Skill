# Third-Party Notices

This repository contains original work plus references, adapted workflow ideas, and bundled materials derived from or inspired by the following open-source projects.

## Directly Referenced / Adapted Projects

### 1. `ppt-master`

- Repository: [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)
- License: MIT
- How it relates to this repository:
  - the source normalization helpers under `skill/academic-ppt/scripts/vendor_source_to_md/` were bundled from that ecosystem and then integrated into this skill pipeline
  - the template-shell workflow and some reference layouts/charts under `skill/academic-ppt/assets/reference-layouts/` and `skill/academic-ppt/assets/reference-charts/` were adapted from the `ppt-master` visual and authoring approach

### 2. `guizang-ppt-skill`

- Repository: [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)
- License: MIT
- How it relates to this repository:
  - the academic-ppt skill selectively borrows layout discipline, readability rules, and workflow lessons for presentation authoring
  - these adaptation notes are documented in `skill/academic-ppt/references/guizang-academic-adaptation.md`

### 3. `PptxGenJS`

- Repository: [gitbrent/PptxGenJS](https://github.com/gitbrent/PptxGenJS)
- License: MIT
- How it relates to this repository:
  - this is the underlying PowerPoint generation library used by the JavaScript authoring path
  - the repository depends on it through `skill/academic-ppt/package.json`

## Dependency Manifests

Additional third-party runtime dependencies are declared through:

- `skill/academic-ppt/package.json`
- `skill/academic-ppt/requirements.txt`
- `skill/academic-ppt/assets/tool_manifest.json`

Their licenses remain the property of their respective authors and projects.

## On-Demand Desktop Tools

The plugin may download desktop validation tools into `skill/academic-ppt/.runtime/tools` on first use. These binaries are not committed to this repository.

- LibreOffice: MPL-2.0 / LGPL-3.0-or-later, used for legacy `.doc` conversion and headless Office export.
- Poppler for Windows: GPL-2.0-or-later, used for PDF rasterization during slide preview validation.
- fontconfig: used when available for font alias discovery; when unavailable, the plugin uses the Python `fontTools` package to scan local font files.

## Maintainer Note

If you identify any adapted file, asset, or workflow that should carry more explicit attribution than what is listed here, update this notice before publishing a new release.
