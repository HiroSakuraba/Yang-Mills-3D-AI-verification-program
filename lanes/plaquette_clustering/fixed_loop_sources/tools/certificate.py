#!/usr/bin/env python3
"""Exact rational SU(2) single-link influence and fixed Wilson-loop certificate.

This audits algebraic constants; the Haar/S^3 moment and Dobrushin--Follmer
covariance inequality are analytic statements requiring independent review.
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction as Q
from pathlib import Path

BETA_MAX = Q(3, 25)  # 0.12, independently of plaquette-KP domain
LINK_NEIGHBORS = 12
STAPLES = 4
S3_SECOND_MOMENT = Q(1, 4)

def fraction(x: Q) -> str:
    return f'{x.numerator}/{x.denominator}'

def certify(beta: Q = BETA_MAX, *, neighbor_cap: int = LINK_NEIGHBORS,
            staples: int = STAPLES, s3_moment: Q = S3_SECOND_MOMENT) -> dict:
    if beta < 0 or beta >= Q(1,2):
        raise ValueError('requires 0 <= beta < 1/2')
    if neighbor_cap < 0 or staples < 1 or s3_moment <= 0:
        raise ValueError('invalid geometric or moment inputs')
    # Haar SU(2)=uniform S^3. For ||v||<=2 and ||s_t||<=staples,
    # Var_{pi_t}(u.v)<=E_{pi_t}[(u.v)^2]<=exp(staples*beta)*||v||^2/4.
    # Derivative TV<= beta/2 * sqrt(Var)<= beta*exp(staples*beta/2)/2,
    # for 4 staples and s3_moment=1/4.
    # Conservative rational exp(2beta) <= 1/(1-2beta).
    if staples != 4 or s3_moment != Q(1,4):
        # This theorem uses exactly four staples and 1/4 Haar second moment.
        return {'pass': False, 'reason':'SU(2) 3D hypotheses not met'}
    influence = beta / (2 * (1 - 2*beta))
    alpha = neighbor_cap * influence
    passed = alpha < 1
    return {
        'pass': passed,
        'beta_max': fraction(beta),
        'max_neighbor_links': neighbor_cap,
        'incident_faces_per_link': staples,
        'haar_s3_variance_per_coordinate':fraction(s3_moment),
        'single_link_TV_influence_cap':fraction(influence),
        'dobrushin_row_sum_cap':fraction(alpha),
        'decay_base':fraction(alpha) if passed else None,
        'wilson_covariance_prefactor_per_support_pair':fraction(4/(1-alpha)) if passed else None,
        'source_comparison':'Cov(W_C,W_D) = d_s d_t log Z(s,t)|_{s=t=0}',
        'covariance_formula':'|Cov(W_C,W_D)| <= [4/(1-alpha)]*|support C|*|support D|*alpha**distance_link(C,D)',
        'hypotheses':'nondegenerate finite periodic cubic SU(2) Wilson theory; normalized fundamental Wilson characters; arbitrary closed finite contours',
        'scope':'finite-volume, volume-uniform at fixed lattice spacing; independent of all-support KP enumeration',
        'not_claimed':['convergent source-marked polymer gas at beta 0.12', 'RG localization after blocking', 'continuum mass gap']
    }

def run(output: Path | None = None) -> dict:
    cap = certify()
    assert cap['pass'] and cap['dobrushin_row_sum_cap']=='18/19'
    assert cap['wilson_covariance_prefactor_per_support_pair']=='76/1'
    assert not certify(Q(1,8))['pass'], 'endpoint must fail strictly'
    assert not certify(BETA_MAX, neighbor_cap=13)['pass'], 'geometry regression control'
    if output:
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(cap,sort_keys=True,indent=2)+'\n')
    return cap

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1]/'artifacts'/'certificate.json')
    args=a.parse_args()
    x=run(args.output)
    print('PASS', x['dobrushin_row_sum_cap'],x['wilson_covariance_prefactor_per_support_pair'])
