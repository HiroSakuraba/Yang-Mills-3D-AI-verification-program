"""Finite geometry and exact finite-group Wilson transfer regression tests.

These are toy/geometry checks only, not a machine proof of SU(2) clustering.
"""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/check_finite_volume_transfer.py"
spec = importlib.util.spec_from_file_location("check_finite_volume_transfer", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FiniteVolumeTransferTests(unittest.TestCase):
    def test_research_scope_explicit_in_output(self):
        import json
        process = subprocess.run(
            [sys.executable, str(SOURCE)], cwd=ROOT,
            text=True, capture_output=True, check=True,
        )
        report = json.loads(process.stdout)
        self.assertEqual(report["status"], "RESEARCH_SANITY_PASS")
        self.assertIs(report["proves_su2_analytic_gap"], False)
        self.assertIs(report["proves_continuum_mass_gap"], False)
        self.assertEqual(report["closes_gates"], [])

    def test_non_degenerate_3d_slab_geometry(self):
        report = mod.graph_audit()
        self.assertEqual(report["link_count"], 99)
        self.assertEqual(report["plaquette_count"], 90)
        self.assertEqual(report["max_face_incidence_per_link"], 4)
        self.assertEqual(report["max_neighbor_links"], 12)
        self.assertEqual(report["max_pair_face_multiplicity"], 1)

    def test_distance_from_spatial_slice_equals_time_steps(self):
        report = mod.graph_audit()
        self.assertEqual(report["time_slice_min_distances"], {
            "1": 1, "2": 2, "3": 3,
        })

    def test_other_spatial_volumes_preserve_incidence(self):
        for L in (3, 4, 5):
            links, faces, incidence, adjacency, multiplicity = mod.cubic_time_slab(L, 2)
            self.assertEqual(len(links), 8*L*L)
            self.assertEqual(len(faces), 7*L*L)
            self.assertEqual(max(incidence.values()), 4)
            self.assertEqual(max(map(len, adjacency.values())), 12)
            self.assertEqual(max(multiplicity.values()), 1)

    def test_one_time_slab(self):
        links, faces, incidence, adjacency, multiplicity = mod.cubic_time_slab(4, 1)
        self.assertEqual(len(links), 5*16)
        self.assertEqual(len(faces), 4*16)
        self.assertEqual(max(multiplicity.values()), 1)

    def test_short_periods_rejected(self):
        for L, T in ((2, 3), (1, 1), (3, 0), (3, -1)):
            with self.subTest(L=L, T=T):
                with self.assertRaises(ValueError):
                    mod.cubic_time_slab(L, T)

    def test_z2_direct_slab_matches_physical_transfer(self):
        result = mod.z2_exact_transfer()
        self.assertEqual(result["physical_basis"], ["one", "plaquette_flux"])
        self.assertIs(result["gauge_slab_equals_positive_BKB"], True)

    def test_z2_transfer_is_symmetric(self):
        mat = [[Q(x) for x in row]
               for row in mod.z2_exact_transfer()["physical_transfer_matrix"]]
        self.assertEqual(mat[0][1], mat[1][0])
        self.assertGreater(mat[0][0], 0)
        self.assertGreater(mat[1][1], 0)

    def test_z2_positive_determinant_and_conservative_alpha(self):
        result = mod.z2_exact_transfer()
        mat = [[Q(x) for x in row] for row in result["physical_transfer_matrix"]]
        det = mat[0][0]*mat[1][1] - mat[0][1]*mat[1][0]
        self.assertEqual(det, Q(result["transfer_determinant"]))
        self.assertGreater(det, 0)
        self.assertLess(Q(result["spectral_ratio_upper"]),
                        Q(result["dobrushin_conservative_alpha"]))
        self.assertLess(Q(result["dobrushin_conservative_alpha"]), 1)

    def test_gauge_orbits_and_complete_physical_basis(self):
        # A square graph has 4 links and 4 vertices; under Z2 vertex gauge
        # transformations its invariant function space has dimension 2,
        # with orbit labels equal to the plaquette flux.
        from itertools import product
        states = list(product((-1, 1), repeat=4))
        gauges = states
        orbits = set()
        for u in states:
            orbit = frozenset(tuple(
                u[e]*h[e]*h[(e+1) % 4] for e in range(4)
            ) for h in gauges)
            orbits.add(orbit)
        self.assertEqual(len(orbits), 2)
        self.assertEqual(sorted(len(o) for o in orbits), [8, 8])
        self.assertEqual({next(iter(o))[0]*next(iter(o))[1]*
                          next(iter(o))[2]*next(iter(o))[3]
                          for o in orbits}, {-1, 1})

    def test_fixed_observable_can_miss_an_excitation(self):
        # Abstract, exactly diagonal, positive transfer with one vacuum
        # and two different excited-state decay rates. A selected channel
        # need not see the slowest nonvacuum mode.
        rates = (Q(1), Q(9, 10), Q(1, 2))
        for n in range(1, 16):
            self.assertLessEqual(rates[2] ** n, Q(3, 5) ** n)
            self.assertGreater(rates[1] ** n, Q(3, 5) ** n)


if __name__ == "__main__":
    unittest.main()
