"""Exact affine action on positively stored links with a traversal sign."""
import json
from pathlib import Path


def transform(rule, base, orientation=1, period=None):
    """Return transformed positive base, axis and traversal direction."""
    if orientation not in (-1, 1) or type(orientation) is not int:
        raise ValueError('Traversal orientation must be +1 or -1.')
    if len(base) != 3 or any(type(v) is not int for v in base):
        raise ValueError('Base must have three integer coordinates.')
    if period is not None and (type(period) is not int or period < 2):
        raise ValueError('Periodic extent must be an integer >= 2.')
    out = [sum(rule['linear'][i][j] * base[j] for j in range(3)) + rule['offset'][i] for i in range(3)]
    if period is not None:
        out = [v % period for v in out]
    return tuple(out), rule['output_axis'], orientation * rule['direction_multiplier']


def build_rows():
    source = Path(__file__).resolve().parents[3] / 'YM3D_M1A_OH_GROUP_GENERATOR_1' / 'artifacts' / 'oh_group_elements.json'
    elements = json.loads(source.read_text())
    rows = []
    for element in elements:
        matrix = element['matrix']; rules = []
        for axis in range(3):
            column = [matrix[i][axis] for i in range(3)]
            target = next(i for i, value in enumerate(column) if value)
            sign = column[target]; offset = [0, 0, 0]
            if sign == -1:
                offset[target] = -1
            rules.append({'input_axis': axis, 'output_axis': target,
                          'direction_multiplier': sign, 'linear': matrix, 'offset': offset})
        rows.append({'element_id': element['element_id'], 'matrix': matrix, 'rules': rules})
    return {'schema_version': 'ym3d.oriented_link_action.v1',
            'representation': 'positive_axis_base_with_traversal_sign', 'elements': rows,
            'periodic_audit_extents': [2, 3, 4]}
