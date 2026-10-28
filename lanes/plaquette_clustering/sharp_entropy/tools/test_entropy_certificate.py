#!/usr/bin/env python3
"""Negative controls for the exact-rational all-support majorant."""
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from entropy_certificate import (check, potential_certificate, branching_polynomials,
    exponential_upper, BETA, ETA, KP_A, DECAY, WITNESS_W, WITNESS_H)


class EntropyWitnessTest(unittest.TestCase):
    def test_valid_witness(self):
        v=potential_certificate()
        self.assertTrue(v['pass'])
        self.assertGreater(Q(v['admissible_growth_z']),Q(13967,100000))
        self.assertLess(Q(v['prefactor_H_to_fourth']),Q(308,100))

    def test_branching_polynomials(self):
        w=Q(1,3);g=branching_polynomials(w)
        self.assertEqual(g[1],3*w+3*w*w+w**3)
        self.assertEqual(g[2],1+2*w+w*w)
        self.assertEqual(g[3],1+w)
        self.assertEqual(g[4],1)

    def test_tampered_witness_fails(self):
        with self.assertRaises(ArithmeticError):
            potential_certificate(w=Q(1,2),H=WITNESS_H)

    def test_small_H_fails(self):
        with self.assertRaises(ArithmeticError):
            potential_certificate(w=WITNESS_W,H=Q(6,5))

    def test_exponential_bound(self):
        self.assertLess(exponential_upper(KP_A+DECAY),Q(27,20))

    def test_invalid_exponential_bound_fails(self):
        with self.assertRaises(ArithmeticError):
            check(exp_upper=Q(13,10))

    def test_invalid_haar_moment_fails(self):
        with self.assertRaises(ArithmeticError):
            check(haar_l4_upper=Q(1,2))

    def test_beta_09_passes(self):
        result=check()
        self.assertTrue(result['pass'])
        self.assertEqual(Q(result['beta_max']),Q(9,100))
        self.assertGreater(Q(result['kp_margin_lower']),Q(1,50))
        self.assertLess(Q(result['R_root_upper']),Q(45,1000))
        self.assertLess(Q(result['M_over_z']),1)

    def test_beta_095_rejected(self):
        with self.assertRaises(ArithmeticError):
            check(beta=Q(19,200))

    def test_source_disk_too_large_rejected(self):
        with self.assertRaises(ArithmeticError):
            check(eta=Q(1,20))

    def test_zero_coupling(self):
        self.assertTrue(check(beta=Q(0))['pass'])

    def test_no_negative_decay(self):
        with self.assertRaises(ValueError):
            check(decay=-Q(1,10))

    def test_no_zero_source_radius(self):
        with self.assertRaises(ValueError):
            check(eta=Q(0))

    def test_improved_at_old_beta(self):
        old=check(beta=Q(3,200))
        self.assertLess(Q(old['plaquette_covariance_prefactor']),Q(6,5))

if __name__=='__main__':unittest.main(verbosity=2)
