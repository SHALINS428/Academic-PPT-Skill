# Deployment Guide

[Chinese Deployment Guide](DEPLOYMENT.zh-CN.md)

This document is the deployment contract for both humans and agents.

Use it when the goal is to:

- install the repository on a new machine
- verify whether the machine is ready
- run the pipeline in minimal or full-validation mode

## Deployment Modes

| Mode | What you get | Required tools |
| --- | --- | --- |
| Minimal run | Build the deck without full validation | Python, Node.js |
| Full validation | Build and validate rendering, images, and fonts | Python, Node.js; LibreOffice/Poppler bootstrap where supported; fontconfig or Python font fallback |

Python and Node dependencies are bootstrapped automatically by the plugin on first run. Full validation can also bootstrap desktop validation tools into `skill/academic-ppt/.runtime/tools`.

## Prerequisites Matrix

| Tool | Minimal run | Full validation | Why it exists |
| --- | --- | --- | --- |
| Python 3.11+ | Required | Required | Runs normalization, planning, validation, and helper scripts |
| Node.js 18+ | Required | Required | Builds the editable PowerPoint deck |
| LibreOffice (`soffice`) | Optional | Auto-bootstrap where supported | Converts legacy `.doc` files and renders PPT/PPTX through headless export |
| Poppler (`pdftoppm`) | Optional | Auto-bootstrap where supported | Rasterizes PDF output into preview images |
| fontconfig (`fc-list`) | Optional | Optional | Improves font alias detection; Python `fontTools` fallback is bundled |

## Deterministic Deployment Steps

### 1. Clone the repository

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill
```

### 2. Run the environment self-check

```powershell
python .\skill\academic-ppt\scripts\doctor.py
```

Interpret the result this way:

- `Minimal run ready: yes` means the repository can build a deck.
- `Full validation ready: yes` means the repository can also run full validation.
- If full validation is not ready, use `--skip-validate` for the first run.

For agent-driven setup, use the machine-readable check:

```powershell
python .\skill\academic-ppt\scripts\doctor.py --json
```

### 3. Prepare a local materials folder

Example:

```text
D:\thesis-materials\
|- paper.docx
|- paper.pdf
|- figures\
|- screenshots\
`- previous_slides.pptx
```

### 4. Run the pipeline

Minimal run:

```powershell
python .\skill\academic-ppt\scripts\run_pipeline.py "D:\thesis-materials" --output-dir .\work\run --skip-validate
```

Full run:

```powershell
python .\skill\academic-ppt\scripts\run_pipeline.py "D:\thesis-materials" --output-dir .\work\run
```

### 5. Verify the expected outputs

After a successful run, check:

- `work\run\pipeline_summary.json`
- `work\run\planning\deck_plan.md`
- `work\run\planning\deck_plan.json`
- `work\run\deck\build_deck.js`
- `work\run\deck\academic-defense.pptx`

If full validation was enabled, also check:

- `work\run\deck\rendered\`
- `work\run\deck\validation_summary.json`

## Windows Setup Guide

This repository is Windows-first. A new Windows user can usually get the project running by following the sequence below.

### Install the base runtime

Required:

- Git
- Python 3.11 or newer
- Node.js 18 or newer

Verify:

```powershell
git --version
python --version
node --version
```

### Bootstrap full validation tools

The plugin downloads supported desktop tools into `skill/academic-ppt/.runtime/tools` when full validation or legacy `.doc` conversion needs them.

Verify or prefetch them explicitly:

```powershell
python .\skill\academic-ppt\scripts\doctor.py --bootstrap-tools
where.exe soffice
where.exe pdftoppm
where.exe fc-list
```

`fc-list` may remain unavailable on Windows. That is acceptable because font checks fall back to the bundled Python `fontTools` path.

## Environment Overrides

The repository prefers environment variables and system `PATH` over maintainer-local absolute paths.

Useful overrides:

```powershell
$env:ACADEMIC_PPT_PYTHON = "C:\path\to\python.exe"
$env:ACADEMIC_PPT_NODE = "C:\path\to\node.exe"
$env:SOFFICE_EXECUTABLE = "C:\path\to\soffice.exe"
$env:PDFTOPPM_EXECUTABLE = "C:\path\to\pdftoppm.exe"
$env:FC_LIST_EXECUTABLE = "C:\path\to\fc-list.exe"
```

Use overrides only when:

- the tool is installed but not on `PATH`
- the machine has multiple versions and the plugin must use a specific one

## Self-Check Commands

```powershell
python .\skill\academic-ppt\scripts\doctor.py
python .\skill\academic-ppt\scripts\doctor.py --json
python .\skill\academic-ppt\scripts\doctor.py --require-full-validation
python .\skill\academic-ppt\scripts\bootstrap_runtime.py --tools
```

Use them this way:

- `doctor`: check whether the repository can build a deck
- `doctor --json`: provide machine-readable readiness for agents and automation
- `doctor --require-full-validation`: bootstrap supported desktop tools and fail unless full validation prerequisites are ready
- `bootstrap_runtime --tools`: prefetch Python, Node, and supported desktop validation dependencies

## Troubleshooting

`python` or `node` is not recognized:

- reopen PowerShell after installation
- check whether the installer added the tool to `PATH`
- if needed, set `ACADEMIC_PPT_PYTHON` or `ACADEMIC_PPT_NODE`

`soffice` is not found:

- run `doctor.py --bootstrap-tools`
- if the automatic download is blocked, install LibreOffice or add it to `PATH`
- otherwise set `SOFFICE_EXECUTABLE`

`pdftoppm` is not found:

- run `doctor.py --bootstrap-tools`
- if the automatic download is blocked, install Poppler or add it to `PATH`
- otherwise set `PDFTOPPM_EXECUTABLE`

`fc-list` is not found:

- this is not a blocker on Windows because font checks use the Python fallback
- install fontconfig only if you need fontconfig-native alias behavior
- otherwise set `FC_LIST_EXECUTABLE`

Legacy `.doc` conversion fails:

- LibreOffice is required for `.doc` to `.docx` bridge conversion
- confirm `where.exe soffice` returns a valid executable

You only want to confirm deck generation first:

- run the pipeline with `--skip-validate`
- let full validation bootstrap LibreOffice and Poppler later
