#!/usr/bin/env python3
"""Independent checker for TWO_FACE_EXACT_SURFACES_1.

Does not import the generator.  It
  1. re-enumerates closed two-face plaquette surfaces through the root with a
     different encoding and the opposite branching rule (largest open edge);
  2. evaluates every Haar integral with a Weingarten contraction: each U^-1 is
     rewritten as eps U^T eps^-1, each link pair is replaced by
     (1/2) eps_ik eps_jl, and the resulting closed network of 2x2 integer
     matrices is traced cycle by cycle (exact integers);
  3. checks the combinatorial formula |W| = 2^(L - E), with L the number of
     vertex-link cycles, and the bound 2^F |W| <= 4 for every surface;
  4. compares counts N(F) and weighted sums A(F) = sum 2^F |W| with the
     generator's JSON, treated as untrusted input.
Exit code 0 only if everything matches.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import sys
from fractions import Fraction

D = 3
EPS = ((0, 1), (-1, 0))
EPS_INV = ((0, -1), (1, 0))


def shift(x, mu, k):
    return x[:mu] + (x[mu] + k,) + x[mu + 1:]


def boundary(p):
    x, a, b = p
    return (((x, a), 1), ((shift(x, a, 1), b), 1), ((shift(x, b, 1), a), -1), ((x, b), -1))


def faces_of(e):
    x, mu = e
    res = []
    for nu in range(D):
        if nu != mu:
            lo, hi = min(mu, nu), max(mu, nu)
            res.append((x, lo, hi))
            res.append((shift(x, nu, -1), lo, hi))
    return res


def surfaces(root, fmax):
    S = [root]
    inS = {root}
    inc = {}
    for e, _ in boundary(root):
        inc[e] = 1
    opened = set(inc)
    found = []

    def go():
        if not opened:
            found.append(frozenset(S))
            return
        if len(S) + -(-len(opened) // 4) > fmax:
            return
        e = max(opened)  # opposite rule to the generator
        for q in faces_of(e):
            if q in inS:
                continue
            qe = [ed for ed, _ in boundary(q)]
            if any(inc.get(ed, 0) == 2 for ed in qe):
                continue
            S.append(q)
            inS.add(q)
            for ed in qe:
                inc[ed] = inc.get(ed, 0) + 1
                (opened.add if inc[ed] == 1 else opened.discard)(ed)
            go()
            for ed in qe:
                inc[ed] -= 1
                if inc[ed] == 0:
                    del inc[ed]
                    opened.discard(ed)
                else:
                    opened.add(ed)
            inS.discard(q)
            S.pop()

    go()
    return found


def weingarten_value(surface):
    """Exact value of int prod Tr(U_p) as a Fraction, by explicit index contraction."""
    tensors = []  # list of (matrix, row_index_id, col_index_id)
    nid = [0]

    def new():
        nid[0] += 1
        return nid[0]

    link_slots = {}  # edge -> list of (row_id, col_id) of each U occurrence
    for p in sorted(surface):
        bd = boundary(p)
        c = [new() for _ in range(4)]
        for k, (e, s) in enumerate(bd):
            a, b = c[k], c[(k + 1) % 4]
            if s == 1:
                link_slots.setdefault(e, []).append((a, b))
            else:
                # (U^-1)_{ab} = sum_{m,n} eps_{bm} U_{mn} eps^-1_{na}
                m, n = new(), new()
                tensors.append((EPS, b, m))
                link_slots.setdefault(e, []).append((m, n))
                tensors.append((EPS_INV, n, a))
    n_links = 0
    for e, occ in link_slots.items():
        if len(occ) != 2:
            raise ValueError("link not used exactly twice")
        (i, j), (k, l) = occ
        tensors.append((EPS, i, k))  # int U_ij U_kl = (1/2) eps_ik eps_jl
        tensors.append((EPS, j, l))
        n_links += 1
    # every index id now appears in exactly two tensor slots: trace the cycles
    where = {}
    for t, (M, r, cidx) in enumerate(tensors):
        where.setdefault(r, []).append((t, 0))
        where.setdefault(cidx, []).append((t, 1))
    for idx, lst in where.items():
        if len(lst) != 2:
            raise ValueError("index not shared by exactly two slots")
    used = [False] * len(tensors)
    total = 1

    def matmul(A, B):
        return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)) for i in range(2))

    def transpose(A):
        return ((A[0][0], A[1][0]), (A[0][1], A[1][1]))

    for t0 in range(len(tensors)):
        if used[t0]:
            continue
        M, r, c = tensors[t0]
        prod = M
        used[t0] = True
        # walk the cycle: leave t0 through its column index, return at its row index
        cur_t, exit_slot = t0, 1
        cur_idx = c
        while True:
            options = where[cur_idx]
            nxt = [(t, s) for (t, s) in options if not (t == cur_t and s == exit_slot)]
            t, s = nxt[0]
            if t == t0 and s == 0:
                break
            Mt = tensors[t][0]
            if s == 0:  # enter at row index: multiply by M
                prod = matmul(prod, Mt)
                exit_slot = 1
                cur_idx = tensors[t][2]
            else:  # enter at column index: multiply by M^T
                prod = matmul(prod, transpose(Mt))
                exit_slot = 0
                cur_idx = tensors[t][1]
            used[t] = True
            cur_t = t
        total *= prod[0][0] + prod[1][1]
    return Fraction(total, 2 ** n_links)


def combinatorics(surface):
    inc = {}
    for p in surface:
        for e, _ in boundary(p):
            inc.setdefault(e, []).append(p)
    ok_two = all(len(v) == 2 for v in inc.values())
    # edge connectivity of faces
    faces = list(surface)
    seen = {faces[0]}
    stack = [faces[0]]
    while stack:
        p = stack.pop()
        for e, _ in boundary(p):
            for q in inc[e]:
                if q not in seen:
                    seen.add(q)
                    stack.append(q)
    connected = len(seen) == len(faces)
    # vertex-link cycles
    corner = {}
    for p in surface:
        bd = [e for e, _ in boundary(p)]
        for v in {e[0] for e in bd} | {shift(e[0], e[1], 1) for e in bd}:
            at = [e for e in bd if e[0] == v or shift(e[0], e[1], 1) == v]
            corner.setdefault(v, []).append(tuple(at))
    L = 0
    for v, pairs in corner.items():
        parent = {}

        def find(u):
            while parent.setdefault(u, u) != u:
                u = parent[u]
            return u
        for a, b in pairs:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
        L += len({find(u) for pr in pairs for u in pr})
    return ok_two, connected, len(inc), L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmax", type=int, required=True)
    ap.add_argument("--generator-json", required=True)
    ap.add_argument("--output", default="check_report.json")
    a = ap.parse_args()
    root = ((0, 0, 0), 0, 1)
    found = surfaces(root, a.fmax)
    problems = []
    per = {}
    if len(set(found)) != len(found):
        problems.append("duplicate surfaces in checker enumeration")
    for S in found:
        ok_two, conn, E, L = combinatorics(S)
        F = len(S)
        if root not in S or not ok_two or not conn:
            problems.append("invalid surface F=%d" % F)
        W = weingarten_value(S)
        if abs(W) != Fraction(2 ** L, 2 ** E):
            problems.append("|W| != 2^(L-E) at F=%d: W=%s L=%d E=%d" % (F, W, L, E))
        if abs(W) * 2 ** F > 4:
            problems.append("2^F|W| > 4 at F=%d" % F)
        d = per.setdefault(F, [0, Fraction(0), Fraction(0)])
        d[0] += 1
        d[1] += abs(W) * 2 ** F
        d[2] += W * 2 ** F
    with open(a.generator_json) as fh:
        gen = json.load(fh)
    if not gen.get("complete"):
        problems.append("generator run incomplete")
    gper = gen["per_F"]
    for F in sorted(set(per) | {int(k) for k in gper}):
        if F > a.fmax:
            continue
        mine = per.get(F, [0, Fraction(0), Fraction(0)])
        theirs = gper.get(str(F))
        if theirs is None:
            problems.append("F=%d missing in generator output" % F)
            continue
        if (theirs["N"], Fraction(theirs["A_abs"]), Fraction(theirs["A_signed"])) != (mine[0], mine[1], mine[2]):
            problems.append("mismatch at F=%d: generator %s vs checker %s" % (F, theirs, mine))
    report = {"id": "TWO_FACE_EXACT_SURFACES_1", "checker_fmax": a.fmax,
              "status": "PASS" if not problems else "FAIL",
              "per_F": {str(F): {"N": v[0], "A_abs": str(v[1]), "A_signed": str(v[2])} for F, v in sorted(per.items())},
              "problems": problems[:20]}
    # Bind the independent check to the exact generator bytes it audited.
    # A changed generator artifact must invalidate the stored PASS report.
    with open(a.generator_json, "rb") as input_file:
        report["generator_sha256"] = hashlib.file_digest(input_file, "sha256").hexdigest()
    with open(a.output, "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
