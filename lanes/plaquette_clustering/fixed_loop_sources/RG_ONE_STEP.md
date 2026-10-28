# Exact one-step RG normalization and the two-Wilson conditional contact term

**Claim type:** exact finite-measure identities, not a constructed iterative RG estimate.

Let \(\mu_0\) be any strictly positive normalized **finite-lattice** gauge-field Gibbs probability, and let \(M:U\mapsto V\) be a measurable, gauge-equivariant blocking map. Put \(\mu_1=M_*\mu_0\). For bounded Wilson insertions \(W_C,W_D\) define three finite signed/complex measures on coarse fields:
\[
 N_C=M_*(W_C\mu_0),\quad N_D=M_*(W_D\mu_0),\quad N_{CD}=M_*(W_CW_D\mu_0).
\]
Since \(|W_C|,|W_D|\le1\), these are absolutely continuous with respect to \(\mu_1\). Let \(F_C=dN_C/d\mu_1\), \(F_D=dN_D/d\mu_1\) and \(F_{CD}=dN_{CD}/d\mu_1\). They are the exact coarse conditional expectations of the original Wilson observables and their product, with modulus bounded by one. Gauge equivariance of M and gauge invariance of the original measure and observables make the resulting conditional versions gauge invariant almost everywhere.

The exact **one-step law of total covariance** is
\[
\boxed{\operatorname{Cov}_{\mu_0}(W_C,W_D)=
\operatorname{Cov}_{\mu_1}(F_C,F_D)
+\mathbb E_{\mu_1}[H_{CD}],\qquad
H_{CD}:=F_{CD}-F_CF_D.}
\]
Proof: \(\mathbb E_{\mu_1}F_{CD}=\mathbb E_{\mu_0}W_CW_D\) and \(\mathbb E_{\mu_1}F_i=\mathbb E_{\mu_0}W_i\); add and subtract \(\mathbb E_{\mu_1}(F_CF_D)\). This identity is exact for **the full physical probability**, including every large-field history, not an unnormalized individual RG branch. `tools/conditional_rg.py` tests the same algebra with exact rational discrete probability models. In particular, the **conditional contact term cannot be omitted** unless it is independently shown small (or zero) under the actual blocking.

It is not enough to replace \(F_{CD}\) by \(F_CF_D\): conditional expectations do not in general commute with multiplication. Nor does our original plaquette/local-link Dobrushin bound immediately imply that \(F_C\) is localized near the blocked image of C: conditioning on the entire coarse field, or history-dependent operations, can create nonlocal dependencies. **No such localization theorem is claimed.**

## Exact normalization at a single step

For unnormalized fine density \(\rho_0\), let \(\rho_1=M_*(\rho_0 dU)\) and \(N_C=M_*(W_C\rho_0 dU)\). The partition function \(Z_0=\int\rho_0dU=\rho_1(1)>0\) remains in the denominator, so
\[
\langle W_C\rangle_0=N_C(1)/Z_0.
\]
The normalized object \(dN_C/d\rho_1\) is precisely the kind of *outgoing Wilson observable* used in the fork's V5 first-step manuscript. It is never a bare insertion evaluated at an arbitrary reconstructed background unless an explicit error bound supplies that identification.

## Exact two-cutoff centred mark

If \(Z_K,\kappa_K,N_K(C)\) denote the positive vacuum mass, the nonzero perimeter/corner renormalization and the Wilson numerator at cutoff K, write \(F_K=N_K/(\kappa_KZ_K)\). For arbitrary positive scalar \(c_K\) introduce the common-carrier **total-mass** centered mark
\[
 H_K(1)=\kappa_{K+1}^{-1}N_{K+1}
  -c_K\kappa_K^{-1}N_K
  -F_K\bigl(Z_{K+1}-c_KZ_K\bigr).
\]
Then the cancellation is algebraic:
\[
 H_K(1)=Z_{K+1}(F_{K+1}-F_K).
\]
Bounding only \(|N_{K+1}-c_KN_K|\) is insufficient: the vacuum normalization term is essential. The fork's `drafts/WILSON_IT1_CONTINUUM_CUTOFF_COMPARISON_2026_10_27.md` §2 gives the **measure-valued** formulation, preserving histories and cutoff-dependent R-operations; this equation is just its exact total-mass reduction, *not* an estimate of either side.

## Handoff checklist for a genuine RG-to-clustering theorem

1. **Source support:** bound the *generated* gauge-invariant multi-loop interactions and both loop insertions in a norm tracking their link/cube support and analytic source radius. The direct fixed-lattice covariance bound does not bound their RG images.
2. **Conditional contact:** show \(H_{CD}\) is small with a connected distance penalty, not merely bounded in sup norm by 2. For separated loops, the contact may be created by integrated-out fluctuations.
3. **Observable locality:** show \(F_C\) admits a localized expansion near C with summable exponentially decaying tails. Gauge covariance and a global pushforward identity alone are insufficient.
4. **Physical normalization:** preserve the numerator with its original full denominator through the R-operation and compare old/new vacuum masses at fixed stopping scale. Individual signed/complex selected branch integrals need not admit positive normalizations.
5. **UV stability:** obtain a sum over scale-dependent errors uniform in cutoff, instead of importing the present β≤3/25 condition into the weak-bare-coupling continuum regime.

These obligations match the source distinctions in `HiroSakuraba/4D_Wilson_Loop_RG`: V5's first-step `N_1`, `rho_1`, `W_1`; the 27 October cutoff note's §2 centered mark, §6.10 unresolved Wilson-root second-class re-entry and §6.11 unreviewed recent-step calculations; and the D2.7 `R-far''` localization reading that had not been re-reviewed in the status report. They are **comparisons, not imported proof inputs**.

Exact source links:
- https://github.com/HiroSakuraba/4D_Wilson_Loop_RG/blob/main/Manuscripts%20under%20Construction/WILSON_FIRST_RG_STEP_V5.tex
- https://github.com/HiroSakuraba/4D_Wilson_Loop_RG/blob/main/drafts/WILSON_IT1_CONTINUUM_CUTOFF_COMPARISON_2026_10_27.md
- https://github.com/HiroSakuraba/4D_Wilson_Loop_RG/blob/main/drafts/WILSON_IT1_STATUS_REPORT_2026_10_27.md
