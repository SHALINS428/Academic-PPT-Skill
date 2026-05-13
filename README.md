# Academic PPT Skill

Academic PPT Skill is an open-source skill bundle for generating rigorous, concise, editable thesis defense presentations from local academic materials.

It is designed for workflows where the source materials already exist locally, such as:

- undergraduate thesis defense
- graduate research presentation
- project progress defense
- academic report or lab presentation

The main deliverable is not a static slide export. The skill is built to produce:

- editable `.pptx`
- rebuildable JavaScript authoring source
- planning artifacts such as `deck_plan.md` and `source_manifest.json`
- rendered slide previews
- validation outputs for overflow, rendering, and font checks

## 中文说明

Academic PPT Skill 是一个面向毕业答辩和学术汇报场景的开源技能仓库，用于把本地论文、PDF、PPT、图片等材料整理成一套结构严谨、内容精炼、可继续编辑的答辩 PPT。

它强调的不是“自动生成一套花哨幻灯片”，而是：

- 突出学生自己的工作
- 形成清晰叙事：问题 -> 方法 -> 验证 -> 结论 -> 创新
- 保留可编辑的 `.pptx` 与可重建的 JS 源文件
- 在交付前做渲染、溢出、字体等验证

## Repository Layout

```text
academic-ppt-skills/
|- .gitignore
|- CHANGELOG.md
|- CONTRIBUTING.md
|- GITHUB_METADATA.md
|- LICENSE
|- README.md
|- THIRD_PARTY_NOTICES.md
`- skill/
   `- academic-ppt/
      |- SKILL.md
      |- package.json
      |- requirements.txt
      |- agents/
      |- assets/
      |- references/
      `- scripts/
```

## Core Characteristics

- input-aware planning instead of generic template filling
- editable PowerPoint output generated with JavaScript
- thesis-native figure reuse when possible
- diagram fallback only when the thesis lacks a usable visual
- validation before delivery
- explicit traceability back to source files

## Supported Inputs

- `.doc`
- `.docx`
- `.pdf`
- `.md`
- `.pptx`
- common images such as `.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`

Inputs may be:

- a single file
- multiple files
- a mixed folder of thesis materials

## Quick Start

Clone the repository:

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill\skill\academic-ppt
```

Install Node dependencies:

```powershell
npm install
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Then use the skill entry file:

```text
skill/academic-ppt/SKILL.md
```

## Build Workflow

The skill pipeline is organized as:

1. audit source materials
2. normalize mixed inputs into a working brief
3. generate a defense-oriented deck plan
4. scaffold a task-local deck workspace
5. author slides in JavaScript
6. render and validate before delivery

For the full workflow and command examples, see:

- [skill/academic-ppt/SKILL.md](skill/academic-ppt/SKILL.md)
- [skill/academic-ppt/references/workflow.md](skill/academic-ppt/references/workflow.md)

## Development Notes

This repository is intended to be used as a skill bundle rather than an npm package or a Python package.

Full validation may require desktop tools already available on the host machine:

- LibreOffice
- Poppler
- fontconfig / `fc-list`
- draw.io / diagrams.net desktop

## Open-Source References

This repository includes original work plus adapted ideas and bundled materials influenced by upstream open-source projects.

Key references are documented in:

- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

Referenced projects currently include:

- [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)
- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)
- [gitbrent/PptxGenJS](https://github.com/gitbrent/PptxGenJS)

## License

This repository is released under the MIT License.

See [LICENSE](LICENSE).
