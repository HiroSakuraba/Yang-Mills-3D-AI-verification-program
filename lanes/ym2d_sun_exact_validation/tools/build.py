#!/usr/bin/env python3
"""Export exact rational 2D SU(2) reference artifacts for independent checking."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from ym2d_wilson import build


def main():
    data = build()
    art = ROOT / 'artifacts'; art.mkdir(exist_ok=True)
    (art / 'reference.json').write_text(json.dumps(data, sort_keys=True, indent=2) + '\n')
    print(f"Generated {len(data['loops'])} oriented rectangles and {len(data['area_law_expectations'])} area-law enclosures.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
