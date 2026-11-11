# Finite-volume physical transfer gap: analytic audit IV

**Scope:** 3D SU(2) Wilson pure-gauge theory with spatial torus
`(Z/LZ)^2`, `L >= 3`, infinite integer time, and `0 < beta < 1/12`.
This is a **research-level conditional theorem with explicit hypotheses**;
its supporting executable tests prove only finite geometry and a finite
`Z2` Wilson transfer analogue. It is not a Lean proof, a completed
analytic gate, an infinite-volume Hilbert-space construction or a
continuum mass-gap result. The existing 2D-validation meta-guard remains.

## 1. Exact object and proposed finite-L theorem

Use the unfixed Wilson probability law with normalized Haar on links,
`phi_p(U) = Tr_2(U_p)/2` and density proportional to
`exp(beta * sum_p phi_p(U))`. On a finite spatial torus, let
`X = SU(2)^(2L^2)`, `H = L^2(X, product Haar; C)`.
Let `P` be the Haar-averaging projector for time-slice gauge
transformations and set `Hphys = ran(P)`.

For a spatial plaquette sum `S(U) = sum_spatial_p phi_p(U)`, define
`B(U) = exp(beta * S(U)/2)`, a positive, continuous,
gauge-invariant multiplier. Let

```text
k_beta(g) = exp(beta * Tr_2(g)/2)
(Kf)(U) = integral [prod_spatial_links k_beta(U_e V_e^-1)] f(V) dV
T = B P K B on H; Tphys = B K B on Hphys.
```

**Conditional theorem:** If the Wilson temporal-slab identity and
Dobrushin–Föllmer comparison estimate from Sections 2–3 hold in the
declared infinite-time Gibbs state, then `Tphys` has a simple positive
maximum eigenvalue `lambda_0` with eigenvector `Omega`, and, with
`That=Tphys/lambda_0` and `H_L=-log(That)/a_t`, the spectrum of
`H_L` on `Omega^perp` is bounded below by

```text
m_L >= -log(12*beta)/a_t > 0.
```

The bound's *rate* is independent of spatial `L` within the fixed-beta
window; its derivation does **not** thereby construct the
infinite-volume physical Hilbert space. All claims are subject to the
operator identity and comparison hypotheses being independently
verified.

## 2. Transfer positivity and vacuum

The central convolution kernel `k_beta` has strictly positive
Peter–Weyl coefficients for `beta > 0` (see the SU(2) character-series
calculation in the [scalar spectral lane](../../lanes/scalar_spectral_bridge/README.md)).
Consequently `K` is bounded, compact, self-adjoint, positive and
injective. The strictly positive and bounded multiplier `B` commutes
with gauge projection `P`; centrality of `k_beta` gives `KP=PK`.
Thus `Tphys=BKB` is positive, compact, self-adjoint and injective.

As an *integral kernel*, `B(U) prod_e k_beta(U_e V_e^-1) B(V)`
is continuous and strictly positive on compact `X × X`.
Perron/Jentzsch positivity yields a simple maximal eigenvalue and a
strictly positive continuous eigenfunction. Gauge invariance of the
kernel makes that unique eigenfunction gauge invariant. Normalization
sets `||Omega||=1` and `That Omega=Omega`.

**Independent audit obligation A:** Derive the one-slab Wilson
identity with temporal link Haar integration, including plaquette
orientation and all normalization factors. Then verify in the 3D
model—not by asserting a general theorem for a different lattice—that
its cylinder state has the above `That` correlations. Strong
positivity in this paragraph applies to the *finite spatial* model.

## 3. Common correlation rate for arbitrary time-slice observables

Consider a real-valued, bounded gauge-invariant measurable `F` of the
finite set of spatial links on one time slice, and define its
single-link oscillation `delta_e F`. The sum
`V_F = sum_spatial_e delta_e F` is finite (at most
`2 L^2 osc(F)`).

In the 3D link-interaction graph two distinct links are neighbors only
if they occur in a common plaquette. Each interior link occurs in
four faces and has at most twelve neighboring links. The local SU(2)
conditional comparison used in the scalar lane gives

```text
0 <= C[e,f] <= tanh(beta) * common_plaquette_count(e,f)
row_sum(C), column_sum(C) <= alpha := 12*beta < 1.
```

The symmetric *majorant* is used here, not an assumption that the
exact influence matrix is symmetric. Since one adjacency step changes
a link's time coordinate by at most one, spatial links on times
`0` and `n` are at graph distance at least `n`.
For `D=(I-C)^-1 = sum_{j>=0} C^j` it follows that

```text
D[e,f] <= alpha^n/(1-alpha) for spatial e@0, f@n.
```

Provided the cited covariance comparison applies with the stated
oscillation normalization, the connected cylinder correlator satisfies

```text
0 <= G_F(n) = <(F-<F>)Omega, That^n (F-<F>)Omega>
             = Cov_mu(F@0, F@n)
           <= V_F^2 * alpha^n / (4*(1-alpha)).
```

The first nonnegativity uses `That >= 0`, not a separate FKG
inequality for SU(2). For each *fixed* spatial `L` and `F`, the
prefactor is finite, while the same decay rate `alpha` works for all
such `F`.

**Independent audit obligation B:** Verify the 1/4 covariance
normalization against an explicit Föllmer/Dobrushin theorem, including
the boundary-to-infinite-time limit and the temporal-link variables.
The local graph-incidence assertions are exercised by
[`check_finite_volume_transfer.py`](../../tools/check_finite_volume_transfer.py).
That script checks no SU(2) conditional law or comparison theorem.

## 4. Why the gauge-invariant observable family is dense

The physical Hilbert space is `ran P`, the closed gauge-invariant
part of `L^2(X,dU)`. Since `X` is compact and the gauge group acts
continuously, gauge averaging of continuous functions is continuous,
invariant, and `L^2`-dense in `ran P`. Those functions are bounded.

The Perron eigenfunction `Omega` is strictly positive and
continuous on compact `X`, so there are constants
`0 < c <= Omega <= C < infinity`. Multiplication by
`Omega` and `1/Omega` are bounded and invertible on
`L^2(X)` and preserve the invariant subspace.

Hence vectors `F Omega` with bounded gauge-invariant `F` form a
dense subset of `Hphys`. Centering `F` using
`<F>_Omega = <Omega,F Omega>` makes
`(F-<F>_Omega)Omega` dense in `Omega^perp`.
Real-valued `F` suffice for real/imaginary parts; the complex
linear span is dense.

This is a **finite-L density argument only**. The continuum or
infinite-volume reconstructed physical Hilbert space requires a
separate dense-field identification.

**Independent audit obligation C:** Make sure the gauge projection,
vacuum measure and observable centering all use the *same* Wilson
cylinder state. No arbitrary gauge-fixed Hilbert identification.

## 5. Spectral deduction and exact boundary

For every centered vector from the dense subset, the comparison bound
has the form `<psi,That^n psi> <= C_psi alpha^n`.
For any spectral threshold `s > alpha`,

```text
s^n ||1_[s,1](That) psi||²
 <= <psi, That^n psi> <= C_psi alpha^n.
```

Let `n→infinity`; every projection `1_[s,1](That)` kills
the dense centered subset, hence `Omega^perp). Consequently
`spec(That | Omega^perp) ⊆ [0,alpha]`, proving the claimed
finite-L Hamiltonian lower endpoint. The `beta=0` endpoint is
excluded because `T` need not be injective there.

## 6. What the executable analogue actually checks

[`check_finite_volume_transfer.py`](../../tools/check_finite_volume_transfer.py)
constructs an `L=3`, three-time-step *3D cubic lattice link graph*:
99 link variables, 90 plaquettes, maximum 4 faces per link,
maximum 12 other links adjacent by a face, and minimum
cross-time-slice graph distances exactly 1, 2 and 3.

It additionally enumerates a **different model**, one finite
`Z2` spatial square with four links and four vertex-gauge
variables. On its complete two-dimensional invariant basis
`{1,plaquette_flux}`, it compares the exact temporal-link-slab
Haar sum with `B K B`, verifies strict 2x2 transfer positivity,
and checks its (conservative) spectral bound using exact rationals.

The two executable checks play distinct roles: cubic geometry
can detect incidence/distance mistakes in the 3D proof plan,
while the finite-group analogue can detect transfer-factorization
and normalization errors. Neither transfers coefficient bounds,
spectral estimates or gauge-group arguments from `Z2` to SU(2).

## 7. Stop conditions and next genuine mathematical step

The proposed fixed-L theorem becomes eligible for external
mathematical review only after independently confirming A–C.
Its source references are [Lüscher (1977)](https://doi.org/10.1007/BF01614090),
[Rebeschini–van Handel (2014)](https://arxiv.org/abs/1308.4117),
and the [existing scalar spectral derivation](../../lanes/scalar_spectral_bridge/README.md).

**Do not promote** this finite-spacing result to a 3D
continuum mass gap. Along `beta(a)=4/(g3² a)`, the sufficient
hypothesis `12 beta<1` fails as `a→0`.
A new weak-bare-coupling or scale-indexed estimate is essential.
The [prior bridge](SPECTRAL_GAP_BRIDGE_3.md) records six still-open
continuum obligations; this tranche closes none of them.
