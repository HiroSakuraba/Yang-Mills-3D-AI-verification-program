#!/usr/bin/env python3
"""Independent finite-geometry and exact Z2 transfer sanity checks.

This executable DOES NOT prove a 3D SU(2) spectral theorem or a continuum gap.
It checks elementary support geometry and a separate, fully enumerated finite
Z2 Wilson analogue of the gauge-projected time-slab/transfer identity.
"""
from collections import Counter, deque
from fractions import Fraction as Q
import itertools
import json


def cubic_time_slab(length=3, last_time=3):
    """Link/plaquette incidence on a 2D spatial torus times an open time slab."""
    if not (isinstance(length, int) and length >= 3
            and isinstance(last_time, int) and last_time >= 1):
        raise ValueError("Require nondegenerate L>=3 and last_time>=1")

    def mod(x):
        return x % length

    def e(axis, x, y, z):
        return (axis, mod(x), mod(y), z)

    links = set()
    for z in range(last_time + 1):
        for x, y in itertools.product(range(length), repeat=2):
            links.add(e(0, x, y, z))
            links.add(e(1, x, y, z))
            if z < last_time:
                links.add(e(2, x, y, z))
    plaquettes = []
    for z in range(last_time + 1):
        for x, y in itertools.product(range(length), repeat=2):
            plaquettes.append(frozenset((
                e(0, x, y, z), e(1, x+1, y, z),
                e(0, x, y+1, z), e(1, x, y, z)
            )))
            if z < last_time:
                plaquettes.append(frozenset((
                    e(0, x, y, z), e(2, x+1, y, z),
                    e(0, x, y, z+1), e(2, x, y, z)
                )))
                plaquettes.append(frozenset((
                    e(1, x, y, z), e(2, x, y+1, z),
                    e(1, x, y, z+1), e(2, x, y, z)
                )))
    incidence = Counter()
    adjacency = {link: set() for link in links}
    pair_multiplicity = Counter()
    for p in plaquettes:
        if len(p) != 4 or not p.issubset(links):
            raise ValueError("degenerate or unidentified face")
        for link in p:
            incidence[link] += 1
            adjacency[link].update(p - {link})
        for pair in itertools.combinations(sorted(p), 2):
            pair_multiplicity[pair] += 1
    return links, plaquettes, incidence, adjacency, pair_multiplicity


def shortest_distance(adjacency, sources, destinations):
    """Multi-source BFS; count edges in the link-sharing-a-face graph."""
    frontier = deque(sources)
    visited = set(sources)
    destinations = set(destinations)
    distance = 0
    while frontier:
        for _ in range(len(frontier)):
            link = frontier.popleft()
            if link in destinations:
                return distance
            for neighbor in adjacency[link]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    frontier.append(neighbor)
        distance += 1
    return None


def graph_audit():
    links, faces, incidence, adjacency, pairs = cubic_time_slab()
    if max(incidence.values()) != 4 or max(map(len, adjacency.values())) != 12:
        raise AssertionError("incorrect degree/four-face incidence")
    if max(pairs.values()) != 1:
        raise AssertionError("two distinct links unexpectedly share multiple faces")
    distances = {}
    for n in range(1, 4):
        start = [e for e in links if e[0] in (0, 1) and e[3] == 0]
        finish = [e for e in links if e[0] in (0, 1) and e[3] == n]
        d = shortest_distance(adjacency, start, finish)
        if d != n:
            raise AssertionError(f"incorrect time-slice distance at {n}: {d}")
        distances[str(n)] = d
    return {
        "spatial_period": 3,
        "time_slab": 3,
        "link_count": len(links),
        "plaquette_count": len(faces),
        "max_face_incidence_per_link": max(incidence.values()),
        "max_neighbor_links": max(map(len, adjacency.values())),
        "max_pair_face_multiplicity": max(pairs.values()),
        "time_slice_min_distances": distances,
    }


def z2_exact_transfer():
    """Compare Wilson slab integration against B K B on the gauge-invariant basis.

    Gauge group Z2 on one open spatial square with four edges and four vertices.
    This model is NOT SU(2) and is used only to detect algebraic errors.
    Choose r=1/40 and t=2r/(1+r^2) to make B=1+r*flux rational.
    A plaquette weight B^2 is proportional to the Wilson factor 1+t*flux
    = exp(beta*flux)/cosh(beta), with t=tanh(beta).
    """
    r = Q(1, 40)
    t = 2*r/(1+r*r)
    states = list(itertools.product((-1, 1), repeat=4))
    gauges = states
    flux = lambda u: u[0]*u[1]*u[2]*u[3]
    B = lambda u: 1+r*flux(u)
    k = lambda x: 1+t*x

    # This is the direct temporal-link (gauge) integral for one Wilson slab.
    # First compare it as an operator on the complete gauge-invariant
    # function basis {1, flux}, rather than only a selected correlator.
    def slab_apply(rep, basis_index):
        total = Q(0)
        for v in states:
            temporal_sum = Q(0)
            for h in gauges:
                word = Q(1)
                for edge in range(4):
                    word *= k(rep[edge]*v[edge]*h[edge]*h[(edge+1) % 4])
                temporal_sum += word
            f_v = Q(1) if basis_index == 0 else flux(v)
            total += (B(rep)*B(v)*f_v*temporal_sum)/256
        return total

    # Reconstruct coefficients of output c0+c1*flux from each orbit rep.
    plus = (1, 1, 1, 1)
    minus = (-1, 1, 1, 1)
    computed = []
    for col in (0, 1):
        out_plus = slab_apply(plus, col)
        out_minus = slab_apply(minus, col)
        computed.append(((out_plus+out_minus)/2, (out_plus-out_minus)/2))

    power = t**4
    # In basis (1,flux), multiplication by B=[[1,r],[r,1]],
    # and product-link convolution K=diag(1,t^4); hence T=B K B.
    analytic = (
        (1+r*r*power, r*(1+power)),
        (r*(1+power), r*r+power),
    )
    if computed != [
        (analytic[0][0], analytic[1][0]),
        (analytic[0][1], analytic[1][1])
    ]:
        raise AssertionError("direct gauge-slab integration disagrees with B K B")

    # T is strictly positive as an operator, and its top eigenvalue is
    # simple: symmetric positive-entry 2x2 with positive determinant.
    determinant = analytic[0][0]*analytic[1][1]-analytic[0][1]**2
    expected_determinant = (1-r*r)**2*power
    if determinant != expected_determinant or determinant <= 0:
        raise AssertionError("strict transfer positivity failed")
    if analytic[0][1] <= 0:
        raise AssertionError("no positivity improvement")
    # Without radicals: lambda_min <= T11, lambda_max >= T00.
    # Both positive, hence lambda_min/lambda_max <= T11/T00.
    ratio_bound = analytic[1][1]/analytic[0][0]
    alpha = 12*t
    if not (Q(0) < ratio_bound < alpha < Q(1)):
        raise AssertionError("toy spectral ratio not below safe Dobrushin bound")
    return {
        "model": "finite_Z2_Wilson_analogue_not_SU2",
        "spatial_edges": 4,
        "physical_basis": ["one", "plaquette_flux"],
        "r": str(r),
        "tanh_beta": str(t),
        "physical_transfer_matrix": [
            [str(analytic[0][0]), str(analytic[0][1])],
            [str(analytic[1][0]), str(analytic[1][1])]
        ],
        "transfer_determinant": str(determinant),
        "spectral_ratio_upper": str(ratio_bound),
        "dobrushin_conservative_alpha": str(alpha),
        "gauge_slab_equals_positive_BKB": True,
    }


def main():
    print(json.dumps({
        "status": "RESEARCH_SANITY_PASS",
        "graph": graph_audit(),
        "finite_group_analogue": z2_exact_transfer(),
        "proves_su2_analytic_gap": False,
        "proves_continuum_mass_gap": False,
        "closes_gates": [],
    }, indent=2))


if __name__ == "__main__":
    main()
