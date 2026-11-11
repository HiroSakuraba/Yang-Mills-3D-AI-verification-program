"""Adversarial tests for source-pinned research-only crosswalk metadata."""
import copy
import json
import unittest
from pathlib import Path

from tools.audit_upstream_ym4 import validate_crosswalk, read_program_gate_ids, parse_source_roots

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/upstream-4d-lean-audit/crosswalk.json"


class TestUpstreamCrosswalk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.gates = read_program_gate_ids(ROOT / "program.yaml")

    def test_valid_research_only_map(self):
        self.assertEqual(validate_crosswalk(self.base, self.gates), [])

    def test_unpinned_source_url_rejected(self):
        v = copy.deepcopy(self.base)
        v["records"][0]["source_url"] = "https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/main/PublicWilson.lean"
        self.assertTrue(any("not pinned" in e for e in validate_crosswalk(v, self.gates)))

    def test_no_3d_proof_promotion(self):
        v = copy.deepcopy(self.base)
        v["records"][0]["claim_strength"] = "transferred_and_verified"
        self.assertTrue(any("unverified proof/transfer" in e for e in validate_crosswalk(v, self.gates)))

    def test_no_gate_closure_promotion(self):
        v = copy.deepcopy(self.base)
        v["records"][0]["gate_closed"] = True
        self.assertTrue(any("forbidden gate-closure" in e for e in validate_crosswalk(v, self.gates)))

    def test_duplicate_record_rejected(self):
        v = copy.deepcopy(self.base)
        v["records"][1]["id"] = v["records"][0]["id"]
        self.assertTrue(any("duplicate record" in e for e in validate_crosswalk(v, self.gates)))

    def test_unrecognized_gate_rejected(self):
        v = copy.deepcopy(self.base)
        v["records"][0]["target_gate"] = "YM3D_INVENTED_GATE_1"
        self.assertTrue(any("absent from program.yaml" in e for e in validate_crosswalk(v, self.gates)))

    def test_unsafe_path_rejected(self):
        v = copy.deepcopy(self.base)
        v["records"][0]["path"] = "../../leak.txt"
        self.assertTrue(any("unsafe" in e for e in validate_crosswalk(v, self.gates)))

    def test_bad_upstream_revision_rejected(self):
        v = copy.deepcopy(self.base)
        v["upstreams"][0]["commit"] = "main"
        self.assertTrue(any("full lowercase Git SHA" in e for e in validate_crosswalk(v, self.gates)))

    def test_missing_transfer_boundary_rejected(self):
        v = copy.deepcopy(self.base)
        v["global_nonclaims"] = []
        self.assertTrue(any("non-claims" in e for e in validate_crosswalk(v, self.gates)))

    def test_strict_source_root_labels(self):
        with self.assertRaises(ValueError):
            parse_source_roots(["october=/tmp/x", "october=/tmp/y"])


if __name__ == "__main__":
    unittest.main()
