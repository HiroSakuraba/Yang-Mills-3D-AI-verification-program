# Auditing the October 2026 4D Lean Yang–Mills construction for YM3D
Status: **research crosswalk only**. This directory does not close any gate in `program.yaml`.

## Purpose

The source-pinned matrix in [crosswalk.json](crosswalk.json) traces selected interfaces and dependencies in the October 28 Lean release and the Yang–Mills working group's November 10 review. The intent is to identify code and proof patterns worth adapting to 3D without promoting four-dimensional statements to three-dimensional analytic estimates.

## Key findings

1. **Hard dimensional obstruction:** the upstream lattice is indexed by `Fin 4`, while its public Wilson regularity condition requires `beta / log(1/a)` to approach a positive slope. For the 3D SU(2) Wilson convention used in this project, bare beta scales as `4/(g3^2 a)`. The upstream running-coupling clause must be replaced and proved anew.
2. **Useful finite-lattice interfaces:** plaquette products, Haar-normalized Wilson measures, insertion/moment readouts, and common-witness acceptance contracts have adaptable mathematical shapes. No 3D bounds follow automatically.
3. **Promising but unproved analytic research targets:** the `Funded` campaign conditions, resource/precision scheduling and nonperturbative extraction machinery merit detailed proof-dependency analysis, particularly for polymer norms and multiscale constants.
4. **Immediately reusable engineering pattern:** independent theorem-statement comparison, axiom whitelists, frozen source/toolchain pins, and kernel replay.
5. **Physical boundary:** the submitted construction and reviewed positive lattice probe do not establish mass-gap or confinement claims.

## Evidence policy

- Every source link is pinned to a Git commit; `crosswalk.json` contains a literal anchor from the file.
- An anchor establishes **source location only**; it does not certify the interpretation.
- `candidate_only` means a proof/interface pattern might be useful after a new 3D lemma, **not** that the result has transferred.
- `no_direct_transfer` bars direct use as a 3D premise.
- `engineering_reuse_only` authorizes methodology, not analytic conclusions.
- Working-group checks are **reported upstream evidence**, not checks executed by this repository.

The upstream review explicitly distinguishes a selected scalar OS check from a complete independent all-field OS interface, full fixed-volume UV convergence from extracted IR convergence, and a positive lattice probe from an intrinsic mass gap.

## Running the crosswalk check

```sh
python tools/audit_upstream_ym4.py
python -m unittest discover -s tests -p 'test_upstream_ym4_audit.py'
```

The default audit validates schema-level claims and source pins *offline*. To check source anchors against exact pinned local checkouts:

```sh
python tools/audit_upstream_ym4.py \
  --source-root october=/path/to/OpenAI-YM-20261028 \
  --source-root assessment=/path/to/YM \
  --strict-source
```

The source audit checks `git rev-parse HEAD` against both frozen commits and verifies literal anchors. It does **not** run Lean or validate physical semantics. Full Lean/Comparator replay is a separate, substantially more expensive task, documented upstream.

## Second tranche: finite gas stability and dependency tracing

The [source dependency trace](DEPENDENCY_TRACE_2.md) follows the upstream
funded-run selection through named budget/resource suppliers and identifies a
portable **finite** signed-activity inequality in the beta-transport source.
The [finite transfer proof and exact example](FINITE_GAS_TRANSFER.md) include
a hand-constructed 3D plaquette-support inventory, an independently audited
[rational artifact](finite_gas_seed.json), 10 input/negative controls, an
exhaustive two-label coefficient-grid test, and a mask-change counterexample.

```sh
python tools/build_finite_gas_transfer.py --output docs/upstream-4d-lean-audit/finite_gas_seed.json
python tools/check_finite_gas_transfer.py docs/upstream-4d-lean-audit/finite_gas_seed.json
python -m unittest discover -s tests -p 'test_finite_gas_transfer.py' -v
```

Neither the source trace nor the finite algebra establishes bounds for actual
SU(2) Wilson activities, uniform polymer norms, RG contraction or a mass gap.
The next mathematical obligation is to derive and certify such coefficients.

## Next analytic research tranche

A. Trace `constructionRun` → campaign selection → actual numeric source estimates, recording theorem hypotheses and dependence on dimension, volume, scale and gauge.

B. Identify whether a *specific, sourced* polymer norm or collision estimate can be proved in the 3D K-star setup. Demand explicit 3D definitions and a new gate, not import-by-analogy.

C. Compare OS transfer to our reflection-plane factorization checker and keep selected-scalar OS checks distinct from full gauge-invariant reconstruction.

D. Evaluate proof-assistant reuse after Milestone 1A orbit/support closure.

See [MATHEMATICAL_CROSSWALK.md](MATHEMATICAL_CROSSWALK.md) for the detailed analysis.
