# 部署文档

[English Deployment Guide](DEPLOYMENT.md)

这份文档同时面向人工使用者和 Codex agent，说明插件如何部署、检查和运行。

适用目标：

- 在新机器上安装这个插件仓库
- 判断当前机器是否满足运行条件
- 以最小运行或完整校验模式执行 pipeline

## 部署模式

| 模式 | 结果 | 必要工具 |
| --- | --- | --- |
| 最小运行 | 生成 PPT，但不做完整校验 | Python、Node.js |
| 完整校验 | 生成 PPT，并完成渲染、图像、字体检查 | Python、Node.js；LibreOffice/Poppler 按需引导；fontconfig 或 Python 字体兜底 |

插件首次运行会自动补齐 Python 和 Node 依赖。完整校验会把支持的平台工具下载到 `skill/academic-ppt/.runtime/tools`。

## 依赖矩阵

| 工具 | 最小运行 | 完整校验 | 用途 |
| --- | --- | --- | --- |
| Python 3.11+ | 必需 | 必需 | 执行规范化、规划、校验和辅助脚本 |
| Node.js 18+ | 必需 | 必需 | 构建可编辑 PowerPoint |
| LibreOffice (`soffice`) | 可选 | 支持自动引导 | 转换旧版 `.doc`，并通过无头导出参与渲染 |
| Poppler (`pdftoppm`) | 可选 | 支持自动引导 | 生成预览图 |
| fontconfig (`fc-list`) | 可选 | 可选 | 改善字体别名识别；不可用时使用 Python `fontTools` 兜底 |

## 确定性部署步骤

### 1. 克隆仓库

```powershell
git clone https://github.com/SHALINS428/Academic-PPT-Skill.git
cd Academic-PPT-Skill
```

### 2. 运行环境自检

```powershell
python .\skill\academic-ppt\scripts\doctor.py
```

结果解释：

- `Minimal run ready: yes` 表示已经可以生成 PPT
- `Full validation ready: yes` 表示也可以执行完整校验
- 如果完整校验未就绪，可以先用 `--skip-validate`

如需预取完整校验工具：

```powershell
python .\skill\academic-ppt\scripts\doctor.py --bootstrap-tools
```

如果是 agent 自动部署，建议使用机器可读模式：

```powershell
python .\skill\academic-ppt\scripts\doctor.py --json
```

### 3. 准备本地材料目录

示例：

```text
D:\thesis-materials\
|- paper.docx
|- paper.pdf
|- figures\
|- screenshots\
`- previous_slides.pptx
```

### 4. 运行 pipeline

最小运行：

```powershell
python .\skill\academic-ppt\scripts\run_pipeline.py "D:\thesis-materials" --output-dir .\work\run --skip-validate
```

完整运行：

```powershell
python .\skill\academic-ppt\scripts\run_pipeline.py "D:\thesis-materials" --output-dir .\work\run
```

### 5. 检查预期输出

成功运行后，重点查看：

- `work\run\pipeline_summary.json`
- `work\run\planning\deck_plan.md`
- `work\run\planning\deck_plan.json`
- `work\run\deck\build_deck.js`
- `work\run\deck\academic-defense.pptx`

如果启用了完整校验，还应检查：

- `work\run\deck\rendered\`
- `work\run\deck\validation_summary.json`

## Windows 首次安装指南

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

### 引导完整校验工具

完整校验需要 LibreOffice 和 Poppler。插件会优先使用已经安装的工具；找不到时，会尝试按 `assets/tool_manifest.json` 下载并解包到 `.runtime/tools`。

```powershell
python .\skill\academic-ppt\scripts\doctor.py --bootstrap-tools
where.exe soffice
where.exe pdftoppm
where.exe fc-list
```

`fc-list` 在 Windows 上可能仍然不可用，这不是阻塞项，因为字体检测会使用 Python `fontTools` 扫描本机字体文件。

## 环境变量覆盖

项目优先按“环境变量 -> `.runtime/tools` -> 系统 PATH”查找运行时和桌面工具。

常用覆盖方式：

```powershell
$env:ACADEMIC_PPT_PYTHON = "C:\path\to\python.exe"
$env:ACADEMIC_PPT_NODE = "C:\path\to\node.exe"
$env:SOFFICE_EXECUTABLE = "C:\path\to\soffice.exe"
$env:PDFTOPPM_EXECUTABLE = "C:\path\to\pdftoppm.exe"
$env:FC_LIST_EXECUTABLE = "C:\path\to\fc-list.exe"
```

只有在下面两种情况下才需要这样做：

- 工具已安装，但没有加入 `PATH`
- 机器上装了多个版本，必须固定使用某一个

## 自检命令

```powershell
python .\skill\academic-ppt\scripts\doctor.py
python .\skill\academic-ppt\scripts\doctor.py --json
python .\skill\academic-ppt\scripts\doctor.py --require-full-validation
python .\skill\academic-ppt\scripts\bootstrap_runtime.py --tools
```

用法：

- `doctor`：检查当前仓库是否能生成 PPT
- `doctor --json`：给 agent 和自动化流程提供机器可读结果
- `doctor --require-full-validation`：自动引导支持的桌面工具，并在完整校验仍不满足时失败
- `bootstrap_runtime --tools`：预取 Python、Node 和支持的桌面校验依赖

## 常见问题

`python` 或 `node` 无法识别：

- 安装完成后重新打开 PowerShell
- 检查安装器是否加入了 `PATH`
- 必要时设置 `ACADEMIC_PPT_PYTHON` 或 `ACADEMIC_PPT_NODE`

`soffice` 找不到：

- 先运行 `doctor.py --bootstrap-tools`
- 如果自动下载被网络或策略阻止，安装 LibreOffice 或把它加入 `PATH`
- 否则设置 `SOFFICE_EXECUTABLE`

`pdftoppm` 找不到：

- 先运行 `doctor.py --bootstrap-tools`
- 如果自动下载被网络或策略阻止，安装 Poppler 或把它加入 `PATH`
- 否则设置 `PDFTOPPM_EXECUTABLE`

`fc-list` 找不到：

- Windows 上这不是阻塞项，字体检测会使用 Python 兜底
- 只有需要 fontconfig 原生别名行为时才安装 fontconfig
- 否则设置 `FC_LIST_EXECUTABLE`

旧版 `.doc` 转换失败：

- `.doc` 转 `.docx` 依赖 LibreOffice
- 先运行 `doctor.py --bootstrap-tools`
- 确认 `where.exe soffice` 或 `SOFFICE_EXECUTABLE` 能返回有效路径

第一次只想确认能否生成 PPT：

- 使用 `--skip-validate`
- 完整校验工具可在后续运行时自动引导
