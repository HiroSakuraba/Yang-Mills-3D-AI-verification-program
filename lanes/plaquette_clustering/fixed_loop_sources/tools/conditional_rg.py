"""Small exact rational conditional-covariance examples for RG bookkeeping.

These are diagnostic finite discrete probability spaces, NOT SU(2) simulation.
"""
from fractions import Fraction as Q

def coarsen_joint_law(table, coarse):
    """table: sequence of (fine_state, nonnegative rational mass).
    coarse: map from fine_state to a hashable blocked state.
    Return Cov_f, Cov_coarse(E[X|B],E[Y|B]), E Cov(X,Y|B).
    Fine states are pairs (x,y) of rational values.
    """
    total=sum((Q(weight) for _,weight in table),Q(0))
    if total<=0:raise ValueError('positive normalizer required')
    buckets={}
    for (x,y),mass in table:
        if mass<0:raise ValueError('negative mass')
        b=coarse((x,y))
        buckets.setdefault(b,[]).append((Q(x),Q(y),Q(mass)))
    ex=ey=exy=Q(0);ebxy=Q(0);contact=Q(0)
    for b,rows in buckets.items():
        z=sum((w for x,y,w in rows),Q(0))
        if not z: continue
        px=z/total
        mx=sum((x*w for x,y,w in rows),Q(0))/z
        my=sum((y*w for x,y,w in rows),Q(0))/z
        mxy=sum((x*y*w for x,y,w in rows),Q(0))/z
        ex+=px*mx;ey+=px*my;exy+=px*mxy
        ebxy+=px*mx*my
        contact+=px*(mxy-mx*my)
    fine_cov=exy-ex*ey
    coarse_cov=ebxy-ex*ey
    assert fine_cov == coarse_cov + contact
    return {'fine_cov':fine_cov, 'coarse_cov':coarse_cov,
            'conditional_contact':contact, 'normalizer':total}
