#!/usr/bin/env python3
"""Independent Fraction/Haar-moment audit; imports no generator code.

--report-only checks the reference without emitting a program gate decision.
The full gate additionally requires the unchanged geometry prerequisites and
an explicit completion certificate for integration with that geometry pipeline.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
import json
from math import comb, factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
PREREQUISITES = (
    'YM3D_ORIENTED_LINK_ACTION_1', 'YM3D_SUPPORT_LIFT_1',
    'YM3D_CUBIC_SYMMETRY_ORBIT_REDUCTION_1',
    'YM3D_ORBIT_CLOSURE_CONSISTENCY_CHECK_1',
    'YM3D_ORBIT_REDUCTION_EXPANDED_GRAPH_AUDIT_1',
)


def rational(value):
    if not isinstance(value, str):
        raise ValueError('Rational endpoints/couplings must be canonical fraction strings.')
    result = F(value)
    if str(result) != value:
        raise ValueError('Noncanonical rational string.')
    return result


def ints(value, length):
    if not isinstance(value, list) or len(value) != length or any(type(v) is not int for v in value):
        raise ValueError('Invalid exact integer tuple.')
    return tuple(value)


def haar_moment(power):
    if power % 2:
        return F(0)
    k = power // 2
    return F(comb(2 * k, k), (k + 1) * 4 ** k)


def coefficient(n, power):
    # Independently integrate normalized characters 1, t, (4t^2-1)/3.
    if n == 0:
        moment = haar_moment(power)
    elif n == 1:
        moment = haar_moment(power + 1)
    elif n == 2:
        moment = (4 * haar_moment(power + 2) - haar_moment(power)) / 3
    else:
        raise ValueError('Representation is outside the declared SU(2) benchmark.')
    return moment / factorial(power)


def moment_enclosure(beta, n):
    maximum_power = 48 + n  # k=0,...,24 in the nonzero parity sector.
    lower = sum((coefficient(n, p) * beta ** p for p in range(maximum_power + 1)), F(0))
    first_power = maximum_power + 2
    first_coefficient = coefficient(n, first_power)
    next_coefficient = coefficient(n, first_power + 2)
    first = first_coefficient * beta ** first_power
    # The coefficient ratio has denominator increasing with k; it bounds
    # every subsequent ratio, as derived algebraically in DERIVATION.md.
    ratio = beta ** 2 * next_coefficient / first_coefficient
    if not first_coefficient > 0 or not 0 <= ratio < 1:
        raise ValueError('Invalid independent tail certificate.')
    return lower, lower + first / (1 - ratio)


def dyadic_interval(lo, hi):
    scale = 2 ** 96
    low = (lo.numerator * scale) // lo.denominator
    up = -((-hi.numerator * scale) // hi.denominator)
    return F(low, scale), F(up, scale)


def interval(record, bounds):
    if not isinstance(record, dict) or set(record) != {'lower', 'upper'}:
        raise ValueError('Invalid interval record.')
    lo, hi = rational(record['lower']), rational(record['upper'])
    if (lo, hi) != dyadic_interval(*bounds) or hi - lo > F(1, 2 ** 80):
        raise ValueError('Interval disagrees with independent enclosure or is too wide.')
    return lo, hi


def reduce_word(word):
    stack = []
    for x, y, sign in word:
        letter = (x, y, sign)
        if stack and stack[-1] == (x, y, -sign):
            stack.pop()
        else:
            stack.append(letter)
    return stack


def check_geometry(data):
    tree = data['comb_tree']
    expected_tree = {((x, y), (x+1, y)) for x in range(4) for y in range(4)}
    expected_tree |= {((0, y), (0, y+1)) for y in range(3)}
    exported_tree = [(ints(edge[0], 2), ints(edge[1], 2)) for edge in tree]
    if len(exported_tree) != 19 or set(exported_tree) != expected_tree:
        raise ValueError('Incorrect comb-tree export.')
    reached = {(0, 0)}
    while True:
        previous = len(reached)
        for a, b in exported_tree:
            if a in reached: reached.add(b)
            if b in reached: reached.add(a)
        if previous == len(reached): break
    if len(reached) != 20:
        raise ValueError('Comb tree does not span the open grid.')
    # 19 edges connecting 20 vertices are a tree. Remaining 12 vertical links
    # correspond bijectively to the 12 plaquettes via triangular Haar changes.
    expected_keys = {(a,b,c,d,o) for a,b in combinations(range(5),2)
                     for c,d in combinations(range(4),2) for o in (-1,1)}
    seen, areas = set(), set()
    for loop in data['loops']:
        if set(loop) != {'rectangle', 'orientation', 'vertices', 'axial_word', 'interior_plaquettes', 'area'}:
            raise ValueError('Unexpected loop fields.')
        a,b,c,d = ints(loop['rectangle'], 4); o = loop['orientation']
        if type(o) is not int or o not in (-1,1) or (a,b,c,d,o) not in expected_keys or (a,b,c,d,o) in seen:
            raise ValueError('Unexpected or duplicate oriented rectangle.')
        seen.add((a,b,c,d,o))
        expected_path = [(x,c) for x in range(a,b)] + [(b,y) for y in range(c,d)]
        expected_path += [(x,d) for x in range(b,a,-1)] + [(a,y) for y in range(d,c-1,-1)]
        if o == -1: expected_path.reverse()
        path = [ints(p, 2) for p in loop['vertices']]
        if path != expected_path:
            raise ValueError('Boundary path does not match the rectangle.')
        twice_area = sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(path,path[1:]))
        area = (b-a)*(d-c)
        if type(loop['area']) is not int or loop['area'] != area or twice_area != 2*o*area:
            raise ValueError('Area/orientation mismatch.')
        interior = {(x,y) for x in range(a,b) for y in range(c,d)}
        exported_interior = [ints(p,2) for p in loop['interior_plaquettes']]
        if len(exported_interior) != area or set(exported_interior) != interior:
            raise ValueError('Interior plaquette inventory mismatch.')
        # Right vertical side has V(b,y)=P(b-1,y)...P(0,y).
        right = [(x,y,1) for y in range(c,d) for x in range(b-1,-1,-1)]
        # Left side is traversed downward, in reverse row order.
        left = [(x,y,-1) for y in range(d-1,c-1,-1) for x in range(a)]
        word = right + left
        if o == -1: word = [(x,y,-s) for x,y,s in reversed(word)]
        exported = [ints(letter,3) for letter in loop['axial_word']]
        if exported != word:
            raise ValueError('Noncommutative axial-gauge boundary word mismatch.')
        counts = Counter((x,y) for x,y,s in word if (x,y) in interior)
        if set(counts) != interior or any(v != 1 for v in counts.values()):
            raise ValueError('Interior variables do not occur exactly once.')
        if any(s != o for x,y,s in word if (x,y) in interior):
            raise ValueError('Interior traversal sign mismatch.')
        residual = [letter for letter in word if letter[:2] not in interior]
        if reduce_word(residual):
            raise ValueError('Exterior variables do not freely cancel after interior integration.')
        areas.add(area)
    if seen != expected_keys:
        raise ValueError('Incomplete rectangle audit schedule.')
    return sorted(areas)


def audit(data):
    try:
        required = {'schema_version','gauge_group','spacetime_dimensions','boundary','action','observable',
                    'grid_plaquettes','series_max_k','outward_dyadic_bits','couplings','twice_spins',
                    'comb_tree','loops','one_plaquette','area_law_expectations'}
        if not isinstance(data, dict) or set(data) != required:
            raise ValueError('Unexpected reference fields.')
        fixed = {'schema_version':'ym2d.su2_wilson_reference.v1','gauge_group':'SU(2)',
                 'spacetime_dimensions':2,'boundary':'open_rectangle',
                 'action':'exp(beta*sum_plaquettes(Tr(U_p)/2))', 'observable':'chi_j(U_loop)/(2*j+1)',
                 'grid_plaquettes':[4,3],'series_max_k':24,'outward_dyadic_bits':96,
                 'couplings':['0','1/2','2','4'],'twice_spins':[0,1,2]}
        for key, expected in fixed.items():
            if data[key] != expected or type(data[key]) is not type(expected):
                raise ValueError(f'Unsupported or weakened benchmark convention: {key}')
        ints(data['grid_plaquettes'],2); ints(data['twice_spins'],3)
        areas = check_geometry(data)
        couplings = [F(0), F(1,2), F(2), F(4)]
        exact = {(beta,n):moment_enclosure(beta,n) for beta in couplings for n in (0,1,2)}
        expected_keys = set(exact); seen = set(); checked_intervals = 0
        for row in data['one_plaquette']:
            if set(row) != {'beta','twice_spin','kernel_integral','normalized_character_mean'}:
                raise ValueError('Invalid coefficient fields.')
            beta, n = rational(row['beta']), row['twice_spin']
            if type(n) is not int or (beta,n) not in expected_keys or (beta,n) in seen:
                raise ValueError('Repeated or invalid representation/coupling row.')
            seen.add((beta,n)); lo,hi = exact[beta,n]; zlo,zhi = exact[beta,0]
            interval(row['kernel_integral'], (lo,hi))
            interval(row['normalized_character_mean'], (lo/zhi,hi/zlo) if n else (F(1),F(1)))
            checked_intervals += 2
        if seen != expected_keys:
            raise ValueError('Incomplete one-plaquette schedule.')
        expected_loops = {(b,n,a) for b in couplings for n in (1,2) for a in areas}
        seen = set()
        for row in data['area_law_expectations']:
            if set(row) != {'beta','twice_spin','area','normalized_wilson_loop'}:
                raise ValueError('Invalid Wilson-loop fields.')
            beta = rational(row['beta']); n = row['twice_spin']; area = row['area']
            if type(n) is not int or type(area) is not int or (beta,n,area) not in expected_loops or (beta,n,area) in seen:
                raise ValueError('Invalid or repeated area-law case.')
            seen.add((beta,n,area)); lo,hi=exact[beta,n]; zlo,zhi=exact[beta,0]
            interval(row['normalized_wilson_loop'], ((lo/zhi)**area,(hi/zlo)**area))
            checked_intervals += 1
        if seen != expected_loops:
            raise ValueError('Incomplete area-law schedule.')
        # Strong-coupling leading terms detect character and trace normalization.
        if [coefficient(1,p) for p in (0,1,2)] != [F(0),F(1,4),F(0)] or coefficient(2,2) != F(1,24):
            raise ValueError('Haar leading coefficients disagree with normalization.')
        return True, {'oriented_rectangles':len(data['loops']), 'grid_plaquettes':12,
                      'one_plaquette_cases':len(expected_keys),'area_law_cases':len(expected_loops),
                      'rational_intervals':checked_intervals,'absolute_interval_width_limit':'1/1208925819614629174706176',
                      'reference_method':'independent Catalan Haar moments, normalized character polynomials and geometric tails',
                      'geometry_method':'comb-tree spanning audit, ordered boundary words and exact free-word cancellation'}
    except (KeyError,TypeError,ValueError,IndexError,ZeroDivisionError) as exc:
        return False, {'reason':str(exc)}


def readiness(state):
    gates = state.get('gates', {}) if isinstance(state,dict) else {}
    return [key for key in PREREQUISITES if gates.get(key,{}).get('status') != 'CLOSED']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args(); art = ROOT / 'artifacts'
    try:
        passed, report = audit(json.loads((art/'reference.json').read_text()))
    except (OSError,ValueError) as exc:
        passed, report = False, {'reason':str(exc)}
    result = {'status':'PASS' if passed else 'FAIL','scope':'standalone 2D SU(2) open-boundary reference audit',
              'program_gate_closed':False,'report':report,
              'non_claims':['No general SU(N), periodic-surface or 3D result',
                            'No completed integration with support/orbit/collision exports',
                            'No analytic 3D permission or mass-gap statement']}
    (art/'benchmark_report.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    if not passed:
        print('FAIL: independent 2D reference audit'); return 1
    if args.report_only:
        print('PASS: standalone 2D SU(2) reference audit; no program gate decision emitted'); return 0
    state_path = REPOSITORY/'artifacts'/'state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    missing = readiness(state)
    # This initial benchmark does not yet consume the future geometry exports.
    # It cannot unlock analytic 3D work even if a state file names closed parents.
    decision = {'gate_id':'YM2D_SUN_EXACT_VALIDATION_LANE_0','status':'BLOCKED',
                'closed_obligations':[], 'reference_obligations_verified':report,
                'missing_prerequisites':missing,
                'non_claims':result['non_claims'],
                'next_obligation':'Integrate the SU(2) reference with independently audited support/orbit/collision exports; define broader SU(N) acceptance scope.'}
    (art/'decision.json').write_text(json.dumps(decision,sort_keys=True,indent=2)+'\n')
    print('BLOCKED: reference passed; full program validation still requires geometry integration')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
