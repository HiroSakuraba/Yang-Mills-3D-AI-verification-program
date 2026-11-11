"""Independent negative controls for a fixed-census finite signed gas."""
import copy
import itertools
from fractions import Fraction
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / 'tools/build_finite_gas_transfer.py'
CHECK = ROOT / 'tools/check_finite_gas_transfer.py'


class FiniteGasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'seed.json'
            subprocess.run([sys.executable, str(GEN), '--output', str(out)], check=True, capture_output=True)
            cls.seed = json.loads(out.read_text(encoding='utf-8'))

    def check(self, obj, expected_code):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'case.json'
            path.write_text(json.dumps(obj), encoding='utf-8')
            p = subprocess.run([sys.executable, str(CHECK), str(path)], capture_output=True, text=True)
            self.assertEqual(p.returncode, expected_code, p.stdout + p.stderr)
            return json.loads(p.stdout)

    def test_seed(self):
        result = self.check(self.seed, 0)
        self.assertEqual(result['status'], 'RESEARCH_EXAMPLE_PASS')
        self.assertFalse(result['proves_3d_rg'])

    def test_wrong_source_pin(self):
        v = copy.deepcopy(self.seed)
        v['source']['commit'] = 'main'
        self.assertIn('source identity/pin mismatch', self.check(v, 1)['errors'])

    def test_tampered_bound(self):
        v = copy.deepcopy(self.seed)
        v['global_product_bound'] = '0/1'
        self.assertTrue(any('global_product_bound' in z for z in self.check(v, 1)['errors']))

    def test_tampered_gas(self):
        v = copy.deepcopy(self.seed)
        v['gas_p'] = '1/1'
        self.assertTrue(any('gas_p' in z for z in self.check(v, 1)['errors']))

    def test_different_eligibility(self):
        v = copy.deepcopy(self.seed)
        v['same_admissibility_for_p_and_q'] = False
        self.assertTrue(any('admissibility' in z for z in self.check(v, 1)['errors']))

    def test_incorrect_support_lift(self):
        v = copy.deepcopy(self.seed)
        v['entries'][0]['support'][0] = [20, 20, 20]
        self.assertTrue(any('support' in z for z in self.check(v, 1)['errors']))

    def test_missing_cover(self):
        v = copy.deepcopy(self.seed)
        v['admissible_subsets'] = []
        self.assertTrue(any('admissible subsets' in z for z in self.check(v, 1)['errors']))

    def test_underbounded_signed_activity(self):
        v = copy.deepcopy(self.seed)
        v['entries'][0]['majorant'] = '1/100'
        self.assertTrue(any('majorant' in z for z in self.check(v, 1)['errors']))

    def test_noncanonical_rational(self):
        v = copy.deepcopy(self.seed)
        v['entries'][0]['activity_p'] = '2/16'
        self.assertTrue(any('rational' in z for z in self.check(v, 1)['errors']))

    def test_changed_flags(self):
        v = copy.deepcopy(self.seed)
        v['flags'] = [[3, 0, 0]]
        self.assertTrue(any('admissible subsets' in z for z in self.check(v, 1)['errors']))

    def test_exhaustive_two_label_signed_grid(self):
        # Finite statement stress-test: every admissibility family on two
        # labels and all coefficients in {-1, 0, 1} for both models.
        universe = [(), (0,), (1,), (0, 1)]
        for mask in range(16):
            families = [part for index, part in enumerate(universe) if mask & (1 << index)]
            for p0, p1, q0, q1 in itertools.product((-1, 0, 1), repeat=4):
                p, q = (Fraction(p0), Fraction(p1)), (Fraction(q0), Fraction(q1))
                h = (Fraction(1), Fraction(1))
                def term(v, subset):
                    prod = Fraction(1)
                    for i in subset:
                        prod *= v[i]
                    return prod
                z_p = sum((term(p, subset) for subset in families), Fraction(0))
                z_q = sum((term(q, subset) for subset in families), Fraction(0))
                local = sum((abs(p[i]-q[i])*term(h, tuple(j for j in subset if j != i))
                             for subset in families for i in subset), Fraction(0))
                global_bound = sum((abs(p[i]-q[i])*(1+h[1-i]) for i in range(2)), Fraction(0))
                self.assertLessEqual(abs(z_p-z_q), local)
                self.assertLessEqual(local, global_bound)

    def test_eligibility_change_counterexample(self):
        # Identical coefficient vectors with distinct masks can change the gas.
        p = Fraction(1)
        left = Fraction(1) + p
        right = Fraction(1)
        delta = abs(p - p)
        self.assertEqual(delta, 0)
        self.assertNotEqual(left, right)


if __name__ == '__main__':
    unittest.main()
