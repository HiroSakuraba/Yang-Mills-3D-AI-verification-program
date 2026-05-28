#!/usr/bin/env python3
"""Generator step for YM3D_OH_SIGNED_PERMUTATION_GROUP_1.

Imports the generator package and writes the artifacts that the INDEPENDENT
checker (tools/check_oh_group.py) will audit without importing this code.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ym3d.group_oh import group_report, export_elements  # noqa: E402


def main() -> int:
    art = ROOT / "artifacts"
    art.mkdir(exist_ok=True)
    (art / "oh_group_report.json").write_text(
        json.dumps(group_report(), indent=2, sort_keys=True) + "\n")
    (art / "oh_group_elements.json").write_text(
        json.dumps(export_elements(), indent=2, sort_keys=True) + "\n")
    print("generated O_h artifacts (report + elements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
