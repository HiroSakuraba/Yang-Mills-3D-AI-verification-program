"""Exact finite Z2 hypergraph toy for the MARKED_POLYMER_IDENTITY factorization.

This tests the *combinatorial* link-support bookkeeping, not the SU(2) Haar
activity estimates or convergence of the augmented polymer Mayer series.
"""
from collections import defaultdict
from fractions import Fraction as Q
from itertools import combinations


def selected_components(selected, supports):
    remaining=set(selected)
    groups=[]
    while remaining:
        seed=min(remaining);remaining.remove(seed);group={seed};queue=[seed]
        while queue:
            current=queue.pop()
            neighbors=[j for j in sorted(remaining) if supports[j] & supports[current]]
            for j in neighbors:
                remaining.remove(j);group.add(j);queue.append(j)
        groups.append(frozenset(group))
    return groups


def z2_haar_component_weight(selected, supports):
    """Product of normalized Haar Z2 characters: one iff each link has even incidence."""
    odd=set()
    for i in selected:
        odd.symmetric_difference_update(supports[i])
    return Q(int(not odd))


def direct_partition(supports, face_indices, mark_names):
    """Return polynomial with monomials (power_beta,power_s,power_t)."""
    indices=list(supports)
    coeffs=defaultdict(Q)
    for k in range(len(indices)+1):
        for selected in combinations(indices,k):
            key=(len(set(selected)&set(face_indices)), int('C' in selected), int('D' in selected))
            coeffs[key]+=z2_haar_component_weight(selected,supports)
    return {k:v for k,v in coeffs.items() if v}


def component_partition(supports, face_indices, mark_names):
    indices=list(supports)
    coeffs=defaultdict(Q)
    for k in range(len(indices)+1):
        for selected in combinations(indices,k):
            components=selected_components(selected,supports)
            # Independent Haar link integration factorizes on pairwise disjoint supports.
            weight=Q(1)
            for comp in components:
                weight*=z2_haar_component_weight(comp,supports)
            key=(len(set(selected)&set(face_indices)),int('C' in selected),int('D' in selected))
            coeffs[key]+=weight
    return {k:v for k,v in coeffs.items() if v}


def bridge_case():
    # Two 4-link face factors intersect in precisely link 3, and source supports
    # C,D are disjoint. This is an algebraic finite-group toy, not a physical
    # pair of 3D Wilson loops. All six vertices/links are symbolic.
    supports={'P':frozenset([0,1,2,3]),'Q':frozenset([3,4,5,6]),
              'C':frozenset([0,1,2]),'D':frozenset([4,5,6])}
    return supports, {'P','Q'}, {'C','D'}


def bridge_result():
    supports,faces,marks=bridge_case()
    direct=direct_partition(supports,faces,marks)
    components=component_partition(supports,faces,marks)
    assert direct==components
    return direct
