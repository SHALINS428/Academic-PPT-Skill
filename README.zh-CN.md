# Academic PPT Skill

[English](README.md)

Academic PPT Skill 是一个开源 skill 仓库，用于把本地论文材料整理成结构严谨、内容精炼、可继续编辑的学术答辩 PPT。

适用场景：

- 本科毕业答辩
- 研究生科研汇报
- 项目中期或阶段性答辩
- 实验室或课程学术汇报

## 最终产物

本仓库默认生成：

- 可编辑的 `.pptx`
- 可重建的 JavaScript 生成源码
- `deck_plan.md`
- `deck_plan.json`
- `source_manifest.json`
- 幻灯片渲染预览图
- 文本溢出、渲染、字体检查结果

## 支持的输入

- `.doc`
- `.docx`
- `.pdf`
- `.md`
- `.pptx`
- `.png`、`.jpg`、`.jpeg`、`.svg`、`.webp` 等图片

输入形式可以是：

- 单个文件
- 多个文件
- 一个混合材料目录

## 部署模式

这个项目有两个实际可用的部署目标。

| 模式 | 结果 | 必要工具 |
| --- | --- | --- |
| 最小运行 | 生成 PPT，但不做完整验证 | Python、Node.js |
| 完整验证 | 生成 PPT，并完成渲染、图像、字体验证 | Python、Node.js、LibreOffice、Poppler、fontconfig |

`draw.io` / `diagrams.net` 桌面版是可选项，只在导出 `.drawio` 为 PNG 时需要。

## 依赖矩阵

| 工具 | 最小运行 | 完整验证 | 用途 |
| --- | --- | --- | --- |
| Python 3.11+ | 必需 | 必需 | 执行规范化、规划、验证和辅助脚本 |
| Node.js 18+ | 必需 | 必需 | 构建可编辑的 PowerPoint |
| LibreOffice (`soffice`) | 可选 | 必需 | 转换旧版 `.doc`，并通过无头导出参与 PPT 渲染 |
| Poppler (`pdftoppm`) | 可选 | 必需 | 把 PDF 输出转成预览图 |
| fontconfig (`fc-list`) | 可选 | 必需 | 检查字体缺失和字体替换 |
| draw.io / diagrams.net | 可选 | 可选 | 导出 `.drawio` 图为 PNG |

## 确定性部署步骤

下面这套顺序既适合人工操作，也适合 agent 自动执行。

### 1. 克隆仓库

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill\skill\academic-ppt
```

### 2. 安装 Python 依赖

```powershell
python -m pip install -r requirements.txt
```

### 3. 安装 Node 依赖

```powershell
npm install
```

### 4. 运行环境自检

```powershell
npm run doctor
```

结果按下面理解：

- `最小运行环境: 就绪` 表示已经可以生成 PPT
- `完整验证环境: 就绪` 表示可以执行完整验证
- 如果只有第一项就绪，第一次运行请加 `--skip-validate`

如果是 agent 自动部署，建议使用机器可读的检查方式：

```powershell
python .\scripts\doctor.py --json
```

agent 应按下面方式解释 JSON：

- `minimal_run_ready: true` 表示已经可以生成 PPT
- `full_validation_ready: true` 表示已经可以做完整验证
- `blockers` 会列出缺失的安装步骤

### 5. 准备本地材料目录

例如：

```text
D:\thesis-materials\
|- paper.docx
|- paper.pdf
|- figures\
|- screenshots\
`- previous_slides.pptx
```

### 6. 运行 pipeline

最小运行：

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run --skip-validate
```

完整运行：

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run
```

如果还希望自动生成可编辑 `.drawio` 草图：

```powershell
python .\scripts\run_pipeline.py "D:\thesis-materials" --output-dir ..\..\work\run --materialize-diagrams
```

### 7. 检查预期输出

成功运行后，重点查看：

- `work\run\pipeline_summary.json`
- `work\run\planning\deck_plan.md`
- `work\run\planning\deck_plan.json`
- `work\run\deck\build_deck.js`
- `work\run\deck\academic-defense.pptx`

如果开启了完整验证，还应检查：

- `work\run\deck\rendered\`
- `work\run\deck\validation_summary.json`

## Windows 首次安装指南

本仓库优先面向 Windows。新的 Windows 用户通常按下面顺序就可以装好并跑通。

### 安装基础运行时

必需：

- Git
- Python 3.11 或更高版本
- Node.js 18 或更高版本

验证：

```powershell
git --version
python --version
node --version
```

### 安装完整验证工具

如果你要完整验证，请安装：

- LibreOffice
- Poppler
- fontconfig / `fc-list`

验证：

```powershell
where.exe soffice
where.exe pdftoppm
where.exe fc-list
where.exe draw.io
```

说明：

- 前三条命令是完整验证所必需的
- `where.exe draw.io` 找不到不会阻塞主流程

## 环境变量覆盖

项目现在优先按“环境变量 -> 系统 `PATH`”查找运行时和桌面工具，不再依赖维护者本机绝对路径。

常用覆盖方式：

```powershell
$env:ACADEMIC_PPT_PYTHON = "C:\path\to\python.exe"
$env:ACADEMIC_PPT_NODE = "C:\path\to\node.exe"
$env:SOFFICE_EXECUTABLE = "C:\path\to\soffice.exe"
$env:PDFTOPPM_EXECUTABLE = "C:\path\to\pdftoppm.exe"
$env:FC_LIST_EXECUTABLE = "C:\path\to\fc-list.exe"
$env:DRAWIO_EXECUTABLE = "C:\path\to\draw.io.exe"
$env:DIAGRAMS_NET_EXECUTABLE = "C:\path\to\diagrams.net.exe"
```

只在下面两种情况下需要这样做：

- 工具已安装，但没有加入 `PATH`
- 机器上装了多个版本，必须固定使用某一个

## 自检命令

```powershell
python .\scripts\doctor.py
python .\scripts\doctor.py --json
npm run doctor
npm run doctor:full
```

用法：

- `doctor`：检查当前仓库是否已经能生成 PPT
- `doctor --json`：给 agent 和自动化流程提供机器可读结果
- `doctor:full`：如果完整验证环境不满足则直接失败

## 常见问题

`python` 或 `node` 无法识别：

- 安装完成后重新打开 PowerShell
- 检查安装器是否加入了 `PATH`
- 必要时设置 `ACADEMIC_PPT_PYTHON` 或 `ACADEMIC_PPT_NODE`

`soffice` 找不到：

- 安装 LibreOffice 或把它加入 `PATH`
- 否则设置 `SOFFICE_EXECUTABLE`

`pdftoppm` 找不到：

- 安装 Poppler 或把它加入 `PATH`
- 否则设置 `PDFTOPPM_EXECUTABLE`

`fc-list` 找不到：

- 安装 fontconfig 或把它加入 `PATH`
- 否则设置 `FC_LIST_EXECUTABLE`

旧版 `.doc` 转换失败：

- `.doc` 转 `.docx` 依赖 LibreOffice
- 确认 `where.exe soffice` 能返回有效路径

第一次只想确认能否生成 PPT：

- 使用 `--skip-validate`
- 完整验证工具可以后装

## 仓库结构

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

## 示例输出

下图是基于本地研究论文 `TwiBot-20.pdf` 生成的公开示例预览图。原始论文 PDF 不包含在本仓库中。

![Example montage](examples/twibot20/montage.png)

示例上下文和验证说明见 [examples/twibot20/README.md](examples/twibot20/README.md)。

## 补充文档

- [skill/academic-ppt/SKILL.md](skill/academic-ppt/SKILL.md)
- [skill/academic-ppt/references/workflow.md](skill/academic-ppt/references/workflow.md)
- [REPOSITORY_FOOTPRINT.md](REPOSITORY_FOOTPRINT.md)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

## 开源参考

当前已注明的参考项目：

- [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)
- [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)
- [gitbrent/PptxGenJS](https://github.com/gitbrent/PptxGenJS)

## 许可证

本仓库采用 MIT License，见 [LICENSE](LICENSE)。
