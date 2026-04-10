#!/usr/bin/env python3
"""Simple consistency checks for OPM baseline artifacts."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "opm" / "system-context.opm.md",
    ROOT / "opm" / "data-lifecycle.opm.md",
    ROOT / "opm" / "deployment-process.opm.md",
    ROOT / "opm" / "ownership-matrix.md",
    ROOT / "contracts" / "trade_event.schema.json",
]


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        print("[FAIL] Missing required artifacts:")
        for item in missing:
            print(f" - {item}")
        return 1

    print("[PASS] OPM baseline artifacts are complete.")
    for path in REQUIRED_FILES:
        print(f" - {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
