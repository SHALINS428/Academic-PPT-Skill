# Academic PPT Plugin

[English](README.md)

Academic PPT Plugin 是一个面向 Codex 的开源插件，用来把本地论文、答辩材料和研究资料整理成结构严谨、可编辑、可复现的学术答辩 PPT。

适用场景：

- 本科毕业答辩
- 研究生科研汇报
- 项目中期或阶段性答辩
- 实验室或课程学术汇报

## 产出内容

插件默认产出：

- 可编辑的 `.pptx`
- 可重建的 JavaScript 生成源码
- `deck_plan.md`
- `deck_plan.json`
- `source_manifest.json`
- 幻灯片渲染预览
- 溢出、渲染、字体检查结果

## 支持输入

- `.doc`
- `.docx`
- `.pdf`
- `.md`
- `.pptx`
- 图片：`.png`、`.jpg`、`.jpeg`、`.svg`、`.webp`

输入可以是单个文件、多个文件，或一个混合材料文件夹。

## 核心特点

- 不是通用模板填空，而是按论文内容规划答辩叙事
- 使用 JavaScript 生成可编辑 PowerPoint
- 强调学生本人工作、方法、证据链和创新点
- 优先复用论文原图、截图和已有材料
- 首次运行自动补齐 Python、Node 依赖
- 完整校验按需引导 LibreOffice、Poppler，并为字体检测提供 Python 兜底
- 交付前执行渲染、溢出和字体校验
- 可回溯到原始来源文件

## 插件特性

- 仓库根目录已经包含 `.codex-plugin/plugin.json`
- 插件首次运行会自动补齐本地 Python 和 Node 依赖
- 完整校验会把支持的平台工具下载到 `skill/academic-ppt/.runtime/tools`
- `fontconfig/fc-list` 不可用时，字体检测使用 `fontTools` 扫描本机字体文件
- 插件只负责从本地材料生成学术 PPT，不包含外部图表编辑工作流
- 需要流程、架构或路线视觉时，只在插件内部复用已有素材和 PPT 原生布局

## 部署摘要

| 模式 | 结果 | 必要工具 |
| --- | --- | --- |
| 最小运行 | 生成 PPT，但不做完整校验 | Python、Node.js |
| 完整校验 | 生成 PPT，并完成渲染、图像、字体检查 | Python、Node.js；LibreOffice/Poppler 按需引导；fontconfig 或 Python 字体兜底 |

完整部署说明见：

- [DEPLOYMENT.md](DEPLOYMENT.md)
- [DEPLOYMENT.zh-CN.md](DEPLOYMENT.zh-CN.md)

## 仓库结构

```text
academic-ppt-skills/
|- .codex-plugin/
|  `- plugin.json
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

## 示例输出

下面这张图是基于本地研究论文 `TwiBot-20.pdf` 生成的公开示例预览图，原始论文文件本身不包含在仓库里。

![Example montage](examples/twibot20/montage.png)

示例说明见 [examples/twibot20/README.md](examples/twibot20/README.md)。

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

## 许可协议

本仓库采用 MIT License，见 [LICENSE](LICENSE)。
