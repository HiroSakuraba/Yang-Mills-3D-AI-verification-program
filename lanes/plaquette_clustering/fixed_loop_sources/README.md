# YM3D fixed Wilson-loop sources and one-step RG audit

**Status:** new analytic candidate for independent mathematical review; its exact-rational acceptance test and finite-geometry/finite-probability controls pass. This is a standalone extension of `lanes/plaquette_clustering`. It does not depend on the imported branched-Haar reports, the β ≤ 0.09 sharp-entropy candidate, or any claimed 4D RG result.

## Main candidate result: arbitrary finite closed fundamental Wilson loops

Consider a finite nondegenerate three-dimensional periodic cubic lattice (each period at least four), with oriented links, product normalized SU(2) Haar measure and

\[
 d\mu_\beta(U)={1\over Z_\beta}\exp\{\beta\sum_{p}\phi_p(U)\}\prod_e dH(U_e),\qquad \phi_p(U)=\tfrac12\operatorname{Tr}_2 U(\partial p),\quad 0\le\beta\le\tfrac3{25}.
\]

For any closed contours C,D, including contours with repeated links, define the normalized fundamental Wilson observables \(W_C=\frac12\operatorname{Tr}_2\operatorname{Hol}_U C\), \(W_D\) similarly, and their distinct-link supports \(S_C,S_D\). Set \(d_L(S_C,S_D)\) to the minimum graph distance in the **link-interaction graph**: distinct links are neighbors if they occur together in one elementary plaquette. (For intersecting supports, the distance is zero.) Every \(|W_C|\le1\), and every single-link oscillation is at most 2.

The **candidate theorem** obtained from the explicit single-link influence bound below plus the published Dobrushin–Föllmer covariance theorem is

\[
\boxed{\left|\langle W_C;W_D\rangle_\beta\right|\le 76\,|S_C|\,|S_D|\left(\tfrac{18}{19}\right)^{d_L(S_C,S_D)}.}
\]

The constants are **volume uniform at fixed lattice spacing**, not sharp, and do not confer cutoff-uniform physical mass. For any fixed finite loops the right side decays exponentially with separation, albeit slowly at the chosen endpoint. The same formula applies to plaquette Wilson loops; the plaquette-specific β ≤ 0.09 KP bound has a different metric and prefactor and is a separate candidate.

### Exact SU(2) Haar moment and conditional law

Write a group element as a unit quaternion \(u=(u_0,u_1,u_2,u_3)\in S^3\). For any unit quaternion A, an oriented plaquette contribution through a singled-out link e is \(\frac12\operatorname{Tr}(U_e^{\pm1}A)=u\cdot a\) for some unit vector \(a\in S^3\) (the sign/orientation is absorbed in a). A link belongs to four plaquettes in three dimensions. Its one-link conditional distribution is therefore

\[
 \pi_s(du)={e^{\beta u\cdot s}\over J(s)}\,dH(u),\qquad
 s=\sum_{j=1}^4 a_j,\quad |s|\le4,\quad J(s)=\int e^{\beta u\cdot s}\,dH(u)\ge1.
\]

The last inequality is Jensen's, using \(\int u\,dH=0\). The exact Haar covariance is \(\int u_i u_j\,dH(u)=\delta_{ij}/4\). It follows that for any vector v,

\[
 \operatorname{Var}_{\pi_s}(u\cdot v)\le \mathbb E_{\pi_s}(u\cdot v)^2\le \frac{e^{4\beta}}4|v|^2.
\]

Changing a different link e' changes at most one of the four plaquette staples (the n≥4 lattice geometry is checked in `tools/lattice_geometry.py`); if e' is not a link-neighbor of e it changes none. Thus s changes to s'=s+v with \(|v|\le2\). Interpolate \(s_t=(1-t)s+ts'\), for which \(|s_t|\le4\). The derivative of the normalized conditional density is the exact **centred score**

\[
 {d\pi_{s_t}\over dt}(u)=\beta\,[(u-\mathbb E_{\pi_{s_t}}u)\cdot v] \,\pi_{s_t}(u).
\]

Using total variation \(\|P-Q\|_{TV}=\frac12\int|dP-dQ|\), Cauchy–Schwarz and the Haar variance bound,

\[
 c_{e e'}\le\tfrac\beta2\int_0^1\sqrt{\operatorname{Var}_{\pi_{s_t}}(u\cdot v)}dt
 \le\frac{\beta e^{2\beta}}{4}|v|
 \le\frac{\beta e^{2\beta}}2
 \le \frac{\beta}{2(1-2\beta)}.
\]

Here \(e^x\le(1-x)^{-1}\) for \(0\le x<1\). Each link has exactly twelve distinct link-neighbors, so

\[
 \alpha:=\sup_e\sum_{e'}c_{ee'}\le\frac{6\beta}{1-2\beta}\le\frac{18}{19}<1
 \quad (\beta\le3/25).
\]

The finite-volume Dobrushin–Föllmer covariance estimate with a conservative convention (no factor 1/4 improvement taken) reads

\[
 |\operatorname{Cov}(F,G)|\le\sum_{e,e'}\operatorname{osc}_e(F) [(I-c)^{-1}]_{ee'}\operatorname{osc}_{e'}(G).
\]

Since \((I-c)^{-1}=\sum_{k\ge0}c^k\), its (e,e') entry is at most \(\alpha^{d_L(e,e')}/(1-\alpha)\): for k<d the entry vanishes, and for larger k it is at most the row sum \(\alpha^k\). Substitute oscillation ≤2 for each support link and the displayed alpha; \(4/(1-18/19)=76\). The rest is the standard covariance theorem applied to this finite compact-spin Gibbs specification. **Independent review must check the convention and application of that external theorem; the local code only audits arithmetic and geometry.**

The corresponding real-space inverse correlation length in *link-interaction-graph units* has lower bound \(\log(19/18)\); no assertion about physical mass at lattice spacing tending to zero is made. In particular β=3/25 is **not** in the ultraviolet Yang–Mills continuum regime.

### Relationship to the earlier result

The earlier `WILSON_LOOP_EXTENSION.md` bounded individual link influence using a worst-case likelihood-ratio inequality, giving the safe domain β ≤ 3/200 and α ≤ 36/47. This improvement uses **only** the exact SU(2) quaternion Haar second moment and the centred normalization score, not the stronger polymer entropy estimates. A link-level test at β=3/25 genuinely enlarges the domain for *arbitrary* finite loops beyond the separate β≤9/100 plaquette result.

### Reproduction

Run from the repository root:

```sh
python lanes/plaquette_clustering/fixed_loop_sources/tools/certificate.py
python -m unittest discover -s lanes/plaquette_clustering/fixed_loop_sources/tools -p 'test_*.py' -v
```

Expected canonical outputs: `alpha = 18/19`, covariance prefactor `76`, 27 tests including a finite Z2 marked-bridge algebra regression. Regression tests reject the equality endpoint β=1/8 for the rational sufficient criterion, an extra link neighbor, incorrect Haar moment/number of staples, and a negative coupling. A different analytic variance estimate could extend the threshold, but is not claimed.

**External theorem sources:** H. Föllmer, *A Covariance Estimate for Gibbs Measures*, J. Funct. Anal. 46 (1982), 387–395, DOI `10.1016/0022-1236(82)90053-2`; H. Künsch, *Decay of Correlations under Dobrushin's Uniqueness Condition and Its Applications*, Comm. Math. Phys. 84 (1982), 207–222.

Additional files: [`MARKED_POLYMER_IDENTITY.md`](MARKED_POLYMER_IDENTITY.md) for the exact source-augmented formal gas, and [`RG_ONE_STEP.md`](RG_ONE_STEP.md) for the normalized one-step RG identity and 4D comparison.
