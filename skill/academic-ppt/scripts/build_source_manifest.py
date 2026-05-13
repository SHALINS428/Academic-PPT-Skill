#!/usr/bin/env python3
"""Scan local academic materials and write a normalized source manifest."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_KINDS = {
    ".doc": "doc",
    ".docx": "docx",
    ".pdf": "pdf",
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".pptx": "pptx",
    ".pptm": "pptx",
    ".ppsx": "pptx",
    ".ppsm": "pptx",
    ".potx": "pptx",
    ".potm": "pptx",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".svg": "image",
}

ROLE_HINTS = {
    "thesis_manuscript": ["thesis", "dissertation", "paper", "manuscript", "final"],
    "proposal_or_report": ["proposal", "report", "interim", "progress", "milestone"],
    "defense_deck": ["defense", "presentation", "slides", "deck"],
    "figure_asset": ["figure", "fig", "image", "diagram", "flow", "architecture"],
    "notes": ["note", "summary", "readme", "outline", "memo"],
}


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def infer_role(path: Path, kind: str) -> str:
    name = path.name.lower()
    for role, hints in ROLE_HINTS.items():
        if any(hint in name for hint in hints):
            return role
    if kind in {"doc", "docx", "pdf"}:
        return "source_document"
    if kind == "markdown":
        return "notes"
    if kind == "pptx":
        return "reference_deck"
    if kind == "image":
        return "figure_asset"
    if kind == "text":
        return "notes"
    return "supporting_material"


def iter_supported_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in SUPPORTED_KINDS else []
    files = []
    for item in sorted(path.rglob("*")):
        if item.is_file() and item.suffix.lower() in SUPPORTED_KINDS:
            files.append(item)
    return files


def collect_files(inputs: list[Path]) -> list[Path]:
    collected: list[Path] = []
    seen: set[Path] = set()
    for input_path in inputs:
        for file_path in iter_supported_files(input_path):
            resolved = file_path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                collected.append(resolved)
    collected.sort()
    return collected


def build_manifest(inputs: list[Path]) -> dict:
    files = collect_files(inputs)
    items = []
    for index, file_path in enumerate(files, start=1):
        stat = file_path.stat()
        suffix = file_path.suffix.lower()
        kind = SUPPORTED_KINDS[suffix]
        items.append(
            {
                "id": f"src-{index:03d}",
                "path": str(file_path),
                "name": file_path.name,
                "suffix": suffix,
                "kind": kind,
                "role": infer_role(file_path, kind),
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
            }
        )
    return {
        "generated_at": iso_now(),
        "input_roots": [str(path.resolve()) for path in inputs],
        "file_count": len(items),
        "files": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="File(s) or folder(s) to scan")
    parser.add_argument("--output", required=True, help="Output JSON manifest path")
    args = parser.parse_args()

    inputs = [Path(value).expanduser().resolve() for value in args.inputs]
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(inputs)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
