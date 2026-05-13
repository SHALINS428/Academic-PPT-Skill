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

## Core Characteristics

- content-aware planning instead of generic template filling
- editable PowerPoint output generated from JavaScript
- emphasis on the student's own work, method, evidence, and innovation points
- preference for thesis-native figures and screenshots when available
- validation before delivery
- explicit traceability back to source files

## Documentation Map

If you want:

- project overview: this file
- Chinese project overview: [README.zh-CN.md](README.zh-CN.md)
- deployment guide in English: [DEPLOYMENT.md](DEPLOYMENT.md)
- deployment guide in Chinese: [DEPLOYMENT.zh-CN.md](DEPLOYMENT.zh-CN.md)
- skill behavior and internal workflow: [skill/academic-ppt/SKILL.md](skill/academic-ppt/SKILL.md)
- command-level workflow reference: [skill/academic-ppt/references/workflow.md](skill/academic-ppt/references/workflow.md)

## Deployment Summary

There are two practical deployment targets:

| Mode | What you get | Required tools |
| --- | --- | --- |
| Minimal run | Build the deck without full validation | Python, Node.js |
| Full validation | Build and validate rendering, images, and fonts | Python, Node.js, LibreOffice, Poppler, fontconfig |

`draw.io` / `diagrams.net` desktop is optional. It is only needed when exporting `.drawio` files to PNG.

For full setup instructions, use:

- [DEPLOYMENT.md](DEPLOYMENT.md)
- [DEPLOYMENT.zh-CN.md](DEPLOYMENT.zh-CN.md)

## Repository Layout

```text
academic-ppt-skills/
|- README.md
|- README.zh-CN.md
|- DEPLOYMENT.md
|- DEPLOYMENT.zh-CN.md
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
