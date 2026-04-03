#!/usr/bin/env python3
"""
add_report.py

Usage:
    python add_report.py <path_to_report.html> [<path_to_report2.html> ...]

Copies each HTML report into reports/, then rebuilds reports.json.
"""

import shutil
import sys
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_report.py <path_to_report.html> [...]")
        sys.exit(1)

    REPORTS_DIR.mkdir(exist_ok=True)

    for src in sys.argv[1:]:
        src_path = Path(src)
        if not src_path.is_file():
            print(f"  Skipping (not found): {src}")
            continue
        dest = REPORTS_DIR / src_path.name
        shutil.copy2(str(src_path), str(dest))
        print(f"  Copied: {src_path.name} → reports/")

    # Rebuild manifest
    print("\nRebuilding manifest...")
    import build_manifest

    build_manifest.build_manifest()


if __name__ == "__main__":
    main()
