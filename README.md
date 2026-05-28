# YM3D — A Ledger-Gated Constructive RG Program for 3D Yang–Mills
[![CI](https://github.com/BenjaminJohnSchulz/ym3d-constructive-rg/actions/workflows/ci.yml/badge.svg)](../../actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
A formal, **auditable** architecture for three-dimensional Euclidean lattice
Yang–Mills theory (compact `SU(2)`, Wilson action), together with an executable
harness that lets a human or a coding agent advance the program one rigorously
checked **gate** at a time.
> **This is not a claimed proof of a mass gap.** It is an architecture for
> converting local block-RG calculations into independently audited claims,
> with exact arithmetic, hard acceptance gates, an explicit kill/pivot budget,
> and an automated guard against over-claiming. See the
> [non-claims](design/YM3D_CONSTRUCTIVE_RG_DESIGN.md#14-non-claims) in the design.
## What's here
| Path | What it is |
|------|------------|
| `design/YM3D_CONSTRUCTIVE_RG_DESIGN.md` | The full design specification (v1.8). Also `.docx`, `.tex`. |
| `program.yaml` | The single authoritative gate-dependency graph (executable source of truth). |
| `orchestrator/` | The scheduler, claim ratchet, manifest tool, and gate scaffolder. |
| `schemas/` | Canonical JSON Schemas (Draft 2020-12) for ledger rows. |
| `bundles/` | One directory per implemented gate (generator + independent checker). |
| `docs/` | Conceptual pipeline DAG (`.mmd`, `.json`). |
| `AGENTS.md` / `CLAUDE.md` | Operating contract for coding agents (Codex / Claude Code). |
## Quick start
```bash
make setup          # install pyyaml + jsonschema
make status         # gate board (2 gates CLOSED today)
make next           # the single next gate to work on, as JSON
make all            # run the whole DAG, fail-stop at the first gap
make claims         # claim ratchet over the manuscript
make verify         # re-run all CLOSED gates from clean (reproducibility)
```
Requires Python 3.11+. The only runtime dependencies are `pyyaml` and
`jsonschema`.
## How a gate closes
A gate is **CLOSED** only when its *independent* checker exits 0, writes a
`decision.json` with `status: PASS`, and any declared schemas validate. Two
gates ship closed today:
- `YM3D_SCHEMA_DISCRIMINATOR_NULL_TEST_1` — proves the stage-discriminated
  schemas reject ill-formed rows (combinatorial rows may not carry analytic
  certificate fields; bad discriminator values are rejected).
- `YM3D_OH_SIGNED_PERMUTATION_GROUP_1` — proves the cubic group `O_h` is the 48
  signed-permutation matrices. The checker **re-derives** the group from scratch
  and audits the generator's export as untrusted input — it does not import the
  generator.
Everything downstream is `BLOCKED` until its bundle is built. `make next` always
names the one gate to work on.
## Design guarantees the harness enforces
- **One DAG.** Dependencies, milestones, and sanity gates are reconciled in
  `program.yaml`; the scheduler runs a gate only when its parents are closed.
- **Fail-stop.** Stops at the first failing gate; never "fix and continue".
- **Independent checkers.** `strict` gates run the checker in a path-scrubbed
  subprocess and a lint rejects a checker that imports its generator.
- **Claim ratchet.** Prose asserting a result whose gate is not closed fails CI.
- **Kill / pivot budget.** If the RG contraction does not materialise after a
  declared number of attempts, the harness recommends the fallback route
  instead of letting the program stall silently.
- **Exact arithmetic + deterministic manifests.** No floats in gate decisions;
  SHA-256 over source files only.
## For coding agents
Read [`AGENTS.md`](AGENTS.md) (Codex) / [`CLAUDE.md`](CLAUDE.md) (Claude Code)
first. The loop is: `make next` → if the workdir is missing, `make scaffold` →
implement the generator and an independent checker → `make gate GATE=<id>` →
repeat.
## Citation
Benjamin John Schulz, *A Ledger-Gated Constructive RG Program for
Three-Dimensional Yang–Mills Theory*, v1.8, 2026.
## License
MIT — see [`LICENSE`](LICENSE).
