#!/usr/bin/env python3
"""
build_manifest.py

Scans the reports/ directory for HTML files, extracts metadata
(title, category, date) from each, and writes reports.json.

Metadata extraction rules:
  - Title:    content of the <title> tag
  - Category: text inside the first element with class="rl"
  - Date:     text of the second <div> inside <footer class="rf">,
              expected format "Updated: (HH:MM) DD.MM.YYYY"
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


REPORTS_DIR = Path(__file__).resolve().parent / "reports"
MANIFEST_PATH = Path(__file__).resolve().parent / "reports.json"


def extract_title(html: str) -> str:
    """Extract content of <title> tag."""
    m = re.search(r"<title>([^<]+)</title>", html)
    return m.group(1).strip() if m else ""


def extract_category(html: str) -> str:
    """Extract text from the first element with class='rl'."""
    m = re.search(r'class="rl"[^>]*>([^<]+)<', html)
    return m.group(1).strip() if m else ""


def extract_date(html: str) -> str:
    """
    Extract the date string from the footer.
    Expected pattern inside <footer class="rf">:
      <div>...</div>
      <div>Updated: (HH:MM) DD.MM.YYYY</div>
    Returns ISO-ish string like "2026-04-03T20:39" or empty string.
    """
    # Find footer block
    footer_match = re.search(
        r'<footer\s+class="rf"[^>]*>(.*?)</footer>', html, re.DOTALL
    )
    if not footer_match:
        return ""

    footer_html = footer_match.group(1)
    # Find all <div> contents inside footer
    divs = re.findall(r"<div[^>]*>(.*?)</div>", footer_html, re.DOTALL)
    if len(divs) < 2:
        return ""

    date_text = divs[1].strip()
    # Expected: "Updated: (20:39) 03.04.2026"
    m = re.search(r"\((\d{2}:\d{2})\)\s+(\d{2})\.(\d{2})\.(\d{4})", date_text)
    if not m:
        return ""

    time_str, day, month, year = m.group(1), m.group(2), m.group(3), m.group(4)
    return f"{year}-{month}-{day}T{time_str}"


def build_manifest():
    """Scan reports/ and produce reports.json."""
    if not REPORTS_DIR.is_dir():
        print(f"Error: reports directory not found at {REPORTS_DIR}", file=sys.stderr)
        sys.exit(1)

    entries = []
    for html_file in sorted(REPORTS_DIR.glob("*.html")):
        html = html_file.read_text(encoding="utf-8", errors="replace")
        title = extract_title(html)
        category = extract_category(html)
        date = extract_date(html)

        if not title:
            print(f"  Warning: no title found in {html_file.name}, skipping.")
            continue

        entries.append(
            {
                "file": html_file.name,
                "title": title,
                "category": category,
                "date": date,
            }
        )
        print(f"  Indexed: {html_file.name}  →  {title}")

    # Sort by date descending (newest first), then title
    entries.sort(key=lambda e: (e["date"] or "", e["title"]), reverse=True)

    MANIFEST_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nManifest written to {MANIFEST_PATH} ({len(entries)} reports)")


if __name__ == "__main__":
    build_manifest()
