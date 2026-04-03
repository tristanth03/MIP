#!/usr/bin/env python3
"""
build_data_manifest.py

Scans data/ recursively for .md files, extracts rich metadata from
YAML frontmatter (if present) and falls back to folder-path inference.

Expected folder structure: data/{country}/{sector}/{file}.md
Frontmatter fields (all optional):
  title, country, sector, source, type, tags

Writes data.json with entries:
  { file, title, country, sector, source, type, tags }
"""

import json
import re
import sys
from pathlib import Path

DATA_DIR      = Path(__file__).resolve().parent / "data"
MANIFEST_PATH = Path(__file__).resolve().parent / "data.json"


def parse_frontmatter(md: str) -> tuple[dict, str]:
    """Parse YAML frontmatter block. Returns (meta_dict, body)."""
    meta = {}
    if not md.startswith("---"):
        return meta, md
    end = md.find("\n---", 3)
    if end == -1:
        return meta, md
    fm_block = md[3:end]
    body = md[end + 4:].lstrip("\n")
    for line in fm_block.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip().lower()
        v = v.strip().strip('"').strip("'")
        # Handle simple YAML lists: [a, b, c]
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        meta[k] = v
    return meta, body


def extract_title(md: str, stem: str) -> str:
    m = re.search(r"^#\s+(.+)", md, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return stem.replace("-", " ").replace("_", " ").title()


def infer_from_path(parts: list[str]) -> dict:
    """Infer country/sector from folder path segments."""
    inferred = {}
    # Strip leading 'api' segment if present
    if parts and parts[0].lower() == "api":
        parts = parts[1:]
    if len(parts) >= 1:
        inferred["country"] = parts[0]
    if len(parts) >= 2:
        inferred["sector"] = parts[1]
    return inferred


def build_data_manifest():
    if not DATA_DIR.is_dir():
        print(f"Error: data/ directory not found at {DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    entries = []
    for md_file in sorted(DATA_DIR.rglob("*.md")):
        rel   = md_file.relative_to(DATA_DIR).as_posix()
        text  = md_file.read_text(encoding="utf-8", errors="replace")

        fm, body = parse_frontmatter(text)
        title    = fm.get("title") or extract_title(text, md_file.stem)

        # Path-based fallback for country/sector
        path_parts = rel.split("/")[:-1]   # folder segments only
        inferred   = infer_from_path(path_parts)

        entry = {
            "file":    rel,
            "title":   title,
            "country": fm.get("country") or inferred.get("country", ""),
            "sector":  fm.get("sector")  or inferred.get("sector",  ""),
            "source":  fm.get("source")  or "",
            "type":    fm.get("type")    or "",
            "tags":    fm.get("tags")    or [],
        }
        entries.append(entry)
        print(f"  Indexed: {rel}  →  {title} [{entry['country']}]")

    MANIFEST_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nManifest written to {MANIFEST_PATH} ({len(entries)} files)")


if __name__ == "__main__":
    build_data_manifest()
