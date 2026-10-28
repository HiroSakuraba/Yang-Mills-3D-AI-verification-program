#!/usr/bin/env python3
"""Kotecky-Preiss test for the strong-coupling polymer gas of 3D SU(2) lattice gauge theory.

Polymers: surviving supports X in Z^3 (link-connected, every link in 0 or >= 2
faces of X); activity w(X) = int prod_{p in X} f(U_p) dU, f = sum_{a>=1} r_a chi_a
(all labellings summed); incompatible = share a link.  A link of Z^3 lies in 4
plaquettes and a polymer through it contains >= 2 of them, so the polymers
through a link have total weight <= 2 R(c); a polymer has <= 2F links.  With
a(X) = c F(X) the KP condition therefore holds if

    4 R(c) <= c,      R(c) = sum_{X contains root} |w(X)| e^{c F(X)}.

Bound on R(c), all parts with interval arithmetic (mpmath.iv):

  two-face supports, every constant label a:  |w| = d_a^chi t_a^F exactly
      (TWO_FACE Lemma B for all a), exact counts by (F, chi) for F <= F2
      (3D generator run, checked), Lemma A beyond: N(F) <= 3^{F-1}, |w| <= d_a^2 t_a^F.
  branched supports with F <= Fb: exhaustive list (3D branched run, checked);
      each bounded by Finner's inequality prod_p N_{q_p}, q_p in {2, 4}.
  every support with F > Fb: the smaller of two bounds,
    (a) Finner with q = 4 on every face and Lemma D for all supports (z1 = 0.13967), and
    (b) Finner with the face weights
      prod_p N_{q_p} <= N_2^F rho^{sum over branched links of k_e},  rho = N_4/N_2,
      and the potential lemma (analysis/entropy.py) with bump costs rho^3 when a
      link count goes 2 -> 3 and rho when it goes 3 -> 4:
        sum_X rho^{...} z^{F-1} <= R1^4   whenever g_c(z R^3) <= h(c), c = 1..4,
      h(1) = R, h(2) = R^2, h(3) = R^3 / rho^3, h(4) = R^4 / rho^4.
      Then sum_{F > Fb} <= z0 (z0/z1)^Fb R1^4 with z0 = N_2 e^c.

N_q (q even) from the positive series int f^q = sum prod r_{a_i} dim Inv, with a
rigorous tail.  Usage: kp_3d.py two_face.json branched.json
"""
import json
import sys
from fractions import Fraction
from math import comb

from mpmath import iv, mp, mpf

mp.dps = 30
iv.dps = 30
J = 8
STAR = 4
Z1_ALL = Fraction(13967, 100000)   # Lemma D, all supports in Z^3: z >= 0.1396785 (entropy_3d.json)
R4_ALL = iv.mpf("3.0795")          # its prefactor R^4 <= 3.07943
Z_EVENCAT = Fraction(21653, 100000)  # Lemma D, even supports, Catalan weights: z >= 0.2165348


def r_heat(tau, a):
    tv = iv.mpf(tau) if not isinstance(tau, Fraction) else iv.mpf(tau.numerator) / tau.denominator
    return iv.mpf(a + 1) * iv.exp(-tv * a * (a + 2) / 8)


def iv_besseli(n, x, K=60):
    """Rigorous enclosure of I_n(x), x >= 0 an interval: positive power series
    sum_k (x/2)^{2k+n} / (k! (k+n)!), truncated after K terms, with the tail bounded
    by a geometric series (term ratio <= (x/2)^2 / ((K+1)(K+1+n)) < 1/2 for x <= 20)."""
    h = x / 2
    s = iv.mpf(0)
    fk, fkn = iv.mpf(1), iv.mpf(1)
    for j in range(1, n + 1):
        fkn = fkn * j
    term = None
    for k in range(K + 1):
        if k > 0:
            fk = fk * k
            fkn = fkn * (k + n)
        term = h ** (2 * k + n) / (fk * fkn)
        s = s + term
    ratio = h ** 2 / ((K + 1) * (K + 1 + n))
    assert ratio.b < 0.5
    s = s + iv.mpf([0, (term * ratio / (1 - ratio)).b])
    return s


def r_wilson(x, a):
    """Wilson character ratio r_a = (a+1) I_{a+1}(x) / I_1(x) for e^{x tr U}, tr = Tr/2."""
    xv = iv.mpf(x) if not isinstance(x, Fraction) else iv.mpf(x.numerator) / x.denominator
    return (a + 1) * iv_besseli(a + 1, xv) / iv_besseli(1, xv)


def norm_even(r, q):
    dist = {0: iv.mpf(1)}
    for _ in range(q):
        new = {}
        for c, m in dist.items():
            for a in range(1, J + 1):
                for d in range(abs(c - a), c + a + 1, 2):
                    new[d] = new.get(d, iv.mpf(0)) + m * r[a]
        dist = new
    s = dist.get(0, iv.mpf(0))
    big = sum((r[a] * (a + 1) for a in range(1, J + 1)), iv.mpf(0))
    tail_a = r[J + 1] * (J + 2) * 2
    s = s + q * tail_a * (big + tail_a) ** (q - 1)
    return s ** (iv.mpf(1) / q)


def setup(kind, par):
    rr = {a: (r_heat(par, a) if kind == "heat" else r_wilson(par, a)) for a in range(1, J + 2)}
    assert (rr[J + 1] * (J + 2)).b < 0.5 * (rr[J] * (J + 1)).a
    N = {q: norm_even(rr, q) for q in (2, 4)}
    t = {a: rr[a] / (a + 1) for a in range(1, J + 2)}
    return rr, t, N


# ------------------------------------------------------------ potential lemma with Finner bumps
def g_list(w, rho):
    out = []
    for c in range(1, STAR + 1):
        avail = STAR - c
        s = 0
        for j in range(0, avail + 1):
            k = c + j
            if k < 2:
                continue
            bump = 1
            for cc in range(c, k):  # bumps cc -> cc+1 at the decided link
                if cc == 2:
                    bump = bump * rho ** 3
                elif cc >= 3:
                    bump = bump * rho
            s = s + comb(avail, j) * w ** j * bump
        out.append(s)
    return out


def h_scale(c, rho):
    """h(c) / R^c."""
    return 1 if c <= 2 else rho ** (-(3 + (c - 3)))


def need_R(w, rho):
    R = 1
    for c, g in enumerate(g_list(w, rho), start=1):
        R = max(R, (g / h_scale(c, rho)) ** (1.0 / c))
    return R


def lemma_d_finner(rho_iv):
    """Certified (z1 lower, R1^4 upper) for the bump cost rho (interval)."""
    rho_f = float(rho_iv.b)
    best = None
    for i in range(1, 3000):
        w = i / 5000
        R = need_R(w, rho_f)
        z = w / R ** 3
        if best is None or z > best[0]:
            best = (z, Fraction(i, 5000))
    w = best[1]
    wv = iv.mpf(w.numerator) / w.denominator
    rho_up = iv.mpf(rho_iv.b)  # costs are increasing in rho: use the upper end
    R = iv.mpf(1)
    for c, g in enumerate(g_list(wv, rho_up), start=1):
        root = (g / h_scale(c, rho_up)) ** (iv.mpf(1) / c)
        R = iv.mpf([max(R.a, root.a), max(R.b, root.b)])
    # the R-ratios for the other links of a new face: h(c+1)/h(c) times the bump cost
    # equals R exactly by construction of h (cost 1, 1, rho^3, rho at c = 0, 1, 2, 3)
    z = wv / R ** 3
    return z.a, (R ** 4).b


# ------------------------------------------------------------ data
def load_two_face(path):
    d = json.load(open(path))
    assert d["complete"]
    return d["fmax_requested"], {int(F): {int(k): v for k, v in x["by_chi"].items()}
                                 for F, x in d["per_F"].items()}


def load_branched(path):
    d = json.load(open(path))
    assert d["complete"]
    cls = {}
    for F, x in d["per_F"].items():
        for key, n in x["finner_classes"].items():
            q = tuple(int(v) for v in key.split(","))
            assert q[2] == 0
            cls[(int(F), q[0], q[1])] = n
    return d["fmax_requested"], cls


def R_parts(c, t, N, two, br, lem, tail_mode="min"):
    ec = iv.exp(c)
    fmax2, by = two
    Fb, cls = br
    labs = [a for a in t if a <= J]
    s = iv.mpf(0)
    for F, chis in by.items():
        for chi, n in chis.items():
            for a in labs:
                s += n * iv.mpf(a + 1) ** chi * (t[a] * ec) ** F
    tail = iv.mpf(0)
    for a in labs:
        q = 3 * t[a] * ec
        if q.b >= 1:
            return None
        tail += iv.mpf(a + 1) ** 2 / 3 * q ** (fmax2 + 1) / (1 - q)
    qJ = 3 * t[J + 1] * ec
    tail += 2 * iv.mpf(J + 2) ** 2 * qJ ** 6 / (3 * (1 - qJ))
    b = iv.mpf(0)
    for (F, n2, n4), n in cls.items():
        b += n * (N[2] * ec) ** n2 * (N[4] * ec) ** n4
    # two valid tail bounds; use the smaller.
    # (a) plain Lemma D (class "all", out/entropy_3d.json) with Finner q = 4 on every face
    tails = []
    z0p = N[4] * ec
    z1p = iv.mpf(Z1_ALL.numerator) / Z1_ALL.denominator
    if z0p.b < z1p.a:
        tails.append(z0p * (z0p / z1p) ** Fb * R4_ALL)
    # (b) Lemma D with Finner bump costs (q_p = 2 away from branched links)
    z1, R14 = lem
    z0 = N[2] * ec
    if tail_mode == "min" and z0.b < z1:
        tails.append(z0 * (z0 / z1) ** Fb * R14)
    if not tails:
        return None
    allt = tails[0] if len(tails) == 1 else (tails[0] if tails[0].b <= tails[1].b else tails[1])
    return {"two_face_head": s, "two_face_tail": tail, "branched_head": b, "all_tail": allt,
            "total": s + tail + b + allt}


def best(kind, par, two, br, tail_mode="min"):
    """tail_mode "plain" uses only bound (a), which is monotone in the character ratios."""
    rr, t, N = setup(kind, par)
    rho = N[4] / N[2]
    lem = lemma_d_finner(rho)
    out = None
    for k in range(1, 600):
        c = iv.mpf(k) / 1000
        P = R_parts(c, t, N, two, br, lem, tail_mode)
        if P is None:
            break
        m = c - 4 * P["total"]
        if out is None or m.a > out[0].a:
            out = (m, c, P)
    return out, t, N, lem


def two_face_only_ok(kind, par, two):
    """KP for the gas of closed two-face surfaces alone (all labels): 4 R2(c) <= c."""
    rr, t, N = setup(kind, par)
    for k in range(1, 600):
        c = iv.mpf(k) / 1000
        ec = iv.exp(c)
        fmax2, by = two
        s = iv.mpf(0)
        ok = True
        for F, chis in by.items():
            for chi, n in chis.items():
                for a in range(1, J + 1):
                    s += n * iv.mpf(a + 1) ** chi * (t[a] * ec) ** F
        for a in range(1, J + 1):
            q = 3 * t[a] * ec
            if q.b >= 1:
                ok = False
                break
            s += iv.mpf(a + 1) ** 2 / 3 * q ** (fmax2 + 1) / (1 - q)
        if not ok:
            return False
        qJ = 3 * t[J + 1] * ec
        s += 2 * iv.mpf(J + 2) ** 2 * qJ ** 6 / (3 * (1 - qJ))
        if (c - 4 * s).a > 0:
            return True
    return False


def bisect(pred, lo, hi, increasing_ok):
    for _ in range(36):
        mid = (lo + hi) / 2
        if pred(mid) == increasing_ok:
            hi = mid
        else:
            lo = mid
    return lo, hi


def main():
    two = load_two_face(sys.argv[1])
    br = load_branched(sys.argv[2])
    res = {"two_face_fmax": two[0], "branched_fmax": br[0]}
    for kind, pars in (("heat", (3, 4, 5, 6, 7, 8)), ("wilson", (0.1, 0.2, 0.3, 0.4, 0.5))):
        for par in pars:
            b, t, N, lem = best(kind, par, two, br)
            row = {"t1": float(t[1].a), "N2": float(N[2].b), "N4": float(N[4].b),
                   "rho": float((N[4] / N[2]).b), "lemmaD_z1": float(lem[0]), "lemmaD_R4": float(lem[1])}
            if b is None:
                row["kp_holds"] = False
                row["note"] = "tail not summable at any c > 0 (N_2 >= z1)"
            else:
                m, c, P = b
                row.update({"kp_holds": bool(m.a > 0), "margin_lower": float(m.a), "c": float(c.a)})
                row.update({k: float(v.b) for k, v in P.items()})
            res["%s_%s" % (kind, par)] = row

    def ok(kind, par):
        b = best(kind, par, two, br)[0]
        return b is not None and b[0].a > 0
    lo, hi = bisect(lambda tau: ok("heat", tau), 2.0, 20.0, True)
    res["whole_gas_kp_heat_tau_min_upper"] = hi
    lo, hi = bisect(lambda x: not ok("wilson", x), 0.005, 1.5, True)
    res["whole_gas_kp_wilson_beta_max_lower"] = lo
    # diagnostic (not a KP statement): all-fundamental branched sector summable when
    # t_1 4^{1/6} < z (Theorem C with Lemma D for even supports, Catalan weights)
    zE = iv.mpf(Z_EVENCAT.numerator) / Z_EVENCAT.denominator
    fund = lambda kind, par: (setup(kind, par)[1][1] * iv.mpf(4) ** (iv.mpf(1) / 6)).b < zE.a
    res["fundamental_branched_summable_heat_tau_gt"] = bisect(lambda tau: fund("heat", tau), 2.0, 20.0, True)[1]
    res["fundamental_branched_summable_wilson_beta_lt"] = bisect(lambda x: not fund("wilson", x), 0.005, 3.0, True)[0]
    lo, hi = bisect(lambda tau: two_face_only_ok("heat", tau, two), 2.0, 20.0, True)
    res["two_face_gas_kp_heat_tau_min_upper"] = hi
    lo, hi = bisect(lambda x: not two_face_only_ok("wilson", x, two), 0.005, 3.0, True)
    res["two_face_gas_kp_wilson_beta_max_lower"] = lo
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
