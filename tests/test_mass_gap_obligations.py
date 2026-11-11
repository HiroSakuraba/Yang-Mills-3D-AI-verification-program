"""Adversarial checks of the research-only continuum mass-gap obligation ledger."""
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/upstream-4d-lean-audit/mass_gap_obligations.json"
CHECKER = ROOT / "tools/check_mass_gap_obligations.py"


class ContinuumMassGapBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads(LEDGER.read_text(encoding="utf-8"))

    def check(self, data, exit_code):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(CHECKER), str(path)],
                check=False, capture_output=True, text=True,
            )
        self.assertEqual(process.returncode, exit_code, process.stdout + process.stderr)
        report = json.loads(process.stdout)
        self.assertFalse(report["proves_continuum_mass_gap"])
        self.assertEqual(report["closes_gates"], [])
        return report

    def mutate(self, operation, keyword):
        doc = copy.deepcopy(self.seed)
        operation(doc)
        result = self.check(doc, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any(keyword in reason for reason in result["errors"]), result)

    def test_canonical_ledger_is_research_only(self):
        result = self.check(self.seed, 0)
        self.assertEqual(result["status"], "RESEARCH_SCOPE_PASS")
        self.assertFalse(result["analytic_theorem_verified"])

    def test_fake_mass_gap_rejected(self):
        self.mutate(lambda d: d.update(proves_continuum_mass_gap=True), "promotion")

    def test_fake_gate_closure_rejected(self):
        self.mutate(lambda d: d.update(closes_gates=["YM3D_FAKE_GAP_GATE"]), "promotion")

    def test_wrong_dimension_rejected(self):
        self.mutate(lambda d: d["convention"].update(dimension=4), "convention")

    def test_wrong_beta_at_one_spacing_rejected(self):
        self.mutate(lambda d: d["coupling_examples"][0].update(beta="1/25"), "coupling")

    def test_falsely_sufficient_weak_regime_rejected(self):
        self.mutate(lambda d: d["coupling_examples"][-1].update(in_sufficient_regime=True), "coupling")

    def test_wrong_alpha_rejected(self):
        self.mutate(lambda d: d["coupling_examples"][1].update(alpha_upper="1/2"), "coupling")

    def test_noncanonical_arithmetic_rejected(self):
        self.mutate(lambda d: d["coupling_examples"][0].update(a="192/2"), "coupling")

    def test_toy_mass_bound_tampering_rejected(self):
        self.mutate(lambda d: d["collapsing_rate_toy"]["examples"][-1].update(mass_upper="1/1"), "collapsing")

    def test_toy_improper_promotion_rejected(self):
        self.mutate(lambda d: d["collapsing_rate_toy"].update(physical_mass_lower_bound_proved=True), "collapsing")

    def test_missing_density_obligation_rejected(self):
        self.mutate(lambda d: d["obligations"].pop(4), "obligations")

    def test_claiming_uniform_physical_decay_rejected(self):
        self.mutate(lambda d: d["obligations"][2].update(status="proved"), "obligations")

    def test_wrong_upstream_pin_rejected(self):
        self.mutate(lambda d: d["source"].update(upstream_commit="main"), "pin")

    def test_unknown_success_field_rejected(self):
        self.mutate(lambda d: d.update(proves_wightman_mass_gap=True), "key set")

    def test_one_channel_can_miss_slow_state(self):
        # T has vacuum eigenvalue 1, slow nonvacuum mode 9/10, fast 1/2.
        # The measured fast channel satisfies a 3/5 rate, but the full
        # vacuum-orthogonal spectrum does not.
        for n in range(20):
            measured_channel = F(1, 2) ** n
            self.assertLessEqual(measured_channel, F(3, 5) ** n)
        self.assertGreater(F(9, 10), F(3, 5))

    def test_polynomial_lattice_prefactor_cannot_hide_slow_atom_forever(self):
        n = 100
        self.assertGreater(F(4, 5) ** n, (n + 1) ** 2 * F(3, 5) ** n)

    def test_positive_lattice_gaps_may_collapse_in_physical_units(self):
        # For rho(a)=1-a^2, -log(rho)/a <= a/(1-a^2) -> 0.
        previous = None
        for k in range(2, 12):
            a = F(1, 2**k)
            upper = a / (1 - a*a)
            self.assertLess(upper, 2*a)
            if previous is not None:
                self.assertLess(upper, previous)
            previous = upper


if __name__ == "__main__":
    unittest.main()
