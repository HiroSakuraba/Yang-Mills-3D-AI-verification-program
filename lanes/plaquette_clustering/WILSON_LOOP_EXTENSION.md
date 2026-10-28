# Extended Wilson-loop correlations: a separate Dobrushin route

**Status:** analytic derivation offered for external review. The arithmetic certificate passes; application of the known Dobrushin--Föllmer covariance theorem remains a cited theorem, not a machine-verification output.

## Claim and observable

For a closed contour C made of directed links in the same 3D SU(2) cubic lattice, set

\[
W_C(U)=\tfrac12\operatorname{Tr}\!\prod_{\ell\in C}U_\ell^{\pm 1}.
\]

Gauge invariance follows because the holonomy of a closed loop transforms by conjugation at its basepoint. Since SU(2) is unitary, |W_C|<=1, and changing one link in C changes W_C by at most 2; outside C its single-link oscillation vanishes. This applies to arbitrary **fixed finite** closed loops, not just 1x1 loops.

## Single-link conditional laws and Dobrushin constant

Conditioning on every link except e gives a Haar density proportional to the exponential of the contributions from the four plaquettes containing e. If the configuration of a *different* link e' is modified, the conditional density changes only if e and e' belong to a common plaquette. There are at most 4*3=12 such links.

When one neighboring link changes, each affected normalized trace \(\phi_p\) changes by at most 2 pointwise. In a nondegenerate 3D cubic box, e and e' share at most one plaquette. The unnormalized conditional likelihood ratio is therefore between \(e^{-2\beta}\) and \(e^{2\beta}\), and after normalization the ratio between the two conditional probability densities is between \(e^{-4\beta}\) and \(e^{4\beta}\). The total variation distance satisfies

\[
 c_{e,e'} \le e^{4\beta}-1 \le \frac{4\beta}{1-4\beta},
\]

using \(e^x\le(1-x)^{-1}\) for 0<=x<1. The finite-dimensional interaction matrix has maximum row sum

\[
 \alpha\le 12\frac{4\beta}{1-4\beta}\le\frac{36}{47}<1
\qquad (0\le\beta\le3/200).
\]

Thus \((I-c)^{-1}=\sum_{n\ge0}c^n\) is well-defined. In the **link-interaction graph** (two link variables adjacent if they enter a common plaquette), \((c^n)_{e,e'}=0\) for n<d(e,e'), and each matrix entry is at most the maximum row sum \(\alpha^n\), giving

\[
 [(I-c)^{-1}]_{e,e'}\le\frac{\alpha^{d(e,e')}}{1-\alpha}.
\]

The Dobrushin--Föllmer covariance estimate bounds the connected correlation of bounded local functions by the sum over their link oscillations and the entries of \((I-c)^{-1}\). Inserting \(\delta_e W_C\le2\) yields the conservative bound

\[
\boxed{\left|\langle W_C;W_D\rangle\right|
 \le\frac{4|C||D|}{1-\alpha}\alpha^{d_{\rm link}(C,D)}
 \le\frac{188}{11}|C||D|(36/47)^{d_{\rm link}(C,D)}.}
\]

Here `distance(C,D)=min_{e in support C,e' in support D} d(e,e')`; the number of distinct links in the supports may be used in place of the (larger) contour lengths. For disjoint contours d>=1. There is no assumption that a bare Wilson insertion is itself a local plaquette activity. This bound is **independent of physical torus volume**, with constants depending on the loop lengths.

**References.** H. Föllmer, *A Covariance Estimate for Gibbs Measures*, Journal of Functional Analysis 46 (1982), 387–395, DOI `10.1016/0022-1236(82)90053-2`; H. Künsch, *Decay of Correlations under Dobrushin's Uniqueness Condition and Its Applications*, Communications in Mathematical Physics 84 (1982), 207–222.

**Limitations.** Neither \(36/47\) nor the prefactor is optimized. At weak bare coupling (large beta) the Dobrushin row sum fails. The estimate is not directly uniform in physical distance as lattice spacing approaches zero. Reflection positivity, a transfer-matrix spectral conclusion and RG compatibility are separate obligations.

## Relation to the marked-polymer route

Unit plaquette loops have both the marked-polymer result and this Dobrushin bound, with different metrics. Extended loops use the Dobrushin route as a complete baseline; **a dressed-loop polymer estimate at a substantially larger beta remains an open research task**. This distinction prevents replacing the inserted numerator by an unmarked partition function or asserting that a plaquette-only activity vector covers an extended contour.
