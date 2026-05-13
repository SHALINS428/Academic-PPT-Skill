#!/usr/bin/env python3
"""Normalize local academic source files into a single Markdown brief."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from build_source_manifest import build_manifest
from python_runtime import build_skill_environment, get_path_value, resolve_python_executable


SCRIPT_DIR = Path(__file__).resolve().parent
VENDOR_DIR = SCRIPT_DIR / "vendor_source_to_md"

CONVERTER_BY_KIND = {
    "doc": VENDOR_DIR / "doc_to_md.py",
    "docx": VENDOR_DIR / "doc_to_md.py",
    "pdf": VENDOR_DIR / "pdf_to_md.py",
    "pptx": VENDOR_DIR / "ppt_to_md.py",
}


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def markdown_output_path(target_dir: Path, source_item: dict) -> Path:
    source_path = Path(source_item["path"])
    safe_name = source_path.stem.replace(" ", "_")
    return target_dir / f"{source_item['id']}_{safe_name}.md"


def run_converter(converter: Path, source_path: Path, output_path: Path) -> None:
    command = [
        resolve_python_executable(),
        str(converter),
        str(source_path),
        "-o",
        str(output_path),
    ]
    subprocess.run(command, check=True, env=build_skill_environment())


def convert_legacy_word(source_path: Path, bridge_dir: Path) -> Path:
    bridge_dir.mkdir(parents=True, exist_ok=True)
    env = build_skill_environment()
    soffice = shutil.which("soffice", path=get_path_value(env))
    if not soffice:
        raise FileNotFoundError(
            "LibreOffice `soffice` was not found. It is required to convert `.doc` to `.docx`."
        )
    command = [
        soffice,
        "--headless",
        "--convert-to",
        "docx",
        "--outdir",
        str(bridge_dir),
        str(source_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True, env=env)
    converted = bridge_dir / f"{source_path.stem}.docx"
    if not converted.exists():
        raise FileNotFoundError(f"LibreOffice did not produce the expected DOCX bridge file: {converted}")
    return converted


def normalize_markdown_or_text(source_path: Path, output_path: Path) -> None:
    text = source_path.read_text(encoding="utf-8", errors="ignore")
    if source_path.suffix.lower() == ".txt":
        text = f"# {source_path.stem}\n\n{text.strip()}\n"
    output_path.write_text(text, encoding="utf-8")


def build_combined_brief(manifest: dict, markdown_files: list[dict], image_files: list[dict]) -> str:
    lines = [
        "# Normalized Academic Brief",
        "",
        f"Generated at: {iso_now()}",
        "",
        "## Source Summary",
        "",
    ]
    for item in manifest["files"]:
        lines.append(
            f"- `{item['id']}` | {item['kind']} | {item['role']} | {item['path']}"
        )

    for item in markdown_files:
        source = item["source"]
        lines.extend(
            [
                "",
                f"## Source: {source['name']}",
                "",
                f"- Source ID: `{source['id']}`",
                f"- Source Path: `{source['path']}`",
                f"- Converted Path: `{item['path']}`",
                f"- Kind: `{source['kind']}`",
                f"- Role: `{source['role']}`",
                "",
                item["content"].rstrip(),
                "",
            ]
        )

    if image_files:
        lines.extend(["", "## Image Assets", ""])
        for item in image_files:
            lines.append(f"- `{item['id']}` | {item['path']} | role=`{item['role']}`")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="File(s) or folder(s) to normalize")
    parser.add_argument("--output-dir", required=True, help="Directory for normalized outputs")
    args = parser.parse_args()

    input_paths = [Path(value).expanduser().resolve() for value in args.inputs]
    output_dir = Path(args.output_dir).expanduser().resolve()
    converted_dir = output_dir / "converted"
    bridge_dir = output_dir / "doc_bridge"
    copied_dir = output_dir / "sources"
    output_dir.mkdir(parents=True, exist_ok=True)
    converted_dir.mkdir(parents=True, exist_ok=True)
    bridge_dir.mkdir(parents=True, exist_ok=True)
    copied_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(input_paths)
    (output_dir / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    markdown_files = []
    image_files = []

    for item in manifest["files"]:
        source_path = Path(item["path"])
        shutil.copy2(source_path, copied_dir / f"{item['id']}_{source_path.name}")
        kind = item["kind"]

        if kind == "image":
            image_files.append(item)
            continue

        output_path = markdown_output_path(converted_dir, item)
        converter_input = source_path

        if kind == "doc":
            converter_input = convert_legacy_word(
                source_path, bridge_dir / f"{item['id']}_{source_path.stem}"
            )

        if kind in CONVERTER_BY_KIND:
            run_converter(CONVERTER_BY_KIND[kind], converter_input, output_path)
        elif kind in {"markdown", "text"}:
            normalize_markdown_or_text(source_path, output_path)
        else:
            continue

        markdown_files.append(
            {
                "source": item,
                "path": str(output_path),
                "content": output_path.read_text(encoding="utf-8", errors="ignore"),
            }
        )

    brief = build_combined_brief(manifest, markdown_files, image_files)
    brief_path = output_dir / "normalized_brief.md"
    brief_path.write_text(brief, encoding="utf-8")
    print(brief_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
