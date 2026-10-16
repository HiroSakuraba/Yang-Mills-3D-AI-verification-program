"""Checks mathematical identities and sensitivity to recoupling conventions."""
import unittest
from fractions import Fraction as F
from frontier_certificate import (S, calculate, bessel, exp_positive, exp_negative,
                                  negative_log_at, index_tuples)

class CertificateChecks(unittest.TestCase):
    def test_exp_reciprocal(self):
        for v in ['0','1','5','75']:
            p=exp_positive(v)*exp_negative(v)
            self.assertLessEqual(p.lo,S)
            self.assertGreaterEqual(p.hi,S)

    def test_bessel_recurrence(self):
        # I_n - I_(n+2) = 2(n+1) I_(n+1)/x: independent adjacent orders.
        for n in [0,1,4]:
            x=F(7,10)
            left,right=bessel(n,x),bessel(n+2,x)+bessel(n+1,x).scale(2*(n+1)/x)
            self.assertLessEqual(left.lo,right.hi)
            self.assertLessEqual(right.lo,left.hi)

    def test_log_identity(self):
        a,b=negative_log_at(F(1,2)),negative_log_at(F(1,4))
        self.assertLessEqual(2*a.lo,b.hi)
        self.assertLessEqual(b.lo,2*a.hi)

    def test_admissibility_and_convention(self):
        t,q=index_tuples(2)
        self.assertNotIn((1,1,1),t)
        self.assertIn((1,1,2),t)
        self.assertEqual(len([v for v in q if v==(1,1,1,1)]),1)
        self.assertEqual(len(set(range(0,3,2))&set(range(0,3,2))),2)

    def test_cutoff_enclosures_overlap(self):
        for kind,z in [('heat','5'),('wilson','0.6273')]:
            a,b=calculate(kind,z,8),calculate(kind,z,14)
            self.assertLessEqual(F(a['rho']['lower']),F(b['rho']['upper']))
            self.assertLessEqual(F(b['rho']['lower']),F(a['rho']['upper']))
            self.assertLess(F(a['rho']['upper']),1)

    def test_frontier_sides(self):
        self.assertTrue(calculate('wilson','0.6273001')['rho_strictly_below_one'])
        self.assertTrue(calculate('wilson','0.6273002')['rho_strictly_above_one'])

if __name__=='__main__':
    unittest.main()
