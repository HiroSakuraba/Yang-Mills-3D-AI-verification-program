# Design Delta v1.15a — Wilson Plaquette Normalization / Spin-Network Block Identification Audit

## Purpose

v1.14 closed the heat/Wilson coefficient-ratio tail guards and the coefficient-histogram convolution envelope as theorem-skeleton fragments. Claude's review correctly identified the remaining load-bearing risk: v1.14 may bound an idealized recoupled spin-network block rather than the actual Wilson lattice transfer block.

v1.15a is therefore a foundation check before any infinite-grid/volume extension. It asks whether the v1.14 scalar histogram/tensor-network block is:

1. exactly the Wilson plaquette transfer block;
2. a proven dominating envelope for that block;
3. only an idealized spin-network model pending a normalization/intertwiner theorem.

## New executable

```text
wilson_plaquette_spin_network_normalization_audit_v1_15a.py
```

## Main decision

```text
V114_BLOCK_IDENTIFIED_AS_SPINFOAM_ENVELOPE_REAL_WILSON_TRANSFER_NORMALIZATION_OPEN
```

## What the audit verifies

### 1. Wilson plaquette character expansion

The local plaquette weight has the standard central character expansion

\[
 e^{\beta\cos\theta}=
 \sum_{a\ge0}c_a(\beta)\chi_{a+1}(\theta),
\]

with doubled spin index \(a=2j\) and

\[
 c_a(\beta)=I_a(\beta)-I_{a+2}(\beta)
 =\frac{2(a+1)}{\beta}I_{a+1}(\beta)>0.
\]

The executable checks the recurrence numerically over the audit range. The maximum relative recurrence discrepancy is \(4.05\times10^{-16}\), i.e. roundoff.

### 2. Central Haar convolution

For central characters,

\[
 \int \chi_a(xU)\chi_b(x^{-1}V)\,dx
 =\delta_{ab}\frac{\chi_a(UV)}{a+1}.
\]

This confirms the v0.97 character-coordinate pivot: central convolution/link integration is diagonal by Peter--Weyl orthogonality.

### 3. General link integration is a projector network

For a link incident to multiple plaquette representations, Haar integration gives an orthogonal projector

\[
 \int \prod_i D^{j_i}(g)\,dg
 =P_{\operatorname{Inv}(\otimes_i V_{j_i})}.
\]

Thus the exact Wilson spin-foam object has intertwiner/projector structure. It is not automatically equal to a scalar histogram envelope.

The audit detects multi-dimensional intertwiner spaces in the finite scan:

- degree 3 with an external channel already has dimension \(>1\);
- degree 4 without an external channel has dimension \(>1\);
- higher degrees grow rapidly.

## Consequence for v1.14

The v1.14 block remains valuable, but it should now be classified as:

\[
\boxed{\text{idealized spin-network / invariant-count envelope, not yet identified exactly with Wilson transfer.}}
\]

The next theorem step is not infinite volume. It is a projector-norm domination theorem:

\[
 \|T_{\rm Wilson}^{\rm block}\|
 \le
 C\,\mathcal E_{v1.14},
\]

or an exact derivation showing the v1.14 envelope is the correct transfer object in the intended reduced model.

## Outputs

```text
wilson_plaquette_character_expansion.csv
wilson_link_integration_intertwiner_factors.csv
wilson_vs_v114_block_identification.csv
wilson_normalization_gap_report.csv
wilson_plaquette_normalization_theorem_pieces.csv
wilson_plaquette_normalization_decision.json
wilson_plaquette_normalization_manifest.json
```

## Obligation updates

Closed/hardened:

- `LO-C-WILSON-CHARACTER-EXPANSION-NORMALIZATION`
- `LO-C-HAAR-LINK-PROJECTOR-FORM`

Still open/narrowed:

- `LO-C-REAL-PLAQUETTE-NORMALIZATION`
- `LO-C-PROJECTOR-NORM-DOMINATION`
- `LO-C-ACTIVITY-SCREEN-IMPLIES-CONTRACTION`
- `LO-C-INFINITE-GRID-SPINNETWORK-CONTRACTION`

## Recommendation

Do not proceed directly to the old v1.15 infinite-grid extension. The next bundle should be:

```text
v1.15b — projector-norm domination and activity-screen-implies-contraction lemma audit
```

Only after that should the infinite-grid/volume skeleton be revived.
