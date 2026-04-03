#!/usr/bin/env python3
"""
build_data_manifest.py

Scans the data/ directory for Markdown files and writes data.json.
Each entry: { "file": "name.md", "title": "..." }
Title is taken from the first # heading, or the filename if none found.
"""

import json
import re
import sys
from pathlib import Path

DATA_DIR      = Path(__file__).resolve().parent / "data"
MANIFEST_PATH = Path(__file__).resolve().parent / "data.json"


def extract_title(md: str, filename: str) -> str:
    m = re.search(r"^#\s+(.+)", md, re.MULTILINE)
    return m.group(1).strip() if m else filename.replace("-", " ").replace("_", " ").rsplit(".", 1)[0]


def build_data_manifest():
    if not DATA_DIR.is_dir():
        print(f"Error: data/ directory not found at {DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    entries = []
    for md_file in sorted(DATA_DIR.glob("*.md")):
        text  = md_file.read_text(encoding="utf-8", errors="replace")
        title = extract_title(text, md_file.name)
        entries.append({"file": md_file.name, "title": title})
        print(f"  Indexed: {md_file.name}  →  {title}")

    MANIFEST_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nManifest written to {MANIFEST_PATH} ({len(entries)} files)")


if __name__ == "__main__":
    build_data_manifest()
