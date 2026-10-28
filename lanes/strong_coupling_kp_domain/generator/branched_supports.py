#!/usr/bin/env python3
"""BRANCHED_SUPPORTS_EXACT_1 generator.

Enumerates every surviving plaquette support X through the root with F <= fmax
(generator/supports.py), and for each support records

  * F, the link-valence profile (n_2, ..., n_6), and whether X is two-face
    (all valences 2) or branched (some valence >= 3);
  * two-face supports: Euler characteristic and pinch data (their Haar weights
    are |W| = d_a^(L-E) for every label a, TWO_FACE_EXACT_SURFACES_1);
  * branched supports:
      - the face classes by q_p = (max valence on the face, rounded up to even),
        used by the Finner bound |w(X)| <= prod_p ||f||_{q_p};
      - the sheets (classes of faces joined through valence-2 links, on which
        any nonvanishing labelling is constant);
      - every admissible sheet labelling with labels in {1, 2} and, when at most
        --n2-cap faces carry label 2, its exact Haar integral W (generator/haar.py);
      - for even supports (all valences even): the all-fundamental W, the strand
        bound S(X) = prod_e (k_e/2+1)!^{-1} * sum_sigma 2^{L(sigma)}, the bound
        of Theorem C, 2^{-F} prod_e Cat(k_e/2) 4^{floor(F/6)}, and the maximum
        number of resolved components.

Output: JSON with per-F aggregates and a list of all branched supports.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from fractions import Fraction

from supports import enumerate_supports, links_of, plaq_links, valence_profile, add, ROOT
from haar import haar_integral, pairings_list, inv_mult_from_labels  # noqa: F401


def catalan(n):
    return math.comb(2 * n, n) // (n + 1)


def sheets_of(X, cnt):
    faces = sorted(X)
    parent = {p: p for p in faces}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u
    at = {}
    for p in faces:
        for e in links_of(p):
            at.setdefault(e, []).append(p)
    for e, ps in at.items():
        if len(ps) == 2:
            a, b = find(ps[0]), find(ps[1])
            if a != b:
                parent[a] = b
    roots = sorted({find(p) for p in faces})
    idx = {r: i for i, r in enumerate(roots)}
    return [idx[find(p)] for p in faces], faces, at


def vertices_of_face(p):
    x, mu, nu = p
    return [x, add(x, mu), add(add(x, mu), nu), add(x, nu)]


def strand_data(X, at):
    """For an even support: sum over resolutions sigma of 2^{L(sigma)}, and max components."""
    faces = sorted(X)
    links = sorted(at)
    choices = []
    for e in links:
        ps = at[e]
        choices.append([tuple(tuple(ps[i] for i in pr) for pr in m)
                        for m in pairings_list(tuple(range(len(ps))))])
    # corners: face p at vertex v joins its two links at v
    corners = {}
    for p in faces:
        L = [e for e, _ in plaq_links(p)]
        vs = vertices_of_face(p)
        # link i of p runs from vs[i] to vs[i+1] (as a set); corner at vs[i] joins links i-1 and i
        for i in range(4):
            corners[(p, vs[i])] = (L[i - 1], L[i])
    total = 0
    maxC = 0
    nsig = 0
    for sig in itertools.product(*choices):
        nsig += 1
        partner = {}
        for e, m in zip(links, sig):
            for a, b in m:
                partner[(a, e)] = b
                partner[(b, e)] = a
        # vertex cycles
        seen = set()
        Lcount = 0
        for (p, v), (e1, e2) in corners.items():
            if (p, v) in seen:
                continue
            Lcount += 1
            cur, came = p, e1
            while True:
                seen.add((cur, v))
                a, b = corners[(cur, v)]
                out = b if a == came else a
                nxt = partner[(cur, out)]
                cur, came = nxt, out
                if (cur, v) in seen:
                    break
        # components
        par = {p: p for p in faces}

        def find(u):
            while par[u] != u:
                par[u] = par[par[u]]
                u = par[u]
            return u
        for (a, e), b in partner.items():
            ra, rb = find(a), find(b)
            if ra != rb:
                par[ra] = rb
        C = len({find(p) for p in faces})
        maxC = max(maxC, C)
        total += 2 ** Lcount
    denom = 1
    for e in links:
        denom *= math.factorial(len(at[e]) // 2 + 1)
    return Fraction(total, denom), maxC, nsig


def euler_two_face(X, at):
    verts = set()
    for p in X:
        verts.update(vertices_of_face(p))
    return len(verts) - len(at) + len(X)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmax", type=int, required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--time-limit", type=float, default=36000)
    ap.add_argument("--n2-cap", type=int, default=8,
                    help="exact W only for labellings with at most this many label-2 faces")
    a = ap.parse_args()
    t0 = time.time()
    deadline = t0 + a.time_limit
    per_F = {}
    branched = []
    complete = True
    try:
        for X in enumerate_supports(a.fmax, deadline=deadline):
            prof, cnt = valence_profile(X)
            F = len(X)
            d = per_F.setdefault(F, {"N": 0, "two_face": 0, "branched": 0, "two_face_by_chi": {},
                                      "profiles": {}, "finner_classes": {}, "even_branched": 0,
                                      "label_sums": {}})
            d["N"] += 1
            key = ",".join(map(str, prof[2:]))
            d["profiles"][key] = d["profiles"].get(key, 0) + 1
            sheet, faces, at = sheets_of(X, cnt)
            if max(prof[3:]) == 0:
                d["two_face"] += 1
                chi = str(euler_two_face(X, at))
                d["two_face_by_chi"][chi] = d["two_face_by_chi"].get(chi, 0) + 1
                continue
            d["branched"] += 1
            # Finner classes
            qv = [0, 0, 0]
            for p in faces:
                k = max(cnt[e] for e in links_of(p))
                q = k + (k % 2)
                qv[q // 2 - 1] += 1
            qkey = ",".join(map(str, qv))
            d["finner_classes"][qkey] = d["finner_classes"].get(qkey, 0) + 1
            rec = {"F": F, "profile": list(prof[2:]), "finner_q2_q4_q6": qv,
                   "n_sheets": max(sheet) + 1, "plaquettes": [[list(x), m, n] for x, m, n in faces]}
            even = all(v % 2 == 0 for v in cnt.values())
            rec["even"] = even
            # labellings with labels in {1,2}, constant on sheets
            labs = []
            for assign in itertools.product((1, 2), repeat=max(sheet) + 1):
                lab = {p: assign[s] for p, s in zip(faces, sheet)}
                ok = True
                for e, ps in at.items():
                    if len(ps) >= 3 and not inv_mult_from_labels(tuple(lab[p] for p in ps)):
                        ok = False
                        break
                if not ok:
                    continue
                n2 = sum(1 for p in faces if lab[p] == 2)
                if n2 > a.n2_cap:
                    labs.append({"sheet_labels": list(assign), "n1": F - n2, "n2": n2, "W": None})
                    d["labellings_not_computed"] = d.get("labellings_not_computed", 0) + 1
                    continue
                W = haar_integral(lab)
                labs.append({"sheet_labels": list(assign), "n1": F - n2, "n2": n2, "W": str(W)})
                ls = d["label_sums"].setdefault("%d,%d" % (F - n2, n2), [0, "0", "0"])
                ls[0] += 1
                ls[1] = str(Fraction(ls[1]) + abs(W))
                ls[2] = str(Fraction(ls[2]) + W)
            rec["labellings_le2"] = labs
            if even:
                d["even_branched"] += 1
                S, maxC, nsig = strand_data(X, at)
                bound_C = Fraction(4 ** (F // 6), 2 ** F)
                for e, ps in at.items():
                    bound_C *= catalan(len(ps) // 2)
                Wf = Fraction([l["W"] for l in labs if l["n2"] == 0][0])
                rec.update({"W_fund": str(Wf), "strand_bound": str(S), "theoremC_bound": str(bound_C),
                            "max_components": maxC, "n_resolutions": nsig})
                if abs(Wf) > S or S > bound_C:
                    raise AssertionError("bound violated at %r" % rec)
            branched.append(rec)
    except TimeoutError:
        complete = False
    out = {"id": "BRANCHED_SUPPORTS_EXACT_1", "root": [list(ROOT[0]), ROOT[1], ROOT[2]],
           "fmax_requested": a.fmax, "n2_cap": a.n2_cap, "complete": complete, "seconds": round(time.time() - t0, 1),
           "per_F": {str(F): v for F, v in sorted(per_F.items())}, "branched_supports": branched}
    with open(a.output, "w") as fh:
        json.dump(out, fh)
    summary = {k: v for k, v in out.items() if k != "branched_supports"}
    print(json.dumps(summary, indent=1))
    return 0 if complete else 2


if __name__ == "__main__":
    sys.exit(main())
