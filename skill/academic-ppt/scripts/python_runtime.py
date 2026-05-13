#!/usr/bin/env python3
"""Resolve the Python runtime used by the academic-ppt skill."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ENV_VAR_NAME = "ACADEMIC_PPT_PYTHON"
DEFAULT_TWIBOT_PYTHON = Path(
    r"D:\shalins\study\minconda\conda_envs\twibot\python.exe"
)
LIBREOFFICE_PROGRAM_DIR = Path(r"D:\shalins\useful\skill-tools\Liber-office\program")
POPPLER_BIN_DIR = Path(
    r"D:\shalins\useful\skill-tools\Poppler\Release-25.12.0-0\poppler-25.12.0\Library\bin"
)
FONTCONFIG_BIN_DIR = Path(r"D:\shalins\useful\msys64\ucrt64\bin")
FONTCONFIG_PATH_DIR = Path(r"D:\shalins\useful\msys64\ucrt64\etc\fonts")
FONTCONFIG_FILE_PATH = FONTCONFIG_PATH_DIR / "fonts.conf"


def resolve_python_executable() -> str:
    override = os.environ.get(ENV_VAR_NAME, "").strip()
    if override:
        return str(Path(override).expanduser())
    if DEFAULT_TWIBOT_PYTHON.exists():
        return str(DEFAULT_TWIBOT_PYTHON)
    return sys.executable


def _path_key(env: dict[str, str]) -> str:
    if "PATH" in env:
        return "PATH"
    if "Path" in env:
        return "Path"
    return "PATH"


def build_skill_environment(base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base_env or os.environ)
    path_key = _path_key(env)
    current_paths = [part for part in env.get(path_key, "").split(os.pathsep) if part]
    prepend_paths = [
        str(DEFAULT_TWIBOT_PYTHON.parent),
        str(DEFAULT_TWIBOT_PYTHON.parent / "Scripts"),
        str(LIBREOFFICE_PROGRAM_DIR),
        str(POPPLER_BIN_DIR),
        str(FONTCONFIG_BIN_DIR),
    ]
    env[path_key] = os.pathsep.join(
        prepend_paths + [part for part in current_paths if part not in prepend_paths]
    )
    env["CONDA_DEFAULT_ENV"] = "twibot"
    env["CONDA_PREFIX"] = str(DEFAULT_TWIBOT_PYTHON.parent)
    env[ENV_VAR_NAME] = resolve_python_executable()
    env["UV_PYTHON"] = resolve_python_executable()
    env["FONTCONFIG_PATH"] = str(FONTCONFIG_PATH_DIR)
    env["FONTCONFIG_FILE"] = str(FONTCONFIG_FILE_PATH)
    return env


def runtime_note() -> str:
    resolved = resolve_python_executable()
    if resolved == sys.executable:
        return (
            f"Python runtime fallback in use: {resolved}. "
            f"Set {ENV_VAR_NAME} or create {DEFAULT_TWIBOT_PYTHON} to pin the skill runtime."
        )
    return f"Python runtime pinned to: {resolved}"
