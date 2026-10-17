# Scalar plaquette correlation bound — derivation for review

This is an analytic research note, not a CLOSED analytic gate. The independent
checker audits the loop geometry, rational constants and constructed reference
matrices. It does not certify the comparison theorem's hypotheses, the physical
transfer representation, or a glueball particle. No 2D-validation waiver is used.

## Action, operator and units

Work in three Euclidean dimensions, with one time direction and two spatial
directions. On SU(2) links use

    μ(dU) ∝ exp[x Σ_p tr U_p] ∏_e dU_e,    tr = Tr/2, x > 0.

Let P_z(t)=1-tr U_xy(z,t) be the spatial elementary plaquette, and let
O_L(t)=Σ_z[P_z(t)-<P_z(t)>] on an L×L spatial torus with L≥3 and infinite time.
Define the connected zero-momentum correlator

    G_L(t) = Cov(O_L(t), O_L(0))/L²
           = Σ_z Cov(P_z(t), P_0(0)).

This normalization is essential. It removes the extensive spatial-volume factor;
a naive product of the oscillation norms of both summed operators would leave
an unnecessary L² dependence. The same absolute estimate below controls the
infinite-spatial-volume sum once the comparison construction is justified.

Each changed link alters a normalized SU(2) plaquette trace by at most two.
There are four links, so ||δP||_1≤8. Subtracting a constant expectation does not
change that oscillation. The time index t is an integer. One physical time step
is a_t in a separately declared unit; dimensionless rates are divided by a_t.

## Conditional influence and a local estimate

A link belongs to four plaquettes in this dimension; each has three other
links. Changing a neighboring link changes a shared plaquette's single-link
log-density by a function of oscillation at most 4x. The total-variation tilt
bound tanh(osc(h)/4) gives a single-plaquette influence at most tanh(x).
Consequently an influence majorant C has row sum at most 12 tanh(x).

For transparent exact arithmetic take the looser rational bound

    α = 12x < 1,    0 < x < 1/12,

using tanh(x)≤x. In the discrete link metric, the Dobrushin comparison theorem
then gives the candidate covariance estimate

    |Cov(F,G)| ≤ (1/4) Σ_(e,f) δ_eF [(I-C)^(-1)]_ef δ_fG.

This follows by tilting the state by exp(sG), applying comparison, and taking
s→0. The factor 1/4 comes from the derivative of the total-variation tilt bound.
The row-norm contraction also yields uniqueness and thermodynamic comparison
under the standard compact finite-range specification assumptions.

In the graph joining links that share a plaquette, each step changes an anchor
coordinate by at most one. The four anchors in a spatial plaquette differ from
its basepoint by at most one in either spatial coordinate. Therefore the distance
between the supports of P_z(t) and P_0(0) is at least

    max(t, ||z||_∞ - 1, 0).

Use minimal periodic representatives for z on the spatial torus. Since C has
range one and row norm at most α, its resolvent entries are bounded by
α^distance/(1-α). Thus

    |Cov(P_z(t),P_0(0))|
      ≤ 16 α^max(t,||z||∞-1,0)/(1-α).

These are support-distance estimates, not continuum radial-distance claims.

## Sum the spatial dependence explicitly

There are (2t+3)² integer points with ||z||∞≤t+1, and 8r points on the shell
||z||∞=r for r≥1. The finite torus's minimal representatives form a subset of
these integer points. Hence, independently of L,

    |G_L(t)| ≤ [16/(1-α)] α^t B(t),
    B(t) = (2t+3)²
           + 8α [(t+2)/(1-α) + α/(1-α)²].

The tail comes from

    Σ_(r=t+2)^∞ r α^(r-1)
      = α^(t+1) [(t+2)/(1-α) + α/(1-α)²].

This explicitly retains the polynomial factor produced by summing positions.
It is incorrect to keep the original local prefactor after that sum.

For a pure exponential choose any rational q with α<q<1. Write
B(t)=b_2 t²+b_1 t+b_0, where

    b_2=4,
    b_1=12+8α/(1-α),
    b_0=9+16α/(1-α)+8α²/(1-α)².

Put r=α/q. Since B(t)r^t≤Σ_(n≥0)B(n)r^n, one may take

    |G_L(t)| ≤ K q^t,
    K = 16/(1-α) [b_2 r(1+r)/(1-r)³
                   + b_1 r/(1-r)² + b_0/(1-r)].

This bound is intentionally conservative. At x=1/20 it gives

    α=3/5, q=4/5,
    B(t)=4t²+24t+51,
    |G_L(t)| ≤ 40 (3/5)^t (4t²+24t+51)
             ≤ 33120 (4/5)^t.

The checker reconstructs these constants independently by finite differences of
B, rather than importing the generator's geometric-moment formula.

## What would turn this into a spectral statement

If the physical positive transfer representation is identified, the centered
zero-momentum operator defines a positive spectral measure. A bound Kq^t for all
t then excludes spectral support below -log(q)/a_t in that operator's channel.
For the numerical example the expression is log(5/4)/a_t.

That implication requires checking the operator-to-Hilbert-space map, positivity,
and time normalization. It concerns the spectral weight seen by this operator.
It does not establish that the operator sees every physical sector or that the
bottom of its spectral support is an isolated single-particle pole. The existing
dense-family lemma is relevant to a full-space gap but has additional hypotheses.

This lane has no continuum scaling estimate: its fixed x<1/12 condition does
not cover the weak-bare-coupling trajectory needed as a→0. Nor does a scalar
channel bound alone establish the mass gap in all channels.

## Larger operator basis

The registry also defines 1×2, 2×2, 1×3 and 2×3 rectangles. For each it records
an exact link-oscillation envelope, obtained by averaging the perimeter link
multiplicities over its spatial square-group orbit. This is a zero-momentum A1
projection: canonicalization uses translations, so the anchored local function
need not itself be invariant under rotations about its chosen anchor. Its spatial
sum is invariant. A1 includes continuum spins 0,4,8,...; scalar identification
requires further spectral and rotational evidence.

The spatial-sum derivation above is for the elementary plaquette only. Applying
it to the full rectangular correlation matrix needs the larger support offsets
and cross-operator oscillation factors; the code does not silently reuse this
plaquette prefactor for larger loops.

## Primary sources

- Rebeschini and van Handel, *Comparison Theorems for Gibbs Measures*,
  Corollaries 2.6 and 2.8, https://arxiv.org/abs/1308.4117.
- Athenodorou and Teper, *SU(N) gauge theories in 2+1 dimensions: glueball spectra
  and k-string tensions*, §2.2, https://arxiv.org/abs/1609.03873.
- Blossier et al., *On the generalized eigenvalue method for energies and matrix
  elements in lattice field theory*, https://arxiv.org/abs/0902.1265.

The first source supplies the comparison framework. The explicit plaquette
support constants and spatial-shell calculation are the derivation in this note.
The other sources motivate the observable conventions and advisory spectroscopy.
