#!/usr/bin/env python3
"""Sufficient SU(2) Wilson-loop covariance bound via link Dobrushin uniqueness.

All numerical comparisons use fractions and an upper bound for exp(4 beta).
The Follmer/Dobrushin covariance inequality is an external analytic theorem;
no simulation or floating point test is substituted for it.
"""
from fractions import Fraction as Q
from pathlib import Path
import json


def check(beta: Q = Q(3,200)) -> dict:
    assert beta >= 0
    u=4*beta
    assert u < 1, 'not in the elementary e^x <= 1/(1-x) regime'
    # At a link there are 4 incident plaquettes, with three other links each.
    # For a changed neighboring link the conditional RN ratio lies in
    # [e^(-4beta), e^(4beta)], hence TV <= e^(4beta)-1 <=u/(1-u).
    link_degree = 12
    influence = u/(1-u)
    alpha=link_degree*influence
    return {
      'pass': alpha < 1,
      'beta_max':str(beta),
      'link_degree':link_degree,
      'individual_tv_influence_upper':str(influence),
      'dobrushin_alpha_upper':str(alpha),
      'one_over_one_minus_alpha': str(1/(1-alpha)) if alpha<1 else None,
      'wilson_prefactor_per_link_pair':str(4/(1-alpha)) if alpha<1 else None,
      'wilson_covariance_bound':
        '|Cov(W_C,W_D)| <= 4*len(C)*len(D)*alpha**dist_link(C,D)/(1-alpha)',
      'scope':'SU(2); distinct closed contours; any finite nondegenerate 3D cubic torus; 0<=beta<=3/200',
      'references':[
          'Follmer, A Covariance Estimate for Gibbs Measures, JFA 46 (1982) 387-395',
          'Kunsch, Decay of Correlations under Dobrushin Uniqueness, CMP 84 (1982) 207-222'],
      'not_claimed': ['four-dimensional theorem', 'continuum mass gap','uniform physical-distance rate as a->0']
    }


def run(path: Path | None=None):
    v=check()
    assert v['pass'], 'Dobrushin condition did not hold'
    if path:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    return v


if __name__=='__main__':
    r=run(Path(__file__).resolve().parents[1]/'artifacts'/'dobrushin.json')
    print('PASS alpha <=',r['dobrushin_alpha_upper'], 'prefactor per link pair:',r['wilson_prefactor_per_link_pair'])
