# Dependency trace II — from the funded construction to a finite-gas inequality

**Scope:** Research-only analysis of the October 2026 formalization at commit 3456e5e75cf8d4cd558955a5c7638fba2d68f464. The upstream Lean build and working-group Comparator checks have not been rerun in this project. Every transfer to 3D remains an independent mathematical obligation.

## Main construction path

The source proof does not create the Wilson continuum theory directly from the public theorem's statement. Its quantitative obligations are deferred through a succession of selected witnesses:

1. [Construction.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/Construction.lean) packages nonperturbative existence into the advertised public construction.
2. [YM/Nonperturbative/Continuum.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/Nonperturbative/Continuum.lean) reads the previously chosen funded run and refines the extraction order.
3. [YM/Independent/ConstructionRun.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/Independent/ConstructionRun.lean#L14-L32) invokes the treasury/period run selector using **garment10**, a native component choice, and an EventuallyPaid requirement specialized to **True**.
4. [YM/Integration/NativePreselectedPostnumericPeriodRun.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/Integration/NativePreselectedPostnumericPeriodRun.lean#L31-L119) selects a sheet, quote, pre-length floors and postnumeric payments, obtaining a Run via allFactorWithTreasuryPeriod and engageWithCustodyFactor.
5. [YM/R2I/Campaign/Accepted.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/R2I/Campaign/Accepted.lean#L60-L87) packages the conditions into Funded, with named components including localBudget, poly, halo, tic, paced and stoves.
6. [YM/RG12/Burst/Wardrobe.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/RG12/Burst/Wardrobe.lean#L18-L63) defines the scale-dependent garment10 Decal, including betaF exponents and degreePrice inequalities bounded by 1/2.

The term **funded** here is a formal predicate, not a 3D proof certificate. The trivial EventuallyPaid witness for True asserts no independent new numeric bound. A usable transfer must trace the actual source inequalities, including their Wilson-integral meaning, scale dependence and all volume factors.

## Quantitative source with a portable algebraic core

The clearest immediately useful estimate is [YM/Push/BETA_TRANSPORT/Activity.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/Push/BETA_TRANSPORT/Activity.lean#L41-L126).

- **product_diff** is a finite-product perturbation bound in terms of individual absolute majorants.
- **gas_diff** lifts it to a gas of forced-label subsets under the explicit assumption that both activity representations have the **same forced-address data**.
- **deviation_diff** combines the gas and additive activity comparisons.
- The module's header says **no volume-independent bound is claimed**.

[YM/RG/Activities.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/RG/Activities.lean#L59-L129) defines the hypotheses precisely: SumBudget requires a nonnegative, absolutely summable coefficient list; a forced address has support/inventory and a test; admissibility enforces disjoint supports and an exact union of inventories matching the cutoff flags.

The source gas_diff upper bound has the schematic form

\[
\lvert G_S(U)-G_T(U)\rvert\le \delta\exp\!\left(2\left[\sum_i k_i+1\right]\right),
\]

given a common forced list, positive delta at most one, a summable majorant list and the stated difference-budget hypotheses. The source does **not** establish that the sum of k_i is uniformly bounded in lattice volume for our 3D theory.

This distinction is crucial: the finite algebraic lemma transfers to arbitrary finite support geometries; its required coefficient bounds and any thermodynamic limit do not transfer automatically.

## Nonterminal polymer warning

[YM/Push/ABSOLUTE_SUMS/Clusters.lean](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/Push/ABSOLUTE_SUMS/Clusters.lean#L4-L22) explicitly distinguishes absolute bounds on a graph series from the physical gas-positivity and gas-to-log identities. Our 3D K-star compatibility matrix therefore needs a separately proved identification with actual Wilson activities and an independently verified convergence condition.

## What the next 3D proof must supply

1. Explicit gauge-invariant SU(2) activity coefficients arising from the genuine 3D Wilson measure, not the hand-selected rational values used in the test example.
2. Fixed-census/admissibility transfer or a separate bound on any support/cutoff-induced eligibility changes.
3. A common weighted norm and absolute summability uniformly in volume and the scale slab.
4. A dyadic RG map and gauge-ripple correction bound expressed in that norm.
5. An observable-specific reconstruction and physical spectral bound before any mass-gap claim.

The finite calculation and independent checker are documented in [FINITE_GAS_TRANSFER.md](FINITE_GAS_TRANSFER.md). They do not close any gate in program.yaml.
