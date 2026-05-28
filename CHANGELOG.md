# Changelog

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
