"""Exact regression and corruption controls; checker imports no generator."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from ym3d_link_action import build_rows, transform
spec = importlib.util.spec_from_file_location('independent_link_checker', ROOT / 'tools' / 'check_link_action.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class LinkActionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_rows()

    def test_full_independent_audit(self):
        passed, report = checker.audit(self.data)
        self.assertTrue(passed, report)
        self.assertEqual(report['composition_identities'], 48 * 48 * 3)
        self.assertEqual(report['periodic_directed_link_cases'], 48 * 6 * (8 + 27 + 64))

    def test_reflection_shift_and_reversal(self):
        row = next(r for r in self.data['elements'] if r['matrix'] == [[-1,0,0],[0,1,0],[0,0,1]])
        rule = row['rules'][0]
        self.assertEqual(transform(rule, (3, 2, -1)), ((-4, 2, -1), 0, -1))
        self.assertEqual(transform(rule, (3, 2, -1), -1, 4), ((0, 2, 3), 0, 1))

    def test_corruptions_rejected(self):
        mutations = []
        a = deepcopy(self.data); a['elements'][0]['rules'][0]['offset'][0] += 1; mutations.append(a)
        a = deepcopy(self.data); a['elements'][0]['rules'][0]['direction_multiplier'] *= -1; mutations.append(a)
        a = deepcopy(self.data); a['elements'][0]['rules'][0]['linear'][0][0] = 7; mutations.append(a)
        a = deepcopy(self.data); a['elements'][0]['rules'][0]['input_axis'] = False; mutations.append(a)
        a = deepcopy(self.data); a['elements'].pop(); mutations.append(a)
        a = deepcopy(self.data); a['elements'][1] = a['elements'][0]; mutations.append(a)
        a = deepcopy(self.data); a['periodic_audit_extents'] = [3, 4]; mutations.append(a)
        for data in mutations:
            self.assertFalse(checker.audit(data)[0])

    def test_invalid_traversal_and_period(self):
        rule = self.data['elements'][0]['rules'][0]
        with self.assertRaises(ValueError): transform(rule, (0, 0, 0), True)
        with self.assertRaises(ValueError): transform(rule, (0, 0, 0), period=1)


if __name__ == '__main__':
    unittest.main()
