#!/usr/bin/env python3
"""
Scaffold a new gate bundle with the correct generator/checker separation.

The design requires that the independent checker NOT import the generator's
code. This scaffolder enforces that physically: it creates

    bundles/<GATE_ID>/
        src/<pkg>/__init__.py        generator package (the agent fills this)
        tools/build.py               runs the generator, writes artifacts/
        tools/check_<short>.py       INDEPENDENT checker -- reads artifacts only,
                                     re-derives the invariant from scratch, and
                                     must not import src/<pkg>.

Usage:
    scaffold_gate.py <GATE_ID> [--pkg ym3d_link] [--short link_action]
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUILD_TPL = '''#!/usr/bin/env python3
"""Generator for {gate}. Produces artifacts/ for an INDEPENDENT checker to audit."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from {pkg} import build_rows  # noqa: E402

def main() -> int:
    art = ROOT / "artifacts"; art.mkdir(exist_ok=True)
    rows = build_rows()
    (art / "rows.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\\n")
    print(f"generated {{len(rows)}} rows for {gate}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''

CHECK_TPL = '''#!/usr/bin/env python3
"""INDEPENDENT checker for {gate}.

CONTRACT (enforced by the harness independence lint):
  * MUST NOT import the generator package `{pkg}`.
  * MUST re-derive the claimed invariant from first principles / raw data.
  * MUST read only the generated artifacts as untrusted input.
  * Writes artifacts/decision.json with status PASS|FAIL and the named metrics.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]

def audit(rows) -> tuple[bool, dict]:
    # TODO: re-derive the invariant independently here.
    # Return (passed, metrics_dict). Keep all arithmetic exact (int/Fraction).
    checks = {{}}
    return all(checks.values()), {{"checks": checks}}

def main() -> int:
    art = ROOT / "artifacts"; art.mkdir(exist_ok=True)
    rows = json.loads((art / "rows.json").read_text())
    passed, report = audit(rows)
    decision = {{
        "gate_id": "{gate}",
        "status": "PASS" if passed else "FAIL",
        "report": report,
        "non_claims": ["scaffold: fill in the real audit"],
    }}
    (art / "decision.json").write_text(json.dumps(decision, indent=2, sort_keys=True) + "\\n")
    print(("PASS" if passed else "FAIL") + ": {gate}")
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("gate_id")
    ap.add_argument("--pkg", default=None)
    ap.add_argument("--short", default=None)
    a = ap.parse_args()
    short = a.short or a.gate_id.lower().replace("ym3d_", "").replace("_1", "")[:16]
    pkg = a.pkg or ("ym3d_" + short)

    base = ROOT / "bundles" / a.gate_id
    (base / "src" / pkg).mkdir(parents=True, exist_ok=True)
    (base / "tools").mkdir(parents=True, exist_ok=True)
    (base / "artifacts").mkdir(parents=True, exist_ok=True)

    (base / "src" / pkg / "__init__.py").write_text(
        '"""Generator package. Implement build_rows() returning a list of dict rows."""\n'
        "def build_rows():\n    raise NotImplementedError\n")
    (base / "tools" / "build.py").write_text(
        BUILD_TPL.format(gate=a.gate_id, pkg=pkg))
    (base / "tools" / f"check_{short}.py").write_text(
        CHECK_TPL.format(gate=a.gate_id, pkg=pkg))
    (base / "README.md").write_text(
        f"# {a.gate_id}\n\nGenerator: `tools/build.py` -> `src/{pkg}`.\n"
        f"Independent checker: `tools/check_{short}.py` (must not import `{pkg}`).\n")
    print(f"scaffolded bundles/{a.gate_id}")
    print(f"  generator_cmd: python tools/build.py")
    print(f"  checker_cmd:   python tools/check_{short}.py")
    print("Update program.yaml workdir/checker_cmd to match, then `run.py gate "
          f"{a.gate_id}`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
