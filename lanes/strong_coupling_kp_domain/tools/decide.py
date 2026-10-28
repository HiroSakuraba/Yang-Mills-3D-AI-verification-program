#!/usr/bin/env python3
"""Decision for YM3D_STRONG_COUPLING_KP_DOMAIN_1 (lane-internal; not a program.yaml gate).

Writes artifacts/decision.json with status PASS only if
  1. both independent checker reports exist and say PASS
     (artifacts/check_two_face_f22.json, artifacts/check_branched_f18.json);
  2. the entropy constants hard-wired in analysis/kp_3d.py are re-certified by
     analysis/entropy.py (interval arithmetic);
  3. the Kotecky-Preiss condition 4 R(c) <= c is certified with interval arithmetic
     at the rational endpoints below, for the whole gas and for the two-face gas.
Monotonicity (every term of the bound increases with the character ratios r_a, which
increase with the Wilson beta and decrease with the heat-kernel time tau) extends each
endpoint statement to all smaller beta / larger tau.
"""
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "analysis"))

import entropy  # noqa: E402
import kp_3d  # noqa: E402

ART = os.path.join(ROOT, "artifacts")
TWO = os.path.join(ART, "two_face_f22.json")
BR = os.path.join(ART, "branched_f18.json")
CHK2 = os.path.join(ART, "check_two_face_f22.json")
CHKB = os.path.join(ART, "check_branched_f18.json")

WHOLE_WILSON = Fraction(37, 200)   # beta <= 0.185
WHOLE_HEAT = Fraction(819, 100)    # tau >= 8.19
TWO_WILSON = Fraction(1, 1)        # beta <= 1
TWO_HEAT = Fraction(19, 5)         # tau >= 3.8


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


EXPECTED = (
    (TWO, CHK2, "TWO_FACE_EXACT_SURFACES_1", 22),
    (BR, CHKB, "BRANCHED_SUPPORTS_EXACT_1", 18),
)


def audit_artifacts():
    """Check proof-report identity, exact input bytes, horizon and summary consistency."""
    problems = []
    for generator_path, checker_path, expected_id, fmax in EXPECTED:
        name = os.path.basename(generator_path)
        if not os.path.isfile(generator_path) or not os.path.isfile(checker_path):
            problems.append("missing input or checker report for " + name)
            continue
        try:
            with open(generator_path, encoding="utf-8") as fh:
                generator = json.load(fh)
            with open(checker_path, encoding="utf-8") as fh:
                check = json.load(fh)
            if not generator.get("complete") or generator.get("fmax_requested") != fmax:
                problems.append("incomplete generator or unexpected horizon for " + name)
            if (check.get("id") != expected_id or check.get("checker_fmax") != fmax
                    or check.get("status") != "PASS" or check.get("problems") != []):
                problems.append("invalid checker identity, horizon, or status for " + name)
            if check.get("generator_sha256") != sha(generator_path):
                problems.append("checker input SHA-256 mismatch for " + name)
            actual_per = generator.get("per_F", {})
            checked_per = check.get("per_F", {})
            if set(actual_per) != set(checked_per):
                problems.append("checker F-index mismatch for " + name)
            for f, checked in checked_per.items():
                if int(actual_per.get(f, {}).get("N", -1)) != checked.get("N"):
                    problems.append("checker count mismatch at F=%s for %s" % (f, name))
                    break
            if expected_id == "TWO_FACE_EXACT_SURFACES_1":
                for f, checked in checked_per.items():
                    observed = actual_per.get(f, {})
                    if (observed.get("A_abs") != checked.get("A_abs") or
                            observed.get("A_signed") != checked.get("A_signed")):
                        problems.append("checker weight mismatch at F=%s for %s" % (f, name))
                        break
            else:
                if (check.get("n2_cap", -1) < 6 or
                        check.get("labellings_recomputed", -1) < 3433 or
                        check.get("single_link_splits_checked", -1) < 784):
                    problems.append("branched checker exact-labelling/split coverage reduced")
                for f, checked in checked_per.items():
                    if actual_per.get(f, {}).get("profiles") != checked.get("profiles"):
                        problems.append("checker profile mismatch at F=%s for %s" % (f, name))
                        break
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as e:
            problems.append("invalid input/checker JSON for %s: %s" % (name, e))
    return problems


def main():
    problems = audit_artifacts()
    # Recompute analytic bounds only on a complete, matching input/checker pair.
    # Otherwise fail closed, without overwriting the last successful evidence.
    if problems:
        decision = {"gate_id": "YM3D_STRONG_COUPLING_KP_DOMAIN_1", "status": "FAIL",
                    "problems": problems, "report": {}, "claim_strength": "fallback_domain_only"}
        with open(os.path.join(ART, "decision.json"), "w") as fh:
            json.dump(decision, fh, indent=1)
        print(json.dumps({"status": "FAIL", "problems": problems}, indent=1))
        return 1
    # Entropy endpoint comparisons use mpmath interval objects all the way
    # through the acceptance decision (no lossy float coercions).
    from mpmath import iv
    phi_iv = iv.mpf(14143) / 10000
    ia = entropy.certify_intervals("all", Fraction(3247, 10000), phi_iv)
    ie = entropy.certify_intervals("even_cat", Fraction(1821, 5000), phi_iv)
    lim_z1 = iv.mpf(kp_3d.Z1_ALL.numerator) / kp_3d.Z1_ALL.denominator
    lim_ze = iv.mpf(kp_3d.Z_EVENCAT.numerator) / kp_3d.Z_EVENCAT.denominator
    if not (ia["z"].a >= lim_z1.b and (ia["R"] ** 4).b <= kp_3d.R4_ALL.a):
        problems.append("Lemma D (all) constants not re-certified")
    if not (ie["z"].a >= lim_ze.b):
        problems.append("Lemma D (even, Catalan) constant not re-certified")
    two = kp_3d.load_two_face(TWO)
    br = kp_3d.load_branched(BR)
    ca = entropy.certify("all", Fraction(3247, 10000), phi_iv)
    ce = entropy.certify("even_cat", Fraction(1821, 5000), phi_iv)
    report = {"inputs_sha256": {os.path.basename(p): sha(p) for p in (TWO, BR, CHK2, CHKB)},
              "lemma_D_all": ca, "lemma_D_even_catalan": ce,
              "acceptance_arithmetic": "mpmath.iv endpoint comparisons; display floats excluded"}
    for name, kind, par in (("whole_gas_wilson", "wilson", WHOLE_WILSON), ("whole_gas_heat", "heat", WHOLE_HEAT)):
        # tail bound (a) only: every term is then increasing in the character ratios,
        # so the endpoint statement extends to all smaller beta / larger tau
        b = kp_3d.best(kind, par, two, br, tail_mode="plain")[0]
        ok = b is not None and b[0].a > 0
        report[name] = {"parameter": str(par), "kp_holds": ok,
                        "margin_lower": None if b is None else float(b[0].a),
                        "c": None if b is None else float(b[1].a),
                        "R_upper": None if b is None else float(b[2]["total"].b)}
        if not ok:
            problems.append("KP not certified for %s at %s" % (name, par))
    for name, kind, par in (("two_face_gas_wilson", "wilson", TWO_WILSON), ("two_face_gas_heat", "heat", TWO_HEAT)):
        ok = kp_3d.two_face_only_ok(kind, par, two)
        report[name] = {"parameter": str(par), "kp_holds": ok}
        if not ok:
            problems.append("two-face KP not certified for %s at %s" % (name, par))
    decision = {
        "gate_id": "YM3D_STRONG_COUPLING_KP_DOMAIN_1",
        "registration": "research lane; not in program.yaml; analytic stage, so a program gate "
                        "would be held by the 2D-validation meta-guard",
        "status": "PASS" if not problems else "FAIL",
        "claim_strength": "fallback_domain_only",
        "method": "exact enumeration with independent re-enumeration and Weingarten checks; "
                  "potential-method counting; Finner's inequality; Kotecky-Preiss with mpmath interval arithmetic",
        "closed_obligations": [
            "every surviving plaquette support through a plaquette of Z^3 with F <= 18 listed exactly "
            "(two-face surfaces to F <= 22), independently re-enumerated",
            "exact SU(2) Haar weights of those supports for spins 1/2 and 1 (up to 8 spin-1 faces), "
            "independently recomputed up to 6 spin-1 faces",
            "counting constants in Z^3: two-face 3, all supports 7.16, even supports 3.47 per face",
            "Kotecky-Preiss for the whole strong-coupling polymer gas of the 3D SU(2) Wilson action "
            "for beta <= 37/200, and of the heat-kernel action for tau >= 819/100",
            "Kotecky-Preiss for the gas of closed two-face surfaces alone for Wilson beta <= 1 "
            "and heat-kernel tau >= 19/5",
        ],
        "non_claims": [
            "No mass gap, clustering of observables, or transfer-matrix statement: observable "
            "insertions and boundary terms are not treated",
            "Not the fallback-basin certification row: applies to single-plaquette class-function "
            "actions only; no overlap/majorization with an RG-produced effective action",
            "No continuum, lattice-spacing-uniform or volume-uniform physical statement beyond "
            "the polymer-gas KP condition, which is volume-uniform by construction",
            "Branched supports carrying spin-1 faces are bounded only through Finner's inequality",
        ],
        "next_obligation": "overlap check: show a terminal-scale effective action lies in this domain, "
                           "or sharpen branched-support counting toward the two-face rate",
        "report": report,
        "problems": problems,
    }
    with open(os.path.join(ART, "decision.json"), "w") as fh:
        json.dump(decision, fh, indent=1)
    print(json.dumps({k: decision[k] for k in ("status", "problems")}, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
