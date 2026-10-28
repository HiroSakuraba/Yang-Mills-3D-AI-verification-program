#!/usr/bin/env python3
"""Fail-closed regression controls for the KP-domain archived certificate.

Run after the two independent checkers have regenerated their SHA-bound reports:
    python tools/test_integrity.py

No checker enumeration is skipped by pretending these tests prove the lemmas.
These tests specifically audit the archived report/decision trust boundary.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def decide(root):
    run = subprocess.run([sys.executable, str(root / "tools/decide.py")],
                         cwd=root, capture_output=True, text=True, timeout=45)
    decision = json.loads((root / "artifacts/decision.json").read_text())
    assert (run.returncode == 0) == (decision["status"] == "PASS"), (run.stdout, run.stderr)
    return decision


def change_json(path, op):
    d = json.loads(path.read_text())
    op(d)
    path.write_text(json.dumps(d, indent=1) + "\n")


def run_case(name, change, expected):
    with tempfile.TemporaryDirectory(prefix="kp-integrity-") as tmp:
        root = Path(tmp)
        for rel in ("analysis", "tools"):
            shutil.copytree(ROOT / rel, root / rel, ignore=shutil.ignore_patterns("__pycache__"))
        (root / "artifacts").mkdir()
        for f in ("two_face_f22.json", "branched_f18.json", "check_two_face_f22.json", "check_branched_f18.json"):
            shutil.copy2(ROOT / "artifacts" / f, root / "artifacts" / f)
        change(root / "artifacts")
        result = decide(root)
        assert result["status"] == expected, (name, result)
        print(f"{name}: {expected}")


def no_change(_):
    pass


def rewrite_count(art, name):
    change_json(art / name, lambda x: x["per_F"]["6"].__setitem__("N", 0))


def fake_new_digest(art):
    gen = art / "two_face_f22.json"
    rewrite_count(art, gen.name)
    fresh = hashlib.sha256(gen.read_bytes()).hexdigest()
    change_json(art / "check_two_face_f22.json", lambda d: d.__setitem__("generator_sha256", fresh))


def wrong_fmax(art):
    change_json(art / "check_branched_f18.json", lambda d: d.__setitem__("checker_fmax", 12))


def old_report(art):
    change_json(art / "check_two_face_f22.json", lambda d: d.pop("generator_sha256", None))


def checker_fail(art):
    change_json(art / "check_branched_f18.json", lambda d: d.__setitem__("status", "FAIL"))


def reduced_cap(art):
    change_json(art / "check_branched_f18.json", lambda d: d.__setitem__("n2_cap", 0))


def no_report(art):
    (art / "check_two_face_f22.json").unlink()


def malformed(art):
    (art / "branched_f18.json").write_text("{ not json")


def main():
    for name, fn, status in (
        ("untampered-baseline", no_change, "PASS"),
        ("changed-two-face-count", lambda a: rewrite_count(a, "two_face_f22.json"), "FAIL"),
        ("changed-branched-count", lambda a: rewrite_count(a, "branched_f18.json"), "FAIL"),
        ("forged-matching-digest-but-count-disagrees", fake_new_digest, "FAIL"),
        ("checker-wrong-horizon", wrong_fmax, "FAIL"),
        ("legacy-unbound-report", old_report, "FAIL"),
        ("reduced-exact-coverage", reduced_cap, "FAIL"),
        ("checker-reported-failure", checker_fail, "FAIL"),
        ("missing-checker-report", no_report, "FAIL"),
        ("malformed-generator", malformed, "FAIL"),
    ):
        run_case(name, fn, status)
    print("ALL 10 INTEGRITY CONTROLS PASS")


if __name__ == "__main__":
    main()
