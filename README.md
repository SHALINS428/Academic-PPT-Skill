# academic-ppt-skills

`academic-ppt-skills` is a Codex/Claude-style skill bundle for building rigorous, concise, editable academic defense decks from local thesis materials.

The repository is centered on the `academic-ppt` skill, which turns `.doc`, `.docx`, `.pdf`, `.md`, `.pptx`, and image inputs into:

- editable `.pptx`
- rebuildable JavaScript authoring source
- planning artifacts such as `deck_plan.md` and `source_manifest.json`
- rendered slide previews and validation reports

## Repository Layout

```text
academic-ppt-skills/
├── LICENSE
├── README.md
├── THIRD_PARTY_NOTICES.md
├── .gitignore
└── skill/
    └── academic-ppt/
        ├── SKILL.md
        ├── package.json
        ├── requirements.txt
        ├── scripts/
        ├── references/
        ├── assets/
        └── agents/
```

## What The Skill Emphasizes

- defense-room readability instead of thesis paragraph dumping
- a clear narrative: problem -> method -> validation -> conclusion -> innovation
- the student's own work, not generic background filler
- editable output built with JavaScript and `PptxGenJS`
- validation before delivery: render checks, overflow checks, and font checks

## Install

Clone this repository into your local skills directory, or copy the `skill/academic-ppt` folder into the location your agent runtime uses for custom skills.

Example:

```powershell
git clone <your-repo-url> ~/.codex/skills/academic-ppt-skills
```

Then point your agent environment at:

```text
skill/academic-ppt/SKILL.md
```

## Local Development

Node dependencies:

```powershell
cd skill/academic-ppt
npm install
```

Python dependencies:

```powershell
pip install -r requirements.txt
```

The skill expects additional desktop tooling for full validation and optional conversions:

- LibreOffice
- Poppler
- fontconfig / `fc-list`
- draw.io / diagrams.net desktop for editable diagram PNG export

See [skill/academic-ppt/SKILL.md](skill/academic-ppt/SKILL.md) for the full workflow.

## License

This repository is released under the MIT License. See [LICENSE](LICENSE).

## Acknowledgements

This repository includes ideas, workflows, or adapted assets/code influenced by other open-source projects. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for attribution details and repository links.
