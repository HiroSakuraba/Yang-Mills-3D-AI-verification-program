#!/usr/bin/env python3
"""Independent exact audit. Imports no generator or other bundle package."""
from itertools import permutations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def derive_group():
    # Enumerate images of coordinate axes independently of generator row rules.
    result = set()
    for axes in permutations(range(3)):
        for signs in product((-1, 1), repeat=3):
            columns = [tuple(signs[j] if i == axes[j] else 0 for i in range(3)) for j in range(3)]
            result.add(tuple(tuple(columns[j][i] for j in range(3)) for i in range(3)))
    return result


def mv(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)


def mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def vector(value):
    if not isinstance(value, list) or len(value) != 3 or any(type(v) is not int for v in value):
        raise ValueError('Expected three exact integers.')
    return tuple(value)


def matrix(value):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError('Expected a 3x3 integer matrix.')
    return tuple(vector(row) for row in value)


def audit(data):
    try:
        if set(data) != {'schema_version', 'representation', 'elements', 'periodic_audit_extents'}:
            raise ValueError('Unexpected export fields.')
        if data['schema_version'] != 'ym3d.oriented_link_action.v1' or data['representation'] != 'positive_axis_base_with_traversal_sign':
            raise ValueError('Invalid action convention.')
        if data['periodic_audit_extents'] != [2, 3, 4] or any(type(v) is not int for v in data['periodic_audit_extents']):
            raise ValueError('Unexpected periodic audit schedule.')
        group = derive_group(); rows = data['elements']
        if not isinstance(rows, list) or len(rows) != 48:
            raise ValueError('Expected exactly 48 group elements.')
        table, identifiers = {}, set()
        for row in rows:
            if set(row) != {'element_id', 'matrix', 'rules'} or not isinstance(row['element_id'], str) or not row['element_id'] or row['element_id'] in identifiers:
                raise ValueError('Invalid or repeated element ID.')
            identifiers.add(row['element_id']); m = matrix(row['matrix'])
            if m not in group or m in table or not isinstance(row['rules'], list) or len(row['rules']) != 3:
                raise ValueError('Invalid or repeated group matrix/rules.')
            rules = {}
            for rule in row['rules']:
                if set(rule) != {'input_axis', 'output_axis', 'direction_multiplier', 'linear', 'offset'}:
                    raise ValueError('Invalid rule fields.')
                axis, target, sign = rule['input_axis'], rule['output_axis'], rule['direction_multiplier']
                if type(axis) is not int or axis not in range(3) or axis in rules or type(target) is not int or target not in range(3) or type(sign) is not int or sign not in (-1, 1):
                    raise ValueError('Invalid rule indices/sign.')
                linear, shift = matrix(rule['linear']), vector(rule['offset'])
                if linear != m:
                    raise ValueError('Incorrect affine linear part.')
                delta = tuple(m[i][axis] for i in range(3))
                # Canonical positive edge starts at the coordinatewise smaller endpoint.
                expected_shift = tuple(min(0, d) for d in delta)
                expected_delta = tuple(sign if i == target else 0 for i in range(3))
                if delta != expected_delta or shift != expected_shift:
                    raise ValueError('Incorrect canonical edge or reversal tag.')
                # Equal affine coefficients establish endpoints for arbitrary integer x.
                for orientation in (-1, 1):
                    for endpoint in (0, 1):
                        old_fraction = (1 - orientation) // 2 if endpoint == 0 else (1 + orientation) // 2
                        new_fraction = (1 - orientation * sign) // 2 if endpoint == 0 else (1 + orientation * sign) // 2
                        if tuple(shift[i] + (new_fraction if i == target else 0) for i in range(3)) != tuple(old_fraction * d for d in delta):
                            raise ValueError('Endpoint polynomial identity failed.')
                rules[axis] = (target, sign, shift)
            table[m] = rules
        if set(table) != group:
            raise ValueError('Export does not cover the cubic group.')
        compositions = 0
        for a in group:
            for b in group:
                ab = mm(a, b)
                for axis in range(3):
                    mid, sb, bb = table[b][axis]
                    target, sa, ba = table[a][mid]
                    expected = (target, sa * sb, tuple(x + y for x, y in zip(mv(a, bb), ba)))
                    if expected != table[ab][axis]:
                        raise ValueError('Affine composition/cocycle identity failed.')
                    compositions += 1
        for axis in range(3):
            if table[IDENTITY][axis] != (axis, 1, (0, 0, 0)):
                raise ValueError('Identity action failed.')
        for m in group:
            inverse = tuple(zip(*m))
            if inverse not in group or mm(m, inverse) != IDENTITY or mm(inverse, m) != IDENTITY:
                raise ValueError('Inverse action failed.')
        signatures = {tuple((axis, *table[m][axis][:2]) for axis in range(3)) for m in group}
        if len(signatures) != 48:
            raise ValueError('Action is not faithful.')
        periodic_cases = 0
        for extent in (2, 3, 4):
            for m in group:
                for base in product(range(extent), repeat=3):
                    for axis in range(3):
                        target, sign, shift = table[m][axis]
                        transformed = tuple((v + s) % extent for v, s in zip(mv(m, base), shift))
                        for coordinate in range(3):
                            lift = tuple(base[i] + (extent if i == coordinate else 0) for i in range(3))
                            if transformed != tuple((v + s) % extent for v, s in zip(mv(m, lift), shift)):
                                raise ValueError('Periodic lift independence failed.')
                        for orientation in (-1, 1):
                            start = list(base); end = list(base)
                            start[axis] += (1 - orientation) // 2; end[axis] += (1 + orientation) // 2
                            out_start = list(transformed); out_end = list(transformed)
                            out_start[target] += (1 - orientation * sign) // 2
                            out_end[target] += (1 + orientation * sign) // 2
                            if tuple(v % extent for v in mv(m, start)) != tuple(v % extent for v in out_start) or tuple(v % extent for v in mv(m, end)) != tuple(v % extent for v in out_end):
                                raise ValueError('Periodic endpoint mismatch.')
                            periodic_cases += 1
        return True, {'affine_rules': 144, 'composition_identities': compositions,
                      'periodic_directed_link_cases': periodic_cases, 'faithful_group_actions': len(signatures),
                      'unbounded_coordinate_method': 'equality of affine linear coefficients and constant offsets'}
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        return False, {'reason': str(exc)}


def main():
    art = ROOT / 'artifacts'
    try:
        passed, report = audit(json.loads((art / 'rows.json').read_text()))
    except (OSError, ValueError) as exc:
        passed, report = False, {'reason': str(exc)}
    decision = {'gate_id': 'YM3D_ORIENTED_LINK_ACTION_1', 'status': 'PASS' if passed else 'FAIL',
                'method': 'independent integer endpoint and affine-coefficient reconstruction', 'report': report,
                'closed_obligations': ['faithful cubic action on integer-lattice directed links',
                    'positive-axis canonicalization with correct base shift and traversal sign',
                    'all group-pair affine composition identities and inverses',
                    'periodic quotient endpoint and lift-independence audits at extents 2, 3, 4'] if passed else [],
                'non_claims': ['No composite-support lift, orbit partition or collision-graph identity',
                               'No gauge-field dynamics, analytic bound or mass-gap statement'],
                'next_obligation': 'YM3D_SUPPORT_LIFT_1'}
    (art / 'decision.json').write_text(json.dumps(decision, sort_keys=True, indent=2) + '\n')
    print(('PASS' if passed else 'FAIL') + ': YM3D_ORIENTED_LINK_ACTION_1')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
