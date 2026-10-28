# Cross-project audit: 3D observable lane versus the 4D Wilson-loop RG fork

Source repository (as of 27 October 2026): <https://github.com/HiroSakuraba/4D_Wilson_Loop_RG>, forked from `MathePhysics/4D_Wilson_Loop_RG`. At inspection both tips were `e6a3c4bfd02c5219091aa1654e7f59352ef29fb7`. Documents inspected:

- `Manuscripts under Construction/WILSON_FIRST_RG_STEP_V5.tex`, theorem `thm:main-theorem`.
- `drafts/WILSON_IT1_STATUS_REPORT_2026_10_27.md`, especially *Open Gaps* and *Coverage of the Construction*.
- `drafts/WILSON_IT1_CAUCHY_ESTIMATE_2026_10_27.md`, Sections 6–11.
- `drafts/WILSON_IT1_CONTINUUM_CUTOFF_COMPARISON_2026_10_27.md`, Sections 1–2, 6, 7, focused-review status.

## What is shared, what is not

| Obligation | This 3D baseline | 4D source and comparison |
|---|---|---|
| Local gauge-invariant insertion | `phi_p=Tr_F(U_p)/2`, one elementary face; or `W_C` on a finite loop | V5 begins with a normalized irreducible character on an oriented **closed** loop; this cannot be approximated by an open transport without a covariant frame. |
| Normalization | Mixed derivatives of `log Z`; local `z(beta)` factors cancel for `p!=q`; Dobrushin applies directly to the **normalized physical Gibbs law** | V5 uses `N_1=T[rho_0 W_C]`, `rho_1=T[rho_0]`, `W_1=dN_1/d rho_1` and separates perimeter/corner factors `kappa_C`. The cutoff note's Eq. (1) has the *centered denominator mark*, not just numerator differences. |
| Connected structure | `log Xi` Ursell clusters touching both marked plaquettes; line/loop covariance from Dobrushin influence paths | D2.7 and the iteration drafts require a linked polymer/line-defect gas; their localization of loop insertion pieces and large-field R-operations must be paid for together. |
| Spatial localization | Plaquette link-adjacency distance and link conditional-interaction distance; elementary finite-range metrics | The 4D notes use nonlocal field reconstruction, transported slots, collar supports, and tree-length localization. Substituting our graph metric for their scale-dependent norms would be unjustified. |
| Large fields | Compact-link strong-coupling bounds treat all group configurations directly; no field cutoffs or R-operations | The October 27 status report identifies D2.7 R-operation obligations and recently repaired but not re-reviewed localization statements R-far-double-prime. |
| Scale or volume | Uniform in finite *volume* only, at beta<=0.015, lattice spacing fixed | V5 is a **first** RG step. Full-sequence cutoff comparison, large-field normalization and second-class re-entry in the later drafts are not proved. |

## Two explicit normalization traps

1. A Wilson loop's extracted perimeter factor may become exponentially small as the contour grows. An *absolute* error small in bare coupling is not necessarily small **relative** to `kappa_C`. V5's main theorem/remarks explicitly distinguish these conditions.
2. For comparing two UV cutoffs, subtracting only their Wilson numerators does not control the ratio of normalized expectations. The 4D cutoff note uses a centered measure mark: `H_K = omega_K^+ - c_K omega_K^- - F_K(nu_K^+ - c_K nu_K^-)`, and `F_{K+1}-F_K=H_K(1)/Z_{K+1}`. This denominator must remain with the marked expansion.

## Roadmap after the independent baseline

1. **Strengthen 3D:** validate fresh branched-source input and replace the elementary animal/N4 bound with the imported enumerated KP majorant, *plus a complex-source stability margin*. The current beta<=0.185 unmarked certificate alone does not prove source analyticity or a positive decay exponent at that endpoint.
2. **Marked 3D transfer:** construct the double-source inserted polymer expansion explicitly for a finite rectangular Wilson contour. Track the normalization/connected subtraction using `log Z(s,t)`. Audit gauge-covariant closure and sources on the boundary; compare against the unit-loop Dobrushin bound.
3. **4D only as a separate project:** construct a typed dictionary between 3D activities and the 4D dressed-loop species, with explicit dimension factors (4 versus 6 plaquettes per link), step index, source radii, gauge-localization domain, and strong/weak coupling conventions. Do not transplant `beta<=0.015` or 3D entropy caps to 4D.
4. **Continuum:** the 4D draft's missing one-step cutoff-stability source, second-class re-entry budget, and stopping-scale relative weights require independent estimates; no such closure is claimed by this lane.
