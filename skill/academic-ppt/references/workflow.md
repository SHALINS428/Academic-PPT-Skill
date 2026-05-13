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

Environment self-check:

```powershell
python scripts\doctor.py
```

Python runtime for this skill:

```powershell
$env:ACADEMIC_PPT_PYTHON = 'D:\path\to\python.exe'
```

If you do not set this variable, the skill reuses the current Python interpreter automatically.

## External Tool Checklist

For the core build path, no extra desktop tool is required beyond Node.js and Python.
The plugin bootstraps its local Python and Node dependencies automatically on first run.

For full validation, the plugin also tries to bootstrap these tools into `.runtime/tools`:

- `LibreOffice`
  Required for `render_slides.py` and `detect_font.py` because both rely on `soffice`.
- `Poppler`
  Required for slide rasterization through `pdf2image`; `pdftoppm` must be available.
- `fontconfig` / `fc-list`
  Used when available. If it is missing, `detect_font.py` falls back to Python `fontTools` and local font-file scanning.

Recommended verification:

```powershell
where.exe soffice
where.exe pdftoppm
where.exe fc-list
python scripts\doctor.py --bootstrap-tools
```

Windows note:

- For headless validation, this skill uses the LibreOffice command-line path through `soffice`.
- If you manually double-click `soffice.exe`, or test the wrong binary from a broken working directory, you may see a misleading `bootstrap.ini` popup.
- For this skill, trust the scripted validation path instead: `scripts/validate_deck.py` already calls LibreOffice in the supported headless mode.

After tool bootstrap, rerun:

```powershell
python scripts\validate_deck.py work\deck\academic-defense.pptx
```

### Build Source Manifest

```powershell
python scripts\build_source_manifest.py /path/to/materials --output work/source_manifest.json
```

### Normalize Sources

```powershell
python scripts\normalize_sources.py /path/to/materials --output-dir work/intake
```

### Scaffold Deck Workspace

```powershell
python scripts\scaffold_deck_workspace.py work/deck --title "Thesis Defense"
```

### Plan The Deck

```powershell
python scripts\plan_deck.py work/intake/normalized_brief.md --manifest work/intake/source_manifest.json --output-dir work/planning
```

### One-Command Pipeline

```powershell
python scripts\run_pipeline.py /path/to/materials --output-dir work/run
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
python work/deck/scripts/render_slides.py work/deck/academic-defense.pptx --output_dir work/deck/rendered
```

### Overflow Check

```powershell
python work/deck/scripts/slides_test.py work/deck/academic-defense.pptx
```

### Font Check

```powershell
python work/deck/scripts/detect_font.py work/deck/academic-defense.pptx --json
```

### Validation Wrapper

```powershell
python scripts\validate_deck.py work/deck/academic-defense.pptx
```

## Validation Gate

Do not deliver until:
- titles are readable
- text does not overflow
- figures are legible
- fonts are available or substitutions are acceptable
- no obvious overlap or out-of-bounds errors remain
