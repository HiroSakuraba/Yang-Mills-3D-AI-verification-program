#!/usr/bin/env python3
"""Proved entropy constants for surviving supports in Z^3 (Lemma D, three-dimensional form).

Potential method on the decision encoding (see generator/supports.py).  A state
has undecided touched links with counts c >= 1; give such a link the weight
h(c), and h(0) = 1.  For the Catalan-weighted version also give a factor phi
each time a face raises a link count from c >= 2 to c + 1 (phi^2 >= 2 and
phi^4 >= 5 in 4D; in 3D only k <= 4 occurs, so phi^2 >= 2 suffices).

Deciding a link with count c by adding a set J of new faces multiplies the
potential by 1/h(c) times, for each new face, the ratios h(c'+1)/h(c') (times
phi if c' >= 2) at its three other links -- each of those links is raised by
exactly one face of J, because two plaquettes share at most one link.  With
R = max over c' of those ratios this is at most R^{3|J|}/h(c).  So if

    g_c(w) := sum over admissible J of w^{|J|} (phi-factors at the decided link) <= h(c)
    for every c, with w = z R^3,

then by induction over the decision tree  sum_{X contains root} weight(X) z^{F(X)-1} <= h(1)^4.

The best choice is h(c) = R^c (times phi^{-(c-2)} for c > 2 in the weighted
case), which turns the conditions into g_c(w) <= R^c (resp. R^c / phi^{c-2}).
We maximise z = w / R^3 over w on a grid and certify the chosen rational w with
interval arithmetic.  rate = 1/z.

Classes:
  two_face : every link in exactly 0 or 2 faces (recovers Lemma A, rate 5)
  all      : every link in 0 or >= 2 faces
  even     : every link in 0, 2, 4 or 6 faces (the supports that admit an
             all-fundamental labelling)
  even_cat : even supports weighted by prod_e Catalan(k_e/2), phi = 1.4143 (3D: k <= 4)
"""
import json
from fractions import Fraction
from math import comb

from mpmath import iv, mp, mpf

mp.dps = 30
iv.dps = 30


DIM = 3
STAR = 2 * (DIM - 1)  # plaquettes on a link: 4 in three dimensions


def g_list(cls, w, phi):
    """Return the list of g_c(w), c = 1..STAR, for the class."""
    out = []
    for c in range(1, STAR + 1):
        avail = STAR - c
        s = 0
        for j in range(0, avail + 1):
            k = c + j
            if k < 2:
                continue
            if cls == "two_face" and k != 2:
                continue
            if cls in ("even", "even_cat") and k % 2:
                continue
            term = comb(avail, j) * w ** j
            if cls == "even_cat":
                bumps = max(0, k - max(c, 2))
                term = term * phi ** bumps
            s = s + term
        if cls == "two_face" and c > 2:
            continue
        out.append(s)
    return out


def need_R(cls, gs, phi):
    """Smallest R with g_c <= R^c (or R^c / phi^(c-2) for c > 2 in the weighted class)."""
    R = 1
    for c, g in enumerate(gs, start=1):
        if cls == "even_cat" and c > 2:
            g = g * phi ** (c - 2)
        R = max(R, g ** (1.0 / c))
    return R


def z_of(cls, w, phi):
    gs = g_list(cls, w, phi)
    R = need_R(cls, gs, phi)
    return w / R ** 3, R


def optimise(cls, phi):
    best = None
    for i in range(1, 4000):
        w = Fraction(i, 10000)
        z, R = z_of(cls, float(w), float(phi))
        if best is None or z > best[0]:
            best = (z, w)
    return best[1]


def certify_intervals(cls, w, phi_iv):
    """Return actual interval enclosures for gate checks; never round to floats."""
    wv = iv.mpf(w.numerator) / w.denominator
    gs = g_list(cls, wv, phi_iv)
    R = iv.mpf(1)
    for c, g in enumerate(gs, start=1):
        if cls == "even_cat" and c > 2:
            g = g * phi_iv ** (c - 2)
        root = g ** (iv.mpf(1) / c)
        R = iv.mpf([max(R.a, root.a), max(R.b, root.b)])
    return {"R": R, "z": wv / R ** 3}


def certify(cls, w, phi_iv):
    """Human-readable diagnostics only; rounded floats are not gate inputs."""
    ivals = certify_intervals(cls, w, phi_iv)
    R, z = ivals["R"], ivals["z"]
    return {"w": str(w), "R_upper": float(R.b), "z_lower": float(z.a),
            "rate_upper": float((1 / z).b), "prefactor_h1_4_upper": float((R ** 4).b)}


def main():
    # weights Catalan(k/2) for k = 2, 4 only in 3D: need PHI^2 >= 2
    PHI = Fraction(14143, 10000)
    assert PHI ** 2 >= 2
    phi = mpf(PHI.numerator) / PHI.denominator
    phi_iv = iv.mpf(PHI.numerator) / PHI.denominator
    out = {}
    for cls in ("two_face", "all", "even", "even_cat"):
        w = optimise(cls, phi)
        out[cls] = certify(cls, w, phi_iv)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
