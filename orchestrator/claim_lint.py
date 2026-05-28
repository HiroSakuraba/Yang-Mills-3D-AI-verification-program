#!/usr/bin/env python3
"""
Claim ratchet.

Scans manuscript files (.md / .tex) for strong mathematical claim language
and FAILS if a claim is asserted that is not yet backed by a CLOSED gate in
program.yaml. This is the automated guard against prose outrunning proof --
the failure mode the program's own history flags as costly.

A claim phrase is "earned" only if the gate(s) that unlock it are CLOSED in
artifacts/state.json. Mapping lives in claim_map below and is intentionally
conservative: unknown strong claims fail closed.

Usage:
    claim_lint.py <file1> [<file2> ...]
    claim_lint.py --all          # lint every .md/.tex under the design bundle
Exit 0 == clean.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "artifacts" / "state.json"

# claim phrase (regex, case-insensitive) -> gate id that must be CLOSED to earn it
CLAIM_MAP: list[tuple[str, str]] = [
    (r"\bmass gap (is|has been) (proved|established|closed)\b",
     "YM3D_ONE_STEP_RG_RUNG_SCALE_INDEXED_1"),
    (r"\b(we|this work) prove[sd]? (a|the) mass gap\b",
     "YM3D_ONE_STEP_RG_RUNG_SCALE_INDEXED_1"),
    (r"\bRG (contraction|rung)\b.*\b(proved|established|holds)\b",
     "YM3D_ONE_STEP_RG_RUNG_SCALE_INDEXED_1"),
    (r"\bcontinuum (Yang.?Mills )?(is )?constructed\b",
     "__NEVER__"),   # not a target of this program; always fail
    (r"\bclustering (bound )?(is )?(proved|established)\b",
     "YM3D_VOLUME_UNIFORM_CLUSTERING_1"),
    (r"\bterminal KP (smallness|bound) (proved|holds|established)\b",
     "YM3D_TERMINAL_KP_ACTIVITY_MAP_SCALE_INDEXED_1"),
    (r"\b2D (validation|benchmark) (passed|reproduced)\b",
     "YM2D_SUN_EXACT_VALIDATION_LANE_0"),
]

# phrases that are always allowed (hedged / non-claims), used to suppress
# false positives when the surrounding sentence is explicitly a non-claim.
SAFE_CONTEXT = re.compile(
    r"\b(do(es)? not claim|non-?claim|not (yet )?(a )?(proof|proved|established)|"
    r"target|goal|conjectur|aim to|intend to|would (prove|establish)|"
    r"placeholder|advisory)\b", re.I)


def closed_gates() -> set[str]:
    if not STATE.exists():
        return set()
    data = json.loads(STATE.read_text())
    return {g for g, r in data.get("gates", {}).items()
            if r.get("status") == "CLOSED"}


def lint_file(path: Path, closed: set[str]) -> list[str]:
    text = path.read_text(errors="ignore")
    lines = text.splitlines()
    viol = []
    for pat, gate in CLAIM_MAP:
        rx = re.compile(pat, re.I)
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                if SAFE_CONTEXT.search(line):
                    continue
                earned = (gate != "__NEVER__") and (gate in closed)
                if not earned:
                    reason = ("claim is out of scope for this program"
                              if gate == "__NEVER__"
                              else f"requires gate {gate} CLOSED (it is not)")
                    viol.append(f"{path.name}:{i}: unearned claim -- {reason}\n"
                                f"        > {line.strip()[:100]}")
    return viol


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: claim_lint.py <files...> | --all")
        return 2
    if args == ["--all"]:
        files = list((ROOT / "design").rglob("*.md")) + \
                list((ROOT / "design").rglob("*.tex"))
    else:
        files = [Path(a) for a in args]

    closed = closed_gates()
    all_viol = []
    for f in files:
        if f.exists():
            all_viol += lint_file(f, closed)

    if all_viol:
        print(f"CLAIM RATCHET: {len(all_viol)} unearned claim(s):\n")
        print("\n".join(all_viol))
        print(f"\nCLOSED gates that earn claims: {sorted(closed) or '(none)'}")
        return 1
    print(f"CLAIM RATCHET: clean ({len(files)} file(s) scanned, "
          f"{len(closed)} gates CLOSED)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
