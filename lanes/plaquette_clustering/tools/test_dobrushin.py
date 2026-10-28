import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dobrushin import check,run

class TestDobrushin(unittest.TestCase):
    def test_bound(self):
        v=run()
        self.assertEqual(Q(v['dobrushin_alpha_upper']), Q(36,47))
        self.assertEqual(Q(v['wilson_prefactor_per_link_pair']),Q(188,11))
    def test_at_zero(self):
        self.assertEqual(Q(check(Q(0))['dobrushin_alpha_upper']),0)
    def test_threshold_is_fail_closed(self):
        self.assertFalse(check(Q(1,40))['pass'])
    def test_large_input_rejected(self):
        with self.assertRaises(AssertionError): check(Q(1,4))
    def test_negative_input_rejected(self):
        with self.assertRaises(AssertionError): check(Q(-1,100))

if __name__=='__main__':unittest.main(verbosity=2)
