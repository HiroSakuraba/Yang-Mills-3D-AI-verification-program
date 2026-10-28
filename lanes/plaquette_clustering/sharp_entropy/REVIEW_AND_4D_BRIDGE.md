# Scope and comparison with the 4D Wilson-loop RG manuscripts

This note compares the new **strong-coupling plaquette result** with the source project `HiroSakuraba/4D_Wilson_Loop_RG` as of 27 October 2026. The fork is currently identical to `MathePhysics/4D_Wilson_Loop_RG` at commit `e6a3c4bfd02c5219091aa1654e7f59352ef29fb7`. Links below are exact source locations, not a claim that their proofs have been independently certified by us.

## What transfers conceptually

- **Connected observable markings.** The finite-volume 3D computation takes mixed derivatives of the physical `log Z`, with the product of local plaquette normalizers removed only after confirming the two distinct sources give no mixed derivative. See `SHARP_ENTROPY.md`, §§1 and 5. The 4D first-step manuscript, `Manuscripts under Construction/WILSON_FIRST_RG_STEP_V5.tex`, similarly distinguishes the unmarked measure `rho_1 = T[rho_0]` from the inserted complex measure `N_1=T[rho_0 W]`, and defines a Radon–Nikodym ratio `W_1=dN_1/d rho_1`. These are different transformations of the same physical object and should not be conflated.
- **Normalization cannot be discarded.** The 4D draft `drafts/WILSON_IT1_CONTINUUM_CUTOFF_COMPARISON_2026_10_27.md`, §2, uses a *centered cutoff mark* combining numerator and denominator differences: `H_K(1)=Z_(K+1)(F_(K+1)-F_K)`. Our 3D proof derives an exact mixed `log Z` identity at one cutoff. It does **not** supply a cutoff-comparison estimate or control the Bałaban `R`-operation.
- **Localization.** The direct 3D polymer gas is link-connected, so a marked cluster touching `p` and `q` must span their plaquette-graph distance. The 4D iteration draft requires a much subtler localization of *dressed* loop insertions, including characteristic functions, complex backgrounds, large-field polymers and external-field tails. In particular the October 27 status report labels the revised `R-far''` reading and subsequent repairs as not fully re-reviewed.

## Why our new 3D bound does not close the 4D gaps

1. The new estimate holds only at **small lattice beta**. In four-dimensional asymptotically free YM, ultraviolet refinement goes to weak bare coupling, a very different regime. Neither 3D threshold (0.09 or the reported 0.185) can be substituted for 4D RG control.
2. The source-free 3D KP measure is positive at real beta. Our complexification is at **two local plaquette sources** with an explicit disk. It is not the full moving-domain, complex-background, multi-scale analyticity class of the 4D dressed-loop induction.
3. Dobrushin covers arbitrary *fixed* finite loops at beta <=0.015; the stronger `0.09` result covers two unit plaquettes only. The 4D manuscript targets renormalized large loops and correlations over iterated scales.
4. The 4D cutoff comparison explicitly reports its Wilson-root extension in §6.10 as unresolved due to second-class re-entry, while §6.11 and parts of §6.12 are unreviewed. Our local KP calculation avoids those sectors entirely rather than solving them.

## Concrete interface for a later RG-to-clustering bridge

A future handoff would need: (a) a scale-local, source-analytic bound for the *generated multi-loop effective action* and dressed insertion after `T` and `R`; (b) enough localization in the physical observable to charge a connected cluster spanning a separation; (c) a uniform nonvanishing/normalization estimate for the physical denominator under the inserted/empty comparisons; and (d) a uniform-in-cutoff summable error estimate along the RG flow. The current scripts verify **none** of (a)–(d).

Source anchors:

- `https://github.com/HiroSakuraba/4D_Wilson_Loop_RG/blob/main/Manuscripts%20under%20Construction/WILSON_FIRST_RG_STEP_V5.tex`
- `https://github.com/HiroSakuraba/4D_Wilson_Loop_RG/blob/main/drafts/WILSON_IT1_STATUS_REPORT_2026_10_27.md`
- `https://github.com/HiroSakuraba/4D_Wilson_Loop_RG/blob/main/drafts/WILSON_IT1_CONTINUUM_CUTOFF_COMPARISON_2026_10_27.md`

**Research gates:** keep the β≤0.09 candidate at `analytic_review_pending`; keep the source KP data integrity lane separately pending its branched checker; neither gate closes an RG or continuum target.
