#!/usr/bin/env python3
"""Independent arithmetic/scope audit for the CONDITIONAL mass-gap research ledger.

No analytic inequality, reflection positivity, OS reconstruction, or mass gap
is established by this script. The authoritative gate DAG remains unchanged.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path

PIN = "3456e5e75cf8d4cd558955a5c7638fba2d68f464"
OBLIGATIONS = (
    "wilson_observable_identification",
    "physical_reflection_positivity",
    "uniform_physical_distance_decay",
    "compatible_uv_ir_extraction",
    "dense_gauge_invariant_field_family",
    "continuum_spectral_support",
)
A_SAMPLES = (Fraction(96), Fraction(48), Fraction(24),
             Fraction(1), Fraction(1, 4))
TOY_SAMPLES = (Fraction(1, 2), Fraction(1, 4), Fraction(1, 8))


def fraction(value):
    if type(value) is not str or "/" not in value:
        raise ValueError("exact rationals must be numerator/denominator strings")
    number = Fraction(value)
    if value != f"{number.numerator}/{number.denominator}":
        raise ValueError("noncanonical rational")
    return number


def audit(doc):
    errors = []
    if not isinstance(doc, dict):
        return ["expected a JSON object"]
    if set(doc) != {"schema_version", "audit_kind", "source", "convention",
                    "coupling_examples", "collapsing_rate_toy", "obligations",
                    "claim_strength", "proves_continuum_mass_gap", "closes_gates"}:
        errors.append("invalid ledger key set")
    if doc.get("schema_version") != "1.0" or doc.get("audit_kind") != "3d_su2_continuum_mass_gap_boundary_not_a_proof":
        errors.append("invalid research scope")
    if doc.get("claim_strength") != "research_arithmetic_and_conditional_spectral_lemma_only":
        errors.append("claim strength was promoted")
    if doc.get("proves_continuum_mass_gap") is not False or doc.get("closes_gates") != []:
        errors.append("false mass-gap or proof-gate promotion")
    src = doc.get("source", {})
    if not isinstance(src, dict) or src != {
        "upstream_repository": "yang-mills-group/OpenAI-YM-20261028",
        "upstream_commit": PIN,
        "three_d_lane": "lanes/scalar_spectral_bridge/README.md",
    }:
        errors.append("upstream pin or 3D evidence lane mismatch")
    convention = doc.get("convention", {})
    if not isinstance(convention, dict) or convention != {
        "dimension": 3,
        "gauge_group": "SU(2)",
        "g3_squared": "1/1",
        "beta_formula": "4/(g3_squared*a)",
        "dobrushin_alpha_upper_formula": "12*beta",
        "sufficient_regime": "alpha_upper<1",
    }:
        errors.append("3D SU(2) coupling convention altered")
    try:
        coupling = doc["coupling_examples"]
        if not isinstance(coupling, list) or len(coupling) != len(A_SAMPLES):
            raise ValueError("missing/extra sample")
        for i, (row, a) in enumerate(zip(coupling, A_SAMPLES)):
            if not isinstance(row, dict) or set(row) != {
                "a", "beta", "alpha_upper", "in_sufficient_regime"
            }:
                raise ValueError(f"invalid row shape {i}")
            beta = Fraction(4, 1) / a  # sample uses g3_squared = 1
            alpha = 12 * beta
            if (fraction(row["a"]) != a
                    or fraction(row["beta"]) != beta
                    or fraction(row["alpha_upper"]) != alpha
                    or row["in_sufficient_regime"] is not (alpha < 1)):
                raise ValueError(f"wrong beta/alpha/threshold at sample {i}")
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as e:
        errors.append(f"3D coupling arithmetic mismatch: {e}")
    try:
        toy = doc["collapsing_rate_toy"]
        if not isinstance(toy, dict) or set(toy) != {
            "definition", "physical_mass_upper_bound", "examples",
            "physical_mass_lower_bound_proved"
        }:
            raise ValueError("invalid collapsing-rate record")
        if (toy["definition"] != "rho(a)=1-a*a"
                or toy["physical_mass_upper_bound"] != "a/(1-a*a)"
                or toy["physical_mass_lower_bound_proved"] is not False):
            raise ValueError("toy bound misrepresented as a proved physical gap")
        examples = toy["examples"]
        if not isinstance(examples, list) or len(examples) != len(TOY_SAMPLES):
            raise ValueError("missing/extra toy samples")
        prev = None
        for i, (row, a) in enumerate(zip(examples, TOY_SAMPLES)):
            if not isinstance(row, dict) or set(row) != {"a", "rho", "mass_upper"}:
                raise ValueError(f"invalid toy row shape {i}")
            rate = 1 - a * a
            upper = a / rate
            if (fraction(row["a"]) != a
                    or fraction(row["rho"]) != rate
                    or fraction(row["mass_upper"]) != upper):
                raise ValueError(f"wrong collapsing-rate arithmetic {i}")
            if not (0 < rate < 1 and upper > 0 and (prev is None or upper < prev)):
                raise ValueError("collapsing toy does not have decreasing mass upper bounds")
            prev = upper
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as e:
        errors.append(f"collapsing-rate arithmetic mismatch: {e}")
    obligations = doc.get("obligations")
    if (not isinstance(obligations, list) or len(obligations) != len(OBLIGATIONS)
            or any(not isinstance(row, dict) or set(row) != {"id", "status"}
                   for row in obligations)
            or [row["id"] for row in obligations if isinstance(row, dict)] != list(OBLIGATIONS)
            or any(row.get("status") != "open" for row in obligations if isinstance(row, dict))):
        errors.append("unmet continuum proof obligations promoted, missing or reordered")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        problems = audit(json.loads(args.ledger.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        problems = [f"invalid ledger: {exc}"]
    print(json.dumps({
        "status": "RESEARCH_SCOPE_PASS" if not problems else "FAIL",
        "arithmetical_scope_only": True,
        "analytic_theorem_verified": False,
        "proves_continuum_mass_gap": False,
        "closes_gates": [],
        "errors": problems,
    }, indent=2))
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
