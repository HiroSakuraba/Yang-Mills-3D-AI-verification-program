#!/usr/bin/env python3
"""Validate a source-pinned 4D-to-3D research crosswalk.

This is an audit of metadata and (optionally) pinned source anchors.
It is not a Lean proof checker and NEVER emits a gate decision.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs/upstream-4d-lean-audit/crosswalk.json"
GATE_RE = re.compile(r"^[A-Z0-9_]+$")
ID_RE = re.compile(r"^[a-z][a-z0-9-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CATEGORIES = {
    "interface_pattern", "dimension_obstruction", "scope_reference",
    "analytic_candidate", "verification_pattern", "review_scope",
    "mass_gap_boundary",
}
ALLOWED_STRENGTHS = {"candidate_only", "no_direct_transfer", "engineering_reuse_only"}
PROHIBITED_CLAIM_WORDS = {"transferred", "certified_3d", "proved_3d", "closed_gate"}


def validate_crosswalk(data: dict, known_gates: set[str] | None = None) -> list[str]:
    """Pure, independent structural audit of the research crosswalk."""
    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if data.get("audit_id") != "YM3D_UPSTREAM_4D_CONSTRUCTION_AUDIT_0":
        errors.append("audit_id differs from registered research lane")
    if data.get("audit_status") != "research_only_not_a_closed_gate":
        errors.append("audit must remain research_only_not_a_closed_gate")
    if data.get("transfer_certificates") != []:
        errors.append("transfer certificates require a new, separately reviewed gate")
    if set(data.get("allowed_claim_strengths", [])) != ALLOWED_STRENGTHS:
        errors.append("allowed claim strengths must match the frozen non-proof set")
    if len(data.get("global_nonclaims", [])) < 4:
        errors.append("global non-claims must remain explicit")
    upstreams: dict[str, dict] = {}
    for row in data.get("upstreams", []):
        if not isinstance(row, dict):
            errors.append("upstream row not an object")
            continue
        key = row.get("id")
        if not isinstance(key, str) or not ID_RE.fullmatch(key):
            errors.append(f"invalid upstream id: {key!r}")
            continue
        if key in upstreams:
            errors.append(f"duplicate upstream id: {key}")
        upstreams[key] = row
        if not SHA_RE.fullmatch(str(row.get("commit", ""))):
            errors.append(f"invalid pin for {key}: commit must be a full lowercase Git SHA")
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+", str(row.get("repo", ""))):
            errors.append(f"invalid repository name for {key}")
    if set(upstreams) != {"october", "assessment"}:
        errors.append("both original and independent assessment must be pinned")
    seen: set[str] = set()
    records = data.get("records", [])
    if not isinstance(records, list) or not records:
        return errors + ["non-empty records list required"]
    for i, row in enumerate(records):
        if not isinstance(row, dict):
            errors.append(f"record {i} not an object")
            continue
        ident = row.get("id", "")
        if not isinstance(ident, str) or not ID_RE.fullmatch(ident):
            errors.append(f"invalid record id at index {i}")
        if ident in seen:
            errors.append(f"duplicate record id: {ident}")
        seen.add(ident)
        u = upstreams.get(row.get("upstream"))
        if u is None:
            errors.append(f"{ident}: unknown upstream")
            continue
        path = row.get("path")
        if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or ".." in Path(path).parts:
            errors.append(f"{ident}: unsafe or empty source path")
            continue
        expected = f"https://github.com/{u['repo']}/blob/{u['commit']}/{path}"
        if row.get("source_url") != expected:
            errors.append(f"{ident}: source_url not pinned to the declared commit")
        if not isinstance(row.get("anchor"), str) or len(row["anchor"].strip()) < 8:
            errors.append(f"{ident}: source anchor missing or too short")
        if row.get("category") not in CATEGORIES:
            errors.append(f"{ident}: invalid comparison category")
        strength = row.get("claim_strength")
        if strength not in ALLOWED_STRENGTHS:
            errors.append(f"{ident}: unverified proof/transfer strength {strength!r}")
        if any(key in row for key in ("gate_closed", "proof_transferred", "analytic_bound_passed")):
            errors.append(f"{ident}: forbidden gate-closure claim")
        for field in ("finding", "obligation"):
            if not isinstance(row.get(field), str) or len(row[field].strip()) < 30:
                errors.append(f"{ident}: {field} must be a substantive sentence")
        gate = row.get("target_gate")
        if not isinstance(gate, str) or not GATE_RE.fullmatch(gate):
            errors.append(f"{ident}: missing/invalid target_gate")
        elif known_gates is not None and gate not in known_gates:
            errors.append(f"{ident}: target_gate {gate} absent from program.yaml")
    if len(seen) != len(records):
        errors.append("duplicate records violate one-to-one record IDs")
    return errors


def read_program_gate_ids(path: Path) -> set[str]:
    """Read only YAML gate IDs, avoiding dependence on program status semantics."""
    import yaml
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {x["id"] for x in document["gates"]}


def source_checks(data: dict, roots: dict[str, Path], strict: bool) -> tuple[list[str], dict]:
    """Check pinned source roots and literal source anchors; not theorem validity."""
    errors: list[str] = []
    detail: dict = {"mode": "NOT_RUN" if not roots else "SOURCE_ANCHORS_ONLY", "roots": {}}
    upstreams = {u["id"]: u for u in data.get("upstreams", [])}
    if strict and set(roots) != set(upstreams):
        errors.append("--strict-source requires exact local roots for october and assessment")
    for label, root in roots.items():
        if label not in upstreams:
            errors.append(f"unknown source root label {label}")
            continue
        if not root.is_dir():
            errors.append(f"source root does not exist: {root}")
            continue
        revision = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        )
        sha = revision.stdout.strip()
        expected = upstreams[label]["commit"]
        if revision.returncode or sha != expected:
            errors.append(f"{label}: git HEAD mismatch; expected {expected}, obtained {sha!r}")
        checked = 0
        for row in data["records"]:
            if row["upstream"] != label:
                continue
            path = root / row["path"]
            if not path.is_file():
                errors.append(f"{row['id']}: missing pinned source file {row['path']}")
                continue
            if row["anchor"] not in path.read_text(encoding="utf-8"):
                errors.append(f"{row['id']}: literal anchor absent in {row['path']}")
            else:
                checked += 1
        detail["roots"][label] = {"git_head": sha, "anchors_found": checked}
    return errors, detail


def parse_source_roots(values: list[str]) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for item in values:
        if "=" not in item:
            raise ValueError("--source-root must have form upstream_id=/path")
        label, value = item.split("=", 1)
        if label in roots or label not in {"october", "assessment"} or not value:
            raise ValueError("duplicate/unknown/empty --source-root mapping")
        roots[label] = Path(value).resolve()
    return roots


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--program", type=Path, default=ROOT / "program.yaml")
    ap.add_argument("--source-root", action="append", default=[],
                    help="october=/local/pinned/original or assessment=/local/pinned/review")
    ap.add_argument("--strict-source", action="store_true")
    ap.add_argument("--report", type=Path)
    args = ap.parse_args(argv)
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        gates = read_program_gate_ids(args.program)
        errors = validate_crosswalk(data, gates)
        roots = parse_source_roots(args.source_root)
        if not errors:
            source_errors, verification = source_checks(data, roots, args.strict_source)
            errors.extend(source_errors)
        else:
            verification = {"mode": "NOT_RUN", "roots": {}}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors = [f"fatal input error: {exc}"]
        verification = {"mode": "NOT_RUN", "roots": {}}
    report = {
        "audit_id": "YM3D_UPSTREAM_4D_CONSTRUCTION_AUDIT_0",
        "status": "STRUCTURAL_PASS" if not errors else "FAIL",
        "source_verification": verification,
        "proves_3d_transfer": False,
        "closes_program_gates": [],
        "errors": errors,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
