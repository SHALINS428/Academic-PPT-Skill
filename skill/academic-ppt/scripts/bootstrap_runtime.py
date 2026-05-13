#!/usr/bin/env python3
"""Bootstrap local Python and Node dependencies for the academic-ppt plugin."""

from __future__ import annotations

import argparse

from runtime_bootstrap import bootstrap_runtime, print_summary
from tools_bootstrap import bootstrap_tools


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    parser.add_argument(
        "--tools",
        action="store_true",
        help="Also bootstrap desktop validation tools into .runtime/tools.",
    )
    args = parser.parse_args()

    summary = bootstrap_runtime()
    if args.tools:
        summary["desktop_tools"] = bootstrap_tools(["libreoffice", "poppler", "fontconfig"])
        summary["ok"] = summary["ok"] and summary["desktop_tools"]["ok"]
    if args.json:
        print_summary(summary)
    else:
        print_summary(summary)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
