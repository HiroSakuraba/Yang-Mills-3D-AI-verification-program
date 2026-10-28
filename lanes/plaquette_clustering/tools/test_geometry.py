import sys
from fractions import Fraction as Q
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from leading_cube import cube_faces, common_cubes, coefficient, incident_cubes

class TestGeometry(unittest.TestCase):
    def test_cube_has_six_faces(self):
        for corner in [(0,0,0),(4,-2,3)]:
            self.assertEqual(len(cube_faces(corner)),6)
    def test_each_face_belongs_to_two_cubes(self):
        for f in cube_faces((0,0,0)):
            self.assertEqual(len(incident_cubes(f)),2)
            self.assertTrue(all(f in cube_faces(c) for c in incident_cubes(f)))
    def test_opposite_faces_one_cube(self):
        p=(2,(0,0,0)); q=(2,(0,0,1))
        self.assertEqual(common_cubes(p,q),((0,0,0),))
        self.assertEqual(coefficient(p,q),Q(1,1024))
    def test_far_faces_none(self):
        self.assertEqual(coefficient((2,(0,0,0)),(2,(0,0,3))),0)
    def test_same_face_rejected(self):
        with self.assertRaises(ValueError):
            coefficient((2,(0,0,0)),(2,(0,0,0)))

if __name__=='__main__': unittest.main(verbosity=2)
