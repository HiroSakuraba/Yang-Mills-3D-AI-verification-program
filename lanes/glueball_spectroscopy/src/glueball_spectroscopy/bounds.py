"""Exact arithmetic for a review-stage scalar plaquette correlation derivation.
Checking these formulas does not validate their analytic hypotheses.
"""
from fractions import Fraction as F


def scalar_budget(x='1/20'):
    x=F(x)
    if not 0<x<F(1,12):raise ValueError('Conservative window requires 0 < x < 1/12.')
    alpha=12*x  # >=12*tanh(x); a deliberately rational conservative bound.
    q=(1+alpha)/2;r=alpha/q
    b2=F(4);b1=12+8*alpha/(1-alpha)
    b0=9+16*alpha/(1-alpha)+8*alpha**2/(1-alpha)**2
    prefactor=16/(1-alpha)*(b2*r*(1+r)/(1-r)**3+b1*r/(1-r)**2+b0/(1-r))
    return {'schema_version':'ym3d.scalar_decay_budget.v1','wilson_x':str(x),
            'alpha_upper':str(alpha),'pure_exponential_base':str(q),
            'pure_exponential_prefactor':str(prefactor),
            'polynomial_coefficients':[str(b0),str(b1),str(b2)],
            'local_covariance_prefactor':str(16/(1-alpha)),
            'rate_formula':'m_review = -log(q)/a_t',
            'status':'EXACT_FORMULA_EVALUATION_ANALYTIC_DERIVATION_FOR_REVIEW',
            'non_claims':['No analytic 3D gate closed','No transfer-space identification certified',
                          'No isolated glueball pole established','No continuum limit']}


def spatial_sum_bound(t,alpha):
    if type(t) is not int or t<0:raise ValueError('t must be a nonnegative integer.')
    alpha=F(alpha)
    if not 0<alpha<1:raise ValueError('Require 0 < alpha < 1.')
    bracket=(2*t+3)**2+8*alpha*((t+2)/(1-alpha)+alpha/(1-alpha)**2)
    return 16*alpha**t*bracket/(1-alpha)
