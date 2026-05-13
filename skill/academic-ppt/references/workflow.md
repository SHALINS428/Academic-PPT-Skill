# Workflow

## End-To-End Steps

1. Build a source manifest
2. Normalize supported materials into Markdown
3. Write `deck_plan.md` and `deck_plan.json`
   The planner is content-aware by default: it scores thesis sections, extracts cover metadata, matches native figures, and chooses defense-specific slide titles and layouts instead of reusing one generic content page recipe.
   It should also enforce a density budget: shorter takeaways, fewer bullets, and stronger visual priority for method and result pages.
   It should also respect the minimum readable text floor of `18px` for visible editable text.
4. Scaffold a task-local deck workspace
5. Author the deck in JavaScript on top of borrowed `ppt-master` SVG shells
6. Render and inspect slides
7. Run overflow and font checks
8. Fix issues and deliver

## Example Commands

Default Python runtime for this skill:

```powershell
$env:ACADEMIC_PPT_PYTHON = 'D:\shalins\study\minconda\conda_envs\twibot\python.exe'
```

If you do not set this variable, the skill still prefers that same `twibot` interpreter automatically.

## External Tool Checklist

For the core build path, no extra desktop tool is required beyond Node.js and the pinned Python runtime.

For full validation and optional exports, install these tools manually:

- `LibreOffice`
  Required for `render_slides.py` and `detect_font.py` because both rely on `soffice`.
- `Poppler`
  Required for slide rasterization through `pdf2image`; `pdftoppm` must be available.
- `fontconfig` / `fc-list`
  Required only if you want the full font-missing and font-substitution check from `detect_font.py`.
- `draw.io` / `diagrams.net` desktop
  Optional. Needed only when you want to export `.drawio` sources to PNG through `scripts/export-drawio-png.ps1`.

Recommended verification after installation:

```powershell
where.exe soffice
where.exe pdftoppm
where.exe fc-list
where.exe draw.io
```

Windows note:

- For headless validation, this skill uses the LibreOffice command-line path through `soffice`.
- If you manually double-click `soffice.exe`, or test the wrong binary from a broken working directory, you may see a misleading `bootstrap.ini` popup.
- For this skill, trust the scripted validation path instead: `scripts/validate_deck.py` already calls LibreOffice in the supported headless mode.

If `draw.io` is installed but not on `PATH`, set one of these variables before exporting diagrams:

```powershell
$env:DRAWIO_EXECUTABLE = 'D:\path\to\draw.io.exe'
# or
$env:DIAGRAMS_NET_EXECUTABLE = 'D:\path\to\diagrams.net.exe'
```

After tool installation, rerun:

```powershell
& $env:ACADEMIC_PPT_PYTHON scripts\validate_deck.py work\deck\academic-defense.pptx
```

### Build Source Manifest

```powershell
& $env:ACADEMIC_PPT_PYTHON scripts/build_source_manifest.py /path/to/materials --output work/source_manifest.json
```

### Normalize Sources

```powershell
& $env:ACADEMIC_PPT_PYTHON scripts/normalize_sources.py /path/to/materials --output-dir work/intake
```

### Scaffold Deck Workspace

```powershell
& $env:ACADEMIC_PPT_PYTHON scripts/scaffold_deck_workspace.py work/deck --title "Thesis Defense"
```

### Plan The Deck

```powershell
& $env:ACADEMIC_PPT_PYTHON scripts/plan_deck.py work/intake/normalized_brief.md --manifest work/intake/source_manifest.json --output-dir work/planning
```

### One-Command Pipeline

```powershell
& $env:ACADEMIC_PPT_PYTHON scripts/run_pipeline.py /path/to/materials --output-dir work/run
```

### Build The Deck

```bash
node work/deck/build_deck.js
```

Current generator behavior:
- cover, toc, chapter, and ending pages are driven by copied `ppt-master` SVG shells
- content slides reuse the copied content shell and overlay editable PowerPoint-native cards
- visual direction is controlled by `deck_plan.json -> deck_identity.visual_direction`
- school identity should normally be applied through `deck_identity.branding_mode = "subtle_badge"` instead of a full campus shell
- when `deck_plan.json` includes matched visuals, narrative and method/result pages should render thesis-native screenshots or figures directly instead of default placeholder cue cards
- page density and bullet length should follow `references/page-layout-principles.md` rather than the most permissive template shell
- selective borrowing from `guizang-ppt-skill` should be applied through layout discipline and readability rules, not through web-native gimmicks

### Render The Deck

```powershell
& $env:ACADEMIC_PPT_PYTHON work/deck/scripts/render_slides.py work/deck/academic-defense.pptx --output_dir work/deck/rendered
```

### Overflow Check

```powershell
& $env:ACADEMIC_PPT_PYTHON work/deck/scripts/slides_test.py work/deck/academic-defense.pptx
```

### Font Check

```powershell
& $env:ACADEMIC_PPT_PYTHON work/deck/scripts/detect_font.py work/deck/academic-defense.pptx --json
```

### Validation Wrapper

```powershell
& $env:ACADEMIC_PPT_PYTHON scripts/validate_deck.py work/deck/academic-defense.pptx
```

## Validation Gate

Do not deliver until:
- titles are readable
- text does not overflow
- figures are legible
- fonts are available or substitutions are acceptable
- no obvious overlap or out-of-bounds errors remain
