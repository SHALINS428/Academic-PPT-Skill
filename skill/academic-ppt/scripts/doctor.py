#!/usr/bin/env python3
"""Check whether the academic-ppt skill can run on this machine."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from python_runtime import (
    ENV_VAR_NAME,
    NODE_ENV_VAR_NAME,
    build_skill_environment,
    get_path_value,
    resolve_python_executable,
)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
MIN_PYTHON = (3, 11)
MIN_NODE_MAJOR = 18
PYTHON_MODULES = {
    "mammoth": "mammoth",
    "numpy": "numpy",
    "pdf2image": "pdf2image",
    "Pillow": "PIL",
    "PyMuPDF": "fitz",
    "python-pptx": "pptx",
}
NODE_MODULES = (
    "fontkit",
    "linebreak",
    "mathjax-full",
    "pptxgenjs",
    "prismjs",
    "skia-canvas",
)


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def parse_version_numbers(raw: str) -> list[int]:
    cleaned = raw.strip().lstrip("vV")
    parts = cleaned.split(".")
    numbers: list[int] = []
    for part in parts:
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
            }
        )
        return data

    parsed = json.loads(version_result.stdout)
    version_info = parsed["version_info"]
    data["version"] = parsed["version"]
    data["version_ok"] = tuple(version_info) >= MIN_PYTHON
    data["status"] = status_from_bool(data["version_ok"])
    data["source"] = (
        f"env:{ENV_VAR_NAME}" if os.environ.get(ENV_VAR_NAME, "").strip() else "auto"
    )

    modules_script = (
        "import importlib.util, json;"
        f"modules={json.dumps(PYTHON_MODULES, ensure_ascii=False)};"
        "results={name: bool(importlib.util.find_spec(mod)) for name, mod in modules.items()};"
        "print(json.dumps(results, ensure_ascii=False))"
    )
    modules_result = run_command([python_path, "-c", modules_script], env=env)
    if modules_result.returncode == 0:
        modules = json.loads(modules_result.stdout)
    else:
        modules = {name: False for name in PYTHON_MODULES}
    data["modules"] = modules
    data["modules_ok"] = all(modules.values())
    return data


def check_node(env: dict[str, str]) -> dict:
    node_info = resolve_command(env, ("node", "node.exe"), (NODE_ENV_VAR_NAME,))
    data = dict(node_info)
    if not node_info["found"]:
        data.update({"status": "missing", "version": None, "version_ok": False})
        data["modules_ok"] = False
        return data

    version_result = run_command([str(node_info["path"]), "--version"], env=env)
    version = (version_result.stdout or version_result.stderr).strip()
    version_numbers = parse_version_numbers(version)
    version_ok = bool(version_numbers) and version_numbers[0] >= MIN_NODE_MAJOR
    data["version"] = version
    data["version_ok"] = version_ok
    data["status"] = status_from_bool(version_ok)

    node_modules_dir = SKILL_DIR / "node_modules"
    missing_modules = [
        module_name for module_name in NODE_MODULES if not (node_modules_dir / module_name).exists()
    ]
    data["modules_ok"] = not missing_modules
    data["missing_modules"] = missing_modules
    data["node_modules_dir"] = str(node_modules_dir)
    data["node_modules_present"] = node_modules_dir.exists()
    if missing_modules:
        data["modules_error"] = f"Missing packages: {', '.join(missing_modules)}"

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
            note="Needed for legacy .doc conversion and deck rendering.",
        ),
        "pdftoppm": check_tool(
            env,
            "Poppler / pdftoppm",
            ("pdftoppm", "pdftoppm.exe"),
            ("PDFTOPPM_EXECUTABLE",),
            required_for_minimal=False,
            required_for_full_validation=True,
            note="Needed for slide preview rendering and validation images.",
        ),
        "fc-list": check_tool(
            env,
            "fontconfig / fc-list",
            ("fc-list", "fc-list.exe"),
            ("FC_LIST_EXECUTABLE",),
            required_for_minimal=False,
            required_for_full_validation=True,
            note="Needed for robust font missing and substitution checks.",
        ),
        "drawio": check_tool(
            env,
            "draw.io / diagrams.net",
            ("draw.io", "drawio", "diagrams.net", "draw.io.exe", "diagrams.net.exe"),
            ("DRAWIO_EXECUTABLE", "DIAGRAMS_NET_EXECUTABLE"),
            required_for_minimal=False,
            required_for_full_validation=False,
            note="Optional. Needed only when exporting .drawio sources to PNG.",
        ),
    }

    minimal_ready = all(
        [
            python_info["found"],
            python_info["version_ok"],
            python_info["modules_ok"],
            node_info["found"],
            node_info["version_ok"],
            node_info["modules_ok"],
        ]
    )
    full_validation_ready = minimal_ready and all(
        tools[name]["found"] for name in ("soffice", "pdftoppm", "fc-list")
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
        blockers.append("Python dependencies are incomplete. Run `python -m pip install -r requirements.txt`.")

    if not node_info["found"]:
        blockers.append("Node.js runtime not found.")
    elif not node_info["version_ok"]:
        blockers.append(f"Node.js {node_info['version']} is too old. Need >= {MIN_NODE_MAJOR}.")
    elif not node_info["modules_ok"]:
        blockers.append("Node dependencies are incomplete. Run `npm install` in `skill/academic-ppt`.")

    for name in ("soffice", "pdftoppm", "fc-list"):
        if not tools[name]["found"]:
            warnings.append(
                f"{tools[name]['name']} is missing. Full validation is not ready."
            )
    if not tools["drawio"]["found"]:
        warnings.append("draw.io / diagrams.net is missing. Diagram PNG export will be unavailable.")

    if require_full_validation and not full_validation_ready:
        blockers.append("Full validation prerequisites are incomplete.")

    return {
        "python": python_info,
        "node": node_info,
        "tools": tools,
        "minimal_run_ready": minimal_ready,
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
    print(f"最小运行环境: {'就绪' if summary['minimal_run_ready'] else '未就绪'}")
    print(f"完整验证环境: {'就绪' if summary['full_validation_ready'] else '未就绪'}")
    print("")

    print("Python")
    print(f"- 路径: {python_info.get('path')}")
    print(f"- 来源: {python_info.get('source')}")
    print(f"- 版本: {python_info.get('version')}")
    print(
        f"- 依赖: {'完整' if python_info.get('modules_ok') else '缺失'}"
    )

    print("Node.js")
    print(f"- 路径: {node_info.get('path')}")
    print(f"- 来源: {node_info.get('source')}")
    print(f"- 版本: {node_info.get('version')}")
    print(
        f"- 依赖: {'完整' if node_info.get('modules_ok') else '缺失'}"
    )
    npm_info = node_info.get("npm", {})
    print(
        f"- npm: {npm_info.get('path') if npm_info.get('found') else '未找到'}"
    )

    print("桌面工具")
    for key in ("soffice", "pdftoppm", "fc-list", "drawio"):
        tool = tools[key]
        readiness = "已找到" if tool["found"] else "未找到"
        print(f"- {tool['name']}: {readiness}")
        if tool["path"]:
            print(f"  路径: {tool['path']}")
        print(f"  说明: {tool['note']}")

    if summary["blockers"]:
        print("")
        print("阻塞项")
        for item in summary["blockers"]:
            print(f"- {item}")

    if summary["warnings"]:
        print("")
        print("提示")
        for item in summary["warnings"]:
            print(f"- {item}")

    print("")
    print("建议命令")
    if not python_info.get("modules_ok"):
        print("- python -m pip install -r requirements.txt")
    if not node_info.get("modules_ok"):
        print("- npm install")
    if not summary["minimal_run_ready"]:
        print("- 先修复上面的阻塞项，再运行 `python .\\scripts\\run_pipeline.py <materials> --output-dir ..\\..\\work\\run --skip-validate`")
    elif not summary["full_validation_ready"]:
        print("- 补齐 LibreOffice / Poppler / fontconfig 后，再运行 `python .\\scripts\\run_pipeline.py <materials> --output-dir ..\\..\\work\\run`")
    else:
        print("- 现在可以直接运行完整 pipeline。")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument(
        "--require-full-validation",
        action="store_true",
        help="Return a non-zero exit code unless full validation tools are ready.",
    )
    args = parser.parse_args()

    summary = build_summary(require_full_validation=args.require_full_validation)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human_summary(summary)

    if summary["blockers"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
