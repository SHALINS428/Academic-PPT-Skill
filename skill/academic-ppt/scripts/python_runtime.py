#!/usr/bin/env python3
"""Resolve the Python runtime used by the academic-ppt skill."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


ENV_VAR_NAME = "ACADEMIC_PPT_PYTHON"
NODE_ENV_VAR_NAME = "ACADEMIC_PPT_NODE"
EXECUTABLE_ENV_VARS = (
    ENV_VAR_NAME,
    NODE_ENV_VAR_NAME,
    "SOFFICE_EXECUTABLE",
    "LIBREOFFICE_EXECUTABLE",
    "PDFTOPPM_EXECUTABLE",
    "FC_LIST_EXECUTABLE",
    "DRAWIO_EXECUTABLE",
    "DIAGRAMS_NET_EXECUTABLE",
)
FONTCONFIG_PATH_ENV = "FONTCONFIG_PATH"
FONTCONFIG_FILE_ENV = "FONTCONFIG_FILE"


def _normalized_path(value: str | None) -> str | None:
    if not value:
        return None
    return str(Path(value).expanduser())


def resolve_python_executable() -> str:
    override = _normalized_path(os.environ.get(ENV_VAR_NAME, "").strip())
    if override:
        return override
    if sys.executable:
        return sys.executable
    discovered = shutil.which("python") or shutil.which("python.exe")
    return discovered or "python"


def _path_key(env: dict[str, str]) -> str:
    if "PATH" in env:
        return "PATH"
    if "Path" in env:
        return "Path"
    return "PATH"


def get_path_value(env: dict[str, str]) -> str:
    return env.get(_path_key(env), "")


def _prepend_path_entries(env: dict[str, str], entries: list[str]) -> None:
    path_key = _path_key(env)
    current_paths = [part for part in get_path_value(env).split(os.pathsep) if part]
    prepend_paths = [part for part in entries if part]
    env[path_key] = os.pathsep.join(
        prepend_paths + [part for part in current_paths if part not in prepend_paths]
    )
    alt_key = "Path" if path_key == "PATH" else "PATH"
    env[alt_key] = env[path_key]


def _candidate_executable_dirs(resolved_python: str, env: dict[str, str]) -> list[str]:
    candidates: list[str] = []
    python_path = Path(resolved_python)
    if python_path.parent.exists():
        candidates.append(str(python_path.parent))
        scripts_dir = python_path.parent / "Scripts"
        if scripts_dir.exists():
            candidates.append(str(scripts_dir))

    for env_var in EXECUTABLE_ENV_VARS:
        configured = _normalized_path(env.get(env_var, "").strip())
        if not configured:
            continue
        parent = Path(configured).parent
        if parent.exists():
            candidates.append(str(parent))

    return candidates


def _resolve_fontconfig_defaults(env: dict[str, str]) -> None:
    fontconfig_file = _normalized_path(env.get(FONTCONFIG_FILE_ENV, "").strip())
    fontconfig_path = _normalized_path(env.get(FONTCONFIG_PATH_ENV, "").strip())

    if fontconfig_file and not fontconfig_path:
        env[FONTCONFIG_PATH_ENV] = str(Path(fontconfig_file).parent)
        return

    if fontconfig_path and not fontconfig_file:
        candidate = Path(fontconfig_path) / "fonts.conf"
        if candidate.exists():
            env[FONTCONFIG_FILE_ENV] = str(candidate)
        return

    if fontconfig_file and fontconfig_path:
        return

    fc_list = shutil.which("fc-list", path=get_path_value(env)) or shutil.which(
        "fc-list.exe",
        path=get_path_value(env),
    )
    if not fc_list:
        return

    executable = Path(fc_list)
    config_candidates = [
        executable.parent.parent / "etc" / "fonts" / "fonts.conf",
        executable.parent.parent.parent / "etc" / "fonts" / "fonts.conf",
    ]
    for candidate in config_candidates:
        if candidate.exists():
            env[FONTCONFIG_FILE_ENV] = str(candidate)
            env[FONTCONFIG_PATH_ENV] = str(candidate.parent)
            return


def build_skill_environment(base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base_env or os.environ)
    resolved_python = resolve_python_executable()
    _prepend_path_entries(env, _candidate_executable_dirs(resolved_python, env))
    env[ENV_VAR_NAME] = resolved_python
    env["UV_PYTHON"] = resolved_python
    _resolve_fontconfig_defaults(env)
    return env


def runtime_note() -> str:
    resolved = resolve_python_executable()
    if os.environ.get(ENV_VAR_NAME, "").strip():
        return f"Python runtime set by {ENV_VAR_NAME}: {resolved}"
    return f"Python runtime auto-detected: {resolved}"
