import unittest
from fractions import Fraction as F
from independent_wilson_check import cube_contraction,link_incidence_row,dobrushin
from frontier_certificate import bessel, S

class IndependentChecks(unittest.TestCase):
    def test_exact_cube_breaks_vertex_parity_rule(self):
        r=cube_contraction()
        self.assertEqual(r['active_edge_degrees'],[3]*8)
        self.assertEqual(F(r['ordinary_character_haar_integral']),F(1,16))

    def test_cube_convention_factors(self):
        r=cube_contraction()
        ordinary=F(r['ordinary_character_haar_integral'])
        normalized=F(r['normalized_character_haar_integral'])
        self.assertEqual(ordinary,64*normalized)
        self.assertEqual(64*ordinary,4)  # dimension-weighted characters violate |I|<=1.

    def test_geometry_in_several_dimensions(self):
        for d in [2,3,4,5]:
            row=link_incidence_row(d)
            self.assertEqual(row['plaquettes_through_link'],2*(d-1))
            self.assertEqual(row['other_link_incidences'],6*(d-1))
            self.assertEqual(row['max_shared_plaquette_multiplicity'],1)

    def test_normalization_at_zero_coupling(self):
        x=F(1,10**6)
        t=bessel(2,x).div(bessel(1,x)).scale(1/x)
        c=t.scale(2)
        self.assertGreater(F(c.lo,S),F(1,2)-F(1,10**10))
        self.assertLess(F(c.hi,S),F(1,2))
        self.assertLess(F(t.hi,S),F(26,100))
        self.assertGreater(F(c.lo,S),F(49,100))

    def test_strict_influence_crossing(self):
        self.assertTrue(dobrushin('0.0556128')['passes'])
        self.assertFalse(dobrushin('0.0556129')['passes'])
        self.assertTrue(dobrushin('0.05')['passes'])

if __name__=='__main__':unittest.main()
