#!/usr/bin/env python3
"""Independent Haar-moment/polynomial audit; no analytic gate decision."""
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def rational(s):
    if not isinstance(s,str) or str(F(s))!=s:raise ValueError('Noncanonical rational.')
    return F(s)


def poly_product(a,b):
    out={}
    for x,c in a.items():
        for y,d in b.items():
            key=tuple(sorted(x+y));out[key]=out.get(key,F(0))+c*d
    return out


def univariate_product(a,b):
    out={}
    for i,c in a.items():
        for j,d in b.items():out[i+j]=out.get(i+j,F(0))+c*d
    return out


def audit(data):
    try:
        if data['schema_version']!='ym3d.su2_link_decimation.v1' or data['analytic_gate_closed'] is not False or data['rg_contraction_established'] is not False:
            raise ValueError('Invalid closure/contraction scope.')
        if data['pair_variable']!='c_ij=Tr(S_i*S_j^dagger)/2':raise ValueError('Pair-loop normalization changed.')
        if len(data['cases'])!=2:raise ValueError('Incomplete case schedule.')
        count=0
        for row,m,maximum in zip(data['cases'],(2,4),(F(1,4),F(1,8))):
            if type(row['staple_count']) is not int or row['staple_count']!=m or rational(row['beta_max'])!=maximum:
                raise ValueError('Wrong staple count or coupling window.')
            if row['normalization']!='subtract log_weight at squared_staple_sum_norm=m':raise ValueError('Reference subtraction changed.')
            if row['norm']!='supremum over fixed exterior SU(2) link fields; dimensionless log weight':raise ValueError('Missing norm type.')
            pairs=list(combinations(range(m),2))
            q={():F(m),**{(i,):F(2) for i in range(len(pairs))}}
            # Haar moments of a radial SU(2) coordinate: E[t^2]=1/4, E[t^4]=1/8.
            f2={key:F(1,4)*value/2 for key,value in q.items()}
            f4={key:F(1,8)*value/24 for key,value in poly_product(q,q).items()}
            l4=dict(f4)
            for key,value in poly_product(f2,f2).items():l4[key]=l4.get(key,F(0))-value/2
            expected={(2,key):value for key,value in f2.items() if key}
            expected.update({(4,key):value for key,value in l4.items() if key and value})
            actual={}
            for term in row['normalized_log_weight_coefficients']:
                if set(term)!={'beta_power','pair_factors','coefficient'}:raise ValueError('Unexpected polynomial fields.')
                power=term['beta_power']
                if type(power) is not int:raise ValueError('Noninteger beta power.')
                factors=[]
                for pair in term['pair_factors']:
                    if not isinstance(pair,list) or len(pair)!=2 or any(type(v) is not int for v in pair) or tuple(pair) not in pairs:
                        raise ValueError('Invalid pair variable.')
                    factors.append(pairs.index(tuple(pair)))
                key=(power,tuple(sorted(factors)))
                if key in actual:raise ValueError('Repeated polynomial monomial.')
                actual[key]=rational(term['coefficient'])
            if actual!=expected:raise ValueError('Effective interaction coefficients failed independent Haar/log expansion.')
            B=F(m*m,4)*maximum**2
            if rational(row['u_max'])!=B or not 0<B<1:raise ValueError('Invalid uniform field/coupling range.')
            # Tail of Z(2sqrt(u)): coefficient of u^3 is 1/144;
            # next-term ratio <=B/20. Bound |delta| and |log(1+y)-y+y^2/2|.
            d=F(1,144)/(1-B/20)
            y={1:F(1,2),2:F(1,12),3:d}
            square=univariate_product(y,y);square[2]-=F(1,4)
            cube=univariate_product(univariate_product(y,y),y)
            C=d+sum((v*B**(k-3)/2 for k,v in square.items() if v),F(0))
            C+=sum((v*B**(k-3)/3 for k,v in cube.items()),F(0))
            R=C*F(m*m,4)**3
            for key,value in [('log_Z_u_remainder_coefficient',C),
                              ('unnormalized_log_weight_error_le_beta6_times',R),
                              ('normalized_log_weight_error_le_beta6_times',2*R),
                              ('normalized_error_at_beta_max',2*R*maximum**6)]:
                if rational(row[key])!=value:raise ValueError('Uniform remainder majorant mismatch.')
            if 2*R*maximum**6>=F(1,10000):raise ValueError('Declared endpoint error exceeds the reference budget.')
            count+=len(actual)
        return True,{'local_maps':2,'checked_interaction_monomials':count,
                     'endpoint_normalized_log_weight_error_less_than':'1/10000',
                     'analytic_gate_closed':False,'rg_contraction_established':False}
    except (KeyError,TypeError,ValueError,ZeroDivisionError) as exc:return False,{'reason':str(exc)}


def main():
    passed,report=audit(json.loads((ROOT/'artifacts'/'local_step.json').read_text()))
    out={'status':'EXACT_LOCAL_ALGEBRA_AUDIT_PASSED' if passed else 'FAIL','report':report,
         'analytic_gate_closed':False,'rg_contraction_established':False,
         'non_claims':['No complete spatial blocking transformation or contraction',
                       'No norm conversion to polymer activities or continuum uniformity',
                       'Haar reduction and analytic remainder proof remain a written derivation for review']}
    (ROOT/'artifacts'/'local_audit.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(out['status']);return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
