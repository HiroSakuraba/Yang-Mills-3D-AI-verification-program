"""
Exact signed-permutation representation of the full cubic group O_h.

The group is represented as tuples of 9 integers in row-major order.
All arithmetic is exact integer arithmetic.  No numerical linear algebra
is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from typing import Iterable, List, Tuple, Dict


Matrix = Tuple[int, int, int, int, int, int, int, int, int]


IDENTITY: Matrix = (
    1, 0, 0,
    0, 1, 0,
    0, 0, 1,
)


def idx(i: int, j: int) -> int:
    return 3 * i + j


def generate_oh() -> List[Matrix]:
    """Generate all 48 signed-permutation matrices in O_h."""
    elements = []
    for perm in permutations(range(3)):
        for signs in product((-1, 1), repeat=3):
            m = [0] * 9
            for row, col in enumerate(perm):
                m[idx(row, col)] = signs[row]
            elements.append(tuple(m))
    # Sort lexicographically for deterministic export.
    return sorted(set(elements))


def transpose(m: Matrix) -> Matrix:
    return tuple(m[idx(j, i)] for i in range(3) for j in range(3))


def matmul(a: Matrix, b: Matrix) -> Matrix:
    out = []
    for i in range(3):
        for j in range(3):
            out.append(sum(a[idx(i, k)] * b[idx(k, j)] for k in range(3)))
    return tuple(out)


def det(m: Matrix) -> int:
    a, b, c, d, e, f, g, h, i = m
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def is_signed_permutation(m: Matrix) -> bool:
    if len(m) != 9:
        return False
    if any(x not in (-1, 0, 1) for x in m):
        return False

    for r in range(3):
        row = [m[idx(r, c)] for c in range(3)]
        if sum(1 for x in row if x != 0) != 1:
            return False
        if sum(abs(x) for x in row) != 1:
            return False

    for c in range(3):
        col = [m[idx(r, c)] for r in range(3)]
        if sum(1 for x in col if x != 0) != 1:
            return False
        if sum(abs(x) for x in col) != 1:
            return False

    return True


def is_orthogonal(m: Matrix) -> bool:
    return matmul(transpose(m), m) == IDENTITY and matmul(m, transpose(m)) == IDENTITY


def inverse(m: Matrix) -> Matrix:
    """For signed-permutation matrices, the inverse is the transpose."""
    return transpose(m)


def matrix_to_rows(m: Matrix) -> List[List[int]]:
    return [[m[idx(i, j)] for j in range(3)] for i in range(3)]


def matrix_from_rows(rows: List[List[int]]) -> Matrix:
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise ValueError("expected 3x3 rows")
    return tuple(int(rows[i][j]) for i in range(3) for j in range(3))


def as_jsonable(m: Matrix) -> List[List[int]]:
    return matrix_to_rows(m)


def from_jsonable(rows: List[List[int]]) -> Matrix:
    return matrix_from_rows(rows)


def group_report() -> Dict[str, object]:
    elements = generate_oh()
    element_set = set(elements)

    signed_permutation_failures = [m for m in elements if not is_signed_permutation(m)]
    orthogonality_failures = [m for m in elements if not is_orthogonal(m)]

    closure_failures = []
    for a in elements:
        for b in elements:
            c = matmul(a, b)
            if c not in element_set:
                closure_failures.append((a, b, c))
                break
        if closure_failures:
            break

    inverse_failures = []
    for m in elements:
        inv = inverse(m)
        if inv not in element_set or matmul(m, inv) != IDENTITY or matmul(inv, m) != IDENTITY:
            inverse_failures.append((m, inv))

    det_counts = {-1: 0, 1: 0}
    det_failures = []
    for m in elements:
        d = det(m)
        if d not in (-1, 1):
            det_failures.append((m, d))
        else:
            det_counts[d] += 1

    checks = {
        "unique_element_count_is_48": len(elements) == 48,
        "identity_present": IDENTITY in element_set,
        "all_signed_permutation_matrices": not signed_permutation_failures,
        "all_orthogonal": not orthogonality_failures,
        "closed_under_multiplication": not closure_failures,
        "all_inverses_present": not inverse_failures,
        "determinants_are_pm_one": not det_failures,
        "determinant_distribution_24_24": det_counts == {-1: 24, 1: 24},
    }

    return {
        "gate_id": "YM3D_OH_SIGNED_PERMUTATION_GROUP_1",
        "definition": "O_h as all 3x3 signed-permutation matrices over Z",
        "representation": "row-major tuple of nine exact integers",
        "element_count": len(elements),
        "determinant_counts": {str(k): v for k, v in det_counts.items()},
        "checks": checks,
        "pass": all(checks.values()),
        "failure_counts": {
            "signed_permutation_failures": len(signed_permutation_failures),
            "orthogonality_failures": len(orthogonality_failures),
            "closure_failures": len(closure_failures),
            "inverse_failures": len(inverse_failures),
            "determinant_failures": len(det_failures),
        },
    }


def export_elements() -> List[Dict[str, object]]:
    out = []
    for n, m in enumerate(generate_oh()):
        out.append({
            "element_id": f"oh_{n:02d}",
            "matrix": as_jsonable(m),
            "determinant": det(m),
        })
    return out
