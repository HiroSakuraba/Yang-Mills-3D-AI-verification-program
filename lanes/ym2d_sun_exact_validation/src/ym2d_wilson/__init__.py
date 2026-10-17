"""Exact rational reference generator for open-boundary 2D SU(2) Wilson theory."""
from fractions import Fraction as F
from math import factorial

COUPLINGS = (F(0), F(1, 2), F(2), F(4))
TERMS = 24
BITS = 96
GRID = (4, 3)


def outward(lo, hi):
    scale = 1 << BITS
    lower = (lo * scale).__floor__()
    upper = (hi * scale).__ceil__()
    return {'lower': str(F(lower, scale)), 'upper': str(F(upper, scale))}


def kernel_interval(beta, twice_spin):
    # Integral of normalized SU(2) character times exp(beta Tr(U)/2).
    n = twice_spin
    term = beta ** n / (2 ** n * factorial(n + 1))
    lower = term
    for k in range(1, TERMS + 1):
        term *= beta * beta / (4 * k * (k + n + 1))
        lower += term
    first = term * beta * beta / (4 * (TERMS + 1) * (TERMS + n + 2))
    ratio = beta * beta / (4 * (TERMS + 2) * (TERMS + n + 3))
    if not 0 <= ratio < 1:
        raise ValueError('Tail schedule is outside its convergence certificate.')
    return lower, lower + first / (1 - ratio)


def loop_vertices(a, b, c, d, orientation):
    point = [a, c]; vertices = [point.copy()]
    for axis, step, count in ((0, 1, b-a), (1, 1, d-c), (0, -1, b-a), (1, -1, d-c)):
        for _ in range(count):
            point = point.copy(); point[axis] += step; vertices.append(point)
    return vertices if orientation == 1 else list(reversed(vertices))


def axial_word(vertices):
    word = []
    for p, q in zip(vertices, vertices[1:]):
        if p[0] != q[0]:
            continue  # Horizontal links belong to the comb tree.
        x = p[0]; y = min(p[1], q[1])
        if q[1] > p[1]:
            word.extend([[i, y, 1] for i in reversed(range(x))])
        else:
            word.extend([[i, y, -1] for i in range(x)])
    return word


def build():
    nx, ny = GRID
    tree = [[[x, y], [x + 1, y]] for y in range(ny + 1) for x in range(nx)]
    tree += [[[0, y], [0, y + 1]] for y in range(ny)]
    loops = []
    for a in range(nx):
        for b in range(a + 1, nx + 1):
            for c in range(ny):
                for d in range(c + 1, ny + 1):
                    for orientation in (-1, 1):
                        vertices = loop_vertices(a, b, c, d, orientation)
                        loops.append({'rectangle': [a, b, c, d], 'orientation': orientation,
                                      'vertices': vertices, 'axial_word': axial_word(vertices),
                                      'interior_plaquettes': [[x, y] for x in range(a, b) for y in range(c, d)],
                                      'area': (b-a)*(d-c)})
    areas = sorted({r['area'] for r in loops})
    coefficients, expectations = [], []
    for beta in COUPLINGS:
        zlo, zhi = kernel_interval(beta, 0)
        for n in (0, 1, 2):
            lo, hi = kernel_interval(beta, n)
            coefficients.append({'beta': str(beta), 'twice_spin': n,
                                 'kernel_integral': outward(lo, hi),
                                 'normalized_character_mean': outward(lo / zhi, hi / zlo) if n else outward(F(1), F(1))})
            if n:
                for area in areas:
                    expectations.append({'beta': str(beta), 'twice_spin': n, 'area': area,
                                         'normalized_wilson_loop': outward((lo / zhi) ** area, (hi / zlo) ** area)})
    return {'schema_version': 'ym2d.su2_wilson_reference.v1', 'gauge_group': 'SU(2)',
            'spacetime_dimensions': 2, 'boundary': 'open_rectangle',
            'action': 'exp(beta*sum_plaquettes(Tr(U_p)/2))',
            'observable': 'chi_j(U_loop)/(2*j+1)', 'grid_plaquettes': list(GRID),
            'series_max_k': TERMS, 'outward_dyadic_bits': BITS,
            'couplings': [str(b) for b in COUPLINGS], 'twice_spins': [0, 1, 2],
            'comb_tree': tree, 'loops': loops, 'one_plaquette': coefficients,
            'area_law_expectations': expectations}
