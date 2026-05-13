#!/usr/bin/env python3
"""Build a defense-oriented slide plan from normalized academic materials."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROLE_SCORE = {
    "thesis_manuscript": 120,
    "source_document": 110,
    "proposal_or_report": 90,
    "defense_deck": 70,
    "reference_deck": 60,
    "notes": 50,
    "supporting_material": 40,
    "figure_asset": 20,
}

KIND_SCORE = {"doc": 29, "docx": 30, "pdf": 28, "markdown": 20, "text": 15, "pptx": 12, "image": 5}

SLIDE_RULES = {
    "zh": [
        {"key": "cover", "slide_type": "cover"},
        {"key": "toc", "slide_type": "toc", "title": "答辩提纲"},
        {
            "key": "background",
            "slide_type": "content",
            "title": "选题背景与研究意义",
            "default_takeaway": "在线招聘、人岗匹配和推荐冷启动等实际问题共同构成了本课题的研究背景。",
            "section_keywords": ["研究背景", "研究意义", "研究现状", "研究空白", "绪论", "背景", "现状"],
            "content_keywords": ["招聘推荐", "人岗匹配", "冷启动", "语义理解", "研究意义", "现有研究", "不足"],
            "avoid_keywords": ["实验结果", "功能测试", "系统界面"],
            "select_sections": 2,
            "visual_type": "none",
            "visual_keywords": [],
            "prefer_metric": False,
        },
        {
            "key": "problem",
            "slide_type": "content",
            "title": "研究目标与核心任务",
            "default_takeaway": "论文围绕方法设计、系统实现与验证评估三条主线展开。",
            "section_keywords": ["研究目的", "研究目标", "研究内容", "主要研究内容", "研究空白总结", "目标", "主要工作"],
            "content_keywords": ["提出", "设计", "实现", "验证", "研究内容", "主要工作", "核心工作"],
            "avoid_keywords": ["实验结果", "功能测试", "系统界面"],
            "select_sections": 2,
            "visual_type": "none",
            "visual_keywords": [],
            "prefer_metric": False,
        },
        {
            "key": "technical_route",
            "slide_type": "content",
            "title": "系统总体架构与技术路线",
            "default_takeaway": "系统总体架构需要把业务流程、算法流程和数据支撑组织成完整闭环。",
            "section_keywords": ["系统框架分析与设计", "整体设计规划", "系统架构", "系统流程", "技术路线", "部署"],
            "content_keywords": ["前后端分离", "算法服务", "后端服务", "前端应用", "MySQL", "Redis", "模块划分", "系统流程"],
            "avoid_keywords": ["实验结果", "模型对比实验"],
            "select_sections": 2,
            "visual_type": "system_architecture",
            "visual_keywords": ["系统架构图", "整体流程", "系统全流程", "技术路线", "推荐流程", "泳道图"],
            "prefer_metric": False,
        },
        {
            "key": "student_work_1",
            "slide_type": "content",
            "title": "核心方法与算法设计",
            "default_takeaway": "论文核心方法通常体现在算法流程、模型结构和融合策略设计上。",
            "section_keywords": ["核心算法设计", "BERT语义匹配算法", "协同过滤算法", "权重融合策略", "动态权重调整", "推荐模型整体架构"],
            "content_keywords": ["BERT", "协同过滤", "动态权重", "融合", "LightGBM", "排序", "特征工程"],
            "avoid_keywords": ["实验结果", "模型对比实验", "功能测试", "界面展示"],
            "select_sections": 2,
            "visual_type": "workflow",
            "visual_keywords": ["核心算法整体流程图", "协同过滤算法流程图", "推荐模型整体架构图", "流程图"],
            "prefer_metric": False,
        },
        {
            "key": "student_work_2",
            "slide_type": "content",
            "title": "工程实现与系统落地",
            "default_takeaway": "系统落地能力体现在模块化实现、缓存优化和角色闭环支撑上。",
            "section_keywords": ["程序结构", "关键实现细节", "语义向量缓存", "可解释推荐理由生成机制", "系统核心功能实现与界面展示", "性能优化"],
            "content_keywords": ["缓存", "推荐理由", "前后端分离", "系统实现", "角色", "接口", "部署", "性能优化"],
            "avoid_keywords": ["实验结果", "模型对比实验"],
            "select_sections": 2,
            "visual_type": "screenshot",
            "visual_keywords": ["岗位推荐首页界面", "人才推荐界面", "登录与注册界面", "前端应用工程结构图", "后端服务工程结构图", "算法服务工程结构图"],
            "prefer_metric": False,
        },
        {
            "key": "experiment",
            "slide_type": "content",
            "title": "实验设计与验证方案",
            "default_takeaway": "实验设计需要说明数据来源、评价指标和对比基线，以支撑后续结论。",
            "section_keywords": ["实验环境", "数据集", "模型设计", "推荐模型整体架构", "系统全维度测试", "功能测试", "实验设计"],
            "content_keywords": ["数据集", "评价指标", "基线", "实验环境", "验证", "测试", "抽样", "部署环境"],
            "avoid_keywords": ["创新点", "研究局限性"],
            "select_sections": 2,
            "visual_type": "system_architecture",
            "visual_keywords": ["推荐模型整体架构图", "核心数据实体关系图", "系统架构图"],
            "prefer_metric": True,
        },
        {
            "key": "results",
            "slide_type": "content",
            "title": "实验结果验证方法有效性",
            "default_takeaway": "结果页需要给出关键指标、对比对象和能支撑结论的核心证据。",
            "section_keywords": ["算法实验结果与分析", "模型对比实验", "动态权重融合策略有效性实验", "功能测试", "性能测试", "系统测试"],
            "content_keywords": ["AUC", "PR AUC", "F1", "提升", "优于", "验证集", "并发", "耗时", "通过率"],
            "avoid_keywords": ["研究现状", "技术选型"],
            "select_sections": 2,
            "visual_type": "chart",
            "visual_keywords": ["特征重要性Top10", "特征重要性Top20", "柱状图", "曲线", "对比实验", "性能测试"],
            "prefer_metric": True,
        },
        {
            "key": "innovation",
            "slide_type": "content",
            "title": "创新点与论文贡献",
            "default_takeaway": "创新点必须回到方法、系统和结果三个层面进行归纳，而不是停留在概念描述。",
            "section_keywords": ["核心创新点", "创新点", "研究空白总结", "主要研究内容", "总结"],
            "content_keywords": ["创新", "提出", "构建", "实现", "改进", "贡献", "融合", "特征工程"],
            "avoid_keywords": ["功能测试"],
            "select_sections": 2,
            "visual_type": "none",
            "visual_keywords": [],
            "prefer_metric": False,
        },
        {
            "key": "limitations",
            "slide_type": "content",
            "title": "不足与后续展望",
            "default_takeaway": "边界条件和后续工作需要主动说明，以提高答辩表达的完整性与可信度。",
            "section_keywords": ["研究局限性分析", "总结和未来工作", "未来工作", "局限", "不足", "展望"],
            "content_keywords": ["局限", "不足", "未来", "展望", "改进", "后续", "优化"],
            "avoid_keywords": ["功能测试", "系统界面"],
            "select_sections": 2,
            "visual_type": "none",
            "visual_keywords": [],
            "prefer_metric": False,
        },
        {"key": "thanks", "slide_type": "closing", "title": "感谢各位老师聆听，期待批评指正"},
    ],
    "en": [
        {"key": "cover", "slide_type": "cover"},
        {"key": "toc", "slide_type": "toc", "title": "Agenda"},
        {"key": "background", "slide_type": "content", "title": "Research Background and Motivation", "default_takeaway": "This topic should be grounded in a concrete engineering or research need.", "section_keywords": ["background", "motivation", "significance", "related work", "introduction"], "content_keywords": ["motivation", "matching", "recommendation", "cold start", "semantic"], "select_sections": 2, "visual_type": "none", "visual_keywords": [], "prefer_metric": False},
        {"key": "problem", "slide_type": "content", "title": "Objective and Main Tasks", "default_takeaway": "The thesis should define what was built, optimized, and verified.", "section_keywords": ["objective", "goal", "contribution", "main work"], "content_keywords": ["propose", "design", "implement", "validate"], "select_sections": 2, "visual_type": "none", "visual_keywords": [], "prefer_metric": False},
        {"key": "technical_route", "slide_type": "content", "title": "System Architecture and Technical Route", "default_takeaway": "The overall architecture should connect business flow, model flow, and system support.", "section_keywords": ["architecture", "overall design", "workflow", "technical route"], "content_keywords": ["frontend", "backend", "service", "database", "cache", "module"], "select_sections": 2, "visual_type": "system_architecture", "visual_keywords": ["architecture", "workflow", "pipeline", "system flow"], "prefer_metric": False},
        {"key": "student_work_1", "slide_type": "content", "title": "Core Method and Algorithm Design", "default_takeaway": "The method slide should explain the algorithm pipeline and the student's main design choices.", "section_keywords": ["method", "algorithm", "model", "fusion", "ranking"], "content_keywords": ["bert", "filtering", "fusion", "ranking", "feature"], "select_sections": 2, "visual_type": "workflow", "visual_keywords": ["algorithm", "workflow", "architecture", "pipeline"], "prefer_metric": False},
        {"key": "student_work_2", "slide_type": "content", "title": "Engineering Implementation", "default_takeaway": "The implementation slide should show how the method was turned into a working system.", "section_keywords": ["implementation", "system", "cache", "interface", "deployment"], "content_keywords": ["cache", "service", "frontend", "backend", "optimization"], "select_sections": 2, "visual_type": "screenshot", "visual_keywords": ["interface", "page", "ui", "screenshot"], "prefer_metric": False},
        {"key": "experiment", "slide_type": "content", "title": "Evaluation Setup", "default_takeaway": "The evaluation should make datasets, metrics, and baselines explicit.", "section_keywords": ["experiment", "dataset", "evaluation", "baseline", "test"], "content_keywords": ["auc", "f1", "metric", "dataset", "baseline"], "select_sections": 2, "visual_type": "system_architecture", "visual_keywords": ["model architecture", "data model", "system architecture"], "prefer_metric": True},
        {"key": "results", "slide_type": "content", "title": "Results and Effectiveness", "default_takeaway": "The results slide should show the metrics that actually support the main claim.", "section_keywords": ["results", "analysis", "comparison", "performance", "test"], "content_keywords": ["auc", "f1", "improve", "latency", "throughput", "better than"], "select_sections": 2, "visual_type": "chart", "visual_keywords": ["top", "chart", "curve", "comparison", "performance"], "prefer_metric": True},
        {"key": "innovation", "slide_type": "content", "title": "Innovation and Contribution", "default_takeaway": "The contribution slide should connect the novelty claim back to the method and evidence.", "section_keywords": ["innovation", "contribution", "summary"], "content_keywords": ["novel", "propose", "build", "improve"], "select_sections": 2, "visual_type": "none", "visual_keywords": [], "prefer_metric": False},
        {"key": "limitations", "slide_type": "content", "title": "Limitations and Future Work", "default_takeaway": "Explicit boundaries improve the credibility of the conclusion.", "section_keywords": ["limitation", "future work", "outlook", "conclusion"], "content_keywords": ["future", "limitation", "scope", "extend"], "select_sections": 2, "visual_type": "none", "visual_keywords": [], "prefer_metric": False},
        {"key": "thanks", "slide_type": "closing", "title": "Thank you for your attention"},
    ],
}

AGENDA_LABELS = {
    "zh": {"background": "研究背景", "problem": "研究目标", "technical_route": "技术路线", "student_work_1": "方法设计", "student_work_2": "工程实现", "experiment": "实验设计", "results": "实验结果", "innovation": "创新贡献", "limitations": "不足与展望"},
    "en": {"background": "Background", "problem": "Objective", "technical_route": "Technical Route", "student_work_1": "Method", "student_work_2": "Implementation", "experiment": "Evaluation", "results": "Results", "innovation": "Contribution", "limitations": "Future Work"},
}

SECTION_COPY = {
    "background": {"zh": {"title": "研究背景", "desc": "问题场景与选题价值"}, "en": {"title": "Background", "desc": "Problem context and topic value"}},
    "problem": {"zh": {"title": "研究目标", "desc": "论文要解决的核心任务"}, "en": {"title": "Objective", "desc": "Core thesis goals and tasks"}},
    "technical_route": {"zh": {"title": "技术路线", "desc": "总体架构与实现路径"}, "en": {"title": "Route", "desc": "Overall architecture and implementation path"}},
    "student_work_1": {"zh": {"title": "方法设计", "desc": "核心算法与模型结构"}, "en": {"title": "Method", "desc": "Core algorithm and model structure"}},
    "student_work_2": {"zh": {"title": "工程实现", "desc": "系统落地与关键优化"}, "en": {"title": "Implementation", "desc": "System landing and key optimizations"}},
    "experiment": {"zh": {"title": "实验设计", "desc": "数据、指标与验证方案"}, "en": {"title": "Evaluation", "desc": "Datasets, metrics, and validation setup"}},
    "results": {"zh": {"title": "实验结果", "desc": "效果验证与量化证据"}, "en": {"title": "Results", "desc": "Effectiveness and quantitative evidence"}},
    "innovation": {"zh": {"title": "创新点", "desc": "贡献归纳与证据回收"}, "en": {"title": "Innovation", "desc": "Contribution summary and evidence"}},
    "limitations": {"zh": {"title": "展望", "desc": "边界条件与未来工作"}, "en": {"title": "Outlook", "desc": "Boundaries and future work"}},
}

CHAPTER_BREAKS = {
    "background": {"num": "01", "zh": {"title": "研究背景与问题", "desc": "从场景、需求与目标展开"}, "en": {"title": "Background and Problem", "desc": "Start from context, need, and objective"}},
    "technical_route": {"num": "02", "zh": {"title": "技术方案与实现", "desc": "说明方法逻辑与本人工作"}, "en": {"title": "Method and Implementation", "desc": "Explain the method and the student's work"}},
    "experiment": {"num": "03", "zh": {"title": "验证设计与结果", "desc": "用实验和测试回答答辩问题"}, "en": {"title": "Evaluation and Findings", "desc": "Use defensible evidence to answer the committee"}},
    "innovation": {"num": "04", "zh": {"title": "结论与展望", "desc": "回收贡献、边界与后续工作"}, "en": {"title": "Conclusion and Outlook", "desc": "Close on contributions, limits, and future work"}},
}

NOISE_EXACT = {
    "zh": {"目录", "摘要", "abstract", "关键词", "key words", "本科毕业论文", "本科毕业论文设计", "第1章", "第2章", "第3章", "第4章", "第5章"},
    "en": {"agenda", "abstract", "keywords", "table of contents"},
}

METRIC_PATTERN = re.compile(r"(AUC|PR\s*AUC|F1(?:-?Score)?|Precision|Recall|准确率|召回率|通过率|耗时|并发|ms|秒|提升|优于)", flags=re.IGNORECASE)
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
FIGURE_CAPTION_PATTERN = re.compile(r"^(图|Figure|FIGURE|表|Table)\s*[0-9一二三四五六七八九十\\-\\.]+", flags=re.IGNORECASE)
META_LABEL_PATTERN = re.compile(r"(作者姓名|作者学号|导师姓名|导师职称|导师单位|所在学院|所学专业|学生|作者|导师|学校|学院|单位)")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def has_han(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def normalize_cjk_spacing(text: str) -> str:
    previous = None
    value = text
    while previous != value:
        previous = value
        value = re.sub(r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff])", r"\1\2", value)
    return value


def clean_text(text: str) -> str:
    value = text or ""
    value = value.replace("\\.", ".").replace("\\-", "-").replace("\\(", "(").replace("\\)", ")")
    value = re.sub(r"<a\b[^>]*>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"</a>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"[*_>#]", " ", value)
    value = re.sub(r"_Ref\d+", " ", value)
    value = re.sub(r"__RefHeading___Toc\d+", " ", value)
    value = normalize_cjk_spacing(value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"^\d+[.)、]\s*", "", value)
    return value.strip(" \t\r\n-—:：|")


def clean_heading_text(text: str) -> str:
    value = clean_text(text)
    value = re.sub(r"^第\s*[一二三四五六七八九十百零0-9]+\s*章\s*", "", value)
    value = re.sub(r"^\d+(?:\.\d+)*\s*", "", value)
    return value.strip(" .-—:：")


def detect_language(text: str) -> str:
    zh = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    en = sum(1 for ch in text if "a" <= ch.lower() <= "z")
    return "zh" if zh >= en else "en"


def shorten(text: str, language: str, limit: int) -> str:
    value = clean_text(text)
    if not value:
        return ""
    parts = re.split(r"[。！？；]" if language == "zh" else r"(?<=[.!?;])\s+", value)
    for part in parts:
        part = clean_text(part)
        if len(part) >= 10:
            return part[:limit].rstrip(" ,;") + ("…" if len(part) > limit else "")
    return value[:limit].rstrip(" ,;") + ("…" if len(value) > limit else "")


def score_source(item: dict) -> int:
    name = item["name"].casefold()
    bonus = 12 if any(token in name for token in ("final", "latest", "定稿", "终稿", "最终")) else 0
    return ROLE_SCORE.get(item["role"], 0) + KIND_SCORE.get(item["kind"], 0) + bonus


def normalize_metadata_text(text: str) -> str:
    value = normalize_cjk_spacing(text)
    value = re.sub(r"\s*([：:])\s*", r"\1", value)
    return value


def looks_like_toc_entry(text: str) -> bool:
    value = clean_text(text)
    if not value:
        return False
    if len(value) <= 72 and re.match(r"^(第?\d+章|[0-9]+(?:\.[0-9]+){0,4})\s+.+\s+\d{1,3}$", value):
        return True
    return False


def is_noise_text(text: str, language: str) -> bool:
    value = clean_text(text)
    if not value:
        return True
    if value.casefold() in NOISE_EXACT[language]:
        return True
    if looks_like_toc_entry(value):
        return True
    if FIGURE_CAPTION_PATTERN.match(value):
        return True
    if re.fullmatch(r"[0-9\-.()]+", value):
        return True
    if META_LABEL_PATTERN.search(value) and len(value) < 32:
        return True
    return False


def split_sentences(text: str, language: str) -> list[str]:
    value = clean_text(text)
    if not value:
        return []
    raw_parts = re.split(r"[。！？；]" if language == "zh" else r"(?<=[.!?;])\s+", value)
    sentences = []
    for part in raw_parts:
        part = clean_text(part)
        if part:
            sentences.append(part)
    return sentences


def sentence_score(text: str, keywords: list[str], prefer_metric: bool) -> int:
    value = clean_text(text)
    if not value:
        return -999
    score = 0
    lowered = value.casefold()
    for keyword in keywords:
        if keyword.casefold() in lowered:
            score += 8 if len(keyword) >= 4 else 5
    if prefer_metric and METRIC_PATTERN.search(value):
        score += 18
    elif METRIC_PATTERN.search(value):
        score += 10
    if 18 <= len(value) <= 88:
        score += 8
    elif len(value) <= 12:
        score -= 20
    elif len(value) > 120:
        score -= 8
    if "代码如下" in value or "如下所示" in value or "见下页" in value:
        score -= 10
    if "\\[" in value or "等人" in value:
        score -= 4
    if looks_like_toc_entry(value):
        score -= 80
    return score


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen = set()
    output = []
    for value in values:
        key = clean_text(value)
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(key)
    return output


def parse_sources(brief_text: str, manifest: dict) -> list[dict]:
    manifest_by_id = {item["id"]: item for item in manifest["files"]}
    chunks = re.split(r"(?m)^## Source: ", brief_text)
    sources = []
    for chunk in chunks[1:]:
        lines = chunk.splitlines()
        if not lines:
            continue
        source_id = None
        converted_path = None
        content = []
        in_meta = True
        for line in lines[1:]:
            if in_meta and line.startswith("- Source ID:"):
                source_id = line.split(":", 1)[1].strip().strip("`")
            elif in_meta and line.startswith("- Converted Path:"):
                converted_path = line.split(":", 1)[1].strip().strip("`")
            elif in_meta and (line.startswith("- ") or not line.strip()):
                continue
            else:
                in_meta = False
                content.append(line)
        if source_id and source_id in manifest_by_id:
            item = manifest_by_id[source_id]
            sources.append({**item, "content": "\n".join(content).strip(), "converted_path": converted_path})
    return sorted(sources, key=score_source, reverse=True)


def extract_cover_title(sources: list[dict], language: str) -> str:
    file_title = ""
    if sources:
        stem = Path(sources[0]["name"]).stem
        stem = re.sub(r"^\d+[-_]", "", stem)
        stem = re.sub(r"^[^-_]+[-_]", "", stem) if len(stem.split("-")) >= 3 else stem
        file_title = clean_text(stem.replace("_", " "))
    for source in sources:
        lines = [clean_text(line) for line in source["content"].splitlines()[:80]]
        title_lines: list[str] = []
        for raw_line in lines:
            line = clean_text(raw_line)
            if not line:
                continue
            if line in {"摘要", "ABSTRACT", "Abstract"}:
                break
            if META_LABEL_PATTERN.search(normalize_metadata_text(line)):
                break
            if line in {"本科毕业论文", "本科毕业论文（设计）", "本科毕业论文(设计)"}:
                continue
            if is_noise_text(line, language):
                continue
            if len(line) < 6:
                continue
            if language == "zh" and has_han(line):
                title_lines.append(line)
            elif language == "en" and len(line.split()) >= 2:
                title_lines.append(line)
            if len(title_lines) >= 3:
                break
        if title_lines:
            merged = clean_text("".join(title_lines) if language == "zh" else " ".join(title_lines))
            if 8 <= len(merged) <= 96:
                if file_title and len(file_title) > len(merged) + 4 and file_title.startswith(merged):
                    return file_title
                return merged
    if file_title:
        return file_title
    return "毕业论文答辩" if language == "zh" else "Academic Defense"


def extract_identity(sources: list[dict], language: str) -> dict:
    combined = "\n".join(source["content"] for source in sources[:3])
    title = extract_cover_title(sources, language)
    meta: dict[str, str] = {"author": "", "advisor": "", "school": "", "college": ""}
    scan_lines = []
    for source in sources[:2]:
        scan_lines.extend(source["content"].splitlines()[:120])
    for raw_line in scan_lines:
        line = normalize_metadata_text(clean_text(raw_line))
        if not line:
            continue
        pairs = [
            ("author", ["作者姓名", "学生姓名", "作者", "学生"]),
            ("advisor", ["导师姓名", "指导教师", "导师"]),
            ("school", ["导师单位", "所在学校", "学校", "university"]),
            ("college", ["所在学院", "学院", "department", "college"]),
        ]
        for key, labels in pairs:
            if meta[key]:
                continue
            for label in labels:
                marker = f"{label}:"
                marker_cn = f"{label}："
                if line.startswith(marker) or line.startswith(marker_cn):
                    meta[key] = clean_text(line.split(":", 1)[1] if ":" in line else line.split("：", 1)[1])
                    break
    institution = meta["school"]
    if meta["college"] and meta["college"] not in institution:
        institution = f"{meta['school']}{meta['college']}" if meta["school"] else meta["college"]
    corpus = combined.casefold()
    defense_type = "general_thesis"
    if any(token in corpus for token in ("实验", "数据集", "指标", "dataset", "baseline", "metric")):
        defense_type = "experimental_thesis"
    if any(token in corpus for token in ("系统", "架构", "模块", "system", "architecture", "module")):
        defense_type = "engineering_thesis"
    visual = "academic_premium"
    if any(token in corpus for token in ("大学", "学院", "university", "college")):
        visual = "campus_academic"
    if any(token in corpus for token in ("医学", "医院", "medical", "clinical", "hospital")):
        visual = "campus_medical"
    return {
        "title": title or ("毕业论文答辩" if language == "zh" else "Academic Defense"),
        "language": "Chinese" if language == "zh" else "English",
        "audience": "答辩委员会" if language == "zh" else "Defense committee",
        "defense_type": defense_type,
        "visual_direction": visual,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "author": meta["author"],
        "advisor": meta["advisor"],
        "institution": institution,
        "output_pptx": "academic-defense.pptx",
    }


def section_copy(language: str, key: str) -> dict[str, str]:
    return SECTION_COPY.get(key, {}).get(language, {"title": key, "desc": ""})


def build_sections_and_images(sources: list[dict], language: str) -> tuple[list[dict], list[dict]]:
    sections: list[dict] = []
    images: list[dict] = []
    section_index = 0
    image_index = 0
    for source in sources:
        converted_path = Path(source["converted_path"]).expanduser().resolve() if source.get("converted_path") else None
        current = {"heading": "", "level": 0, "lines": [], "images": []}
        pending_images: list[dict] = []

        def flush_current() -> None:
            nonlocal section_index, current
            lines = [clean_text(line) for line in current["lines"] if not is_noise_text(line, language)]
            lines = dedupe_keep_order(lines)
            text = " ".join(lines).strip()
            heading = clean_heading_text(current["heading"])
            if not heading and not text and not current["images"]:
                current = {"heading": "", "level": 0, "lines": [], "images": []}
                return
            section_index += 1
            sections.append(
                {
                    "section_id": f"{source['id']}-sec-{section_index:03d}",
                    "source_id": source["id"],
                    "source_path": source["path"],
                    "heading": heading,
                    "level": current["level"],
                    "text": text,
                    "images": list(current["images"]),
                }
            )
            current = {"heading": "", "level": 0, "lines": [], "images": []}

        for raw_line in source["content"].splitlines():
            line = raw_line.strip()
            heading_match = HEADING_PATTERN.match(line)
            if heading_match:
                flush_current()
                current["level"] = len(heading_match.group(1))
                current["heading"] = clean_heading_text(heading_match.group(2))
                pending_images = []
                continue
            image_paths = IMAGE_PATTERN.findall(line)
            if image_paths:
                for rel_path in image_paths:
                    image_index += 1
                    absolute = ""
                    if converted_path:
                        candidate = (converted_path.parent / rel_path).resolve()
                        if candidate.exists():
                            absolute = str(candidate)
                    image = {
                        "image_id": f"img-{image_index:03d}",
                        "source_id": source["id"],
                        "source_path": source["path"],
                        "path": absolute,
                        "caption": "",
                        "heading": current["heading"],
                        "context": "",
                    }
                    current["images"].append(image)
                    images.append(image)
                    pending_images.append(image)
                continue
            cleaned = clean_text(line)
            if not cleaned:
                continue
            if pending_images and FIGURE_CAPTION_PATTERN.match(cleaned):
                for image in pending_images:
                    if not image["caption"]:
                        image["caption"] = cleaned
                pending_images = []
                continue
            if pending_images:
                for image in pending_images:
                    if not image["context"]:
                        image["context"] = cleaned
            current["lines"].append(cleaned)
        flush_current()
    return sections, images


def score_section(section: dict, rule: dict, language: str) -> int:
    heading = clean_heading_text(section["heading"])
    text = clean_text(section["text"])
    if not heading and not text:
        return -999
    score = 0
    target = f"{heading} {text}".casefold()
    for keyword in rule["section_keywords"]:
        if keyword.casefold() in heading.casefold():
            score += 18
        elif keyword.casefold() in target:
            score += 8
    for keyword in rule["content_keywords"]:
        if keyword.casefold() in target:
            score += 5
    if heading and not is_noise_text(heading, language):
        score += 6
    if len(text) >= 120:
        score += 5
    if looks_like_toc_entry(text):
        score -= 60
    if heading.casefold() in {"摘要", "abstract"} and rule["key"] not in {"background", "results", "innovation"}:
        score -= 20
    for keyword in rule.get("avoid_keywords", []):
        if keyword.casefold() in target:
            score -= 18
    return score


def select_sections(sections: list[dict], rule: dict, language: str) -> list[dict]:
    ranked = sorted(((score_section(section, rule, language), section) for section in sections), key=lambda item: item[0], reverse=True)
    chosen = []
    seen_heading = set()
    for score, section in ranked:
        if score < 6:
            continue
        heading_key = clean_heading_text(section["heading"]).casefold()
        if heading_key and heading_key in seen_heading and len(chosen) >= 1:
            continue
        chosen.append(section)
        if heading_key:
            seen_heading.add(heading_key)
        if len(chosen) >= rule.get("select_sections", 2):
            break
    return chosen


def collect_candidate_sentences(selected_sections: list[dict], rule: dict, language: str) -> list[str]:
    candidates = []
    for section in selected_sections:
        for line in section["text"].split("\n"):
            value = clean_text(line)
            if not value or is_noise_text(value, language):
                continue
            if len(value) > 110:
                for sentence in split_sentences(value, language):
                    if sentence and not is_noise_text(sentence, language):
                        candidates.append(sentence)
            else:
                candidates.append(value)
    return dedupe_keep_order(candidates)


def pick_bullets(selected_sections: list[dict], rule: dict, language: str) -> list[str]:
    candidates = collect_candidate_sentences(selected_sections, rule, language)
    ranked = sorted(((sentence_score(sentence, rule["content_keywords"], rule.get("prefer_metric", False)), sentence) for sentence in candidates), key=lambda item: item[0], reverse=True)
    output: list[str] = []
    for score, sentence in ranked:
        if score < 4:
            continue
        value = shorten(sentence, language, 54 if language == "zh" else 84)
        if value and value not in output:
            output.append(value)
        if len(output) >= 3:
            break
    if output:
        return output
    return [rule["default_takeaway"]]


def build_takeaway(bullets: list[str], rule: dict, language: str) -> str:
    if bullets:
        ranked = sorted(((sentence_score(bullet, rule["content_keywords"], rule.get("prefer_metric", False)), bullet) for bullet in bullets), key=lambda item: item[0], reverse=True)
        if ranked and ranked[0][0] >= 4:
            top = shorten(ranked[0][1], language, 44 if language == "zh" else 72)
            if rule["key"] in {"background", "problem"} and ("\\[" in top or "等人" in top):
                return rule["default_takeaway"]
            return top
    return rule["default_takeaway"]


def build_layout_budget(rule: dict, language: str, visual: dict) -> dict:
    return {
        "max_bullets": 3,
        "bullet_char_limit": 28 if language == "zh" else 72,
        "title_mode": "assertion",
        "visual_priority": "high" if visual.get("type") not in {"none", ""} else "medium",
        "top_theme_enabled": True,
    }


def score_image(image: dict, rule: dict) -> int:
    if not image.get("path") or not Path(image["path"]).exists():
        return -999
    text = " ".join([clean_text(image.get("caption", "")), clean_text(image.get("heading", "")), clean_text(image.get("context", ""))]).casefold()
    score = 0
    for keyword in rule["visual_keywords"]:
        if keyword.casefold() in text:
            score += 15
    for keyword in rule["content_keywords"]:
        if keyword.casefold() in text:
            score += 3
    if rule["visual_type"] == "chart" and METRIC_PATTERN.search(text):
        score += 12
    if ("界面" in text or "page" in text or "ui" in text) and rule["visual_type"] == "screenshot":
        score += 8
    if ("架构" in text or "architecture" in text) and rule["visual_type"] == "system_architecture":
        score += 8
    if ("流程" in text or "workflow" in text or "pipeline" in text) and rule["visual_type"] in {"workflow", "technical_roadmap"}:
        score += 8
    return score


def choose_visual(selected_sections: list[dict], all_images: list[dict], rule: dict, language: str) -> dict:
    if rule["visual_type"] == "none":
        return {"type": "none"}
    section_images = []
    selected_source_ids = {section["source_id"] for section in selected_sections}
    for section in selected_sections:
        section_images.extend(section["images"])
    pool = section_images + [image for image in all_images if image["source_id"] in selected_source_ids]
    ranked = sorted(((score_image(image, rule), image) for image in pool), key=lambda item: item[0], reverse=True)
    if ranked and ranked[0][0] >= 10:
        image = ranked[0][1]
        caption = clean_text(image.get("caption") or image.get("heading") or "")
        return {"type": rule["visual_type"], "path": image["path"], "caption": caption or section_copy(language, rule["key"])["desc"]}
    return {"type": rule["visual_type"], "note": "Reserve the right side for an editable figure or chart." if language == "en" else "右侧建议放置可编辑图示或图表，用于支撑本页结论。"}


def agenda_label(language: str, slide: dict) -> str:
    title = clean_text(slide.get("title", ""))
    return AGENDA_LABELS[language].get(slide["key"], title or slide["key"])


def infer_design_hint(slide_key: str, visual_type: str) -> str:
    if slide_key in {"background", "problem"}:
        return "statement_spread"
    if slide_key in {"technical_route", "student_work_1"}:
        return "method_process_band" if visual_type in {"workflow", "technical_roadmap"} else "method_architecture_split"
    if slide_key == "student_work_2":
        return "statement_sidebar"
    if slide_key in {"experiment", "results"}:
        return "results_metric_band"
    if slide_key == "innovation":
        return "innovation_triptych"
    if slide_key == "limitations":
        return "boundary_dual_column"
    return "statement_sidebar"


def build_content_slide(rule: dict, selected_sections: list[dict], all_images: list[dict], language: str) -> dict:
    bullets = pick_bullets(selected_sections, rule, language)
    takeaway = build_takeaway(bullets, rule, language)
    source_ids = sorted({section["source_id"] for section in selected_sections})
    source_paths = sorted({section["source_path"] for section in selected_sections})
    visual = choose_visual(selected_sections, all_images, rule, language)
    return {
        "key": rule["key"],
        "slide_type": "content",
        "title": rule["title"],
        "subtitle": "",
        "takeaway": takeaway,
        "bullets": bullets,
        "source_ids": source_ids,
        "source_paths": source_paths,
        "visual": visual,
        "layout_budget": build_layout_budget(rule, language, visual),
        "design_hint": infer_design_hint(rule["key"], visual["type"]),
        "speaker_note": (
            f"Explain how this slide supports the thesis argument. Sources: {', '.join(source_ids)}"
            if language == "en"
            else f"说明本页结论如何支撑整篇论文论证，并点明证据来自 {', '.join(source_ids)}。"
        ),
    }


def build_plan(brief_path: Path, manifest_path: Path) -> dict:
    brief = read_text(brief_path)
    manifest = json.loads(read_text(manifest_path))
    language = detect_language(brief)
    sources = parse_sources(brief, manifest)
    identity = extract_identity(sources, language)
    rules = SLIDE_RULES[language]
    sections, images = build_sections_and_images(sources, language)

    slides = []
    trace = []
    diagrams = []

    for slide_index, rule in enumerate(rules, start=1):
        slide_type = rule["slide_type"]
        key = rule["key"]
        if slide_type == "cover":
            subtitle = " | ".join(filter(None, [identity["author"], identity["advisor"], identity["institution"], identity["date"]]))
            subtitle = subtitle or ("毕业论文答辩" if language == "zh" else "Academic Defense")
            slide = {"key": key, "slide_type": "cover", "title": identity["title"], "subtitle": subtitle, "takeaway": "", "bullets": [], "source_ids": [], "source_paths": [], "visual": {"type": "none"}, "design_hint": "cover_focus", "speaker_note": "Introduce the thesis topic and the reporting path." if language == "en" else "开场先说明研究主题、答辩身份和汇报结构。"}
        elif slide_type == "toc":
            slide = {"key": key, "slide_type": "toc", "title": rule["title"], "subtitle": "", "takeaway": "", "agenda_items": [], "bullets": [], "source_ids": [], "source_paths": [], "visual": {"type": "none"}, "design_hint": "agenda_clean", "speaker_note": "Preview the talk order." if language == "en" else "概览汇报顺序，提醒评委后续会分别说明方法、结果与创新点。"}
        elif slide_type == "closing":
            slide = {"key": key, "slide_type": "closing", "title": rule["title"], "subtitle": identity["institution"], "takeaway": "", "bullets": [], "source_ids": [], "source_paths": [], "visual": {"type": "none"}, "design_hint": "closing_focus", "speaker_note": "Close the talk and transition into questions." if language == "en" else "结束时回到论文主题，并自然进入问答。"}
        else:
            selected_sections = select_sections(sections, rule, language)
            slide = build_content_slide(rule, selected_sections, images, language)
            if slide["visual"]["type"] in {"system_architecture", "technical_roadmap", "workflow"} and not slide["visual"].get("path"):
                diagrams.append(
                    {
                        "slide_index": slide_index,
                        "slide_key": key,
                        "slide_title": slide["title"],
                        "figure_type": slide["visual"]["type"],
                        "output_name": f"slide_{slide_index:02d}_{key}.drawio",
                        "source_ids": slide["source_ids"],
                        "source_paths": slide["source_paths"],
                        "instruction": f"Create a {slide['visual']['type']} figure for '{slide['title']}'." if language == "en" else f"围绕“{slide['title']}”绘制 {slide['visual']['type']} 图，并与该页结论一致。",
                    }
                )
        slides.append(slide)
        trace.append({"slide_index": slide_index, "slide_key": key, "slide_title": slide["title"], "source_ids": slide["source_ids"], "source_paths": slide["source_paths"]})

    agenda_items = [agenda_label(language, slide) for slide in slides if slide["slide_type"] == "content"]
    for slide in slides:
        if slide["slide_type"] == "toc":
            slide["agenda_items"] = agenda_items

    return {"generated_at": iso_now(), "deck_identity": identity, "slide_count": len(slides), "slides": slides, "source_trace": trace, "diagram_tasks": diagrams}


def render_plan_md(plan: dict) -> str:
    lines = ["# Deck Plan", "", "## Deck Identity", "", f"- Title: {plan['deck_identity']['title']}", f"- Language: {plan['deck_identity']['language']}", f"- Audience: {plan['deck_identity']['audience']}", f"- Defense type: {plan['deck_identity']['defense_type']}", f"- Visual direction: {plan['deck_identity']['visual_direction']}", "", "## Slides", ""]
    for idx, slide in enumerate(plan["slides"], start=1):
        lines.append(f"### {idx}. {slide['title']}")
        lines.append(f"- Slide key: `{slide['key']}`")
        lines.append(f"- Slide type: `{slide['slide_type']}`")
        if slide.get("takeaway"):
            lines.append(f"- Main takeaway: {slide['takeaway']}")
        if slide.get("agenda_items"):
            lines.append(f"- Agenda items: {', '.join(slide['agenda_items'])}")
        lines.append(f"- Visual: `{slide['visual']['type']}`")
        if slide["visual"].get("path"):
            lines.append(f"- Visual path: `{slide['visual']['path']}`")
        if slide.get("layout_budget"):
            lines.append(f"- Layout budget: max_bullets={slide['layout_budget'].get('max_bullets')}, visual_priority={slide['layout_budget'].get('visual_priority')}, title_mode={slide['layout_budget'].get('title_mode')}")
        if slide.get("design_hint"):
            lines.append(f"- Design hint: `{slide['design_hint']}`")
        if slide["source_ids"]:
            lines.append(f"- Source IDs: {', '.join(slide['source_ids'])}")
        if slide["bullets"]:
            lines.append("- Bullets:")
            for bullet in slide["bullets"]:
                lines.append(f"  - {bullet}")
        lines.append("")
    lines.extend(["## Diagram Tasks", ""])
    if not plan["diagram_tasks"]:
        lines.append("- None")
    else:
        for task in plan["diagram_tasks"]:
            lines.append(f"- Slide {task['slide_index']:02d} `{task['slide_key']}` -> {task['figure_type']} -> {task['output_name']}")
            lines.append(f"  - {task['instruction']}")
    lines.append("")
    return "\n".join(lines)


def render_diagram_md(tasks: list[dict]) -> str:
    lines = ["# Diagram Tasks", ""]
    if not tasks:
        lines.append("- No diagram tasks detected.")
        lines.append("")
        return "\n".join(lines)
    for task in tasks:
        lines.append(f"## Slide {task['slide_index']:02d} - {task['slide_title']}")
        lines.append(f"- Figure type: `{task['figure_type']}`")
        lines.append(f"- Output name: `{task['output_name']}`")
        lines.append(f"- Instruction: {task['instruction']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief_path", help="Path to normalized_brief.md")
    parser.add_argument("--manifest", help="Path to source_manifest.json")
    parser.add_argument("--output-dir", required=True, help="Directory for planning outputs")
    args = parser.parse_args()

    brief_path = Path(args.brief_path).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else brief_path.with_name("source_manifest.json")
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    plan = build_plan(brief_path, manifest_path)
    (output_dir / "deck_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "deck_plan.md").write_text(render_plan_md(plan), encoding="utf-8")
    (output_dir / "source_trace.json").write_text(json.dumps(plan["source_trace"], ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "diagram_tasks.json").write_text(json.dumps(plan["diagram_tasks"], ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "diagram_tasks.md").write_text(render_diagram_md(plan["diagram_tasks"]), encoding="utf-8")
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
