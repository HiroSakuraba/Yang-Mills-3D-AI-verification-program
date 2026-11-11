#!/usr/bin/env python3
"""Independent exact-rational audit of finite plaquette gas stability example.

Does NOT import the generator or close any program.yaml gate.
"""
import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path

PIN = '3456e5e75cf8d4cd558955a5c7638fba2d68f464'


def product(xs):
    result = Fraction(1)
    for x in xs:
        result *= x
    return result


def rational(text):
    if not isinstance(text, str) or '/' not in text:
        raise ValueError('rationals must use exact numerator/denominator strings')
    value = Fraction(text)
    if f'{value.numerator}/{value.denominator}' != text:
        raise ValueError('rational is not in canonical reduced form')
    return value


def audit(data):
    problems = []
    if data.get('schema_version') != '1.0' or data.get('audit_kind') != 'finite_3d_support_example_not_analytic_rg':
        problems.append('invalid research-only scope')
    src = data.get('source', {})
    if src.get('commit') != PIN or src.get('path') != 'YM/Push/BETA_TRANSPORT/Activity.lean' or src.get('lemmas') != ['product_diff', 'gas_diff']:
        problems.append('source identity/pin mismatch')
    if data.get('same_admissibility_for_p_and_q') is not True:
        problems.append('different admissibility masks invalidate the fixed-census theorem')
    if data.get('geometry') != 'unwrapped_integer_cubic_lattice':
        problems.append('unexpected geometry')
    if len(data.get('nonclaims', [])) < 3:
        problems.append('missing proof-boundary disclaimer')
    entries = data.get('entries', [])
    if not isinstance(entries, list) or not 1 <= len(entries) <= 12:
        return ['bad activity count']
    by_id = {}
    for row in entries:
        key = row.get('id')
        if not isinstance(key, str) or key in by_id:
            problems.append('duplicate/invalid label id')
            continue
        by_id[key] = row
        anchor, axes = row.get('anchor'), row.get('axes')
        if not (isinstance(anchor, list) and len(anchor) == 3 and
                all(type(x) is int for x in anchor) and isinstance(axes, list) and
                len(axes) == 2 and all(type(x) is int and 0 <= x <= 2 for x in axes) and
                axes[0] < axes[1]):
            problems.append(f'{key}: invalid 3D plaquette coordinates')
            continue
        a, b = axes
        e1 = [int(k == a) for k in range(3)]
        e2 = [int(k == b) for k in range(3)]
        expected = sorted([anchor, [anchor[k]+e1[k] for k in range(3)],
                          [anchor[k]+e2[k] for k in range(3)],
                          [anchor[k]+e1[k]+e2[k] for k in range(3)]])
        if row.get('support') != expected:
            problems.append(f'{key}: incorrect upward plaquette support')
        if row.get('inventory') != [anchor]:
            problems.append(f'{key}: wrong marker inventory')
        try:
            p, q, h = [rational(row[z]) for z in ('activity_p', 'activity_q', 'majorant')]
            if h <= 0 or abs(p) > h or abs(q) > h:
                problems.append(f'{key}: invalid majorant')
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            problems.append(f'{key}: malformed rational')
    flags = data.get('flags')
    if not isinstance(flags, list) or len(flags) != len({tuple(x) for x in flags}) or not all(isinstance(x, list) and len(x) == 3 and all(type(v) is int for v in x) for x in flags):
        problems.append('invalid flags')
    if problems:
        return problems
    flagset = {tuple(x) for x in flags}
    ids = list(by_id)
    computed = []
    for n in range(len(ids)+1):
        for s in itertools.combinations(ids, n):
            supp = [set(map(tuple, by_id[i]['support'])) for i in s]
            if any(supp[a] & supp[b] for a in range(n) for b in range(a+1, n)):
                continue
            markers = set().union(*(set(map(tuple, by_id[i]['inventory'])) for i in s))
            if markers == flagset:
                computed.append(list(s))
    if data.get('admissible_subsets') != computed:
        problems.append('admissible subsets mismatch with pairwise-disjoint support and exact inventory coverage')
    p = {i: rational(by_id[i]['activity_p']) for i in ids}
    q = {i: rational(by_id[i]['activity_q']) for i in ids}
    h = {i: rational(by_id[i]['majorant']) for i in ids}
    z_p = sum((product(p[i] for i in s) for s in computed), Fraction(0))
    z_q = sum((product(q[i] for i in s) for s in computed), Fraction(0))
    diff = abs(z_p-z_q)
    local = sum((abs(p[i]-q[i])*product(h[j] for j in s if j != i)
                 for s in computed for i in s), Fraction(0))
    global_sum = sum((abs(p[i]-q[i])*product(1+h[j] for j in ids if j != i)
                      for i in ids), Fraction(0))
    delta = max(abs(p[i]-q[i])/h[i] for i in ids)
    product_majorant = delta*(product(1+2*h[i] for i in ids)-1)
    expected = {
        'gas_p': z_p, 'gas_q': z_q, 'absolute_difference': diff,
        'local_telescoping_bound': local, 'global_product_bound': global_sum,
        'relative_delta': delta, 'delta_product_bound': product_majorant,
    }
    for label, value in expected.items():
        try:
            if rational(data[label]) != value:
                problems.append(f'{label}: computed exact rational mismatch')
        except (KeyError, TypeError, ValueError):
            problems.append(f'{label}: missing/malformed exact rational')
    if not (diff <= local <= global_sum and diff <= product_majorant):
        problems.append('algebraic majorant inequality failed')
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', type=Path)
    args = ap.parse_args()
    try:
        result = audit(json.loads(args.file.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError, KeyError) as ex:
        result = [f'invalid audit input: {ex}']
    print(json.dumps({'status': 'RESEARCH_EXAMPLE_PASS' if not result else 'FAIL',
                      'proves_3d_rg': False, 'closes_gates': [], 'errors': result}, indent=2))
    return 1 if result else 0


if __name__ == '__main__':
    raise SystemExit(main())
