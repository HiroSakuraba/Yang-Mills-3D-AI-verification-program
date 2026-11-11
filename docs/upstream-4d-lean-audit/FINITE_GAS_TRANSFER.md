# An exact finite polymer-gas perturbation lemma on 3D supports

**Research status:** Elementary finite inequality and a separately audited rational example. This is not a 3D Wilson activity calculation, an RG contraction, or a volume-uniform result.

**Upstream source:** [product_diff and gas_diff](https://github.com/yang-mills-group/OpenAI-YM-20261028/blob/3456e5e75cf8d4cd558955a5c7638fba2d68f464/YM/Push/BETA_TRANSPORT/Activity.lean#L41-L113).

## Statement and proof

For a finite label set I, fix an admissibility family F contained in the powerset of I. Let p_i and q_i be real signed activities, with nonnegative h_i satisfying max(|p_i|,|q_i|) <= h_i. Set

\[
Z_F(p)=\sum_{S\in F}\prod_{i\in S}p_i,\qquad d_i=|p_i-q_i|.
\]

Then

\[
\boxed{
|Z_F(p)-Z_F(q)|\le
\sum_{S\in F}\sum_{i\in S}d_i\prod_{j\in S\setminus\{i\}}h_j
\le\sum_{i\in I}d_i\prod_{j\ne i}(1+h_j).
}
\]

If d_i <= delta h_i for all i, delta >= 0, then also

\[
|Z_F(p)-Z_F(q)|\le
\delta\left(\prod_{i\in I}(1+2h_i)-1\right).
\]

**Proof:** Fix an ordering of S. Telescope the difference of the two products by replacing one factor at a time; each resulting term contains one p_i-q_i and other factors bounded by h_j. Sum absolute values over S in F to get the first bound. Extend the nonnegative sums to every subset of I and expand the finite product to obtain the second. The delta bound follows since for every nonempty S, |S| <= 2^|S|. No positive-activity assumption is made. The admissible family **must be the same** for both sums.

## Reproducible 3D test case

The generator creates six unwrapped integer-lattice plaquettes, each with four explicit vertex sites and an inventory marker. The common admissibility rule requires disjoint supports and exact coverage of two flags. Exactly four subsets satisfy that rule.

| Exact quantity | Value |
|---|---:|
| Z(p) | -1/160 |
| Z(q) | -23/3500 |
| Absolute difference | 9/28000 |
| Restricted telescoping bound | 73/4032 |
| Full product bound | 32125/129024 |
| Maximal relative delta | 4/25 |
| Coarse delta-product bound | 313/450 |

These are deliberately conservative upper bounds. In particular, their magnitude does **not** demonstrate a small RG contraction factor.

The generator emits [finite_gas_seed.json](finite_gas_seed.json). The independent checker reconstructs every support from the coordinate/axis data, recomputes admissibility, products, signed differences and rational bounds from scratch. The regression suite contains ten input/negative controls plus an exhaustive two-label signed-grid test and an explicit eligibility-change counterexample.

## Why eligibility changes matter

If one model admits the empty set and the singleton {1}, while another admits only the empty set, and p_1=q_1=1, then both coefficient lists are identical but the two gas sums differ by 1. Therefore a beta-transport bound cannot be used when cutoff flags, support membership or gauge-lane eligibility changes without an additional error term.

## Reproduction

Run these commands from the repository root:

- python tools/build_finite_gas_transfer.py --output docs/upstream-4d-lean-audit/finite_gas_seed.json
- python tools/check_finite_gas_transfer.py docs/upstream-4d-lean-audit/finite_gas_seed.json
- python -m unittest discover -s tests -p 'test_finite_gas_transfer.py' -v

This finite example has **no generator imports in its independent checker**. Its output explicitly asserts no closed proof gates.

## Requirements for genuine 3D transfer

The next actual Yang-Mills lemma must construct the coefficients from the SU(2) Wilson law, provide configuration-uniform and volume-uniform weighted bounds, and handle changed eligibility/collision supports. Only then can this finite stability bound become part of an independently closed analytic ledger.
