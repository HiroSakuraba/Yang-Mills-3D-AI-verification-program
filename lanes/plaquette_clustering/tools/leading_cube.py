#!/usr/bin/env python3
"""Independent geometrical check of the lowest single-cube character term.
A face is (normal_axis, lower_vertex_3tuple), where its edges lie in the
other two axes.  This code is a perturbative diagnostic, not a convergence proof.
"""
from fractions import Fraction as Q


def cube_faces(corner):
    out=[]
    for normal in range(3):
        for step in (0,1):
            v=list(corner)
            v[normal]+=step
            out.append((normal,tuple(v)))
    return frozenset(out)


def incident_cubes(face):
    normal, pos=face
    lo=list(pos)
    hi=list(pos)
    lo[normal]-=1
    return (tuple(lo),tuple(hi))


def common_cubes(p,q):
    return tuple(sorted(set(incident_cubes(p)) & set(incident_cubes(q))))


def coefficient(p,q):
    if p==q:
        raise ValueError('mixed derivative requires distinct marked plaquettes')
    # Each cube support has Haar weight 2^(2-6)=1/16 for chi_1 at each face;
    # each Wilson coefficient r_1(beta_face)=beta_face/2+O(beta_face^3).
    # Two beta derivatives leave beta^4 * (1/16) / 2^6.
    return Q(len(common_cubes(p,q)),1024)


if __name__=='__main__':
    p=(2,(0,0,0));q=(2,(0,0,1))
    print('opposite faces of cube, shared cubes:', common_cubes(p,q),
          'leading connected covariance coefficient:', coefficient(p,q))
