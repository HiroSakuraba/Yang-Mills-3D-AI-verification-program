#!/usr/bin/env python3
"""Generator for YM3D_ORIENTED_LINK_ACTION_1. Produces artifacts/ for an INDEPENDENT checker to audit."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ym3d_link_action import build_rows  # noqa: E402

def main() -> int:
    art = ROOT / "artifacts"; art.mkdir(exist_ok=True)
    rows = build_rows()
    (art / "rows.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    print(f"generated {len(rows['elements']) * 3} affine rules for YM3D_ORIENTED_LINK_ACTION_1")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
