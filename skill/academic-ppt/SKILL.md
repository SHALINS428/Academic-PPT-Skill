---
name: academic-ppt
description: Use when the user wants to create a thesis defense PPT or academic research presentation from local files or folders, especially `.docx`, `.pdf`, `.md`, `.pptx`, and images. This skill focuses the deck on the student's own work, innovation points, methodological rigor, explained figures, and editable `.pptx` output with a rebuildable `.js` source.
---

# Academic PPT

## Overview

This skill builds graduation thesis defense decks and academic report decks from local materials.

It is optimized for:
- undergraduate thesis defense
- graduate research presentation
- project progress defense
- lab or group academic report

It is not a general business deck workflow.

## Primary Outcome

Default delivery contract:
- editable `.pptx`
- rebuildable `.js` authoring source
- rendered slide previews
- `deck_plan.md`
- `normalized_brief.md`
- `source_manifest.json`

Default robustness contract:
- support `.doc`, `.docx`, `.pdf`, `.md`, `.pptx`, and common images as local inputs
- convert legacy `.doc` sources through LibreOffice when needed before normalization
- infer a defense deck structure from thesis sections instead of relying on fixed generic placeholders
- attach thesis figures or screenshots to suitable content pages when the source material already contains them
- fall back to reusable local chart or layout assets when no suitable source visual can be matched
- enforce page-density guardrails so content pages stay concise enough for defense-room projection
- enforce a visible editable text floor of `18px` (about `13.5pt`) for readability

Default Python runtime:
- use `ACADEMIC_PPT_PYTHON` if you need to pin a specific interpreter
- otherwise reuse the current Python interpreter automatically

## Non-Negotiable Content Rules

- The deck must emphasize the student's own work, not just generic background.
- The narrative must clearly show the chain: problem -> method -> validation -> conclusion -> innovation.
- Innovation claims must be concrete and evidence-backed.
- Every slide should communicate one main point.
- Slide language must be professional, concise, and easy to scan.
- Core figures and charts must include an explanation of what they show and why they matter.
- Do not paste thesis paragraphs directly onto slides.
- Do not use Excel or spreadsheet interaction in this workflow.
- Do not use PowerPoint MCP as the primary authoring path for v1. Use the JS authoring path.

## Backend Choice

Use the slides-style workflow as the main authoring path:
- author slides in JavaScript
- use borrowed `ppt-master` SVG shells as the visual master layer when possible
- generate native editable `.pptx`
- validate by rendering and overflow checks

Do not use `python-pptx` for full deck generation unless the task is inspection-only.

## Content-Aware Planning

This skill should not treat every thesis as a flat text source.

Default planning behavior:
- parse the normalized brief by source, heading hierarchy, and extracted figure references
- distinguish cover metadata, background, problem, method, system architecture, student work, experiment, result, innovation, and limitation sections
- assign canonical defense slide titles instead of copying raw thesis headings directly
- prefer thesis-native figures, screenshots, and workflow images on content pages when they match the current slide purpose
- use bundled reusable visual assets only as a fallback when the thesis lacks a suitable figure for a needed page
- keep chapter divider pages separate from content pages; divider pages should not receive extra top theme labels
- compress slide text before rendering so the generator can preserve whitespace and stronger typography

## Bundled Resources

### Scripts

- `scripts/build_source_manifest.py`
  Scan local files or folders and produce a normalized manifest.
- `scripts/normalize_sources.py`
  Convert supported source files into a single `normalized_brief.md`.
- `scripts/plan_deck.py`
  Extract a defense-oriented slide plan and source trace from normalized materials.
- `scripts/scaffold_deck_workspace.py`
  Create a deck workspace with bundled PptxGenJS helpers, validation scripts, and optional plan artifacts.
- `scripts/validate_deck.py`
  Run rendering, overflow, montage, and font checks against a generated deck.
- `scripts/doctor.py`
  Check whether the current machine is ready for minimal generation or full validation.
- `scripts/run_pipeline.py`
  Orchestrate bootstrap, normalization, planning, workspace scaffold, build, and validation.
- `scripts/bootstrap_runtime.py`
  Install local Python and Node dependencies automatically for first-run use; pass `--tools` to prefetch desktop validation tools where supported.
- `scripts/tools_bootstrap.py`
  Download and expose LibreOffice/Poppler into `.runtime/tools` on supported platforms, with a Python fontTools fallback when `fc-list` is unavailable.
- `scripts/python_runtime.py`
  Resolve the default Python interpreter and prepare tool discovery from environment variables, system `PATH`, and `.runtime/tools`.
- `scripts/vendor_source_to_md/`
  Bundled source converters copied from `ppt-master` for local ingestion.

### References

Read these only when needed:
- `references/academic-defense-style.md`
  Core content, language, figure, and visual requirements.
- `references/deck-structure.md`
  Recommended page structure and page-type defaults.
- `references/source-priority.md`
  Source precedence and conflict resolution.
- `references/template-selection.md`
  When to use each bundled academic visual direction.
- `references/design-language-catalog.md`
  Design-recipe catalog describing what is borrowed from each `ppt-master` style and how subtle school branding should be applied.
- `references/page-layout-principles.md`
  Page-level layout guardrails distilled from academic and scientific slide-design guidance.
- `references/guizang-academic-adaptation.md`
  Selective borrowing notes from `guizang-ppt-skill`, filtered for thesis-defense use instead of blind imitation.
- `references/workflow.md`
  End-to-end workflow and validation commands.
- `references/pptxgenjs-helpers.md`
  Helper API summary copied from the local slides skill.

### Assets

- `assets/pptxgenjs_helpers/`
  Bundled helper code for PptxGenJS authoring.
- `assets/scripts/`
  Bundled slide rendering and validation utilities.
- `assets/reference-layouts/`
  Academic and premium SVG layout shells copied from `ppt-master`.
- `assets/reference-charts/`
  Reference SVG chart and process layouts copied from `ppt-master`.
- `assets/build_deck_template.js`
  Standalone template-driven deck generator that applies the borrowed SVG shells and overlays editable content cards.

## Input Expectations

Preferred local inputs:
- `.doc`
- `.docx`
- `.pdf`
- `.md`
- `.pptx`
- images such as `.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`

Input may be:
- a single file
- multiple files
- one local folder containing mixed materials

## Workflow

### 1. Audit The Material

Start by identifying the usable local inputs.

Use:
- `scripts/build_source_manifest.py`

If `.docx` layout fidelity matters for interpretation, prefer the configured `word` MCP first for inspection or extraction. Use the bundled `doc_to_md.py` path when the goal is fast content normalization rather than exact Word-native layout review.

### 2. Normalize The Sources

Convert local materials into a single working brief.

Use:
- `scripts/normalize_sources.py`

The normalized brief should preserve:
- source identity
- rough source role
- extracted body text
- image references
- slide-deck text from existing PPTX files

### 3. Plan The Defense Narrative

Before writing slides, plan the deck around the defense use case.

Read:
- `references/academic-defense-style.md`
- `references/deck-structure.md`
- `references/source-priority.md`

Produce a `deck_plan.md` that identifies:
- report type
- audience assumptions
- slide order
- per-slide title and main takeaway
- per-slide design hint when a stronger composition is needed
- where innovation is proved
- where figures are needed

Preferred wrapper:
- `scripts/plan_deck.py`

### 4. Choose The Visual Direction

Read:
- `references/template-selection.md`
- `references/design-language-catalog.md`

Default to the premium academic recipe unless the materials clearly fit a more specific style family.

When presentation polish is the priority, prefer the template-driven shell workflow over ad hoc box layouts.

### 5. Scaffold The Deck Workspace

Create a task-local deck workspace.

Use:
- `scripts/scaffold_deck_workspace.py`

This should prepare:
- authoring JS
- helper modules
- validation scripts
- borrowed SVG layout shells
- deck plan files
- output folders

### 6. Author The Deck In JavaScript

Use the bundled PptxGenJS helpers and the local slides-style rules.

Requirements:
- keep output editable
- prefer SVG-shell-driven masters for cover, toc, chapter, content header/footer, and ending pages
- keep titles conclusion-oriented when possible
- use explicit fonts
- keep one major claim per slide
- use notes for speaker guidance
- preserve traceability back to sources

### 7. Add Diagrams When Needed
If the deck needs a process, architecture, or pipeline visual, stay inside this plugin's scope:
- prefer thesis-native figures or screenshots when available
- otherwise compose the page with bundled chart and layout assets inside the PPT itself
- do not delegate to external diagram-editing workflows from this plugin

### 8. Validate Before Delivery

Read:
- `references/workflow.md`

Run the bundled validation utilities until the deck is clean:
- render slides
- inspect previews
- run overflow checks
- detect missing or substituted fonts

Preferred wrapper:
- `scripts/validate_deck.py`

Do not deliver until obvious overflow, clipping, or unreadable density is fixed.

## Authoring Heuristics

- Match the user's language. Use Chinese slide text for Chinese thesis materials unless the user asks otherwise.
- Prefer academic restraint over visual flourish.
- Avoid background-heavy decks that hide the student's contribution.
- Convert complex multi-panel paper figures into slide-friendly versions instead of pasting them unchanged.
- Use source attributions directly on pages when figures or external visuals are shown.
- If conflicting sources cannot be resolved safely, ask the user rather than guessing.
