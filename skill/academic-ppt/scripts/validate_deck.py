#!/usr/bin/env python3
"""Run rendering and quality checks for a generated deck."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from python_runtime import build_skill_environment, resolve_python_executable


SCRIPT_DIR = Path(__file__).resolve().parent
ASSET_SCRIPTS_DIR = SCRIPT_DIR.parent / "assets" / "scripts"


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_command(
    command: list[str],
    cwd: Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> dict:
    env = build_skill_environment()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "ok": result.returncode == 0,
    }


def resolve_scripts_dir(deck_path: Path, override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    local = deck_path.parent / "scripts"
    return local if local.exists() else ASSET_SCRIPTS_DIR


def find_command(name: str) -> str | None:
    env = build_skill_environment()
    return shutil.which(name, path=env.get("PATH") or env.get("Path"))


def summarize_prerequisites() -> dict:
    return {
        "soffice": find_command("soffice") or find_command("soffice.exe"),
        "pdftoppm": find_command("pdftoppm") or find_command("pdftoppm.exe"),
        "fc-list": find_command("fc-list") or find_command("fc-list.exe"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck_path", help="Path to the generated PPTX")
    parser.add_argument("--scripts-dir", help="Optional directory containing validation scripts")
    parser.add_argument("--rendered-dir", help="Directory for rendered slide images")
    args = parser.parse_args()

    deck_path = Path(args.deck_path).expanduser().resolve()
    scripts_dir = resolve_scripts_dir(deck_path, args.scripts_dir)
    rendered_dir = (
        Path(args.rendered_dir).expanduser().resolve()
        if args.rendered_dir
        else deck_path.parent / "rendered"
    )
    rendered_dir.mkdir(parents=True, exist_ok=True)
    temp_root = deck_path.parent / ".validation_tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    skill_python = resolve_python_executable()
    extra_env = {
        "TMP": str(temp_root),
        "TEMP": str(temp_root),
        "TMPDIR": str(temp_root),
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }

    summary = {
        "generated_at": iso_now(),
        "deck_path": str(deck_path),
        "scripts_dir": str(scripts_dir),
        "rendered_dir": str(rendered_dir),
        "temp_root": str(temp_root),
        "prerequisites": summarize_prerequisites(),
        "checks": {},
    }

    summary["checks"]["render"] = run_command(
        [
            skill_python,
            str(scripts_dir / "render_slides.py"),
            str(deck_path),
            "--output_dir",
            str(rendered_dir),
        ],
        extra_env=extra_env,
    )
    summary["checks"]["overflow"] = run_command(
        [skill_python, str(scripts_dir / "slides_test.py"), str(deck_path)],
        extra_env=extra_env,
    )
    summary["checks"]["font"] = run_command(
        [skill_python, str(scripts_dir / "detect_font.py"), str(deck_path), "--json"],
        extra_env=extra_env,
    )
    if summary["checks"]["font"]["stdout"]:
        try:
            summary["checks"]["font"]["parsed"] = json.loads(summary["checks"]["font"]["stdout"])
        except json.JSONDecodeError:
            summary["checks"]["font"]["parsed"] = None

    if summary["checks"]["render"]["ok"]:
        montage_output = rendered_dir / "montage.png"
        if montage_output.exists():
            montage_output.unlink()
        summary["checks"]["montage"] = run_command(
            [
                skill_python,
                str(scripts_dir / "create_montage.py"),
                "--input_dir",
                str(rendered_dir),
                "--output_file",
                str(montage_output),
                "--num_col",
                "4",
                "--cell_width",
                "320",
                "--cell_height",
                "180",
                "--label_mode",
                "number",
            ],
            extra_env=extra_env,
        )

    summary_path = deck_path.parent / "validation_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary_path)
    failures = [name for name, result in summary["checks"].items() if not result.get("ok", True)]
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
