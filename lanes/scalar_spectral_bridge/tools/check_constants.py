#!/usr/bin/env python3
"""Independent exact arithmetic audit, not an analytic proof checker."""
from fractions import Fraction as F
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def fraction(s):
    if not isinstance(s,str) or str(F(s))!=s:raise ValueError('Expected canonical fraction.')
    return F(s)


def audit(data):
    try:
        if data['schema_version']!='ym3d.scalar_spectral_bridge.v1' or data['analytic_gate_closed'] is not False:
            raise ValueError('Invalid scope/closure flag.')
        if data['time_boundary']!='infinite_time_ground_state' or data['scope']!='spectral measure and cyclic transfer subspace of this operator only':
            raise ValueError('Invalid temporal or sector scope.')
        if data['operator']!='sum_z(P_z-mean_P)/L; P=1-Tr(U_xy)/2':raise ValueError('Invalid volume normalization.')
        required=['compact finite-range Wilson specification with normalized Haar measure',
                  'Dobrushin comparison bound and support-distance estimate',
                  'positive self-adjoint physical transfer representation',
                  'infinite-time state equals the transfer ground-state state']
        if data['required_hypotheses']!=required:raise ValueError('Missing analytic hypotheses.')
        rows=data['cases']
        if len(rows)!=2:raise ValueError('Invalid case schedule.')
        for row,beta in zip(rows,(F(1,40),F(1,20))):
            a=12*beta
            if fraction(row['wilson_beta'])!=beta or fraction(row['influence_row_sum_upper'])!=a or fraction(row['channel_transfer_radius_upper'])!=a:
                raise ValueError('Incorrect coupling/influence/radius.')
            # Independently recover the polynomial by finite differences of shell sums.
            def bracket(t):return (2*t+3)**2+8*a*((t+2)/(1-a)+a/(1-a)**2)
            c0=bracket(0);c2=(bracket(2)-2*bracket(1)+bracket(0))/2;c1=bracket(1)-c0-c2
            if list(map(fraction,row['spatial_polynomial_low_to_high']))!=[c0,c1,c2] or fraction(row['covariance_prefactor'])!=16/(1-a):
                raise ValueError('Incorrect shell-sum constants.')
            # Different logarithm expansion: -log(a)=sum_(k>=1)(1-a)^k/k.
            h=1-a;lo=sum((h**k/k for k in range(1,513)),F(0))
            hi=lo+h**513/(513*a)
            left,right=map(fraction,row['dimensionless_energy_lower_endpoint_interval'])
            if not 0<left<=lo<=hi<=right or right-left>F(1,2**90):
                raise ValueError('Logarithm enclosure failed independent series audit.')
        return True,{'cases':2,'arithmetic':'integers and Fraction only','analytic_gate_closed':False}
    except (KeyError,TypeError,ValueError,ZeroDivisionError) as exc:return False,{'reason':str(exc)}


def main():
    passed,report=audit(json.loads((ROOT/'artifacts'/'constants.json').read_text()))
    result={'status':'EXACT_CONSTANT_AUDIT_PASSED' if passed else 'FAIL','analytic_gate_closed':False,
            'report':report,'non_claims':['Does not machine-certify the comparison or transfer construction',
                                       'Does not identify a glueball pole or establish an all-sector/continuum gap']}
    (ROOT/'artifacts'/'constant_audit.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status']);return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
