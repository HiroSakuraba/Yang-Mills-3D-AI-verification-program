#!/usr/bin/env python3
"""Independent checker for BRANCHED_SUPPORTS_EXACT_1.

Does not import the generator.  It

  1. re-enumerates surviving supports through the root with its own code and
     the opposite ordering rule (largest link first), and compares per-F counts,
     valence profiles and the exact set of branched supports with the
     generator's JSON (treated as untrusted input);
  2. recomputes sheets, Finner classes q_p and the admissible {1,2}-labellings
     (admissibility by the parity-and-polygon rule, not by Clebsch-Gordan);
  3. recomputes every exact Haar integral by a different method: faces of label
     2 are expanded with chi_2 = Tr^2 - 1, and each fundamental link integral
     uses the Weingarten formula  int U^{(x)K} = sum_{s,t in B} v_s (G_B^{-1})_{st} v_t^T
     over a basis B of pairing (epsilon) invariants, G_B their Gram matrix,
     with a separate pairwise contraction engine on exact integers;
  4. checks |W_fund| <= Theorem C bound for even supports, and the single-link
     factorisation W(A u B) = W(A) W(B) wherever a support splits at one link;
  5. checks the two-face formula |W_a| = d_a^(L-E) for a = 2 and a = 3 on the
     cubes (larger two-face cases are covered by TWO_FACE_EXACT_SURFACES_1 for
     a = 1 only).
Labellings with more than --n2-cap faces of label 2 are counted but not
recomputed (the chi_2 expansion has 2^{n2} terms); the report says how many.
Exit code 0 only if everything matches.
"""
from __future__ import annotations

import argparse
import itertools
import json
import hashlib
import math
import sys
from fractions import Fraction

import numpy as np

D = 3
ROOT = ((0, 0, 0), 0, 1)
EPS = ((0, 1), (-1, 0))


def sh(x, mu, k):
    return x[:mu] + (x[mu] + k,) + x[mu + 1:]


def edges(p):
    x, a, b = p
    return (((x, a), 1), ((sh(x, a, 1), b), 1), ((sh(x, b, 1), a), -1), ((x, b), -1))


def links(p):
    return [e for e, _ in edges(p)]


def star(e):
    x, mu = e
    out = []
    for nu in range(D):
        if nu != mu:
            lo, hi = min(mu, nu), max(mu, nu)
            out.append((x, lo, hi))
            out.append((sh(x, nu, -1), lo, hi))
    return out


# ------------------------------------------------------------------ 1. enumeration
def supports(fmax):
    S = {ROOT}
    cnt = {e: 1 for e in links(ROOT)}
    done = set()
    res = []

    def go():
        und = [e for e in cnt if e not in done]
        if not und:
            res.append(frozenset(S))
            return
        ones = [e for e in und if cnt[e] == 1]
        if len(S) + (len(ones) + 3) // 4 > fmax:
            return
        e = max(ones) if ones else max(und)  # opposite rule to the generator
        c = cnt[e]
        av = [q for q in star(e) if q not in S and all(l not in done for l in links(q))]
        done.add(e)
        for r in range(len(av) + 1):
            if c + r < 2 or len(S) + r > fmax:
                continue
            for J in itertools.combinations(av, r):
                for q in J:
                    S.add(q)
                    for l in links(q):
                        cnt[l] = cnt.get(l, 0) + 1
                go()
                for q in J:
                    S.discard(q)
                    for l in links(q):
                        cnt[l] -= 1
                        if not cnt[l]:
                            del cnt[l]
        done.discard(e)

    go()
    return res


def incidence(X):
    at = {}
    for p in X:
        for e in links(p):
            at.setdefault(e, []).append(p)
    return at


# ------------------------------------------------------------------ 3. Haar (Weingarten)
def pairings(items):
    if not items:
        yield ()
        return
    a = items[0]
    for j in range(1, len(items)):
        for m in pairings(items[1:j] + items[j + 1:]):
            yield ((a, items[j]),) + m


def eps_vec(m, K):
    v = np.zeros((2,) * K, dtype=object)
    for idx in itertools.product((0, 1), repeat=K):
        val = 1
        for i, j in m:
            val *= EPS[idx[i]][idx[j]]
            if val == 0:
                break
        v[idx] = val
    return v.reshape(-1)


def frac_inverse(M):
    n = len(M)
    A = [[Fraction(M[i][j]) for j in range(n)] + [Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return [row[n:] for row in A]


_WG = {}


def weingarten_pieces(K):
    """Factored Weingarten link integral for K fundamental strands.

    int prod_i U_{r_i c_i} dU = sum_{s,t in B} v_s(r) (G_B^{-1})_{st} v_t(c), returned as
    (V with shape (2,)*K + (|B|,), integer matrix den*G_B^{-1}, den), or None for odd K.
    B is a maximal linearly independent set of pairing invariants; |B| must equal Catalan(K/2).
    """
    if K in _WG:
        return _WG[K]
    if K % 2:
        _WG[K] = None
        return None
    vecs = [eps_vec(m, K) for m in pairings(tuple(range(K)))]
    basis = []
    for v in vecs:
        trial = basis + [v]
        G = [[int(np.dot(x, y)) for y in trial] for x in trial]
        if abs(np.linalg.det(np.array(G, dtype=float))) > 0.5:
            basis = trial
    assert len(basis) == catalan(K // 2), (K, len(basis))
    G = [[int(np.dot(x, y)) for y in basis] for x in basis]
    Gi = frac_inverse(G)
    den = 1
    for row in Gi:
        for x in row:
            den = den * x.denominator // math.gcd(den, x.denominator)
    M = np.array([[int(x * den) for x in row] for row in Gi], dtype=object)
    V = np.stack(basis, axis=-1).reshape((2,) * K + (len(basis),))
    _WG[K] = (V, M, den)
    return _WG[K]


def contract(tensors):
    """Exact contraction of a closed network [(array, [labels])] by pairwise tensordot.

    Greedy: always contract the pair of tensors sharing an index whose result is
    smallest.  Each label occurs in exactly two tensor slots.
    """
    ts = {}
    where = {}
    for k, (arr, lab) in enumerate(tensors):
        ts[k] = (np.asarray(arr, dtype=object), list(lab))
        for x in lab:
            where.setdefault(x, set()).add(k)
    nxt = len(ts)
    scalar = 1

    def size_of(i, j):
        (a, la), (b, lb) = ts[i], ts[j]
        common = set(la) & set(lb)
        s = 1
        for t, lab in ((a, la), (b, lb)):
            for dim, x in zip(t.shape, lab):
                if x not in common:
                    s *= dim
        return s, common

    while ts:
        # closed pieces
        closed = [k for k, (_, l) in ts.items() if not l]
        for k in closed:
            arr, _ = ts.pop(k)
            scalar *= arr.item() if hasattr(arr, "item") else arr
        if not ts:
            break
        best = None
        seen = set()
        for x, ks in where.items():
            if len(ks) != 2:
                continue
            i, j = sorted(ks)
            if i == j or (i, j) in seen:
                continue
            seen.add((i, j))
            sz, common = size_of(i, j)
            if best is None or sz < best[0]:
                best = (sz, i, j, common)
        assert best is not None, "open indices left in the network"
        _, i, j, common = best
        (a, la), (b, lb) = ts.pop(i), ts.pop(j)
        common = sorted(common)
        c = np.tensordot(a, b, axes=([la.index(x) for x in common], [lb.index(x) for x in common]))
        lc = [x for x in la if x not in common] + [x for x in lb if x not in common]
        for x in common:
            del where[x]
        for x in lc:
            where[x].discard(i)
            where[x].discard(j)
            where[x].add(nxt)
        ts[nxt] = (c, lc)
        nxt += 1
    return scalar


EPS_A = np.array(EPS, dtype=object)
EPS_INV_A = np.array(((0, -1), (1, 0)), dtype=object)


def fundamental_W(copies):
    """int prod over face copies of Tr U_p, copies = list of plaquettes (repeats allowed)."""
    cnt = {}
    for p in copies:
        for e in links(p):
            cnt[e] = cnt.get(e, 0) + 1
    if any(v % 2 for v in cnt.values()):
        return Fraction(0)
    nid = [0]

    def new():
        nid[0] += 1
        return nid[0]
    slots = {}
    net = []
    for p in copies:
        c = [new() for _ in range(4)]
        # walk the boundary: entry k goes from corner k to corner k+1
        for k, (e, s) in enumerate(edges(p)):
            a, b = c[k], c[(k + 1) % 4]
            if s == 1:
                slots.setdefault(e, []).append((a, b))  # U_{ab}, row at the link's start
            else:
                # (U^-1)_{ab} = sum eps_{a m} U_{n m} eps^{-1}_{n b}; row n is at the start (corner b side)
                m, n = new(), new()
                net.append((EPS_A, [a, m]))
                net.append((EPS_INV_A, [n, b]))
                slots.setdefault(e, []).append((n, m))
    den = 1
    for e, sl in slots.items():
        V, M, d = weingarten_pieces(len(sl))
        den *= d
        al, be = new(), new()
        net.append((V, [r for r, _ in sl] + [al]))
        net.append((M, [al, be]))
        net.append((V, [t for _, t in sl] + [be]))
    return Fraction(contract(net), den)


def chi_expand(lab):
    """Yield (coefficient, list of face copies) for prod_p chi_{a_p}(U_p), a in {1,2,3}."""
    polys = {1: [(1, 1)], 2: [(1, 2), (-1, 0)], 3: [(1, 3), (-2, 1)]}  # (coef, power of Tr)
    faces = sorted(lab)
    for choice in itertools.product(*[polys[lab[p]] for p in faces]):
        coef = 1
        cop = []
        for p, (cf, pw) in zip(faces, choice):
            coef *= cf
            cop += [p] * pw
        yield coef, cop


def W_labels(lab):
    tot = Fraction(0)
    for coef, cop in chi_expand(lab):
        if not cop:
            tot += coef
            continue
        tot += coef * fundamental_W(cop)
    return tot


# ------------------------------------------------------------------ helpers
def admissible(labels):
    s = sum(labels)
    return s % 2 == 0 and 2 * max(labels) <= s


def sheets(X, at):
    faces = sorted(X)
    comp = {}
    k = 0
    for p in faces:
        if p in comp:
            continue
        stack = [p]
        comp[p] = k
        while stack:
            u = stack.pop()
            for e in links(u):
                if len(at[e]) == 2:
                    for v in at[e]:
                        if v not in comp:
                            comp[v] = k
                            stack.append(v)
        k += 1
    return comp, k


def corners_L(X, at):
    """Number of vertex-link cycles (two-face supports)."""
    cnr = {}
    for p in X:
        x, a, b = p
        vs = [x, sh(x, a, 1), sh(sh(x, a, 1), b, 1), sh(x, b, 1)]
        ls = links(p)
        for i in range(4):
            cnr.setdefault(vs[i], []).append((ls[i - 1], ls[i]))
    L = 0
    for v, prs in cnr.items():
        par = {}

        def f(u):
            while par.setdefault(u, u) != u:
                u = par[u]
            return u
        for a, b in prs:
            par[f(a)] = f(b)
        L += len({f(u) for pr in prs for u in pr})
    return L


def catalan(n):
    return math.comb(2 * n, n) // (n + 1)


def single_link_splits(X, at):
    out = []
    for e, ps in at.items():
        if len(ps) < 4:
            continue
        faces = list(X)
        comp = {}
        k = 0
        for p in faces:
            if p in comp:
                continue
            stack = [p]
            comp[p] = k
            while stack:
                u = stack.pop()
                for l in links(u):
                    if l == e:
                        continue
                    for v in at[l]:
                        if v not in comp:
                            comp[v] = k
                            stack.append(v)
            k += 1
        if k >= 2:
            parts = [frozenset(p for p in faces if comp[p] == i) for i in range(k)]
            out.append((e, parts))
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmax", type=int, required=True)
    ap.add_argument("--generator-json", required=True)
    ap.add_argument("--output", default="check_report.json")
    ap.add_argument("--n2-cap", type=int, default=6,
                    help="recompute labellings with at most this many label-2 faces")
    a = ap.parse_args()
    problems = []
    found = supports(a.fmax)
    # the generator output is read only after the independent enumeration
    import os
    import time as _t
    while not os.path.exists(a.generator_json):
        _t.sleep(30)
    _t.sleep(5)
    gen = json.load(open(a.generator_json))
    if not gen.get("complete"):
        problems.append("generator run incomplete")
    if len(set(found)) != len(found):
        problems.append("checker enumeration produced duplicates")
    per = {}
    mine_br = {}
    two_face = []
    for X in found:
        at = incidence(X)
        if any(len(v) == 1 for v in at.values()):
            problems.append("dangling link in a support")
        F = len(X)
        prof = [0] * 7
        for v in at.values():
            prof[len(v)] += 1
        d = per.setdefault(F, {"N": 0, "profiles": {}})
        d["N"] += 1
        key = ",".join(map(str, prof[2:]))
        d["profiles"][key] = d["profiles"].get(key, 0) + 1
        if max(prof[3:]) == 0:
            two_face.append(X)
        else:
            mine_br[tuple(sorted(X))] = (X, at, prof)
    # compare aggregates
    gper = gen["per_F"]
    for F in sorted(set(per) | {int(k) for k in gper}):
        g = gper.get(str(F))
        m = per.get(F)
        if g is None or m is None or g["N"] != m["N"] or g["profiles"] != m["profiles"]:
            problems.append("per-F mismatch at F=%d" % F)
    gen_br = {}
    for r in gen["branched_supports"]:
        key = tuple(sorted((tuple(x), mu, nu) for x, mu, nu in r["plaquettes"]))
        gen_br[key] = r
    if set(gen_br) != set(mine_br):
        problems.append("branched support sets differ: %d vs %d" % (len(gen_br), len(mine_br)))
    # per-support checks
    n_lab = 0
    n_skip = 0
    n_split = 0
    for key, (X, at, prof) in sorted(mine_br.items()):
        r = gen_br.get(key)
        if r is None:
            continue
        F = len(X)
        if r["profile"] != prof[2:]:
            problems.append("profile mismatch")
        qv = [0, 0, 0]
        for p in X:
            k = max(len(at[e]) for e in links(p))
            qv[(k + 1) // 2 - 1] += 1
        if r["finner_q2_q4_q6"] != qv:
            problems.append("Finner class mismatch")
        comp, ns = sheets(X, at)
        if r["n_sheets"] != ns:
            problems.append("sheet count mismatch")
        faces = sorted(X)
        mine_labs = {}
        for assign in itertools.product((1, 2), repeat=ns):
            lab = {p: assign[comp[p]] for p in faces}
            if all(admissible([lab[p] for p in ps]) for ps in at.values() if len(ps) >= 2):
                mine_labs[tuple(lab[p] for p in faces)] = lab
        # generator labellings are keyed by its own sheet order; compare as face-label vectors
        gen_labs = {}
        gfaces = [(tuple(x), mu, nu) for x, mu, nu in r["plaquettes"]]
        # rebuild generator's sheet map from its labellings is not possible directly; compare
        # multisets of (n2, W) after recomputing W for every admissible labelling here
        mine_vals = []
        for vec, lab in sorted(mine_labs.items()):
            n2 = sum(1 for p in faces if lab[p] == 2)
            if n2 > a.n2_cap:
                n_skip += 1
                mine_vals.append((n2, None))
                continue
            W = W_labels(lab)
            n_lab += 1
            mine_vals.append((n2, W))
        gen_vals = sorted((l["n2"], Fraction(l["W"]) if l["n2"] <= a.n2_cap else None)
                          for l in r["labellings_le2"])
        if sorted(mine_vals, key=lambda t: (t[0], t[1] or 0)) != sorted(gen_vals, key=lambda t: (t[0], t[1] or 0)):
            problems.append("labelling values differ for a support with F=%d: %s vs %s"
                            % (F, sorted(mine_vals)[:4], gen_vals[:4]))
        even = all(len(v) % 2 == 0 for v in at.values())
        if even:
            Wf = W_labels({p: 1 for p in faces})
            bound = Fraction(4 ** (F // 6), 2 ** F)
            for ps in at.values():
                bound *= catalan(len(ps) // 2)
            if abs(Wf) > bound:
                problems.append("Theorem C bound violated")
            if Fraction(r.get("W_fund", "nan")) != Wf or Fraction(r["theoremC_bound"]) != bound:
                problems.append("even-support data mismatch")
            if abs(Wf) > Fraction(r["strand_bound"]) or Fraction(r["strand_bound"]) > bound:
                problems.append("strand bound ordering violated")
            for e, parts in single_link_splits(X, at):
                prod = Fraction(1)
                for P in parts:
                    prod *= W_labels({p: 1 for p in P})
                n_split += 1
                if prod != Wf:
                    problems.append("single-link factorisation fails")
    # two-face label formula
    n_tf = 0
    for X in two_face:
        F = len(X)
        at = incidence(X)
        L = corners_L(X, at)
        E = len(at)
        for lab_a, fcap in ((2, 6), (3, 6)):
            if F <= fcap:
                W = W_labels({p: lab_a for p in X})
                n_tf += 1
                if abs(W) != Fraction((lab_a + 1) ** L, (lab_a + 1) ** E):
                    problems.append("two-face formula fails for a=%d F=%d" % (lab_a, F))
    report = {"id": "BRANCHED_SUPPORTS_EXACT_1", "checker_fmax": a.fmax,
              "status": "PASS" if not problems else "FAIL",
              "supports_enumerated": len(found), "branched": len(mine_br),
              "labellings_recomputed": n_lab, "labellings_not_recomputed_n2_above_cap": n_skip,
              "n2_cap": a.n2_cap, "single_link_splits_checked": n_split,
              "two_face_label_checks": n_tf,
              "per_F": {str(F): v for F, v in sorted(per.items())},
              "problems": problems[:30]}
    # Bind the independent check to the exact generator bytes it audited.
    # A changed generator artifact must invalidate the stored PASS report.
    with open(a.generator_json, "rb") as input_file:
        report["generator_sha256"] = hashlib.file_digest(input_file, "sha256").hexdigest()
    with open(a.output, "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "per_F"}, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
