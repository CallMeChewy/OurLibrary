#!/usr/bin/env python3
# File: ValidateSymlinkCompliance.py
# Path: OurLibrary/Scripts/Common/Tools/ValidateSymlinkCompliance.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-25
# Last Modified: 2025-08-25  01:00PM
# Symlink Pattern: PROJECT_TOOL
"""
Validates that scripts include the v2.3 header & symlink notes.
Works in current directory (Reality), not script location.
See CurrentDesignStandard.md.
"""

import os, sys, re
from pathlib import Path

REQUIRED = [
    r"AIDEV-PascalCase-2\.3",
    r"Symlink Pattern:\s*(PROJECT_TOOL|STANDALONE|ADAPTIVE)",
    r"os\.getcwd\(",
]

def scan(path: Path):
    bad = []
    for p in path.rglob("*.*"):
        if p.suffix.lower() not in {".py", ".sh", ".ts", ".js"}:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        missing = [rx for rx in REQUIRED if not re.search(rx, t)]
        if missing:
            bad.append((p, missing))
    return bad

def main():
    if not (Path(".git").exists()):
        print("❌ Not in a git repo; run from a project root.")
        return 1
    failures = scan(Path.cwd())
    if not failures:
        print("✅ All scanned scripts show v2.3 symlink compliance.")
        return 0
    print("⚠️  Non‑compliant files:")
    for p, miss in failures:
        print(f" - {p}:")
        for rx in miss:
            print(f"    • missing {rx}")
    return 2

if __name__ == "__main__":
    sys.exit(main())