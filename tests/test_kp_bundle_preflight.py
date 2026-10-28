#!/usr/bin/env python3
"""Stdlib-only negative controls for tools/verify_kp_bundle.py."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_kp_bundle import assess


class BundlePreflightTests(unittest.TestCase):
    def setUp(self):
        self.data = {}
        for name, report, label, horizon in (
            ("two_face_f22.json", "check_two_face_f22.json", "TWO_FACE_EXACT_SURFACES_1", 22),
            ("branched_f18.json", "check_branched_f18.json", "BRANCHED_SUPPORTS_EXACT_1", 18),
        ):
            row = {"N": 2, "A_abs": "8", "A_signed": "8"} if horizon == 22 else {"N": 2, "profiles": {"12,0,0,0,0": 2}}
            inp = {"complete": True, "fmax_requested": horizon, "per_F": {"6": row}}
            input_bytes = json.dumps(inp).encode()
            rep = {"id": label, "status": "PASS", "checker_fmax": horizon, "problems": [],
                   "per_F": {"6": row}, "generator_sha256": hashlib.sha256(input_bytes).hexdigest()}
            if horizon == 18:
                rep.update({"n2_cap": 6, "labellings_recomputed": 3433,
                            "single_link_splits_checked": 784})
            self.data["artifacts/" + name] = input_bytes
            self.data["artifacts/" + report] = json.dumps(rep).encode()

    def check(self):
        return assess(self.data.__getitem__)

    def test_valid(self):
        self.assertEqual(self.check(), [])

    def test_modified_generator(self):
        raw = self.data["artifacts/two_face_f22.json"]
        self.data["artifacts/two_face_f22.json"] = raw.replace(b'"N": 2', b'"N": 0')
        self.assertTrue(self.check())

    def test_missing_sha(self):
        key = "artifacts/check_branched_f18.json"
        report = json.loads(self.data[key]); del report["generator_sha256"]
        self.data[key] = json.dumps(report).encode()
        self.assertTrue(self.check())

    def test_fake_sha_but_count_disagrees(self):
        key = "artifacts/branched_f18.json"
        raw = self.data[key].replace(b'"N": 2', b'"N": 0')
        self.data[key] = raw
        ck = "artifacts/check_branched_f18.json"
        report = json.loads(self.data[ck]); report["generator_sha256"] = hashlib.sha256(raw).hexdigest()
        self.data[ck] = json.dumps(report).encode()
        self.assertTrue(any("count mismatch" in s for s in self.check()))

    def test_wrong_horizon(self):
        ck = "artifacts/check_two_face_f22.json"
        report = json.loads(self.data[ck]); report["checker_fmax"] = 12
        self.data[ck] = json.dumps(report).encode()
        self.assertTrue(self.check())

    def test_reduced_exact_coverage(self):
        ck = "artifacts/check_branched_f18.json"
        report = json.loads(self.data[ck]); report["n2_cap"] = 0
        self.data[ck] = json.dumps(report).encode()
        self.assertTrue(any("insufficient exact-labelling" in s for s in self.check()))

    def test_missing_report(self):
        del self.data["artifacts/check_two_face_f22.json"]
        self.assertTrue(self.check())


if __name__ == "__main__":
    unittest.main()
