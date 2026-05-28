#!/usr/bin/env python3
"""
YM3D harness orchestrator.

A small, dependency-light scheduler that drives the ledger-gated proof
program described in program.yaml. It is designed to be driven *by a coding
agent* (Claude Code / Codex) and to give that agent a single, unambiguous
"what do I do next" signal, plus hard guarantees:

  * topological execution by dependency (no gate runs before its parents
    are CLOSED);
  * program-level meta-guards (e.g. no analytic gate closes before the 2D
    validation lane passes);
  * checker independence enforcement (strict gates run the checker in a
    subprocess whose import path cannot see the generator package);
  * fail-stop semantics (stop at the first failing gate; never "fix and
    continue") matching the program's reporting discipline;
  * a deterministic, machine- and human-readable status board.

Commands:
    run.py status                 show the gate board
    run.py next                   print the next runnable gate as JSON (for the agent)
    run.py gate <GATE_ID>         run exactly one gate
    run.py up-to <GATE_ID>        run everything needed to close <GATE_ID>
    run.py all                    run the whole DAG, fail-stop
    run.py verify                 re-run all CLOSED gates from clean (reproducibility)
    run.py kill-check             evaluate kill/pivot criteria
    run.py graph                  emit the resolved DAG (mermaid)

Exit code is 0 only if the requested action ended with no FAIL/ERROR.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "program.yaml"
STATE = ROOT / "artifacts" / "state.json"

PASS_TOKENS = {True, "PASS", "pass", "passed", "CLOSED"}


# --------------------------------------------------------------------------- #
# model
# --------------------------------------------------------------------------- #
@dataclass
class Gate:
    id: str
    spec: dict
    # runtime
    status: str = "OPEN"      # OPEN | CLOSED | FAILED | BLOCKED | ERROR
    detail: str = ""
    closed_at: str = ""

    @property
    def workdir(self) -> Path:
        return ROOT / self.spec["workdir"]

    @property
    def depends_on(self) -> list[str]:
        return list(self.spec.get("depends_on", []))

    @property
    def meta_requires(self) -> list[str]:
        return list(self.spec.get("meta_requires", []))


@dataclass
class Program:
    gates: dict[str, Gate]
    meta_rules: dict
    kill_criteria: list
    order: list[str] = field(default_factory=list)

    @classmethod
    def load(cls) -> "Program":
        doc = yaml.safe_load(PROGRAM.read_text())
        gates = {g["id"]: Gate(g["id"], g) for g in doc["gates"]}
        prog = cls(gates=gates,
                   meta_rules=doc.get("meta_rules", {}),
                   kill_criteria=doc.get("kill_criteria", []))
        prog.order = prog._toposort()
        prog._load_state()
        return prog

    def _toposort(self) -> list[str]:
        seen, order, stack = set(), [], set()

        def visit(gid: str):
            if gid in seen:
                return
            if gid in stack:
                raise ValueError(f"cycle in DAG at {gid}")
            stack.add(gid)
            for dep in self.gates[gid].depends_on:
                if dep not in self.gates:
                    raise ValueError(f"{gid} depends on unknown gate {dep}")
                visit(dep)
            stack.discard(gid)
            seen.add(gid)
            order.append(gid)

        for gid in self.gates:
            visit(gid)
        return order

    # persisted CLOSED status survives across invocations
    def _load_state(self):
        if not STATE.exists():
            return
        data = json.loads(STATE.read_text())
        for gid, rec in data.get("gates", {}).items():
            if gid in self.gates and rec.get("status") == "CLOSED":
                self.gates[gid].status = "CLOSED"
                self.gates[gid].closed_at = rec.get("closed_at", "")
                self.gates[gid].detail = rec.get("detail", "")

    def _save_state(self):
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps({
            "program": "YM3D_CONSTRUCTIVE_RG",
            "gates": {g.id: {"status": g.status,
                             "closed_at": g.closed_at,
                             "detail": g.detail}
                      for g in self.gates.values()},
        }, indent=2) + "\n")

    # ----- guards --------------------------------------------------------- #
    def deps_closed(self, g: Gate) -> bool:
        return all(self.gates[d].status == "CLOSED" for d in g.depends_on)

    def meta_ok(self, g: Gate) -> tuple[bool, str]:
        for key in g.meta_requires:
            rule = self.meta_rules.get(key, {})
            need = rule.get("satisfied_when_closed", [])
            ok = all(self.gates[n].status == "CLOSED"
                     for n in need if n in self.gates)
            if not ok:
                waiver = rule.get("waiver_file")
                if waiver and (g.workdir / waiver).exists():
                    continue
                return False, f"meta guard '{key}' not satisfied (need {need} CLOSED)"
        return True, ""

    def runnable(self, g: Gate) -> tuple[bool, str]:
        if not self.deps_closed(g):
            missing = [d for d in g.depends_on
                       if self.gates[d].status != "CLOSED"]
            return False, f"waiting on deps: {missing}"
        ok, why = self.meta_ok(g)
        if not ok:
            return False, why
        if not g.workdir.exists():
            return False, f"workdir not present yet: {g.spec['workdir']}"
        if not g.spec.get("checker_cmd"):
            return False, "no checker_cmd declared"
        return True, ""


# --------------------------------------------------------------------------- #
# execution
# --------------------------------------------------------------------------- #
def _restricted_env(g: Gate) -> dict:
    """For independence: strict, scrub the generator's src/ from PYTHONPATH so
    the checker subprocess cannot import the generator package."""
    env = dict(os.environ)
    if g.spec.get("independence") == "strict":
        env["YM3D_INDEPENDENT_CHECKER"] = "1"
        # remove any path under this gate's src/ from PYTHONPATH
        bad = str((g.workdir / "src").resolve())
        parts = [p for p in env.get("PYTHONPATH", "").split(os.pathsep)
                 if p and not p.startswith(bad)]
        env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def _independence_lint(g: Gate) -> list[str]:
    """Static check: a strict checker must not import the generator package.
    Returns a list of violations (empty == clean)."""
    if g.spec.get("independence") != "strict":
        return []
    viol = []
    checker = g.spec["checker_cmd"].split()
    # crude: first .py token after 'python'
    pyfile = next((t for t in checker if t.endswith(".py")), None)
    if not pyfile:
        return []
    path = g.workdir / pyfile
    if not path.exists():
        return []
    src_pkgs = {p.name for p in (g.workdir / "src").glob("*")
                if p.is_dir()} if (g.workdir / "src").exists() else set()
    for i, line in enumerate(path.read_text().splitlines(), 1):
        s = line.strip()
        for pkg in src_pkgs:
            if s.startswith(f"from {pkg}") or s.startswith(f"import {pkg}"):
                viol.append(f"{pyfile}:{i}: imports generator package "
                            f"'{pkg}' (independence: strict)")
    return viol


def _read_decision(g: Gate) -> tuple[bool, str, dict]:
    glob = g.spec.get("decision_glob", "artifacts/decision.json")
    matches = sorted(g.workdir.glob(glob))
    if not matches:
        return False, f"no decision artifact matching {glob}", {}
    rec = json.loads(matches[-1].read_text())
    key = g.spec.get("decision_status_key", "status")
    val = rec.get(key)
    ok = val in PASS_TOKENS
    return ok, f"{key}={val!r}", rec


def _validate_schemas(g: Gate) -> tuple[bool, str]:
    schemas = g.spec.get("schemas_validated", [])
    if not schemas:
        return True, ""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return False, "jsonschema not installed"
    for s in schemas:
        sp = g.workdir / s
        if not sp.exists():
            return False, f"schema missing: {s}"
        try:
            Draft202012Validator.check_schema(json.loads(sp.read_text()))
        except Exception as e:  # noqa: BLE001
            return False, f"invalid schema {s}: {e}"
    return True, ""


def run_gate(prog: Program, g: Gate, verbose: bool = True) -> bool:
    runnable, why = prog.runnable(g)
    if not runnable:
        g.status = "BLOCKED"
        g.detail = why
        if verbose:
            print(f"[BLOCKED] {g.id}: {why}")
        return False

    # 1) independence lint (advisory FAIL for strict gates)
    viol = _independence_lint(g)
    indep_note = ""
    if viol:
        indep_note = " | INDEPENDENCE WARNING: " + "; ".join(viol)

    # 2) optional generator
    gen = g.spec.get("generator_cmd")
    if gen:
        rc = _exec(g, gen, dict(os.environ))
        if rc != 0:
            g.status, g.detail = "FAILED", f"generator rc={rc}"
            print(f"[FAIL] {g.id}: generator exit {rc}")
            return False

    # 3) checker (independent subprocess for strict gates)
    rc = _exec(g, g.spec["checker_cmd"], _restricted_env(g))
    if rc != 0:
        g.status, g.detail = "FAILED", f"checker rc={rc}{indep_note}"
        print(f"[FAIL] {g.id}: checker exit {rc}{indep_note}")
        return False

    # 4) decision artifact + schema validation
    ok, det, _ = _read_decision(g)
    sok, sdet = _validate_schemas(g)
    if not (ok and sok):
        g.status = "FAILED"
        g.detail = f"{det}; schema:{sdet}{indep_note}"
        print(f"[FAIL] {g.id}: {g.detail}")
        return False

    g.status = "CLOSED"
    g.closed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    g.detail = (det + indep_note).strip()
    print(f"[CLOSED] {g.id}: {det}{indep_note}")
    return True


def _exec(g: Gate, cmd: str, env: dict) -> int:
    timeout = g.spec.get("timeout_s", 600)
    try:
        p = subprocess.run(cmd, shell=True, cwd=g.workdir, env=env,
                           timeout=timeout, capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        print(f"  ! {g.id} TIMEOUT after {timeout}s on `{cmd}`")
        return 124
    if p.returncode != 0:
        sys.stderr.write(p.stdout[-2000:] + p.stderr[-2000:])
    return p.returncode


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_status(prog: Program):
    print(f"{'GATE':52} {'STATUS':9} DETAIL")
    print("-" * 100)
    for gid in prog.order:
        g = prog.gates[gid]
        if g.status not in ("CLOSED",):
            runnable, why = prog.runnable(g)
            g.status = "RUNNABLE" if runnable else "BLOCKED"
            g.detail = "" if runnable else why
        print(f"{gid:52} {g.status:9} {g.detail[:40]}")
    closed = sum(g.status == "CLOSED" for g in prog.gates.values())
    print("-" * 100)
    print(f"{closed}/{len(prog.gates)} gates CLOSED")


def cmd_next(prog: Program):
    for gid in prog.order:
        g = prog.gates[gid]
        if g.status == "CLOSED":
            continue
        runnable, why = prog.runnable(g)
        if runnable:
            print(json.dumps({
                "next_gate": g.id,
                "title": g.spec.get("title", ""),
                "workdir": g.spec["workdir"],
                "checker_cmd": g.spec.get("checker_cmd"),
                "schema_stage": g.spec.get("schema_stage"),
                "claims_unlocked": g.spec.get("claims_unlocked", []),
                "claim_strength": g.spec.get("claim_strength"),
                "run": f"python orchestrator/run.py gate {g.id}",
            }, indent=2))
            return 0
    print(json.dumps({"next_gate": None,
                      "message": "no runnable gate; build the workdir for the "
                                 "first BLOCKED gate or all gates are CLOSED"}))
    return 0


def cmd_run(prog: Program, target_ids: list[str]) -> int:
    failed = False
    for gid in prog.order:
        if target_ids and gid not in target_ids:
            continue
        g = prog.gates[gid]
        if g.status == "CLOSED":
            print(f"[skip] {gid} already CLOSED")
            continue
        ok = run_gate(prog, g)
        prog._save_state()
        if not ok and g.status == "FAILED":
            failed = True
            print(f"\nFAIL-STOP at {gid}. Not continuing (program policy).")
            break
    return 1 if failed else 0


def _ancestors(prog: Program, gid: str) -> list[str]:
    out, stack = [], [gid]
    while stack:
        cur = stack.pop()
        for d in prog.gates[cur].depends_on:
            if d not in out:
                out.append(d)
                stack.append(d)
    # return in topo order
    return [g for g in prog.order if g in out or g == gid]


def cmd_verify(prog: Program) -> int:
    """Re-run every gate marked CLOSED, from scratch, to confirm reproducibility."""
    for g in prog.gates.values():
        g.status = "OPEN"
    STATE.unlink(missing_ok=True)
    return cmd_run(prog, [])


def cmd_kill_check(prog: Program) -> int:
    print("Kill / pivot criteria:")
    any_trip = False
    for k in prog.kill_criteria:
        g = prog.gates.get(k["gate"])
        rec = {}
        if g:
            _, _, rec = _read_decision(g)
        val = rec.get(k["metric"])
        line = f"  [{k['id']}] {k['gate']}.{k['metric']} = {val}"
        if val is not None:
            try:
                tripped = eval(f"{float(val)} {k['abandon_route_if']}")  # noqa: S307
            except Exception:  # noqa: BLE001
                tripped = False
            if tripped:
                any_trip = True
                line += f"  -> TRIP: after {k['after_attempts']} attempts, PIVOT to {k['pivot_to']}"
        else:
            line += "  (no data yet)"
        print(line)
    return 1 if any_trip else 0


def cmd_graph(prog: Program):
    print("flowchart TD")
    for gid in prog.order:
        g = prog.gates[gid]
        tag = {"CLOSED": ":::closed"}.get(g.status, "")
        short = gid.replace("YM3D_", "").replace("YM2D_", "2D_")
        if not g.depends_on:
            print(f"    {short}{tag}")
        for d in g.depends_on:
            ds = d.replace("YM3D_", "").replace("YM2D_", "2D_")
            print(f"    {ds} --> {short}")
    print("    classDef closed fill:#bdf,stroke:#06c;")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command",
                    choices=["status", "next", "gate", "up-to", "all",
                             "verify", "kill-check", "graph"])
    ap.add_argument("gate_id", nargs="?")
    args = ap.parse_args()

    prog = Program.load()

    if args.command == "status":
        cmd_status(prog); return 0
    if args.command == "next":
        return cmd_next(prog)
    if args.command == "graph":
        cmd_graph(prog); return 0
    if args.command == "kill-check":
        return cmd_kill_check(prog)
    if args.command == "verify":
        return cmd_verify(prog)
    if args.command == "all":
        return cmd_run(prog, [])
    if args.command == "gate":
        if not args.gate_id:
            sys.exit("gate <GATE_ID> required")
        return cmd_run(prog, [args.gate_id])
    if args.command == "up-to":
        if not args.gate_id:
            sys.exit("up-to <GATE_ID> required")
        return cmd_run(prog, _ancestors(prog, args.gate_id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
