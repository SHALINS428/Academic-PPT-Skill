#!/usr/bin/env python3
"""Run the academic-ppt pipeline from local files to deck workspace."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from python_runtime import (
    NODE_ENV_VAR_NAME,
    build_skill_environment,
    get_path_value,
    resolve_python_executable,
)


SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_NODE_MODULES = SCRIPT_DIR.parent / "node_modules"


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_command(command: list[str], cwd: Path | None = None) -> dict:
    env = build_skill_environment()
    if LOCAL_NODE_MODULES.exists():
        current_node_path = env.get("NODE_PATH", "")
        env["NODE_PATH"] = (
            str(LOCAL_NODE_MODULES)
            if not current_node_path
            else f"{LOCAL_NODE_MODULES}{os.pathsep}{current_node_path}"
        )
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
        "cwd": str(cwd) if cwd else None,
        "returncode": result.returncode,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "ok": result.returncode == 0,
    }


def choose_node() -> str | None:
    env = build_skill_environment()
    candidates: list[str] = []
    override = env.get(NODE_ENV_VAR_NAME, "").strip()
    if override:
        candidates.append(str(Path(override).expanduser()))
    for command_name in ("node", "node.exe"):
        discovered = shutil.which(command_name, path=get_path_value(env))
        if discovered and discovered not in candidates:
            candidates.append(discovered)

    for candidate in candidates:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
        except FileNotFoundError:
            continue
        if result.returncode == 0:
            return candidate
    return None


def materialize_diagrams(tasks_path: Path, figures_dir: Path) -> list[dict]:
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    figures_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for task in tasks:
        output_path = figures_dir / task["output_name"]
        result = run_command(
            [
                "powershell.exe",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(SCRIPT_DIR / "new-drawio-figure.ps1"),
                "-OutputPath",
                str(output_path),
                "-Title",
                task["slide_title"],
                "-PageName",
                f"Slide-{task['slide_index']:02d}",
            ]
        )
        results.append({"task": task, "result": result, "output_path": str(output_path)})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="Input file(s) or folder(s)")
    parser.add_argument("--output-dir", required=True, help="Pipeline output directory")
    parser.add_argument("--materialize-diagrams", action="store_true", help="Create starter drawio files from planned diagram tasks")
    parser.add_argument("--skip-build", action="store_true", help="Skip Node deck build")
    parser.add_argument("--skip-validate", action="store_true", help="Skip deck validation")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()
    intake_dir = output_dir / "intake"
    planning_dir = output_dir / "planning"
    deck_dir = output_dir / "deck"
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_python = resolve_python_executable()

    inputs = [str(Path(value).expanduser().resolve()) for value in args.inputs]
    summary = {"generated_at": iso_now(), "inputs": inputs, "output_dir": str(output_dir), "steps": {}}

    summary["steps"]["normalize"] = run_command(
        [skill_python, str(SCRIPT_DIR / "normalize_sources.py"), *inputs, "--output-dir", str(intake_dir)]
    )
    if not summary["steps"]["normalize"]["ok"]:
        (output_dir / "pipeline_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(output_dir / "pipeline_summary.json")
        return 1

    summary["steps"]["plan"] = run_command(
        [
            skill_python,
            str(SCRIPT_DIR / "plan_deck.py"),
            str(intake_dir / "normalized_brief.md"),
            "--manifest",
            str(intake_dir / "source_manifest.json"),
            "--output-dir",
            str(planning_dir),
        ]
    )
    if not summary["steps"]["plan"]["ok"]:
        (output_dir / "pipeline_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(output_dir / "pipeline_summary.json")
        return 1

    plan = json.loads((planning_dir / "deck_plan.json").read_text(encoding="utf-8"))
    summary["steps"]["scaffold"] = run_command(
        [
            skill_python,
            str(SCRIPT_DIR / "scaffold_deck_workspace.py"),
            str(deck_dir),
            "--title",
            plan["deck_identity"]["title"],
            "--plan-json",
            str(planning_dir / "deck_plan.json"),
        ]
    )
    if not summary["steps"]["scaffold"]["ok"]:
        (output_dir / "pipeline_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(output_dir / "pipeline_summary.json")
        return 1

    for name in ("normalized_brief.md", "source_manifest.json"):
        shutil.copy2(intake_dir / name, deck_dir / name)

    if args.materialize_diagrams and (planning_dir / "diagram_tasks.json").exists():
        summary["steps"]["materialize_diagrams"] = materialize_diagrams(
            planning_dir / "diagram_tasks.json", deck_dir / "figures"
        )

    deck_path = deck_dir / plan["deck_identity"]["output_pptx"]
    if args.skip_build:
        summary["steps"]["build"] = {"ok": True, "skipped": True}
    else:
        node = choose_node()
        summary["steps"]["build"] = (
            run_command([node, str(deck_dir / "build_deck.js")], cwd=deck_dir)
            if node
            else {"ok": False, "error": "Node.js executable not found."}
        )

    if args.skip_validate:
        summary["steps"]["validate"] = {"ok": True, "skipped": True}
    elif deck_path.exists():
        summary["steps"]["validate"] = run_command(
            [skill_python, str(SCRIPT_DIR / "validate_deck.py"), str(deck_path)]
        )
    else:
        summary["steps"]["validate"] = {"ok": False, "error": f"Deck file not found: {deck_path}"}

    summary_path = output_dir / "pipeline_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary_path)
    failed = False
    for result in summary["steps"].values():
        if isinstance(result, dict) and not result.get("ok", True):
            failed = True
        if isinstance(result, list) and any(not item["result"].get("ok", True) for item in result):
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
