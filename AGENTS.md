# AGENTS.md — operating contract for the YM3D constructive-RG harness

> This file is the contract for any coding agent (Codex, Claude Code, etc.)
> working in this repository. Claude Code also reads `CLAUDE.md`, which points
> here. Read this fully before acting.

## What this repo is

A **ledger-gated proof program** for 3D SU(2) lattice Yang–Mills. Work is
organized as a DAG of *gates*. A gate is CLOSED only when an **independent
checker** confirms a precisely scoped mathematical/combinatorial fact and emits
a `decision.json` with `status: PASS`. The design (`design/…RG_DESIGN.md`) is the
spec; `program.yaml` is the authoritative, machine-readable gate DAG.

## The loop you run

1. `make next` → returns JSON naming the single next gate to work on.
2. If its `workdir` does not exist, **build it**: `make scaffold GATE=<id> SHORT=<short>`.
   The scaffolder gives you a `tools/build.py` (generator) and a *separate*
   `tools/check_<short>.py` (independent checker).
3. Implement the generator in `src/<pkg>/`, then implement the checker so it
   **re-derives the invariant from scratch** and reads only the generated
   artifacts.
4. `make gate GATE=<id>`. Iterate until `[CLOSED]`.
5. Repeat. Use `make status` and `make graph` to orient.

## Hard rules (violations are bugs, not style)

- **Never edit a CLOSED gate's artifacts or code.** If a closed result is wrong,
  open a new versioned gate (`…_2`) and supersede it in `program.yaml`.
- **Checker independence is physical, not honorary.** A `strict` checker MUST NOT
  `import` the generator package. The harness lints for this and warns; treat a
  warning as a failure to fix. A checker that re-runs the generator proves
  reproducibility, not correctness.
- **Fail-stop.** On any checker failure or runtime error, STOP and report. Do not
  "fix and continue" in the same run, and never weaken a checker to make it pass.
- **Report faithfully.** Never write `status: PASS` when checks fail; never claim
  a gate closes work it doesn't. State confirmed successes plainly.
- **Exact arithmetic only** in checkers (`int`, `fractions.Fraction`, or a pinned
  interval backend). No float comparisons in a gate decision.
- **Respect the claim ratchet.** Do not add prose to the manuscript asserting a
  result whose gate is not CLOSED. `make claims` enforces this.
- **Respect resource schedules.** Gates with a `box_schedule`/`max_expanded_edges`
  in `program.yaml` must not exceed them; the combinatorial graph blows up fast.
- **Meta-guards.** No `analytic` gate may close before
  `YM2D_SUN_EXACT_VALIDATION_LANE_0` is CLOSED (or a recorded waiver exists).

## Definition of done for a gate

`make gate GATE=<id>` prints `[CLOSED]`, AND:
- `decision.json` lists `closed_obligations`, `non_claims`, `next_obligation`;
- the independent checker passed in its own subprocess with no independence
  warning;
- any `schemas_validated` are valid Draft 2020-12;
- `make verify` still reproduces the close from clean.

## Where things are

```
program.yaml              authoritative gate DAG + meta-rules + kill criteria
orchestrator/run.py       scheduler (status/next/gate/up-to/all/verify/graph)
orchestrator/claim_lint.py claim ratchet
orchestrator/scaffold_gate.py  new-gate templates with built-in independence
design/                   the v1.7 design spec (read-only reference)
bundles/<GATE_ID>/        one directory per gate
artifacts/state.json      persisted CLOSED status (managed by the harness)
```

## Do not

- Do not invent capabilities; if a tool/lane is missing, say so and stop.
- Do not promote a terminal-only bound to a full-RG claim.
- Do not sum heterogeneous Δ_k error components without a conversion certificate.
- Do not import comparison/numerical-anchor results as proof dependencies.
