#!/usr/bin/env python3
"""Check integrity bindings for a supplied YM3D KP-domain research bundle.

This is a dependency-free import preflight, NOT an independent Haar/KP proof.
Usage: python tools/verify_kp_bundle.py PATH_TO_ZIP_OR_EXTRACTED_LANE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import zipfile

CHECKS = (("two_face_f22.json", "check_two_face_f22.json", "TWO_FACE_EXACT_SURFACES_1", 22),
          ("branched_f18.json", "check_branched_f18.json", "BRANCHED_SUPPORTS_EXACT_1", 18))


def assess(read_bytes):
    issues = []
    for input_name, report_name, expected_id, expected_horizon in CHECKS:
        try:
            input_bytes = read_bytes("artifacts/" + input_name)
            report_bytes = read_bytes("artifacts/" + report_name)
            data = json.loads(input_bytes)
            report = json.loads(report_bytes)
            if not data.get("complete") or data.get("fmax_requested") != expected_horizon:
                issues.append(input_name + ": incomplete or incorrect enumeration horizon")
            if (report.get("status") != "PASS" or report.get("id") != expected_id or
                    report.get("checker_fmax") != expected_horizon or report.get("problems") != []):
                issues.append(report_name + ": checker status/identity/horizon invalid")
            if report.get("generator_sha256") != hashlib.sha256(input_bytes).hexdigest():
                issues.append(report_name + ": stale or absent SHA-256 input binding")
            cp = report.get("per_F", {})
            gp = data.get("per_F", {})
            if set(cp) != set(gp):
                issues.append(report_name + ": enumerated F keys disagree")
            for key, check in cp.items():
                gen = gp.get(key, {})
                if gen.get("N") != check.get("N"):
                    issues.append(report_name + ": count mismatch at F=" + key)
                if expected_id == "TWO_FACE_EXACT_SURFACES_1":
                    if (gen.get("A_abs"), gen.get("A_signed")) != (check.get("A_abs"), check.get("A_signed")):
                        issues.append(report_name + ": Haar-sum mismatch at F=" + key)
                elif gen.get("profiles") != check.get("profiles"):
                    issues.append(report_name + ": valence-profile mismatch at F=" + key)
        except (KeyError, OSError, ValueError, TypeError, AttributeError) as exc:
            issues.append(input_name + ": missing or malformed evidence: " + str(exc))
    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bundle", help="ZIP or extracted lane directory")
    args = ap.parse_args()
    src = pathlib.Path(args.bundle)
    if not src.exists():
        ap.error("bundle does not exist")
    if src.is_file():
        with zipfile.ZipFile(src) as z:
            files = [n for n in z.namelist() if n.endswith("artifacts/two_face_f22.json")]
            if len(files) != 1:
                ap.error("exactly one lane directory expected in ZIP")
            prefix = files[0][:-len("artifacts/two_face_f22.json")]
            issues = assess(lambda f: z.read(prefix + f))
    else:
        issues = assess(lambda f: (src / f).read_bytes())
    print(json.dumps({"status": "FAIL" if issues else "PASS", "problems": issues}, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
