import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from certificate import BETA_MAX,certify,run
from lattice_geometry import local_geometry,positive_links,face_links
from conditional_rg import coarsen_joint_law

class ExactArithmetic(unittest.TestCase):
    def test_default_certificate(self):self.assertTrue(run()['pass'])
    def test_ratio(self):self.assertEqual(certify()['dobrushin_row_sum_cap'],'18/19')
    def test_covariance_prefactor(self):self.assertEqual(certify()['wilson_covariance_prefactor_per_support_pair'],'76/1')
    def test_smaller_beta(self):self.assertTrue(certify(Q(9,100))['pass'])
    def test_zero_beta(self):self.assertTrue(certify(Q(0))['pass'])
    def test_strict_endpoint(self):self.assertFalse(certify(Q(1,8))['pass'])
    def test_above_endpoint(self):self.assertFalse(certify(Q(13,100))['pass'])
    def test_extra_neighbor_bad(self):self.assertFalse(certify(BETA_MAX,neighbor_cap=13)['pass'])
    def test_wrong_moment_bad(self):self.assertFalse(certify(BETA_MAX,s3_moment=Q(1,3))['pass'])
    def test_wrong_staples_bad(self):self.assertFalse(certify(BETA_MAX,staples=6)['pass'])
    def test_negative_beta_bad(self):
        with self.assertRaises(ValueError):certify(-Q(1,100))
    def test_exp_domain_bad(self):
        with self.assertRaises(ValueError):certify(Q(1,2))

class LinkGeometry(unittest.TestCase):
    def test_n4(self):
        m=local_geometry(4)
        self.assertEqual((m['face_count'],m['link_count']),(192,192))
        self.assertEqual((m['min_link_faces'],m['max_link_faces']),(4,4))
        self.assertEqual((m['min_neighbor_links'],m['max_neighbor_links']),(12,12))
        self.assertEqual(m['max_shared_faces_per_link_pair'],1)
    def test_n5(self):
        m=local_geometry(5)
        self.assertEqual(m['max_neighbor_links'],12)
        self.assertEqual(m['max_shared_faces_per_link_pair'],1)
    def test_reject_tiny(self):
        with self.assertRaises(ValueError):positive_links(3)
        with self.assertRaises(ValueError):face_links(2)

class RGConditionalCovariance(unittest.TestCase):
    def test_identity_map_no_contact(self):
        table=[((x,y),Q(1)) for x in (-1,1) for y in (-1,1)]
        r=coarsen_joint_law(table,lambda xy:xy)
        self.assertEqual(r['conditional_contact'],0)
        self.assertEqual(r['fine_cov'],0)
    def test_flat_map_with_correlation(self):
        table=[((-1,-1),Q(3)),((-1,1),Q(1)),((1,-1),Q(1)),((1,1),Q(3))]
        r=coarsen_joint_law(table,lambda xy:'coarse')
        self.assertEqual(r['fine_cov'],Q(1,2))
        self.assertEqual(r['coarse_cov'],0)
        self.assertEqual(r['conditional_contact'],Q(1,2))
    def test_projection_preserves_covariance_in_coarse(self):
        table=[((-1,-1),Q(3)),((-1,1),Q(1)),((1,-1),Q(1)),((1,1),Q(3))]
        r=coarsen_joint_law(table,lambda xy:xy[0])
        self.assertEqual(r['fine_cov'],Q(1,2))
        self.assertEqual(r['coarse_cov'],Q(1,2))
        self.assertEqual(r['conditional_contact'],0)
    def test_nonzero_contact_even_with_zero_fine_cov(self):
        table=[((x,y),Q(1)) for x in (-1,1) for y in (-1,1)]
        r=coarsen_joint_law(table,lambda xy:1 if xy==(1,1) else 0)
        self.assertEqual(r['fine_cov'],0)
        self.assertEqual(r['coarse_cov'],Q(1,3))
        self.assertEqual(r['conditional_contact'],-Q(1,3))
    def test_reject_negative_mass(self):
        with self.assertRaises(ValueError):coarsen_joint_law([((1,1),Q(-1)),((1,-1),Q(3))],lambda xy:0)

if __name__=='__main__':unittest.main()
