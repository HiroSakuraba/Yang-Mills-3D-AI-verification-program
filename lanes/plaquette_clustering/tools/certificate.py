#!/usr/bin/env python3
"""Exact-rational preflight for a conservative 3D SU(2) two-plaquette
connected-correlation bound.  Does NOT depend on the unverified branched data.

The associated theorem.md supplies the analytic lemmas.  This program audits
all nontrivial scalar inequalities; it does not machine-prove those lemmas.
"""
from __future__ import annotations

import json
from fractions import Fraction as Q
from pathlib import Path

BETA = Q(3, 200)          # 0.015
ETA = Q(1, 500)           # complex source radius, 0.002
A = Q(3, 10)              # KP size cost per face
DECAY = Q(1, 10)          # geometric distance cost
DEGREE = 12               # plaquette link-sharing graph, Z^3
TREE_BOUND = 4 * DEGREE  # plane-tree spanning-tree overcount
NORM4_UPPER = Q(3, 5)     # (int_Haar (Tr U/2)^4)^(1/4) < 3/5
EXP_UPPER = Q(3, 2)      # exp(A+DECAY)=exp(2/5) < 3/2


def rational_string(x: Q) -> str:
    return f"{x.numerator}/{x.denominator}"


def compute(beta: Q = BETA, eta: Q = ETA, a: Q = A, decay: Q = DECAY,
            norm4_upper: Q = NORM4_UPPER, exp_upper: Q = EXP_UPPER) -> dict:
    assert beta >= 0 and eta > 0 and decay > 0 and a > 0
    t = beta + eta
    assert t < 1
    # z(w)=int exp(w phi) dU, int phi=0, |phi|<=1; |z(w)-1|<=D.
    D = t*t / (2*(1-t))
    assert D < 1
    B = ((t / (1-t)) * norm4_upper + D) / (1-D)
    M = B * exp_upper
    ratio = TREE_BOUND * M
    assert ratio < 1, 'elementary animal series does not converge'
    # Every rooted connected face set is overcounted by (4*12)^(F-1).
    # A nonzero polymer has F>=5: each of the root face's four edges needs
    # another face; two distinct elementary plaquettes share at most one edge.
    # Thus the geometric series begins with F=5, without using F>=6.
    R = M * ratio**4 / (1-ratio)
    margin = a - 4*R
    return {
        'pass': margin > 0,
        'beta_max': rational_string(beta),
        'source_radius': rational_string(eta),
        'kp_cost_a': rational_string(a),
        'distance_decay': rational_string(decay),
        'animal_growth_cap': TREE_BOUND,
        'minimal_nonzero_support_faces_used': 5,
        'norm4_upper': rational_string(norm4_upper),
        'exp_upper': rational_string(exp_upper),
        'max_complex_coupling_abs': rational_string(t),
        'normalization_error_upper': rational_string(D),
        'f_L4_upper': rational_string(B),
        'weighted_face_activity_upper': rational_string(M),
        'animal_ratio_upper': rational_string(ratio),
        'root_sum_upper': rational_string(R),
        'kp_margin_lower': rational_string(margin),
        'connected_covariance_prefactor': rational_string(R / eta**2),
        'covariance_formula': 'abs(Cov(phi_p, phi_q)) <= (R/eta^2)*exp(-distance(p,q)/10)',
        'prerequisites': [
            'compact SU(2) Haar moment int phi=0, int phi^4=1/8',
            '3D link-sharing graph degree at most 12',
            'spanning-tree plane-tree enumeration',
            'Finner hypergraph Holder and KP rooted-cluster theorem',
            'periodic cubic boxes with no degenerate plaquettes'
        ],
        'scope': 'distinct elementary plaquettes; finite volume; 0<=beta<=3/200',
        'not_claimed': ['RG passage', 'lattice-spacing uniform physical mass',
                        'continuum mass gap', 'large Wilson loops']
    }


def check_exp_bound() -> bool:
    # exp(x) <= 1+x+x²/2 + x³/(6(1-x/4)) for 0<=x<4,
    # since n! >= 6*4^(n-3) for n>=3.
    x = A+DECAY
    cap = 1 + x + x*x/2 + x**3/(6*(1-x/4))
    return x < 1 and cap < EXP_UPPER


def run(output: Path | None = None) -> dict:
    assert NORM4_UPPER**4 > Q(1, 8), 'claimed Haar fourth-root upper bound invalid'
    assert check_exp_bound(), 'exponential majorant invalid'
    result = compute()
    if not result['pass']:
        raise ArithmeticError('KP threshold failed; no result may be registered')
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1]/'artifacts'/'certificate.json')
    args = parser.parse_args()
    r=run(args.output)
    print('PASS', 'R=', r['root_sum_upper'], '4R margin=', r['kp_margin_lower'])
