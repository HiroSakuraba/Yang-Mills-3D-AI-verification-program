#!/usr/bin/env python3
"""Reproducible, exact-rational, enumeration-independent KP animal majorant.

This program checks rational inequalities only, not the proofs of the
potential induction, Finner, KP, or the rooted cluster theorem.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as Q
from pathlib import Path

BETA = Q(9, 100)                 # 0.09
ETA = Q(1, 500)                 # 0.002, two local complex sources
KP_A = Q(1, 5)                  # KP cost per face
DECAY = Q(1, 10)                # exponential factor for graph distance
EXP_UPPER = Q(27, 20)           # strictly exceeds exp(3/10)
HAAR_L4_UPPER = Q(3, 5)         # (int cos(theta)^4 dH)^1/4 < 3/5
WITNESS_W = Q(3247, 10000)     # z H^3 in the decision induction
WITNESS_H = Q(13247, 10000)     # potential h(c) = H^c


def s(x: Q) -> str:
    return f'{x.numerator}/{x.denominator}'


def exponential_upper(x: Q) -> Q:
    """Rational majorant of exp(x) for 0<=x<4 (factorial tail)."""
    if not 0 <= x < 4:
        raise ValueError('exponential upper bound outside domain')
    # n! >= 6*4^(n-3) for n>=3
    return 1 + x + x*x/2 + x*x*x/(6*(1-x/4))


def branching_polynomials(w: Q) -> dict[int, Q]:
    """3D: each undecided link can carry 1..4 already chosen faces.

    At a link with c chosen faces, select j of the 4-c available faces,
    with c+j>=2. Each new face uses three other links.
    """
    return {
        1: (1+w)**3-1,
        2: (1+w)**2,
        3: 1+w,
        4: Q(1),
    }


def potential_certificate(w: Q = WITNESS_W, H: Q = WITNESS_H) -> dict:
    if w <= 0 or H < 1:
        raise ValueError('invalid potential witness')
    g = branching_polynomials(w)
    checks = {c: g[c] <= H**c for c in range(1, 5)}
    if not all(checks.values()):
        raise ArithmeticError('some branching polynomials exceed potential')
    z = w / H**3
    return {
        'w': s(w), 'H': s(H),
        'admissible_growth_z': s(z),
        'prefactor_H_to_fourth': s(H**4),
        'branching_g': {str(k): s(v) for k,v in g.items()},
        'branching_slack': {str(c): s(H**c-g[c]) for c in range(1,5)},
        'pass': all(checks.values()),
    }


def check(beta: Q = BETA, eta: Q = ETA, kp_a: Q = KP_A,
          decay: Q = DECAY, exp_upper: Q = EXP_UPPER,
          haar_l4_upper: Q = HAAR_L4_UPPER,
          w: Q = WITNESS_W, H: Q = WITNESS_H) -> dict:
    if not(0<=beta and eta>0 and kp_a>0 and decay>0):
        raise ValueError('invalid source/cost parameters')
    if haar_l4_upper**4 <= Q(1,8):
        raise ArithmeticError('claimed Haar fourth-moment upper bound invalid')
    u = kp_a+decay
    if not exponential_upper(u)<exp_upper:
        raise ArithmeticError('strict exponential upper bound not certified')
    witness=potential_certificate(w,H)
    z = w / H**3
    t=beta+eta
    if t>=1:
        raise ValueError('complex-coupling disk must satisfy t<1')
    # z_face(w)=int exp(w*phi)dH; first Haar moment vanishes.
    D=t*t/(2*(1-t))
    if D>=1:
        raise ArithmeticError('normalization nonvanishing not certified')
    B=((t/(1-t))*haar_l4_upper+D)/(1-D)
    M=B*exp_upper
    if M>=z:
        raise ArithmeticError('rooted support generating series cannot be evaluated')
    # F>=5 for a surviving support through a root face.
    # Sum z^(F-1) over all supports <=H^4; extract 4 factors of M/z.
    R=M*(M/z)**4*H**4
    margin=kp_a-4*R
    if margin<=0:
        raise ArithmeticError('weighted KP sum fails')
    return {
        'pass':True,
        'claim_strength':'arithmetically_certified_analytic_argument_for_review',
        'beta_max':s(beta),'source_radius':s(eta),
        'kp_a':s(kp_a),'decay':s(decay),
        'haarl4_upper':s(haar_l4_upper),
        'exp_upper':s(exp_upper),
        'exp_taylor_cap':s(exponential_upper(u)),
        'max_complex_face_coupling':s(t),
        'face_normalization_error':s(D),
        'normalized_face_L4':s(B),
        'M_weighted_face':s(M),
        'M_over_z':s(M/z),
        'R_root_upper':s(R),
        'four_R_upper':s(4*R),
        'kp_margin_lower':s(margin),
        'plaquette_covariance_prefactor':s(R/eta**2),
        'covariance_formula':'|Cov(phi_p,phi_q)| <= (R/eta^2)*exp[-decay*d_plaq(p,q)]',
        'witness':witness,
        'verified_without':'historical enumerated supports or branched Haar checker',
        'not_proved_by_script':['Haar integration and Finner inequality',
            'potential counting lemma for link-connected supports',
            'KP rooted-cluster theorem and Cauchy derivative step'],
        'scope':'distinct plaquettes; periodic cubic side >=4; fixed lattice spacing',
    }


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts'/'entropy_certificate.json')
    args=parser.parse_args()
    result=check()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS beta<=',result['beta_max'],'4R=',result['four_R_upper'],
          'KP margin=',result['kp_margin_lower'])


if __name__=='__main__':
    main()
