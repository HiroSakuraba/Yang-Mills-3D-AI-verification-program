# Design Delta v1.15b — Projector-Norm Domination and Activity-Screen Contraction Audit

## Purpose

v1.15a confirmed that the v1.14 spin-network contraction estimates are not yet an exact derivation of the full Wilson transfer block.  The full Wilson link integration is a projector network over invariant subspaces, and multi-dimensional intertwiner spaces occur.

v1.15b therefore audits two narrower questions before any infinite-grid extension:

1. **Projector-norm domination:** does the Wilson link projector network admit a theorem-skeleton domination by the v1.14 invariant-count/tensor envelope?
2. **Activity screen implies contraction:** do the locked activity diagnostics

\[
R<0.75,\qquad M<0.5
\]

actually imply a block-level nontrivial-channel contraction, at least under the orthogonal channel model used in v1.14?

## New executable

```text
projector_domination_activity_contraction_audit_v1_15b.py
```

## Main decision

```text
PROJECTOR_NORM_DOMINATION_AND_ACTIVITY_CONTRACTION_SCREEN_CLOSED_AS_CONDITIONAL_FRAGMENT
```

## Projector-norm domination result

Haar integration at a link is an orthogonal projector

\[
\int \prod_i D^{j_i}(g)\,dg
=
P_{\operatorname{Inv}(\otimes_i V_{j_i})}.
\]

Therefore

\[
\|P_{\operatorname{Inv}}\|_{\mathrm{op}}\le 1.
\]

The audit keeps the v1.15a finite invariant-rank scan but reclassifies it correctly: multi-intertwiner rank blocks exact scalar equality, but it does not block an operator-norm domination/envelope statement.

For the scanned link degrees, all projector ranks are bounded by the v1.12 closed-form local tensor envelope

\[
\|T_{d,k}^{(K)}\|_F\le (K+1)^{(3d-2)/2}.
\]

Worst finite scan row:

| item | value |
|---|---:|
| max scanned degree | 6 |
| scan cutoff | 6 |
| max projector rank seen | 315 |
| max \(\sqrt{\mathrm{rank}}\) | 17.7482393493 |
| v1.12 bound at degree 6, cutoff 6 | 5,764,801 |

This is very conservative, but it is enough to close the **domination/envelope** obligation at theorem-skeleton level. It does not prove equality with the scalar v1.14 block.

## Activity screen implies contraction result

Under an orthogonal channel decomposition, define

\[
R=\frac{\max_{k>0}E_k}{E_0},
\qquad
M=\frac{\sum_{k>0}E_k}{\sum_k E_k}.
\]

Then

\[
\frac{\|E_k\|_{L^2}}{\|E_0\|_{L^2}}\le \sqrt R,
\qquad
\frac{\|E_{\rm nontriv}\|_{L^2}}{\|E_0\|_{L^2}}
\le
\sqrt{\frac{M}{1-M}}.
\]

Thus if

\[
R<1,
\qquad
M<\frac12,
\]

the nontrivial sector is strictly contractive relative to the trivial channel in this block-level model.

The locked stronger budgets

\[
R<0.75,
\qquad
M<0.5
\]

therefore imply the desired block-level contraction screen.

## Diagnostics imported from v1.14 analytic-tail rows

| slab class | worst \(R\) | worst \(M\) | worst contraction screen |
|---|---:|---:|---:|
| original | \(3.8903796\times10^{-3}\) | \(3.8753032\times10^{-3}\) | \(6.2372907\times10^{-2}\) |
| branch | \(5.9779152\times10^{-7}\) | \(5.9779116\times10^{-7}\) | \(7.7316979\times10^{-4}\) |
| fallback | \(9.0781743\times10^{-12}\) | \(9.0781743\times10^{-12}\) | \(3.0130009\times10^{-6}\) |

All v1.14 analytic-tail theorem-skeleton rows pass the conditional contraction screen.

## What closes

Closed/narrowed:

- `LO-C-PROJECTOR-NORM-DOMINATION`: closed as operator-norm / invariant-count envelope domination, not equality.
- `LO-C-ACTIVITY-SCREEN-IMPLIES-CONTRACTION`: closed conditionally for the orthogonal channel block model.

Still open:

- `LO-C-REAL-PLAQUETTE-NORMALIZATION`: exact equality with full Wilson transfer is still not proven.
- `LO-C-INFINITE-GRID-SPINNETWORK-CONTRACTION`: can now proceed only as a dominated-envelope theorem, not as exact Wilson-transfer equality.
- full Wilson transfer theorem;
- infinite volume;
- continuum limit;
- Clay theorem.

## Interpretation

v1.15b repairs the immediate conceptual gap in v1.14/v1.15a, but only in the correct limited sense.

The safe statement is now:

\[
\boxed{\text{v1.14 gives a dominated spin-network envelope with a conditional block contraction screen.}}
\]

The unsafe statement remains false/unproven:

\[
\boxed{\text{v1.14 is exactly the full Wilson transfer contraction theorem.}}
\]

## Recommendation

The infinite-grid extension may now be revived, but only with the correct label:

```text
v1.16 — infinite-grid dominated-envelope spin-network contraction skeleton
```

It must explicitly carry the distinction between full Wilson equality and dominated-envelope control.
