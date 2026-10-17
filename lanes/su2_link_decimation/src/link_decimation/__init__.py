"""Exact local link elimination formulas; not a certified full RG rung."""
from fractions import Fraction as F
from itertools import combinations


def case(m,beta_max):
    pairs=list(combinations(range(m),2));coefficients=[]
    for pair in pairs:
        coefficients.extend([{'beta_power':2,'pair_factors':[list(pair)],'coefficient':'1/4'},
                             {'beta_power':4,'pair_factors':[list(pair)],'coefficient':str(-F(m,96))},
                             {'beta_power':4,'pair_factors':[list(pair),list(pair)],'coefficient':'-1/96'}])
    for a,b in combinations(pairs,2):
        coefficients.append({'beta_power':4,'pair_factors':[list(a),list(b)],'coefficient':'-1/48'})
    B=F(m*m,4)*beta_max**2
    d=1/(144*(1-B/20));e=F(1,12)+d*B;c=F(1,2)+B/12+d*B*B
    C=d+e/2+e*e*B/2+c**3/3
    R=C*F(m*m,4)**3
    return {'staple_count':m,'beta_max':str(beta_max),'u_max':str(B),
            'normalization':'subtract log_weight at squared_staple_sum_norm=m',
            'normalized_log_weight_coefficients':coefficients,
            'log_Z_u_remainder_coefficient':str(C),
            'unnormalized_log_weight_error_le_beta6_times':str(R),
            'normalized_log_weight_error_le_beta6_times':str(2*R),
            'normalized_error_at_beta_max':str(2*R*beta_max**6),
            'norm':'supremum over fixed exterior SU(2) link fields; dimensionless log weight'}


def build():
    return {'schema_version':'ym3d.su2_link_decimation.v1',
            'status':'LOCAL_ANALYTIC_DERIVATION_WITH_EXACT_ALGEBRA_AUDIT',
            'analytic_gate_closed':False,'rg_contraction_established':False,
            'map':'integrate one link against normalized Haar while keeping its external staples fixed',
            'exact_weight':'Z(beta*sqrt(q)); q=|sum_i S_i|^2=m+2*sum_(i<j) c_ij',
            'pair_variable':'c_ij=Tr(S_i*S_j^dagger)/2',
            'Z_series':'sum_(k>=0) (s^2/4)^k/[k!(k+1)!]',
            'cases':[case(2,F(1,4)),case(4,F(1,8))]}
