# Academic PPT Skill

[中文说明](README.zh-CN.md)

Academic PPT Skill is an open-source skill bundle for turning local thesis materials into rigorous, concise, editable academic defense presentations.

It is designed for:

- undergraduate thesis defense
- graduate research presentation
- project progress defense
- academic report or lab presentation

## What It Produces

The repository is built to generate:

- editable `.pptx`
- rebuildable JavaScript authoring source
- `deck_plan.md`
- `deck_plan.json`
- `source_manifest.json`
- rendered slide previews
- validation outputs for overflow, rendering, and font checks

## Supported Inputs

- `.doc`
- `.docx`
- `.pdf`
- `.md`
- `.pptx`
- images such as `.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`

Inputs may be:

- a single file
- multiple files
- a mixed folder of thesis materials

## Deployment Modes

There are two practical deployment targets.

| Mode | What you get | Required tools |
| --- | --- | --- |
| Minimal run | Build the deck without full validation | Python, Node.js |
| Full validation | Build and validate rendering, images, and fonts | Python, Node.js, LibreOffice, Poppler, fontconfig |

`draw.io` / `diagrams.net` desktop is optional. It is only needed when exporting `.drawio` files to PNG.

## Prerequisites Matrix

| Tool | Minimal run | Full validation | Why it exists |
| --- | --- | --- | --- |
| Python 3.11+ | Required | Required | Runs normalization, planning, validation, and helper scripts |
| Node.js 18+ | Required | Required | Builds the editable PowerPoint deck |
| LibreOffice (`soffice`) | Optional | Required | Converts legacy `.doc` files and renders PPT/PPTX through headless export |
| Poppler (`pdftoppm`) | Optional | Required | Rasterizes PDF output into preview images |
| fontconfig (`fc-list`) | Optional | Required | Detects missing or substituted fonts during validation |
| draw.io / diagrams.net | Optional | Optional | Exports `.drawio` diagrams to PNG |

## Deterministic Deployment Steps

This is the sequence both humans and agents should follow.

### 1. Clone the repository

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill\skill\academic-ppt
```

### 2. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Install Node dependencies

```powershell
npm install
```

### 4. Run the environment self-check

```powershell
npm run doctor
```

Interpret the result this way:

- `最小运行环境: 就绪` means the repository can build a deck
- `完整验证环境: 就绪` means the repository can also run full validation
- if only the first line is ready, use `--skip-validate` for the first run

For agent-driven setup, use the machine-readable check:

```powershell
python .\scripts\doctor.py --json
```

Agents should interpret the JSON this way:

- `minimal_run_ready: true` means deck generation can proceed
- `full_validation_ready: true` means full validation can proceed
- `blockers` lists the missing setup steps

### 5. Prepare a local materials folder

Example:

```text
D:\thesis-materials\
|- paper.docx
|- paper.pdf
|- figures\
|- screenshots\
`- previous_slides.pptx
```

### 6. Run the pipeline

Minimal run:

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run --skip-validate
```

Full run:

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run
```

Full run with starter `.drawio` files:

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run --materialize-diagrams
```

### 7. Verify the expected outputs

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

### Install full validation tools

Install these only if you want complete validation:

- LibreOffice
- Poppler
- fontconfig / `fc-list`

Verify:

```powershell
where.exe soffice
where.exe pdftoppm
where.exe fc-list
where.exe draw.io
```

Notes:

- the first three commands should resolve for full validation
- `where.exe draw.io` may fail without blocking the main workflow

## Environment Overrides

The repository now prefers environment variables and system `PATH` over maintainer-local absolute paths.

Useful overrides:

```powershell
$env:ACADEMIC_PPT_PYTHON = "C:\path\to\python.exe"
$env:ACADEMIC_PPT_NODE = "C:\path\to\node.exe"
$env:SOFFICE_EXECUTABLE = "C:\path\to\soffice.exe"
$env:PDFTOPPM_EXECUTABLE = "C:\path\to\pdftoppm.exe"
$env:FC_LIST_EXECUTABLE = "C:\path\to\fc-list.exe"
$env:DRAWIO_EXECUTABLE = "C:\path\to\draw.io.exe"
$env:DIAGRAMS_NET_EXECUTABLE = "C:\path\to\diagrams.net.exe"
```

Use overrides only when:

- the tool is installed but not on `PATH`
- the machine has multiple versions and the skill must use a specific one

## Self-Check Commands

```powershell
python .\scripts\doctor.py
python .\scripts\doctor.py --json
npm run doctor
npm run doctor:full
```

Use them this way:

- `doctor`: check whether the repository can build a deck
- `doctor --json`: provide machine-readable readiness for agents and automation
- `doctor:full`: fail unless full validation prerequisites are ready

## Troubleshooting

`python` or `node` is not recognized:

- reopen PowerShell after installation
- check whether the installer added the tool to `PATH`
- if needed, set `ACADEMIC_PPT_PYTHON` or `ACADEMIC_PPT_NODE`

`soffice` is not found:

- install LibreOffice or add it to `PATH`
- otherwise set `SOFFICE_EXECUTABLE`

`pdftoppm` is not found:

- install Poppler or add it to `PATH`
- otherwise set `PDFTOPPM_EXECUTABLE`

`fc-list` is not found:

- install fontconfig or add it to `PATH`
- otherwise set `FC_LIST_EXECUTABLE`

Legacy `.doc` conversion fails:

- LibreOffice is required for `.doc` to `.docx` bridge conversion
- confirm `where.exe soffice` returns a valid executable

You only want to confirm deck generation first:

- run the pipeline with `--skip-validate`
- install LibreOffice, Poppler, and fontconfig later

## Repository Layout

```text
academic-ppt-skills/
|- README.md
|- README.zh-CN.md
|- LICENSE
|- THIRD_PARTY_NOTICES.md
|- examples/
|  `- twibot20/
`- skill/
   `- academic-ppt/
      |- SKILL.md
      |- package.json
      |- requirements.txt
      |- assets/
      |- references/
      `- scripts/
```

## Example Output

The image below is a public example preview generated from a local research paper (`TwiBot-20.pdf`). The source paper itself is not redistributed in this repository.

![Example montage](examples/twibot20/montage.png)

See [examples/twibot20/README.md](examples/twibot20/README.md) for the example context and validation notes.

## Additional Documentation

- [skill/academic-ppt/SKILL.md](skill/academic-ppt/SKILL.md)
- [skill/academic-ppt/references/workflow.md](skill/academic-ppt/references/workflow.md)
- [REPOSITORY_FOOTPRINT.md](REPOSITORY_FOOTPRINT.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

## Open-Source References

Referenced projects include:

- [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)
- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)
- [gitbrent/PptxGenJS](https://github.com/gitbrent/PptxGenJS)

## License

This repository is released under the MIT License. See [LICENSE](LICENSE).
