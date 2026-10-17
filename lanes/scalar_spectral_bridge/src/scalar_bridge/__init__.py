"""Exact constants for a spectral research note; no analytic gate closure."""
from fractions import Fraction as F


def outward(lo, hi):
    scale=1<<96
    return [str(F((lo*scale).__floor__(),scale)),str(F((hi*scale).__ceil__(),scale))]


def log_inverse(alpha):
    z=(1-alpha)/(1+alpha); count=96
    lo=2*sum((z**(2*k+1)/(2*k+1) for k in range(count)),F(0))
    tail=2*z**(2*count+1)/((2*count+1)*(1-z*z))
    return outward(lo,lo+tail)


def build():
    cases=[]
    for beta in (F(1,40),F(1,20)):
        a=12*beta
        b=[9+16*a/(1-a)+8*a*a/(1-a)**2,12+8*a/(1-a),F(4)]
        cases.append({'wilson_beta':str(beta),'influence_row_sum_upper':str(a),
                      'spatial_polynomial_low_to_high':[str(v) for v in b],
                      'covariance_prefactor':str(16/(1-a)),
                      'channel_transfer_radius_upper':str(a),
                      'dimensionless_energy_lower_endpoint_interval':log_inverse(a)})
    return {'schema_version':'ym3d.scalar_spectral_bridge.v1',
            'status':'RESEARCH_DERIVATION_WITH_EXACT_CONSTANT_AUDIT',
            'analytic_gate_closed':False,'time_boundary':'infinite_time_ground_state',
            'spatial_boundary':'periodic_square_L_at_least_3',
            'operator':'sum_z(P_z-mean_P)/L; P=1-Tr(U_xy)/2',
            'scope':'spectral measure and cyclic transfer subspace of this operator only',
            'physical_energy_units':'dimensionless energy divided by positive temporal_spacing',
            'required_hypotheses':['compact finite-range Wilson specification with normalized Haar measure',
                                   'Dobrushin comparison bound and support-distance estimate',
                                   'positive self-adjoint physical transfer representation',
                                   'infinite-time state equals the transfer ground-state state'],
            'cases':cases}
