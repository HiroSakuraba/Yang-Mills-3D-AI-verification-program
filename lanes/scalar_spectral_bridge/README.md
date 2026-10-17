# Scalar correlation decay and physical spectral support

This research note supplies the transfer-space identification and spectral
argument missing from the earlier scalar plaquette note. It also sharpens its
conditional channel threshold by using the polynomial decay rate directly.
The reasoning is for review; the executable checker audits constants and scope,
not the full analytic argument. **No analytic program milestone is closed.**
The existing 2D-validation requirement and its unmet prerequisites remain intact.

## Measure, comparison and limits

Use the unfixed Wilson measure with normalized Haar measure on SU(2) links,
weight exp[beta sum_p Tr(U_p)/2], and 0<beta<1/12. Space is an L-by-L torus,
L>=3; Euclidean time tends to the integer line. Each positive link belongs to
four distinct plaquettes. Its conditional density is a bounded, strictly positive
continuous function of finitely many other links. Hence the specification is
quasilocal; compactness supplies finite-volume subsequential Gibbs limits.
No gauge fixing or gauge-variant change of physical measure is used here.

Changing one neighbouring link changes each common-plaquette log weight by a
function with oscillation <=4 beta. For densities related by an exponential
tilt h, total variation distance <=tanh(osc(h)/4). If two links share multiple
plaquettes, sum their multiplicities before using tanh(sum)<=sum tanh. There
are twelve other-link incidences per updated link, so the influence row sum is
at most 12 tanh(beta)<=alpha=12 beta<1, uniformly in volume and boundary values.
The same bound works in the column direction by the symmetric incidence
majorant; use the majorant, rather than asserting symmetry of exact influences.

Apply the classical Dobrushin comparison theorem in the discrete site metric
on link variables. Tilt by exp(sG) and differentiate at s=0: the conditional
change at link f is at most |s| delta_f G/4+o(s). This gives

    |Cov(F,G)| <= (1/4) sum_(e,f) delta_e F [(I-C)^(-1)]_(e,f) delta_f G.

The finite-range contraction excludes boundary influence in the limit and gives
a unique Gibbs state. One may obtain infinite-time cylinder limits first at
fixed L, then take L->infinity for local observables. The row-sum bound and the
support-distance estimates are uniform. Absolute spatial summability, not a
formal unnormalized infinite spatial sum, supplies dominated convergence for
zero-momentum two-point sums. Subtract each state's own vacuum mean.
These steps use the hypotheses of the cited comparison theorem; their analytic
application is documented here and is not certified by the constants script.

For P_z=1-Tr(U_xy(z))/2, delta P has total link oscillation at most 8. Sharing a
plaquette changes a link-anchor coordinate by at most one. The covariance and
spatial-shell estimates therefore give, for the normalized centered sum
F_L=(1/L) sum_z(P_z-<P_z>) and every integer t>=0,

    0 <= G_L(t) <= [16/(1-alpha)] alpha^t B_alpha(t),
    B_alpha(t) = (2t+3)^2
                  +8 alpha [(t+2)/(1-alpha)+alpha/(1-alpha)^2].

The absolute-value bound comes from comparison; nonnegativity comes separately
from the positive transfer representation below. At beta=1/20 this is
40(3/5)^t(4t^2+24t+51), uniformly in L. This bound controls the elementary
plaquette sum; larger loops need their own oscillation/support factors.

## Physical transfer space at finite spatial volume

Let X be the spatial-link configuration space and H=L^2(X, product Haar).
Restrict to the closed subspace invariant under site gauge transformations.
Spatial plaquettes define the bounded, invertible multiplication operator

    B(U)=exp[(beta/2) sum_spatial_plaquettes Tr(U_p)/2].

Let K be the product, over spatial links, of convolution operators with central
kernel k_beta(g)=exp[beta Tr(g)/2]. A temporal-gauge one-slab calculation gives
T=B P K B, with P the orthogonal Haar projector onto gauge-invariant functions.
B and K commute with P, so on the physical subspace T=B K B. This statement
concerns the original Wilson slab: temporal links implement the gauge projector.
It does not assert that arbitrary gauge-fixed/smeared observables preserve it.

For doubled spin n, the convolution eigenvalue on a matrix coefficient is

    kappa_n = integral k_beta(g) chi_n(g)/(n+1) dg
            = sum_(r>=0) beta^(2r+n)/[2^(2r+n) r! (r+n+1)!] > 0.

The division by n+1 is essential: an ordinary character-expansion coefficient
is not the convolution eigenvalue. Thus K is self-adjoint, positive and
injective. The continuous finite-volume kernel is compact. Its strictly
positive integral kernel, after gauge projection and multiplication by B,
supplies a simple positive leading eigenfunction Omega_L with eigenvalue
lambda_L>0. Work with the positive contraction T_hat=T/lambda_L.
This is a dimension-specific reconstruction of the standard transfer-matrix
construction; the cited original source treats a four-dimensional lattice,
so its theorem is not imported as an unexamined 3D black box.

Finite temporal-slab limits with positive endpoint states project onto Omega_L.
Their local expectations satisfy the same Wilson specification. Dobrushin
uniqueness identifies that state with the infinite-time Gibbs state used above.
A bounded, real gauge-invariant time-slice observable F acts by multiplication;
its centered vector is psi=(F-<F>)Omega_L. The slab integral then gives

    <psi,T_hat^t psi> = <F(t) F(0)>_connected.

For F_L the prefactor 1/L makes this exactly the volume-normalized correlator,
not the extensive correlator. Injectivity allows H_L=-log(T_hat)/a_t by spectral
calculus, for a declared physical time step a_t>0. No block-distance conversion
or finite-periodic-time cosh fit enters this infinite-time identity.

## A polynomial prefactor does not weaken the asymptotic threshold

Let mu be the positive spectral measure of psi for T_hat, supported on [0,1].
Suppose its moments satisfy integral lambda^t dmu <=A p(t) alpha^t for all
integer t>=0, with fixed polynomial p and alpha<1. If mu([r,1])>0 for some
r>alpha, then

    mu([r,1]) <= A p(t) (alpha/r)^t -> 0,

which is a contradiction. Thus mu((alpha,1])=0. The spectral theorem then
bounds T_hat by alpha on the closed cyclic subspace generated by psi. Its
Hamiltonian spectral support has energies at least -log(alpha)/a_t.
This argument permits spectral weight exactly at alpha. It proves neither that
the endpoint is attained nor that there is an isolated eigenvalue there.

Consequently the review-stage scalar estimate gives the channel threshold
log(5/3)/a_t at beta=1/20, approximately 0.510826/a_t, rather than the looser
log(5/4)/a_t obtained by first absorbing the polynomial into a (4/5)^t bound.
The code encloses the logarithmic endpoint with rational bounds using two
independent convergent series. It does not turn the analytic premises into a
machine-verified theorem.

The finite-L cyclic statement is precise. For a thermodynamic-limit
zero-momentum correlator, positivity follows from limits of finite positive
moment sequences; bounded total mass and compact [0,1] support give a limiting
positive measure. The uniform spatially summed bound imposes the same support
restriction. This limit is a correlator spectral measure; no assertion is made
that an unnormalized infinite-volume spatial sum is a vector in an arbitrary
reconstruction Hilbert space.

## Limits of the result and executable checks

One observable can miss other states. A channel support bound does not establish
a full-space gap, identify a spin-zero particle, prove a mass value, or establish
continuum scaling. The fixed strong-coupling window does not reach the
weak-bare-coupling trajectory needed when lattice spacing tends to zero.
A full-space conclusion would require a dense physical observable family with
one common decay rate, and the appropriate infinite-volume identification.

```sh
python lanes/scalar_spectral_bridge/tools/build.py
python lanes/scalar_spectral_bridge/tools/check_constants.py
python -m unittest discover -s lanes/scalar_spectral_bridge/tests -v
```

The standalone report has `analytic_gate_closed: false`. It audits two exact
constant sets and independent logarithm enclosures. Tests include five artifact
corruptions, a positive spectral atom above the claimed radius that eventually
violates the polynomial bound, and a three-state example showing that an
observable can miss a slower sector. No decision.json or program.yaml entry is
created. Existing CLOSED code/artifacts are unchanged.

Primary sources:

- Rebeschini and van Handel, *Comparison Theorems for Gibbs Measures*, classical
  comparison theorem and uniqueness discussion: https://arxiv.org/abs/1308.4117.
- Lüscher, *Construction of a selfadjoint, strictly positive transfer matrix for
  Euclidean lattice gauge theories* (1977), https://doi.org/10.1007/BF01614090;
  original manuscript https://bib-pubdb1.desy.de/record/396349/files/7611148.pdf.
- The repository's original [scalar correlation derivation](../glueball_spectroscopy/SCALAR_CORRELATION_DERIVATION.md)
  supplies the explicit link-distance and shell-sum calculation. The spectral
  endpoint argument and specialization are developed in this note for review.
