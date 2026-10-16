# Design Delta v1.16 — Infinite-Grid Dominated-Envelope Spin-Network Contraction Skeleton

## Purpose

v1.15b closed two immediate foundation checks in a limited sense:

1. Haar link integration is an orthogonal projector, so projector networks admit operator-norm domination.
2. The v1.14 activity screen implies a block-level contraction screen under an orthogonal-channel model.

v1.16 asks whether this can be extended to an infinite-grid / infinite-volume **skeleton** without overclaiming exact Wilson-transfer equality.

The result is deliberately framed as a dominated-envelope theorem skeleton, not as Package C and not as a Wilson-transfer theorem.

## New executable

```text
infinite_grid_dominated_envelope_skeleton_v1_16.py
```

## Counting model

For a graph of maximum degree \(\Delta\), use the conservative rooted connected-cluster envelope

\[
N_n(root) \le \bigl(e(\Delta-1)\bigr)^{n-1}.
\]

Let \(q_E\) denote the local energy-level nontrivial/trivial activity ratio and \(q_A=\sqrt{q_E}\) the corresponding amplitude/L2 ratio. Then the rooted energy-level cluster series is bounded if

\[
\lambda_E=e(\Delta-1)q_E<1,
\]

with bound

\[
\sum_{n\ge1}N_n q_E^n \le \frac{q_E}{1-e(\Delta-1)q_E}.
\]

The stronger amplitude-level version requires

\[
\lambda_A=e(\Delta-1)q_A<1.
\]

## Inputs from v1.15b

The audit uses the v1.15b analytic-tail contraction summary:

| slab | worst case | local energy ratio \(q_E\) | local amplitude ratio \(q_A\) |
|---|---|---:|---:|
| original | `original_wilson_beta1p5` | \(3.8903796\times10^{-3}\) | \(6.2372907\times10^{-2}\) |
| branch | `branch_wilson_beta1` | \(5.9779152\times10^{-7}\) | \(7.7316979\times10^{-4}\) |
| fallback | `fallback_heat_tau5` | \(9.0781743\times10^{-12}\) | \(3.0130009\times10^{-6}\) |

## Main result

```text
INFINITE_GRID_DOMINATED_ENVELOPE_SKELETON_PASSES_ENERGY_LEVEL_WITH_STRONGER_SLAB_FOR_AMPLITUDE_LEVEL
```

The audit scans maximum degree

\[
2\le \Delta\le 96.
\]

| slab | max \(\Delta\) passing energy screen | max \(\Delta\) passing amplitude screen | status |
|---|---:|---:|---|
| original | 95 | 6 | `PASS_ENERGY_STRESS_ONLY` |
| branch | 96 | 96 | `PASS_ENERGY_AND_AMPLITUDE_STRESS` |
| fallback | 96 | 96 | `PASS_ENERGY_AND_AMPLITUDE_STRESS` |

Thus the original v1.14 slab is acceptable only for an energy-level skeleton at high graph degree. The deeper branch/fallback slabs pass both energy-level and amplitude-level cluster-counting stress through the scanned range.

## What this closes or narrows

- `LO-C-INFINITE-GRID-SPINNETWORK-CONTRACTION` is narrowed/closed only as a bounded-degree dominated-envelope skeleton.
- `LO-C-ENERGY-LEVEL-CLUSTER-SUMMABILITY` is closed as a skeleton for the v1.14 analytic-tail slabs over the scanned degree stress.
- `LO-C-AMPLITUDE-LEVEL-CLUSTER-SUMMABILITY` is closed for the branch/fallback slabs over the scanned degree stress; the original slab fails large-degree amplitude stress.

## What remains open

1. Exact equality with the full Wilson transfer remains open.
2. The correct Package-C norm — energy-level or amplitude-level — remains open.
3. The thermodynamic/infinite-volume Cauchy construction is still only skeleton-level.
4. Continuum limit and Clay remain open.

## Interpretation

v1.16 is positive, but only after preserving the v1.15b caveat: this is a **dominated-envelope spin-network contraction skeleton**, not a full Wilson transfer theorem.

The next proof-control choice is no longer “does a cluster bound exist?” but:

\[
\boxed{\text{which norm does Package C require: energy-level or amplitude-level?}}
\]

If the energy-level norm suffices, the original strong-coupling slab remains usable in this skeleton. If amplitude-level control is required, the next theorem fragment should move to the branch/fallback slab.

## Recommended next step

```text
v1.17 — norm-selection and thermodynamic-limit Cauchy skeleton
```

In parallel, begin Track 1 paper assembly from the interval-arithmetic row work, because that result is independent of the current infinite-grid caveats.
