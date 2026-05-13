#!/usr/bin/env python3
"""Check whether the academic-ppt plugin can run on this machine."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from python_runtime import (
    ENV_VAR_NAME,
    NODE_ENV_VAR_NAME,
    build_skill_environment,
    get_path_value,
    resolve_python_executable,
)
from runtime_bootstrap import node_missing_modules, python_missing_modules
from tools_bootstrap import bootstrap_tools


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
MIN_PYTHON = (3, 11)
MIN_NODE_MAJOR = 18


def run_command(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def parse_version_numbers(raw: str) -> list[int]:
    cleaned = raw.strip().lstrip("vV")
    numbers: list[int] = []
    for part in cleaned.split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        if not digits:
            break
        numbers.append(int(digits))
    return numbers


def status_from_bool(ok: bool) -> str:
    return "ok" if ok else "missing"


def resolve_command(
    env: dict[str, str],
    command_names: tuple[str, ...],
    env_vars: tuple[str, ...] = (),
) -> dict[str, str | bool | None]:
    for env_var in env_vars:
        configured = env.get(env_var, "").strip()
        if not configured:
            continue
        candidate = str(Path(configured).expanduser())
        if Path(candidate).exists():
            return {
                "found": True,
                "path": candidate,
                "source": f"env:{env_var}",
                "configured_env_var": env_var,
            }
        return {
            "found": False,
            "path": candidate,
            "source": f"env:{env_var}",
            "configured_env_var": env_var,
        }

    search_path = get_path_value(env)
    for command_name in command_names:
        resolved = shutil.which(command_name, path=search_path)
        if resolved:
            return {
                "found": True,
                "path": resolved,
                "source": "PATH",
                "configured_env_var": None,
            }

    return {
        "found": False,
        "path": None,
        "source": "missing",
        "configured_env_var": None,
    }


def check_python(env: dict[str, str]) -> dict:
    python_path = resolve_python_executable()
    version_result = run_command(
        [
            python_path,
            "-c",
            (
                "import json, sys; "
                "print(json.dumps({'version': sys.version.split()[0], "
                "'version_info': list(sys.version_info[:3])}))"
            ),
        ],
        env=env,
    )
    data = {"found": version_result.returncode == 0, "path": python_path}
    if version_result.returncode != 0:
        data.update(
            {
                "status": "missing",
                "version": None,
                "version_ok": False,
                "details": version_result.stderr.strip() or version_result.stdout.strip(),
                "modules": {},
                "modules_ok": False,
                "missing_modules": [],
            }
        )
        return data

    parsed = json.loads(version_result.stdout)
    version_info = parsed["version_info"]
    missing = set(python_missing_modules())
    module_names = (
        "mammoth",
        "markdownify",
        "beautifulsoup4",
        "ebooklib",
        "nbformat",
        "nbconvert",
        "requests",
        "fonttools",
        "numpy",
        "pdf2image",
        "Pillow",
        "PyMuPDF",
        "python-pptx",
    )
    data["version"] = parsed["version"]
    data["version_ok"] = tuple(version_info) >= MIN_PYTHON
    data["status"] = status_from_bool(data["version_ok"])
    data["source"] = f"env:{ENV_VAR_NAME}" if os.environ.get(ENV_VAR_NAME, "").strip() else "auto"
    data["modules"] = {name: name not in missing for name in module_names}
    data["modules_ok"] = all(data["modules"].values())
    data["missing_modules"] = sorted(missing)
    return data


def check_node(env: dict[str, str]) -> dict:
    node_info = resolve_command(env, ("node", "node.exe"), (NODE_ENV_VAR_NAME,))
    data = dict(node_info)
    if not node_info["found"]:
        data.update({"status": "missing", "version": None, "version_ok": False, "modules_ok": False, "missing_modules": []})
        return data

    version_result = run_command([str(node_info["path"]), "--version"], env=env)
    version = (version_result.stdout or version_result.stderr).strip()
    version_numbers = parse_version_numbers(version)
    version_ok = bool(version_numbers) and version_numbers[0] >= MIN_NODE_MAJOR
    missing_modules = node_missing_modules()
    data["version"] = version
    data["version_ok"] = version_ok
    data["status"] = status_from_bool(version_ok)
    data["modules_ok"] = not missing_modules
    data["missing_modules"] = missing_modules
    data["node_modules_dir"] = str(SKILL_DIR / "node_modules")
    npm_info = resolve_command(env, ("npm", "npm.cmd"), ())
    data["npm"] = npm_info
    return data


def check_tool(
    env: dict[str, str],
    name: str,
    command_names: tuple[str, ...],
    env_vars: tuple[str, ...],
    *,
    required_for_minimal: bool,
    required_for_full_validation: bool,
    note: str,
) -> dict:
    info = resolve_command(env, command_names, env_vars)
    return {
        "name": name,
        "found": info["found"],
        "path": info["path"],
        "source": info["source"],
        "configured_env_var": info["configured_env_var"],
        "required_for_minimal": required_for_minimal,
        "required_for_full_validation": required_for_full_validation,
        "note": note,
        "status": status_from_bool(bool(info["found"])),
    }


def build_summary(require_full_validation: bool) -> dict:
    env = build_skill_environment()
    python_info = check_python(env)
    node_info = check_node(env)
    tools = {
        "soffice": check_tool(
            env,
            "LibreOffice / soffice",
            ("soffice", "soffice.exe", "soffice.com", "libreoffice"),
            ("SOFFICE_EXECUTABLE", "LIBREOFFICE_EXECUTABLE"),
            required_for_minimal=False,
            required_for_full_validation=True,
            note="Needed for legacy .doc conversion and slide rendering.",
        ),
        "pdftoppm": check_tool(
            env,
            "Poppler / pdftoppm",
            ("pdftoppm", "pdftoppm.exe"),
            ("PDFTOPPM_EXECUTABLE",),
            required_for_minimal=False,
            required_for_full_validation=True,
            note="Needed for slide preview rendering and image validation.",
        ),
        "fc-list": check_tool(
            env,
            "fontconfig / fc-list",
            ("fc-list", "fc-list.exe"),
            ("FC_LIST_EXECUTABLE",),
            required_for_minimal=False,
            required_for_full_validation=True,
            note="Needed for robust font substitution checks.",
        ),
    }

    minimal_run_ready = all(
        [
            python_info["found"],
            python_info["version_ok"],
            node_info["found"],
            node_info["version_ok"],
            bool(node_info.get("npm", {}).get("found")),
        ]
    )
    fontconfig_ready = bool(tools["fc-list"]["found"]) or bool(python_info["found"])
    full_validation_ready = minimal_run_ready and all(
        [
            tools["soffice"]["found"],
            tools["pdftoppm"]["found"],
            fontconfig_ready,
        ]
    )

    blockers: list[str] = []
    warnings: list[str] = []

    if not python_info["found"]:
        blockers.append("Python runtime not found.")
    elif not python_info["version_ok"]:
        blockers.append(
            f"Python {python_info['version']} is too old. Need >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}."
        )
    elif not python_info["modules_ok"]:
        warnings.append("Python dependencies are not installed yet. They will be bootstrapped automatically on first run.")

    if not node_info["found"]:
        blockers.append("Node.js runtime not found.")
    elif not node_info["version_ok"]:
        blockers.append(f"Node.js {node_info['version']} is too old. Need >= {MIN_NODE_MAJOR}.")
    elif not node_info.get("npm", {}).get("found"):
        blockers.append("npm not found. It is required for the plugin to bootstrap Node dependencies.")
    elif not node_info["modules_ok"]:
        warnings.append("Node dependencies are not installed yet. They will be bootstrapped automatically on first run.")

    for name in ("soffice", "pdftoppm"):
        if not tools[name]["found"]:
            warnings.append(f"{tools[name]['name']} is missing. It will be bootstrapped when full validation runs.")
    if not tools["fc-list"]["found"]:
        warnings.append("fontconfig / fc-list is missing. Font checks will use the bundled Python fontTools fallback.")

    if require_full_validation and not full_validation_ready:
        blockers.append("Full validation prerequisites are incomplete.")

    return {
        "python": python_info,
        "node": node_info,
        "tools": tools,
        "minimal_run_ready": minimal_run_ready,
        "full_validation_ready": full_validation_ready,
        "require_full_validation": require_full_validation,
        "blockers": blockers,
        "warnings": warnings,
    }


def print_human_summary(summary: dict) -> None:
    python_info = summary["python"]
    node_info = summary["node"]
    tools = summary["tools"]

    print("Academic PPT Doctor")
    print("===================")
    print(f"Minimal run ready: {'yes' if summary['minimal_run_ready'] else 'no'}")
    print(f"Full validation ready: {'yes' if summary['full_validation_ready'] else 'no'}")
    print("")

    print("Python")
    print(f"- Path: {python_info.get('path')}")
    print(f"- Source: {python_info.get('source')}")
    print(f"- Version: {python_info.get('version')}")
    print(f"- Dependencies installed: {'yes' if python_info.get('modules_ok') else 'no'}")

    print("Node.js")
    print(f"- Path: {node_info.get('path')}")
    print(f"- Source: {node_info.get('source')}")
    print(f"- Version: {node_info.get('version')}")
    print(f"- Dependencies installed: {'yes' if node_info.get('modules_ok') else 'no'}")
    npm_info = node_info.get("npm", {})
    print(f"- npm: {npm_info.get('path') if npm_info.get('found') else 'not found'}")

    print("Desktop tools")
    for key in ("soffice", "pdftoppm", "fc-list"):
        tool = tools[key]
        print(f"- {tool['name']}: {'found' if tool['found'] else 'missing'}")
        if tool["path"]:
            print(f"  Path: {tool['path']}")
        print(f"  Note: {tool['note']}")

    if summary["blockers"]:
        print("")
        print("Blockers")
        for item in summary["blockers"]:
            print(f"- {item}")

    if summary["warnings"]:
        print("")
        print("Warnings")
        for item in summary["warnings"]:
            print(f"- {item}")

    print("")
    print("Recommended next step")
    print(r"- python .\scripts\run_pipeline.py <materials> --output-dir ..\..\work\run")
    print("  The plugin will bootstrap missing Python and Node dependencies automatically.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument(
        "--require-full-validation",
        action="store_true",
        help="Return a non-zero exit code unless full validation tools are ready.",
    )
    parser.add_argument(
        "--bootstrap-tools",
        action="store_true",
        help="Download/extract desktop validation tools into the plugin runtime before checking.",
    )
    args = parser.parse_args()

    if args.bootstrap_tools or args.require_full_validation:
        bootstrap_tools(["libreoffice", "poppler", "fontconfig"], allow_fallback=True)

    summary = build_summary(require_full_validation=args.require_full_validation)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human_summary(summary)

    return 1 if summary["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
