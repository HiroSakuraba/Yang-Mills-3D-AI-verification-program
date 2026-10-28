#!/usr/bin/env python3
"""TWO_FACE_EXACT_SURFACES_1 generator.

Enumerates every closed two-face plaquette surface S in Z^3 that contains a
fixed root plaquette, up to F_max faces, and computes the exact SU(2) Haar
integral of the product of fundamental characters over S.

Definitions
-----------
* A plaquette is (x, mu, nu) with x in Z^3 and mu < nu.
* A *closed two-face surface* is a finite, edge-connected set of plaquettes in
  which every lattice edge lies in exactly 0 or 2 plaquettes of the set.  These
  are exactly the all-fundamental polymers of the fallback "two-face" grammar
  (each edge in at most two active faces) that survive the dangling-edge
  vanishing lemma (an edge in one active fundamental face integrates to 0).
* W(S) = integral over all link variables of prod_{p in S} chi_{1/2}(U_p),
  with normalized Haar measure and the ordinary character chi_{1/2} = Tr.

Enumeration is exact and complete: start from the root, repeatedly pick the
smallest edge that lies in exactly one chosen plaquette, and branch over the
other plaquettes containing that edge (never letting an edge exceed two).
Every closed surface through the root is produced exactly once, because the
surface itself determines which plaquette covers each chosen edge.

W(S) is computed exactly by integrating out one link at a time with the SU(2)
identities (all traces below are traces of SU(2) words, hence real):
  int tr(U A) tr(U^-1 B) dU = tr(A B)/2
  int tr(U A) tr(U B)    dU = tr(A B^-1)/2
  int tr(U A U^-1 B)     dU = tr(A) tr(B)/2
  int tr(U A U B)        dU = -tr(B A^-1)/2
An empty word contributes tr(1) = 2.

Output: JSON with per-F counts N(F), the weighted sums A(F) = sum_S |W(S)| 2^F
(so that sum over S of |r_1^F W(S)| = sum_F A(F) t_1^F with t_1 = r_1/2), the
signed sums, topology tallies and a sample of explicit surfaces.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from fractions import Fraction

DIM = 3
ROOT = ((0, 0, 0), 0, 1)


def add(x, mu, k=1):
    y = list(x)
    y[mu] += k
    return tuple(y)


def plaq_edges(p):
    """Return the four edges of plaquette p as (point, dir) with traversal signs."""
    x, mu, nu = p
    return [((x, mu), +1), ((add(x, mu), nu), +1), ((add(x, nu), mu), -1), ((x, nu), -1)]


def plaquettes_on_edge(e):
    """All plaquettes of Z^3 containing edge e = (x, mu): 2(d-1) of them."""
    x, mu = e
    out = []
    for nu in range(DIM):
        if nu == mu:
            continue
        for base in (x, add(x, nu, -1)):
            a, b = (mu, nu) if mu < nu else (nu, mu)
            out.append((base, a, b))
    return out


def enumerate_surfaces(f_max, deadline=None):
    """Yield every closed two-face surface containing ROOT with <= f_max faces."""
    chosen = [ROOT]
    chosen_set = {ROOT}
    count = {}
    for e, _ in plaq_edges(ROOT):
        count[e] = 1
    open_edges = {e for e, c in count.items() if c == 1}

    def rec():
        if deadline is not None and time.time() > deadline:
            raise TimeoutError
        if not open_edges:
            yield frozenset(chosen)
            return
        n = len(chosen)
        # each new plaquette closes at most 4 open edges
        if n + (len(open_edges) + 3) // 4 > f_max:
            return
        e = min(open_edges)
        for p in plaquettes_on_edge(e):
            if p in chosen_set:
                continue
            pe = [ed for ed, _ in plaq_edges(p)]
            if any(count.get(ed, 0) >= 2 for ed in pe):
                continue
            chosen.append(p)
            chosen_set.add(p)
            for ed in pe:
                c = count.get(ed, 0) + 1
                count[ed] = c
                if c == 1:
                    open_edges.add(ed)
                else:
                    open_edges.discard(ed)
            yield from rec()
            for ed in pe:
                c = count[ed] - 1
                if c == 0:
                    del count[ed]
                    open_edges.discard(ed)
                else:
                    count[ed] = c
                    open_edges.add(ed)
            chosen_set.discard(p)
            chosen.pop()

    yield from rec()


# ---------------------------------------------------------------- Haar weight

def inverse(word):
    return [(e, -s) for e, s in reversed(word)]


def haar_weight(surface):
    """Exact integral of prod_p Tr(U_p) for an all-fundamental closed surface."""
    traces = [[(e, s) for e, s in plaq_edges(p)] for p in sorted(surface)]
    coef = Fraction(1)
    empties = 0
    while True:
        traces_nonempty = [t for t in traces if t]
        empties += sum(1 for t in traces if not t)
        traces = traces_nonempty
        if not traces:
            break
        e = traces[0][0][0]
        occ = [(i, j, s) for i, t in enumerate(traces) for j, (ed, s) in enumerate(t) if ed == e]
        if len(occ) != 2:
            raise ValueError("edge does not occur exactly twice: %r" % (e,))
        (i1, j1, s1), (i2, j2, s2) = occ
        if i1 != i2:
            t1 = traces[i1][j1:] + traces[i1][:j1]
            t2 = traces[i2][j2:] + traces[i2][:j2]
            if s1 == -1:
                t1 = inverse(t1)
                t1 = t1[-1:] + t1[:-1]  # bring the inverted occurrence back to front
            if s2 == -1:
                t2 = inverse(t2)
                t2 = t2[-1:] + t2[:-1]
            # now both start with (e, +1)
            a, b = t1[1:], t2[1:]
            merged = a + inverse(b)  # int tr(UA) tr(UB) = tr(A B^-1)/2
            coef /= 2
            rest = [t for k, t in enumerate(traces) if k not in (i1, i2)]
            traces = rest + [merged]
        else:
            t = traces[i1]
            j1, j2 = sorted((j1, j2))
            s_first, s_second = t[j1][1], t[j2][1]
            if s_first == -1 and s_second == -1:
                t = inverse(t)
                L = len(t)
                j1, j2 = L - 1 - j2, L - 1 - j1
                s_first, s_second = 1, 1
            elif s_first == -1 and s_second == +1:
                # rotate so the +1 occurrence comes first
                j1, j2 = j2, j1 + len(t)
                s_first, s_second = 1, -1
            tt = t + t
            A = tt[j1 + 1:j2]
            B = tt[j2 + 1:j1 + len(t)]
            coef /= 2
            rest = [x for k, x in enumerate(traces) if k != i1]
            if s_second == -1:  # tr(U A U^-1 B) = tr A tr B / 2
                traces = rest + [A, B]
            else:  # tr(U A U B) = -tr(B A^-1)/2
                coef = -coef
                traces = rest + [B + inverse(A)]
    return coef * (2 ** empties)


# ------------------------------------------------------------- topology data

def topology(surface):
    edges = {}
    for p in surface:
        for e, _ in plaq_edges(p):
            edges.setdefault(e, []).append(p)
    verts = {}
    for e in edges:
        x, mu = e
        verts.setdefault(x, set()).add(e)
        verts.setdefault(add(x, mu), set()).add(e)
    # vertex links: nodes are edges at v, joined by faces (corners)
    L = 0
    for v, ev in verts.items():
        adj = {e: [] for e in ev}
        for p in surface:
            pe = [e for e, _ in plaq_edges(p) if e in ev]
            if len(pe) == 2:
                adj[pe[0]].append(pe[1])
                adj[pe[1]].append(pe[0])
        seen = set()
        for e0 in ev:
            if e0 in seen:
                continue
            L += 1
            stack = [e0]
            while stack:
                u = stack.pop()
                if u in seen:
                    continue
                seen.add(u)
                stack.extend(adj[u])
    F, E, V = len(surface), len(edges), len(verts)
    # orientability by propagation
    orient = {}
    order = sorted(surface)
    orient[order[0]] = 1
    queue = [order[0]]
    orientable = True
    while queue:
        p = queue.pop()
        for e, s in plaq_edges(p):
            for q in edges[e]:
                if q == p:
                    continue
                sq = dict(plaq_edges(q))[e]
                want = -s * orient[p] * sq  # neighbours must traverse e oppositely
                if q not in orient:
                    orient[q] = want
                    queue.append(q)
                elif orient[q] != want:
                    orientable = False
    return {"F": F, "E": E, "V": V, "L": L, "chi": V - E + F, "orientable": orientable}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmax", type=int, default=10)
    ap.add_argument("--time-limit", type=float, default=3000.0)
    ap.add_argument("--output", default="two_face_results.json")
    args = ap.parse_args()

    deadline = time.time() + args.time_limit
    per_F = {}
    samples = []
    t0 = time.time()
    complete = True
    try:
        for S in enumerate_surfaces(args.fmax, deadline):
            W = haar_weight(S)
            top = topology(S)
            F = top["F"]
            d = per_F.setdefault(F, {"N": 0, "A_abs": Fraction(0), "A_signed": Fraction(0),
                                     "by_chi": {}, "nonorientable": 0, "pinched": 0})
            d["N"] += 1
            d["A_abs"] += abs(W) * (2 ** F)
            d["A_signed"] += W * (2 ** F)
            key = str(top["chi"])
            d["by_chi"][key] = d["by_chi"].get(key, 0) + 1
            if not top["orientable"]:
                d["nonorientable"] += 1
            if top["L"] != top["V"]:
                d["pinched"] += 1
            if len([s for s in samples if s["F"] == F]) < 5:
                samples.append({"F": F, "W": str(W), "topology": top,
                                "plaquettes": [[list(x), mu, nu] for x, mu, nu in sorted(S)]})
    except TimeoutError:
        complete = False
    out = {
        "id": "TWO_FACE_EXACT_SURFACES_1",
        "root": [list(ROOT[0]), ROOT[1], ROOT[2]],
        "fmax_requested": args.fmax,
        "complete": complete,
        "seconds": round(time.time() - t0, 2),
        "per_F": {str(F): {"N": d["N"], "A_abs": str(d["A_abs"]), "A_signed": str(d["A_signed"]),
                           "by_chi": d["by_chi"], "nonorientable": d["nonorientable"],
                           "pinched": d["pinched"]}
                  for F, d in sorted(per_F.items())},
        "samples": samples,
    }
    with open(args.output, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "samples"}, indent=1))
    return 0 if complete else 2


if __name__ == "__main__":
    sys.exit(main())
