# An explicit local SU(2) elimination step

This module computes the first nontrivial effective interactions from **actually
integrating a link**, with a written uniform remainder bound. It is a local
research calculation, not a complete renormalization-group (RG) transformation,
a contraction estimate or a CLOSED analytic program result. Existing 2D
validation prerequisites remain unchanged. No analytic waiver is introduced.

## The exact local map in three dimensions

Take an ordinary positive link U from x to x+e_mu on a Wilson lattice, with
normalized weight exp[beta sum_p Tr(U_p)/2]. A link in three dimensions belongs
to four plaquettes. Keeping all exterior links fixed, cyclicity and reality of
the SU(2) trace write their contribution as

    exp[beta sum_(i=1)^m tr(U S_i)],     m=4, tr=Tr/2.

The four staples S_i are SU(2) products of three exterior links. For each nu!=mu:

    S_(nu,+) = U_nu(x+e_mu) U_mu(x+e_nu)^dagger U_nu(x)^dagger,
    S_(nu,-) = U_nu(x-e_nu+e_mu)^dagger U_mu(x-e_nu)^dagger U_nu(x-e_nu).

For the backward plaquette, conjugate its holonomy before cycling its trace to
place U first. This is valid because SU(2) normalized traces are real. No staple
independence is assumed: staples can share exterior links. Extents at least three
avoid short periodic identifications of the eliminated link with itself.

Represent SU(2) as unit quaternions. Haar measure is uniform on the unit sphere
in four real dimensions. The exponent is a real linear functional of that unit
quaternion. Its length is beta*sqrt(q), where

    q = |sum_i S_i|^2 = m + 2 sum_(i<j) c_ij,
    c_ij = tr(S_i S_j^dagger),     0<=q<=m^2.

Thus eliminating U with normalized Haar measure is exactly

    W_beta(S_1,...,S_m) = Z(beta sqrt(q)),
    Z(s) = integral_SU(2) exp[s tr(U)] dU
         = sum_(k>=0) (s^2/4)^k/[k!(k+1)!].

Exterior plaquettes not containing U retain their original Wilson weight. This
is an exact marginalization identity on the original 3D lattice, not a guessed
running coupling. The same formula for m=2 supplies a two-plaquette control in
2D; it is not substituted for the actual four-staple 3D star.

Each c_ij is the normalized trace of a closed exterior six-link word, possibly
with repeated/cancelling links depending on geometry. The staples transform at
the link's endpoints in the same way, so these pair traces are gauge invariant.
The c_ij are constrained by the staple geometry: no claim is made that all
points of the independent cube [-1,1]^6 can occur. The norm bound uses the true
quaternion range of q.

## Explicit effective interactions through fourth order

Put u=beta^2 q/4. The Haar moments E[t^2]=1/4 and E[t^4]=1/8 give

    Z = 1 + u/2 + u^2/12 + ...,
    log W = beta^2 q/8 - beta^4 q^2/384 + R.

To specify the constant convention, subtract log Z(beta sqrt(m)), a
field-independent reference. Let C=sum_(i<j)c_ij. Then

    log W_normalized = (beta^2/4 - m beta^4/96) C
                       - (beta^4/96) C^2 + R_normalized.

The effective action contribution is the **negative** of this log weight.
For the real 3D star (m=4) there are six pair traces, each with coefficient
beta^2/4-beta^4/24. The fourth-order square produces six diagonal and fifteen
cross-pair monomials: diagonal coefficient -beta^4/96, cross coefficient
-beta^4/48 in the log weight. These interactions cannot all be represented by
changing a single Wilson coupling. The export retains all 33 monomials for m=4,
and three for the m=2 control, instead of discarding the generated interactions.

## A uniform, explicitly typed remainder bound

For 0<=u<=B define delta=Z-1-u/2-u^2/12. The first omitted positive term is
u^3/144. Subsequent ratios are at most B/20, so

    0 <= delta <= d u^3,       d = 1/[144(1-B/20)].

Let y=Z-1, e=1/12+d B, c=1/2+B/12+d B^2. Then y<=c u and
r=y-u/2<=e u^2. The identity

    log(1+y) = y-y^2/2 + integral_0^y t^2/(1+t) dt

holds for all y>=0, with the integral between zero and y^3/3. Consequently

    |log Z - (u/2-u^2/24)| <= C_bound u^3,
    C_bound = d + e/2 + e^2 B/2 + c^3/3.

This follows by bounding delta, (y^2-u^2/4)/2 and the integral separately.
For fixed m and beta<=b, take B=m^2 b^2/4. In the supremum norm over all exterior
SU(2) fields, for the dimensionless log weight,

    ||R||_infinity <= C_bound (m^2/4)^3 beta^6,
    ||R_normalized||_infinity <= 2 C_bound (m^2/4)^3 beta^6.

The factor two accounts for subtracting the reference log weight. This is a
specific norm: it is not silently added to a polymer activity, coupling-flow or
transfer-operator error with different units.

The exported windows are b=1/4 for m=2 and b=1/8 for m=4. Both give B=1/16 and
C_bound approximately 0.09205917. At each window endpoint the normalized
remainder is bounded above by approximately 0.000044951, below 1/10000.
The calculations and comparisons in the standalone audit use exact fractions.
These are bounds, not measured errors; the numerical quadrature tests are only
an additional implementation check.

## Run and review

```sh
python lanes/su2_link_decimation/tools/build.py
python lanes/su2_link_decimation/tools/check_local_step.py
# Numerical regression tests additionally use the spectrum lane's NumPy/SciPy dependencies:
python -m unittest discover -s lanes/su2_link_decimation/tests -v
```

The generator exports interaction coefficients and remainder constants. The
independent checker imports no generator package: it expands the Haar moments
and formal logarithm as multivariate polynomials, then obtains the remainder
majorant from a separate polynomial expansion of positive bounds. Five tests
cover all 36 monomials, the 3D six-loop geometry count, reference normalization,
seven deliberate corruptions, and comparison with independent Gauss-Jacobi Haar
quadrature at multiple field norms and couplings.

The report explicitly has `analytic_gate_closed: false` and
`rg_contraction_established: false`. The Haar reduction and remainder argument
are written analytic derivations for review; the exact checker certifies their
exported algebra and constants, not the full source theorem application.

## What remains for an actual RG rung

A single-link marginalization removes a degree of freedom but does not produce
a uniform coarse lattice spacing, establish reflection-compatible repeated
blocking, or imply contraction. To proceed, specify a collection of eliminations
and retained coarse variables; account for overlapping stars and the interactions
they generate; transfer the log-weight remainder into a declared activity norm;
and prove a scale-uniform contraction or controlled descent. An O(beta^6) local
bound at strong coupling does not solve the weak-coupling/continuum problem.

The SU(2) Haar series is derived in the repository's
[2D reference note](../ym2d_sun_exact_validation/DERIVATION.md). The local
four-staple integration, retained interactions and explicit majorant are worked
out above. For the Wilson lattice/action and local SU(2) integration context,
see Creutz, *Monte Carlo study of quantized SU(2) gauge theory*,
https://doi.org/10.1103/PhysRevD.21.2308. No published RG contraction theorem is
claimed as established by this local calculation.
