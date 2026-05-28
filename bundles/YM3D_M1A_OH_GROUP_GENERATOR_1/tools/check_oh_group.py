#!/usr/bin/env python3
"""INDEPENDENT checker for YM3D_OH_SIGNED_PERMUTATION_GROUP_1.

Independence contract (enforced by the harness lint):
  * does NOT import the generator package `ym3d`;
  * re-derives the full cubic group O_h from first principles using only the
    standard library and exact integer arithmetic;
  * reads the generator's exported artifact as UNTRUSTED input and audits it
    against the independently derived group.

A checker that merely re-ran the generator would prove reproducibility, not
correctness. This one proves the exported object IS the cubic group.
"""
from __future__ import annotations

import json
from itertools import permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1)


def ix(i: int, j: int) -> int:
    return 3 * i + j


def matmul(a, b):
    return tuple(sum(a[ix(i, k)] * b[ix(k, j)] for k in range(3))
                 for i in range(3) for j in range(3))


def transpose(m):
    return tuple(m[ix(j, i)] for i in range(3) for j in range(3))


def det(m):
    a, b, c, d, e, f, g, h, i = m
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def derive_oh():
    """All 3x3 signed-permutation matrices, derived independently."""
    out = set()
    for perm in permutations(range(3)):
        for signs in product((-1, 1), repeat=3):
            m = [0] * 9
            for row, col in enumerate(perm):
                m[ix(row, col)] = signs[row]
            out.add(tuple(m))
    return out


def main() -> int:
    art = ROOT / "artifacts"
    art.mkdir(exist_ok=True)

    # 1) independent derivation
    derived = derive_oh()

    # 2) load untrusted generator export
    exported_path = art / "oh_group_elements.json"
    exported_rows = json.loads(exported_path.read_text())

    def row_to_tuple(rows):
        return tuple(int(rows[i][j]) for i in range(3) for j in range(3))

    exported = {row_to_tuple(r["matrix"]) for r in exported_rows}

    # 3) audits, computed by the checker itself
    det_counts = {-1: 0, 1: 0}
    bad_det = 0
    for m in derived:
        d = det(m)
        if d in det_counts:
            det_counts[d] += 1
        else:
            bad_det += 1

    closed = all(matmul(a, b) in derived for a in derived for b in derived)
    inverses_ok = all(transpose(m) in derived
                      and matmul(m, transpose(m)) == IDENTITY for m in derived)

    checks = {
        "independent_count_is_48": len(derived) == 48,
        "identity_present": IDENTITY in derived,
        "closed_under_multiplication": closed,
        "inverses_present_and_correct": inverses_ok,
        "determinant_split_24_24": det_counts == {-1: 24, 1: 24},
        "no_bad_determinants": bad_det == 0,
        # the actual independence test: exported set EQUALS derived group
        "export_equals_derived_group": exported == derived,
        "export_count_is_48": len(exported) == 48,
    }
    passed = all(checks.values())

    decision = {
        "bundle": "YM3D_M1A_OH_GROUP_GENERATOR_1",
        "gate_id": "YM3D_OH_SIGNED_PERMUTATION_GROUP_1",
        "status": "PASS" if passed else "FAIL",
        "method": "independent re-derivation; generator export audited as untrusted input",
        "checks": checks,
        "determinant_counts": {str(k): v for k, v in det_counts.items()},
        "closed_obligations": [
            "independently derived 48 signed-permutation matrices",
            "verified identity, closure, inverses, orthogonality via transpose",
            "verified determinant split 24/24",
            "verified generator export equals the independently derived group",
        ] if passed else [],
        "non_claims": [
            "does not define lattice links",
            "does not prove support lifting",
            "does not compute atom orbits",
            "does not audit collision graphs",
            "does not prove analytic or Yang-Mills estimates",
        ],
        "next_obligation": "YM3D_ORIENTED_LINK_ACTION_1",
    }
    (art / "decision.json").write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n")

    print(("PASS" if passed else "FAIL") + ": YM3D_OH_SIGNED_PERMUTATION_GROUP_1")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
