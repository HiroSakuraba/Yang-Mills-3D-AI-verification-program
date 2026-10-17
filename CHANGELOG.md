# Changelog

## Unreleased

- Prepare numerical glueball correlators from periodic per-configuration operator
  samples with time-origin averaging, per-replica vacuum means, chain-aware
  nonoverlapping block bootstrap, explicit thermalization discard, dependence
  diagnostics and source/sample provenance retained through spectrum analysis.
  Add a synthetic samples-to-fits demonstration and eleven regression checks.

- Implement an independently audited 2D SU(2) open-boundary Wilson reference:
  normalized fundamental/adjoint characters, noncommutative rectangle words and
  exact rational area-law enclosures with controlled infinite-series tails.
  Keep the broader validation milestone blocked pending geometry integration.

- Implement the exact directed-link action of the 48 cubic symmetries. Export
  affine canonicalization rules and independently check endpoint identities,
  group composition, inverses, faithfulness and periodic boundary cases.

- Extend numerical glueball spectroscopy with overlap-based mode tracking,
  fixed-reference correlated mass fits, covariance diagnostics, bootstrap fit
  errors, paired window sensitivity, and JSON/CSV examples. Preserve the frozen
  exact reference lane and add no analytic/proof gate.

- Add the scalar-glueball comparison lane: five exact D4/A1 loop definitions,
  independent rational reference checks, a review-stage volume-normalized
  plaquette correlation derivation, and numerical generalized-eigenvalue analysis.
- Add one combinatorial/reference-only harness result; preserve the analytic
  validation prerequisites and keep numerical spectroscopy outside proof claims.


## 1.8.0 — Open-source / harness revision
- Added `program.yaml`: single authoritative gate-dependency graph.
- Added orchestrator (`run.py`), claim ratchet (`claim_lint.py`), gate
  scaffolder (`scaffold_gate.py`), and deterministic manifest tool.
- Added an explicit program-level **kill / pivot budget** (`kill_criteria`).
- **Checker independence now enforced physically**: the `O_h` checker
  re-derives the group from scratch and no longer imports the generator;
  strict gates run checkers in a path-scrubbed subprocess + static lint.
- **Schema repairs**: working `gauge_geometric` branch (was unreachable in
  v1.7); discriminated unions use `if/then/else`; schemas de-duplicated into a
  single canonical `schemas/` directory.
- Resource schedules (audit box sizes, edge caps, timeouts) on combinatorial
  gates.
- Pinned exact-arithmetic / determinism policy; manifests exclude bytecode.
- Added MIT `LICENSE`, GitHub `README.md`, CI, and agent contracts
  (`AGENTS.md`, `CLAUDE.md`).
- Design document updated to v1.8 (new Section 20).

## 1.7.0 and earlier
See the abstract changelog in `design/YM3D_CONSTRUCTIVE_RG_DESIGN.md`.
