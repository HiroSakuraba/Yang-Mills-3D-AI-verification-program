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

## Four-dimensional comparison research

The [YM4 Wilson audit](docs/ym4-wilson-audit/README.md) collects a coherence map,
exact coefficient calculations, an audit of recovered earlier proof notes, and a
conservative application of the Dobrushin comparison theorem. It includes
[the HTML map](docs/ym4-wilson-audit/YM4-Coherence-Map.html) and a
[downloadable ZIP](docs/ym4-wilson-audit/YM4-Wilson-Audit.zip).

This is a separate four-dimensional research record. Its scripts are consistency
checks, not independent checkers for this repository's three-dimensional proof
program. It does not close a gate in `program.yaml` or supply a proof dependency
for the 3D lane. In particular, the coefficient frontier near `x = 0.6273` is not
a physical clustering or mass-gap claim.

## Quick start

```bash
make setup          # install pyyaml + jsonschema
make status         # gate board (3 implemented checks after make all)
make next           # the single next gate to work on, as JSON
make all            # run the whole DAG, fail-stop at the first gap
make claims         # claim ratchet over the manuscript
make verify         # re-run all CLOSED gates from clean (reproducibility)
```

Requires Python 3.11+. The only runtime dependencies are `pyyaml` and
`jsonschema`.

## How a gate closes

A gate is **CLOSED** only when its *independent* checker exits 0, writes a
`decision.json` with `status: PASS`, and any declared schemas validate. Three
checks are implemented and reproduce through the harness:

- `YM3D_SCHEMA_DISCRIMINATOR_NULL_TEST_1` — proves the stage-discriminated
  schemas reject ill-formed rows (combinatorial rows may not carry analytic
  certificate fields; bad discriminator values are rejected).
- `YM3D_OH_SIGNED_PERMUTATION_GROUP_1` — proves the cubic group `O_h` is the 48
  signed-permutation matrices. The checker **re-derives** the group from scratch
  and audits the generator's export as untrusted input — it does not import the
  generator.

- `YM3D_GLUEBALL_OBSERVABLE_REFERENCE_1` — independently reconstructs five D4
  scalar-loop definitions and exact rational spectral reference identities. This
  comparison-lane result unlocks no analytic or physical mass-gap claim.

The [scalar-glueball lane](lanes/glueball_spectroscopy/README.md) also includes a
review-stage explicit plaquette-correlation derivation and a numerical spectrum
analysis tool, with constructed reference inputs and CPU-only self-tests.

The [spectrum-analysis extension](lanes/glueball_spectrum_analysis/README.md)
adds overlap-based mode tracking, fixed-basis correlated mass fits, covariance
regularization, bootstrap fit errors and fit-window comparisons. It is a
numerical comparison tool and adds no proof gate or automatically selected plateau.
Its [ensemble converter](lanes/glueball_spectrum_analysis/ENSEMBLES.md) prepares
periodic correlators and chain-aware block-bootstrap replicas directly from
per-configuration operator measurements, including vacuum means and provenance.

The [directed-link action bundle](bundles/YM3D_ORIENTED_LINK_ACTION_1/README.md)
independently audits the integer affine action of the cubic symmetries, including
orientation reversals and periodic boundaries. Composite support lifting remains
the next implementation step.

The [exact 2D SU(2) reference](lanes/ym2d_sun_exact_validation/README.md) now has
a standalone independent audit of open-boundary Wilson-loop expectations with
rational tail bounds. It does not yet close the broader 2D pipeline-validation
milestone or unlock analytic 3D results.

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
