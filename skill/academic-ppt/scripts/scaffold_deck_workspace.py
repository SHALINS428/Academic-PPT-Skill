#!/usr/bin/env python3
"""Create a task-local academic deck workspace with bundled helpers and templates."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from python_runtime import NODE_MODULES_DIR


SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_DIR / "assets"

DECK_PLAN_TEMPLATE = """# Deck Plan

## Deck Identity

- Title:
- Audience:
- Visual direction:
- Output file: `academic-defense.pptx`

## Page Order

1. Cover
   Main takeaway:
2. Agenda
   Main takeaway:
3. Research background
   Main takeaway:
4. Problem definition or objective
   Main takeaway:
5. Technical route or overall framework
   Main takeaway:
6. Student work part 1
   Main takeaway:
7. Student work part 2
   Main takeaway:
8. Experimental setup or evaluation
   Main takeaway:
9. Core results
   Main takeaway:
10. Innovation summary
    Main takeaway:
11. Limitations and future work
    Main takeaway:
12. Thanks
    Main takeaway:
"""


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_plan_artifacts(plan_json: Path, output_dir: Path) -> None:
    shutil.copy2(plan_json, output_dir / "deck_plan.json")
    for name in ("deck_plan.md", "source_trace.json"):
        sibling = plan_json.with_name(name)
        if sibling.exists():
            shutil.copy2(sibling, output_dir / name)


def render_build_template() -> str:
    template_path = ASSETS_DIR / "build_deck_template.js"
    template = template_path.read_text(encoding="utf-8")
    return template.replace(
        "__SKILL_NODE_MODULES__",
        json.dumps(str(NODE_MODULES_DIR.resolve())),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", help="Task-local deck workspace directory")
    parser.add_argument("--title", default="Academic Defense", help="Initial deck title")
    parser.add_argument("--plan-json", help="Optional deck_plan.json to seed the workspace")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for relative in ("rendered", "assets", "tmp", "notes"):
        (output_dir / relative).mkdir(parents=True, exist_ok=True)

    copy_tree(ASSETS_DIR / "pptxgenjs_helpers", output_dir / "pptxgenjs_helpers")
    copy_tree(ASSETS_DIR / "scripts", output_dir / "scripts")
    copy_tree(ASSETS_DIR / "reference-layouts", output_dir / "assets" / "reference-layouts")
    copy_tree(ASSETS_DIR / "reference-charts", output_dir / "assets" / "reference-charts")

    build_js = output_dir / "build_deck.js"
    if not build_js.exists():
        build_js.write_text(render_build_template(), encoding="utf-8")

    deck_plan = output_dir / "deck_plan.md"
    if not deck_plan.exists():
        deck_plan.write_text(DECK_PLAN_TEMPLATE, encoding="utf-8")

    if args.plan_json:
        copy_plan_artifacts(Path(args.plan_json).expanduser().resolve(), output_dir)

    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
