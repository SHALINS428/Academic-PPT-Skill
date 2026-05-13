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

## Chinese Overview

Academic PPT Skill 是一个面向毕业答辩和学术汇报场景的开源技能仓库，用于把本地论文、PDF、PPT、图片等材料整理成一套结构严谨、内容精炼、可继续编辑的答辩 PPT。

它强调的不是“自动生成一套花哨幻灯片”，而是：

- 突出学生自己的工作
- 形成清晰叙事：问题 -> 方法 -> 验证 -> 结论 -> 创新
- 保留可编辑的 `.pptx` 与可重建的 JS 源文件
- 在交付前做渲染、溢出、字体等验证

## Example Output

The image below is a public example preview generated from a local research paper (`TwiBot-20.pdf`). The source paper itself is not redistributed in this repository.

![Example montage](examples/twibot20/montage.png)

See [examples/twibot20/README.md](examples/twibot20/README.md) for the example context and validation notes.

## Repository Layout

```text
academic-ppt-skills/
|- .gitignore
|- CHANGELOG.md
|- CONTRIBUTING.md
|- GITHUB_METADATA.md
|- LICENSE
|- README.md
|- REPOSITORY_FOOTPRINT.md
|- THIRD_PARTY_NOTICES.md
|- examples/
|  `- twibot20/
|     |- README.md
|     |- cover.png
|     `- montage.png
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

Clone the repository and enter the skill directory:

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill\skill\academic-ppt
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
npm install
npm run doctor
```

Then review the skill entry file and run the local pipeline:

```text
skill/academic-ppt/SKILL.md
```

## 最小可运行路径

这一节只解决一个问题：让一个第一次接触本项目的 Windows 用户，最快在自己电脑上跑通一次。

适用条件：

- 你的系统是 Windows 10 / 11
- 你的论文材料主要是 `.docx`、`.pdf`、`.md`、`.pptx`、图片
- 你先接受“先生成，再补完整验证”

最少准备这两样：

- Python 3.11 及以上
- Node.js 18 及以上

先在 PowerShell 里确认它们可用：

```powershell
python --version
node --version
```

如果这两条命令都能输出版本号，就继续：

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill\skill\academic-ppt
python -m pip install -r requirements.txt
npm install
python .\scripts\doctor.py
```

准备一个本地材料目录，例如：

```text
D:\你的论文材料
```

第一次试跑，建议先跳过验证：

```powershell
python .\scripts\run_pipeline.py "D:\你的论文材料" --output-dir ..\..\work\run --skip-validate
```

跑通后你会重点看到这些产物：

- `work\run\planning\deck_plan.md`
- `work\run\planning\deck_plan.json`
- `work\run\deck\build_deck.js`
- `work\run\deck\academic-defense.pptx`

这条“最小路径”有两个边界：

- 如果你的输入里包含旧版 `.doc`，还需要安装 LibreOffice 才能先转成 `.docx`
- 如果你要完整渲染检查、字体检查、导出预览图，还需要继续安装下面 Windows 教程里的额外工具

## Windows 首次安装教程

这一节面向中文互联网常见的 Windows 本机环境，目标是把项目装到“可以完整跑 pipeline 和 validation”的状态。

### 1. 安装基础环境

必装：

- Git
- Python 3.11 或更新版本
- Node.js 18 或更新版本

安装后在 PowerShell 检查：

```powershell
git --version
python --version
node --version
```

### 2. 克隆仓库并安装项目依赖

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill\skill\academic-ppt
python -m pip install -r requirements.txt
npm install
npm run doctor
```

如果你只想看“能不能先生成 PPT”，看到下面这两行即可继续：

- `最小运行环境: 就绪`
- `完整验证环境: 未就绪` 也没关系

### 3. 安装完整验证所需桌面工具

建议按下面理解：

- `LibreOffice`：必需于 `.doc` 转 `.docx`，也用于 PPT 渲染
- `Poppler`：用于把 PDF / 幻灯片转成图片，完整验证必需
- `fontconfig / fc-list`：用于字体缺失和替换检查，强烈建议安装
- `draw.io / diagrams.net` 桌面版：只有在你要导出 `.drawio` 为 PNG 时才需要

安装完成后，先检查命令是否能被系统找到：

```powershell
where.exe soffice
where.exe pdftoppm
where.exe fc-list
where.exe draw.io
```

说明：

- 前三条最好都能找到
- `where.exe draw.io` 找不到也没关系，只影响 `.drawio` 导出

### 4. 如果工具不在 PATH，就手动指定

现在项目已经去掉了对维护者私人路径的硬编码。新机器优先按下面顺序找工具：

1. 你自己设置的环境变量
2. 系统 `PATH`
3. 当前正在使用的 Python 解释器

如果某个工具已安装，但 `where.exe` 找不到，就手动指定它的绝对路径。例如：

```powershell
$env:ACADEMIC_PPT_PYTHON = "D:\Python311\python.exe"
$env:ACADEMIC_PPT_NODE = "C:\Program Files\nodejs\node.exe"
$env:SOFFICE_EXECUTABLE = "C:\Program Files\LibreOffice\program\soffice.exe"
$env:PDFTOPPM_EXECUTABLE = "D:\tools\poppler\Library\bin\pdftoppm.exe"
$env:FC_LIST_EXECUTABLE = "D:\tools\msys64\ucrt64\bin\fc-list.exe"
$env:DRAWIO_EXECUTABLE = "C:\Program Files\draw.io\draw.io.exe"
```

通常只在两种情况下需要这样做：

- 你不想改系统 `PATH`
- 你电脑上装了多个 Python / Node / LibreOffice，希望项目固定使用其中一个

### 5. 准备论文材料

建议把答辩相关材料集中到一个目录里，例如：

```text
D:\thesis-materials\
|- paper.docx
|- paper.pdf
|- figures\
|- screenshots\
`- previous_slides.pptx
```

### 6. 运行完整流程

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run
```

如果你还希望自动生成可编辑的 `.drawio` 草图任务：

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run --materialize-diagrams
```

### 7. 查看输出结果

重点看这几个位置：

- `work\run\pipeline_summary.json`
- `work\run\planning\deck_plan.md`
- `work\run\deck\academic-defense.pptx`
- `work\run\deck\rendered\`
- `work\run\deck\validation_summary.json`

### 8. Windows 用户最常见的问题

`python` 或 `node` 命令不存在：

- 说明安装时没有加入 PATH
- 重新打开 PowerShell 再试一次
- 仍不行就手动设置 `ACADEMIC_PPT_PYTHON` 或 `ACADEMIC_PPT_NODE`

`soffice` 找不到：

- LibreOffice 没安装，或者安装后未加入 PATH
- 可以先用 `where.exe soffice` 检查
- 找不到时设置 `SOFFICE_EXECUTABLE`

`pdftoppm` 找不到：

- 说明 Poppler 没装好或没加 PATH
- 找不到时设置 `PDFTOPPM_EXECUTABLE`

`fc-list` 找不到：

- 这通常不会阻止最小生成，但会影响字体检查
- 找不到时设置 `FC_LIST_EXECUTABLE`

输入里有 `.doc`，但转换失败：

- 旧版 `.doc` 依赖 LibreOffice 转桥接 `.docx`
- 先确认 `where.exe soffice` 能找到命令

第一次只想确认能不能生成 PPT：

- 先用 `--skip-validate`
- 等主流程跑通后再补装 LibreOffice / Poppler / fontconfig 做完整检查

不知道自己缺什么：

- 先运行 `python .\scripts\doctor.py`
- 如果你希望“没装完整验证工具就直接报错”，运行 `npm run doctor:full`

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

Runtime discovery now prefers environment variables and system `PATH` over maintainer-local absolute paths.

Useful overrides:

- `ACADEMIC_PPT_PYTHON`
- `ACADEMIC_PPT_NODE`
- `SOFFICE_EXECUTABLE`
- `PDFTOPPM_EXECUTABLE`
- `FC_LIST_EXECUTABLE`
- `DRAWIO_EXECUTABLE`
- `DIAGRAMS_NET_EXECUTABLE`

Built-in self-check:

- `python .\scripts\doctor.py`
- `npm run doctor`
- `npm run doctor:full`

Full validation may require desktop tools already available on the host machine:

- LibreOffice
- Poppler
- fontconfig / `fc-list`
- draw.io / diagrams.net desktop

## Repository Footprint

This repository intentionally keeps the layout shells, chart shells, helper code, and bundled converters required for offline reproducibility.

See [REPOSITORY_FOOTPRINT.md](REPOSITORY_FOOTPRINT.md) for what is intentionally bundled, what is excluded, and what could be split later.

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
