#!/usr/bin/env python3
"""Bootstrap optional desktop tools used by the academic-ppt plugin."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

from python_runtime import (
    RUNTIME_DIR,
    TOOLS_DIR,
    build_skill_environment,
    get_path_value,
)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
MANIFEST_PATH = SKILL_DIR / "assets" / "tool_manifest.json"
DOWNLOAD_DIR = RUNTIME_DIR / "tool-downloads"

TOOL_EXECUTABLES = {
    "libreoffice": ("soffice", "soffice.exe", "soffice.com", "libreoffice", "libreoffice.exe"),
    "poppler": ("pdftoppm", "pdftoppm.exe", "pdfinfo", "pdfinfo.exe"),
    "fontconfig": ("fc-list", "fc-list.exe"),
}

TOOL_ENV_VARS = {
    "libreoffice": ("SOFFICE_EXECUTABLE", "LIBREOFFICE_EXECUTABLE"),
    "poppler": ("PDFTOPPM_EXECUTABLE", "PDFINFO_EXECUTABLE"),
    "fontconfig": ("FC_LIST_EXECUTABLE",),
}


def platform_key() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = "arm64" if machine in {"arm64", "aarch64"} else "x64"
    if system.startswith("windows"):
        return f"windows-{arch}"
    if system == "darwin":
        return f"macos-{arch}"
    if system == "linux":
        return f"linux-{arch}"
    return f"{system}-{arch}"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def manifest_tool(tool_name: str) -> dict | None:
    manifest = load_manifest()
    platform_entry = manifest.get("platforms", {}).get(platform_key(), {})
    return platform_entry.get("tools", {}).get(tool_name)


def _configured_executable(env: dict[str, str], tool_name: str) -> Path | None:
    for env_var in TOOL_ENV_VARS.get(tool_name, ()):
        raw_value = env.get(env_var, "").strip()
        if not raw_value:
            continue
        candidate = Path(raw_value).expanduser()
        if candidate.exists():
            return candidate.resolve()
    return None


def find_tool_executable(tool_name: str, env: dict[str, str] | None = None) -> Path | None:
    env = env or build_skill_environment()
    configured = _configured_executable(env, tool_name)
    if configured:
        return configured
    search_path = get_path_value(env)
    for executable in TOOL_EXECUTABLES.get(tool_name, ()):
        resolved = shutil.which(executable, path=search_path)
        if resolved:
            return Path(resolved).resolve()
    return None


def tool_status(tool_name: str) -> dict:
    env = build_skill_environment()
    executable = find_tool_executable(tool_name, env)
    entry = manifest_tool(tool_name)
    return {
        "tool": tool_name,
        "found": executable is not None,
        "path": str(executable) if executable else None,
        "platform": platform_key(),
        "manifest_available": entry is not None,
        "fallback": entry.get("fallback") if entry else None,
    }


def summarize_tools(tool_names: list[str] | tuple[str, ...]) -> dict[str, dict]:
    return {tool_name: tool_status(tool_name) for tool_name in tool_names}


def _candidate_download_path(tool_name: str, entry: dict) -> Path:
    url = entry.get("download_url", "")
    suffix = Path(url.split("?", 1)[0]).suffix
    if not suffix:
        suffix = ".bin"
    return DOWNLOAD_DIR / f"{tool_name}{suffix}"


def _verify_sha256(path: Path, expected: str) -> None:
    if not expected:
        return
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest().lower()
    if actual != expected.lower():
        raise RuntimeError(f"SHA256 mismatch for {path.name}: expected {expected}, got {actual}")


def _download(tool_name: str, entry: dict) -> Path:
    url = entry.get("download_url", "").strip()
    if not url:
        raise RuntimeError(f"No download_url is configured for {tool_name}.")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = _candidate_download_path(tool_name, entry)
    if not target.exists():
        with urllib.request.urlopen(url, timeout=120) as response:
            target.write_bytes(response.read())
    _verify_sha256(target, entry.get("sha256", ""))
    return target


def _extract_zip(archive: Path, target_dir: Path) -> None:
    if target_dir.exists() and any(target_dir.iterdir()):
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(target_dir)


def _extract_msi_admin(msi_path: Path, target_dir: Path) -> None:
    if not sys.platform.startswith("win"):
        raise RuntimeError("MSI extraction is only supported on Windows.")
    if target_dir.exists() and any(target_dir.iterdir()):
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "msiexec",
        "/a",
        str(msi_path),
        f"TARGETDIR={target_dir}",
        "/qn",
        "/norestart",
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to extract MSI package with msiexec. "
            + (result.stderr or result.stdout or "").strip()
        )


def _install_tool(tool_name: str, entry: dict) -> dict:
    target_dir = TOOLS_DIR / tool_name
    archive = _download(tool_name, entry)
    kind = entry.get("kind")
    if kind == "zip":
        _extract_zip(archive, target_dir)
    elif kind == "msi-admin":
        _extract_msi_admin(archive, target_dir)
    else:
        raise RuntimeError(f"Unsupported bootstrap kind for {tool_name}: {kind}")
    return {"download": str(archive), "install_dir": str(target_dir)}


def bootstrap_tool(tool_name: str, *, allow_fallback: bool = True) -> dict:
    before = tool_status(tool_name)
    if before["found"]:
        before.update({"ok": True, "installed": False, "status": "found"})
        return before

    entry = manifest_tool(tool_name)
    if not entry:
        return {
            **before,
            "ok": False,
            "installed": False,
            "status": "unsupported-platform",
            "error": f"No tool manifest entry for {tool_name} on {platform_key()}.",
        }

    if not entry.get("download_url"):
        ok = allow_fallback and bool(entry.get("fallback"))
        return {
            **before,
            "ok": ok,
            "installed": False,
            "status": "fallback" if ok else "missing",
            "fallback": entry.get("fallback"),
        }

    try:
        install = _install_tool(tool_name, entry)
    except Exception as exc:
        return {
            **before,
            "ok": False,
            "installed": False,
            "status": "install-failed",
            "error": str(exc),
        }

    after = tool_status(tool_name)
    return {
        **after,
        "ok": after["found"],
        "installed": True,
        "status": "installed" if after["found"] else "installed-but-not-found",
        **install,
    }


def bootstrap_tools(tool_names: list[str] | tuple[str, ...], *, allow_fallback: bool = True) -> dict:
    results = {tool_name: bootstrap_tool(tool_name, allow_fallback=allow_fallback) for tool_name in tool_names}
    return {
        "ok": all(item.get("ok") for item in results.values()),
        "platform": platform_key(),
        "tools": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tools",
        nargs="*",
        default=["libreoffice", "poppler", "fontconfig"],
        help="Tool names to bootstrap.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Treat tools with Python fallback as missing if no executable is available.",
    )
    args = parser.parse_args()

    summary = bootstrap_tools(args.tools, allow_fallback=not args.no_fallback)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
