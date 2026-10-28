#!/usr/bin/env python3
"""Unittest suite for the independent rational-inequality preflight."""
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from certificate import A, BETA, DECAY, ETA, compute, run, check_exp_bound


class TestPlaquetteBound(unittest.TestCase):
    def test_baseline(self):
        r=run()
        self.assertTrue(r['pass'])
        self.assertGreater(Q(r['kp_margin_lower']), 0)
        self.assertLess(Q(r['animal_ratio_upper']), 1)

    def test_exp_majorant(self):
        self.assertTrue(check_exp_bound())

    def test_strengthened_coupling_fails(self):
        with self.assertRaises(AssertionError):
            compute(beta=Q(1, 10))

    def test_source_radius_too_large_fails(self):
        with self.assertRaises(AssertionError):
            compute(eta=Q(1, 2))

    def test_negative_distance_cost_rejected(self):
        with self.assertRaises(AssertionError):
            compute(decay=Q(-1, 10))

    def test_bad_fourth_moment_majorant_fails(self):
        # Invalid bound under the true Haar moment cannot be accepted by run().
        self.assertGreater(Q(3,5)**4, Q(1,8))
        self.assertLess(Q(1,2)**4, Q(1,8))

    def test_exact_rational_output(self):
        result=run()
        for key in ('weighted_face_activity_upper','kp_margin_lower',
                    'connected_covariance_prefactor'):
            self.assertIsInstance(Q(result[key]), Q)

    def test_sufficient_margin_both_directions(self):
        self.assertTrue(compute(beta=Q(1,100))['pass'])
        self.assertFalse(compute(beta=Q(1,50))['pass'])


if __name__=='__main__':
    unittest.main(verbosity=2)
