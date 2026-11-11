#!/usr/bin/env python3
"""Generate a finite 3D-plaquette support example of an abstract gas-stability bound.

Research demo only: does not construct the Yang-Mills effective polymer activities.
"""
import argparse
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

ORIGINAL_COMMIT = '3456e5e75cf8d4cd558955a5c7638fba2d68f464'


def vertices(anchor, axes):
    a = tuple(anchor)
    e = [tuple(int(i == axis) for i in range(3)) for axis in axes]
    return sorted([list(a), [a[k]+e[0][k] for k in range(3)],
                   [a[k]+e[1][k] for k in range(3)],
                   [a[k]+e[0][k]+e[1][k] for k in range(3)]])


def product(values):
    out = F(1)
    for value in values:
        out *= value
    return out


def rat(value):
    return str(value.numerator) + '/' + str(value.denominator)


def build():
    entries = [
        ('xy_left', [0, 0, 0], [0, 1], '1/8', '3/20', '1/5'),
        ('xz_left', [0, 0, 0], [0, 2], '1/10', '2/25', '1/8'),
        ('xy_right', [3, 0, 0], [0, 1], '-1/9', '-1/10', '1/8'),
        ('xz_right', [3, 0, 0], [0, 2], '1/12', '1/14', '1/9'),
        ('yz_far_left', [0, 0, 3], [1, 2], '1/5', '1/6', '1/4'),
        ('yz_far_right', [3, 0, 3], [1, 2], '-1/7', '-1/8', '1/6'),
    ]
    rows = [dict(id=id, anchor=a, axes=axes, support=vertices(a, axes),
                 inventory=[a], activity_p=p, activity_q=q, majorant=h)
            for id, a, axes, p, q, h in entries]
    flags = [[0, 0, 0], [3, 0, 0]]
    by_id = {r['id']: r for r in rows}

    def admissible(chosen):
        supports = [set(map(tuple, by_id[id]['support'])) for id in chosen]
        if any(s & t for i, s in enumerate(supports) for t in supports[i+1:]):
            return False
        return set().union(*(set(map(tuple, by_id[id]['inventory'])) for id in chosen)) == set(map(tuple, flags))

    ids = list(by_id)
    sets = [list(chosen) for n in range(len(ids)+1)
            for chosen in itertools.combinations(ids, n) if admissible(chosen)]
    gas_p = sum((product(F(by_id[id]['activity_p']) for id in s) for s in sets), F(0))
    gas_q = sum((product(F(by_id[id]['activity_q']) for id in s) for s in sets), F(0))
    local_bound = sum((abs(F(by_id[id]['activity_p']) - F(by_id[id]['activity_q'])) *
                       product(F(by_id[j]['majorant']) for j in s if j != id)
                       for s in sets for id in s), F(0))
    global_bound = sum((abs(F(r['activity_p']) - F(r['activity_q'])) *
                        product(1 + F(other['majorant']) for other in rows if other['id'] != r['id'])
                        for r in rows), F(0))
    delta = max(abs(F(r['activity_p'])-F(r['activity_q']))/F(r['majorant']) for r in rows)
    product_bound = delta*(product(1 + 2*F(r['majorant']) for r in rows)-1)
    return {
        'schema_version': '1.0',
        'audit_kind': 'finite_3d_support_example_not_analytic_rg',
        'source': {'repository': 'yang-mills-group/OpenAI-YM-20261028',
                   'commit': ORIGINAL_COMMIT,
                   'path': 'YM/Push/BETA_TRANSPORT/Activity.lean',
                   'lemmas': ['product_diff', 'gas_diff']},
        'geometry': 'unwrapped_integer_cubic_lattice',
        'same_admissibility_for_p_and_q': True,
        'flags': flags,
        'entries': rows,
        'admissible_subsets': sets,
        'gas_p': rat(gas_p), 'gas_q': rat(gas_q),
        'absolute_difference': rat(abs(gas_p-gas_q)),
        'local_telescoping_bound': rat(local_bound),
        'global_product_bound': rat(global_bound),
        'relative_delta': rat(delta),
        'delta_product_bound': rat(product_bound),
        'nonclaims': [
            'No 3D Wilson polymer activities or RG coefficients were computed.',
            'No volume-uniform or lattice-spacing-uniform bound is shown.',
            'No result is imported as a closed 3D proof gate.'
        ]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=2) + '\n', encoding='utf-8')
    print(f'Generated {args.output}')


if __name__ == '__main__':
    main()
