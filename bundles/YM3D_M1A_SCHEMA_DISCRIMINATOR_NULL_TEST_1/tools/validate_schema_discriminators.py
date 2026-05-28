#!/usr/bin/env python3
"""Validate Milestone A schema discriminators.

This is the first executable gate for the YM3D constructive-RG Milestone A
program. It verifies that `schema_stage: combinatorial` rows accept only
combinatorial/gauge-geometric fields and reject analytic certificate fields.

Expected convention:
  * files whose basename starts with `valid_` must validate;
  * files whose basename starts with `invalid_` must fail validation.
"""
from __future__ import annotations

import argparse
import os
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", default="../../schemas/atom.schema.json")
    parser.add_argument("--fixtures", default="tests/schema_null_tests")
    parser.add_argument("--report", default="artifacts/schema_null_test_report.json")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    schema_path = (repo / args.schema).resolve()
    fixtures_dir = (repo / args.fixtures).resolve()
    report_path = (repo / args.report).resolve()

    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)

    results = []
    for fixture in sorted(fixtures_dir.glob("*.json")):
        instance = load_json(fixture)
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        valid = not errors
        if fixture.name.startswith("valid_"):
            expected_valid = True
        elif fixture.name.startswith("invalid_"):
            expected_valid = False
        else:
            raise ValueError(f"Fixture name must start with valid_ or invalid_: {fixture.name}")
        passed = valid == expected_valid
        results.append({
            "fixture": fixture.name,
            "expected_valid": expected_valid,
            "actual_valid": valid,
            "passed": passed,
            "error_count": len(errors),
            "errors": [
                {
                    "message": e.message,
                    "path": list(e.path),
                    "schema_path": list(e.schema_path),
                }
                for e in errors[:8]
            ],
        })

    report = {
        "gate_id": "YM3D_SCHEMA_DISCRIMINATOR_NULL_TEST_1",
        "schema": os.path.relpath(schema_path, repo),
        "fixtures_dir": os.path.relpath(fixtures_dir, repo),
        "case_count": len(results),
        "passed_count": sum(1 for r in results if r["passed"]),
        "failed_count": sum(1 for r in results if not r["passed"]),
        "all_passed": all(r["passed"] for r in results),
        "results": results,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
