#!/usr/bin/env python3
"""Install and activate local runtime dependencies for the academic-ppt plugin."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

from python_runtime import (
    NODE_ENV_VAR_NAME,
    NODE_MODULES_DIR,
    PYTHON_VENDOR_DIR,
    activate_local_python_runtime,
    build_skill_environment,
    get_path_value,
    resolve_python_executable,
)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PACKAGE_JSON = SKILL_DIR / "package.json"
PACKAGE_LOCK = SKILL_DIR / "package-lock.json"
REQUIREMENTS_TXT = SKILL_DIR / "requirements.txt"

PYTHON_MODULES = {
    "mammoth": "mammoth",
    "markdownify": "markdownify",
    "beautifulsoup4": "bs4",
    "ebooklib": "ebooklib",
    "nbformat": "nbformat",
    "nbconvert": "nbconvert",
    "requests": "requests",
    "fonttools": "fontTools",
    "numpy": "numpy",
    "pdf2image": "pdf2image",
    "Pillow": "PIL",
    "PyMuPDF": "fitz",
    "python-pptx": "pptx",
}

PYTHON_REQUIREMENT_NAMES = {
    "mammoth": "mammoth",
    "markdownify": "markdownify",
    "beautifulsoup4": "beautifulsoup4",
    "ebooklib": "ebooklib",
    "nbformat": "nbformat",
    "nbconvert": "nbconvert",
    "requests": "requests",
    "fonttools": "fonttools",
    "numpy": "numpy",
    "pdf2image": "pdf2image",
    "Pillow": "pillow",
    "PyMuPDF": "pymupdf",
    "python-pptx": "python-pptx",
}

NODE_MODULES = (
    "fontkit",
    "linebreak",
    "mathjax-full",
    "pptxgenjs",
    "prismjs",
    "skia-canvas",
)


def run_command(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=build_skill_environment(),
    )


def _python_modules_status() -> dict[str, bool]:
    activate_local_python_runtime()
    return {
        name: importlib.util.find_spec(module_name) is not None
        for name, module_name in PYTHON_MODULES.items()
    }


def _node_modules_status() -> dict[str, bool]:
    return {name: (NODE_MODULES_DIR / name).exists() for name in NODE_MODULES}


def python_missing_modules() -> list[str]:
    return [name for name, ok in _python_modules_status().items() if not ok]


def node_missing_modules() -> list[str]:
    return [name for name, ok in _node_modules_status().items() if not ok]


def requirement_specs_for(missing: list[str]) -> list[str]:
    wanted = {PYTHON_REQUIREMENT_NAMES[name].lower() for name in missing}
    specs: list[str] = []
    for raw_line in REQUIREMENTS_TXT.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        package_name = line.split("==", 1)[0].split(">=", 1)[0].split("<=", 1)[0].strip().lower()
        if package_name in wanted:
            specs.append(line)
    return specs


def ensure_python_runtime() -> dict:
    missing = python_missing_modules()
    if not missing:
        return {"ok": True, "installed": False, "missing": []}

    PYTHON_VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    requirement_specs = requirement_specs_for(missing)
    install_args = requirement_specs or ["-r", str(REQUIREMENTS_TXT)]
    command = [
        resolve_python_executable(),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--upgrade",
        "--target",
        str(PYTHON_VENDOR_DIR),
        *install_args,
    ]
    result = run_command(command, cwd=SKILL_DIR)
    missing_after = python_missing_modules()
    return {
        "ok": result.returncode == 0 and not missing_after,
        "installed": True,
        "missing": missing_after,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "command": command,
        "target": str(PYTHON_VENDOR_DIR),
    }


def ensure_node_runtime() -> dict:
    missing = node_missing_modules()
    if not missing:
        return {"ok": True, "installed": False, "missing": []}

    env = build_skill_environment()
    npm = (
        shutil.which("npm", path=get_path_value(env))
        or shutil.which("npm.cmd", path=get_path_value(env))
    )
    if not npm:
        return {
            "ok": False,
            "installed": False,
            "missing": missing,
            "stdout": "",
            "stderr": f"npm not found. Set {NODE_ENV_VAR_NAME} or install Node.js with npm.",
            "command": [],
        }

    command = [
        npm,
        "ci" if PACKAGE_LOCK.exists() else "install",
        "--no-fund",
        "--no-audit",
    ]
    result = run_command(command, cwd=SKILL_DIR)
    missing_after = node_missing_modules()
    return {
        "ok": result.returncode == 0 and not missing_after,
        "installed": True,
        "missing": missing_after,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
        "command": command,
    }


def bootstrap_runtime() -> dict:
    python_result = ensure_python_runtime()
    node_result = ensure_node_runtime()
    return {
        "python": python_result,
        "node": node_result,
        "ok": python_result["ok"] and node_result["ok"],
    }


def print_summary(summary: dict) -> None:
    print(json.dumps(summary, ensure_ascii=False, indent=2))
