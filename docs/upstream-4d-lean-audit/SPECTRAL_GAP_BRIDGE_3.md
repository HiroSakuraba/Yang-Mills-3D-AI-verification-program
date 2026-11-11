# Spectral bridge III — what would convert clustering into a 3D mass gap?

**Status (11 November 2026): conditional spectral lemma and research obligations, NOT a
proved continuum mass gap, and NOT a closed `program.yaml` gate.** This note
extends the [upstream 4D audit](README.md) and the existing
[3D scalar transfer-space analysis](../../lanes/scalar_spectral_bridge/README.md).
The upstream [October 28 construction](https://github.com/yang-mills-group/OpenAI-YM-20261028/tree/3456e5e75cf8d4cd558955a5c7638fba2d68f464)
explicitly excludes a positive mass-gap conclusion.

## 1. A precise conditional theorem

Let `T` be a positive self-adjoint contraction on a physical Hilbert space,
with a one-dimensional vacuum eigenspace `C Ω = ker(I-T)`. Let
`D` be a **dense linear subset of the vacuum-orthogonal subspace**.
Suppose a single `0 < ρ < 1` works for every `ψ in D`, in the sense that
there exist finite `C_ψ` and nonnegative integer `k_ψ` such that

```text
0 <= <ψ, T^n ψ> <= C_ψ (n+1)^k_ψ ρ^n    for every integer n >= 0.
```

Then the spectrum of `T` restricted to the vacuum-orthogonal space is
contained in `[0,ρ]`. With physical time step `a_t > 0`, the spectral
Hamiltonian `H = -log T/a_t` has a gap of at least `-log(ρ)/a_t`
on that subspace (on `ker T`, the logarithm can be interpreted as infinite
energy; the 3D transfer candidate is asserted to be injective).

**Proof.** By the positive spectral measure `μ_ψ`, for any `s > ρ`,
`s^n μ_ψ([s,1]) <= <ψ,T^n ψ> <= C_ψ(n+1)^k_ψ ρ^n`.
Divide by `s^n` and let `n → infinity`: every such spectral projection
annihilates `ψ`. Density of `D` and boundedness of spectral projections
make it vanish on the entire vacuum-orthogonal space. Taking the union over
rational `s > ρ` proves the claim. **The polynomial prefactor does not
weaken the spectral threshold.**

The analogous continuum statement uses `e^{-tH}` and
`C_ψ(1+t)^{k_ψ}e^{-mt}` for all `t >= 0`. Its conclusion is a gap
of at least `m`, provided the tested centered vectors are dense in the
physical vacuum-orthogonal space.

**Essential distinctions:** A nonzero correlator, short-distance OPE,
positive-energy spectrum, isolated lattice probe, decay for one observable
channel, or a sequence of finite-spacing gaps does **not** imply this theorem's
hypotheses for a continuum physical Hilbert space. A centered operator's
vacuum component must be removed before estimating moments.

## 2. Candidate finite-volume strengthening of the existing 3D lane

The [scalar spectral bridge](../../lanes/scalar_spectral_bridge/README.md)
analyzes the unfixed 3D SU(2) Wilson measure and a positive transfer candidate
`T_L = B P K B` on finite spatial `L × L` tori, then identifies
`T_L = B K B` on the gauge-invariant physical subspace. It records a
Dobrushin influence bound `α <= 12 tanh(β) <= 12β < 1`.

For a **bounded, real, gauge-invariant function `F` of a single spatial
time slice**, assume the cited Dobrushin comparison inequality applies to
two time-translated copies of `F` in the infinite-temporal-cylinder Wilson
measure, with link metric satisfying `d(e_0,f_n) >= n`.
Writing `δ_e F` for the single-link oscillation of `F`, the comparison
bound suggests the extension

```text
|Cov(F(0), F(n))| <= [α^n / (4(1-α))] (Σ_e δ_e F)^2.
```

The sum is finite for each fixed spatial `L` and each bounded slice
observable. Its prefactor can depend on `F` and `L`, but its **rate**
`α` is common. If reflection-positive transfer identification, positivity
of `T_L`, the above cylinder estimate, and density of the centered
multiplication vectors `(F - <F>) Ω_L` all hold, Section 1 then yields a
**full physical transfer-space gap at fixed spatial volume**, not merely a
scalar-channel threshold:

```text
gap(H_L) >= -log(α) / a_t  >= -log(12β) / a_t    (0 < β < 1/12).
```

This is a **proposed analytic strengthening for independent review**, not a
result certified by the existing constants checkers. In particular, the link
metric, the temporal-gauge slab identity, the gauge-invariant multiplication
algebra's density, and any `L`-uniform reconstruction need separately
audited hypotheses. Finite-volume full-space control does not by itself
identify the limiting infinite-volume Hilbert space.

At the sample `β=1/20`, the conservative bound gives `α <= 3/5`
and threshold `log(5/3)/a_t`. This is a lattice strong-coupling threshold.

## 3. The quantitative obstacle: the wrong coupling regime

Our convention for 3D SU(2) Wilson action is

```text
β(a) = 4 / (g3_squared * a),       g3_squared > 0 fixed.
α_bound(a) = 12 β(a) = 48 / (g3_squared * a).
```

For `α_bound < 1`, one needs `a > 48/g3_squared`. The continuum
trajectory instead requires `a → 0`, hence `β(a) → infinity`.
The existing Dobrushin sufficient condition **fails before** reaching it.
The original 4D construction's logarithmic running condition is not a
substitute for the 3D inverse-spacing law.

Even a sequence `ρ(a) < 1` at every spacing is insufficient: if
`ρ(a) = 1-a²` (for `0<a<1`), then

```text
0 < -log(ρ(a))/a <= a/(1-a²) → 0.
```

The physical energy gap can collapse. Conversely, a rate of the form
`ρ(a) <= exp(-m*a)` for one **a-independent `m>0`** would be the
correct rate scale, but is not established here.

There is another nonuniformity: a prefactor `(n+1)^k` in **lattice
time** is not a uniform prefactor in physical time `t = n*a`;
it can diverge like `a^{-k}` at fixed `t`. Renormalized, smeared
operators can also occupy increasing numbers of lattice links as `a`
shrinks, making their oscillation sums grow.

## 4. Concrete bridge obligations in dependency order

1. **Observable and law identification.** Fix a common family of
   gauge-invariant, vacuum-centered, renormalized/smeared observables
   `F_{a,L}(f)`, on the *actual* 3D Wilson law at
   `β(a)=4/(g3_squared*a)`; connect them to continuum Wightman/OS
   test functions. No free-field or hand-selected polymer surrogate.
2. **Reflection positivity and transfer.** Establish a positive physical
   transfer semigroup and compatible vacuum identification at all
   `a,L` in the requested extraction order. Audit any gauge-fixing
   steps; do not import the upstream selected-scalar OS test as
   all-field gauge positivity.
3. **Uniform physical-distance bound.** Obtain, for each test observable,
   `|G_{a,L}(n)| <= C_f (1+n*a)^k exp(-m*n*a)` with one
   `m>0` independent of `a,L`, and controlled `C_f,k`.
   Bounds only at fixed `β<1/12` or fixed lattice separation do not qualify.
4. **Compatible limit.** Show that these centered correlators converge in
   the declared infinite-volume and UV extraction procedure, with
   uniform domination needed to retain the bound.
5. **Dense physical observable family.** Prove the tested centered
   vectors are dense in the limiting vacuum-orthogonal physical Hilbert
   space (or explicitly limit the conclusion to a named channel).
6. **Spectral support and units.** Apply the theorem in Section 1 to the
   limiting positive semigroup and record the lower endpoint `m`
   in physical mass units. A single positive lattice probe does not suffice.

## 5. Implementation proposal and stop rules

**Near-term mathematical target (fixed coupling):** independently audit the
Section 2 all-slice extension and its common-rate estimate; test it in the
[exact 2D SU(N) benchmark lane](../../lanes/ym2d_sun_exact_validation/README.md)
before promoting it into 3D gates. Keep this as a fixed-spacing result.

**Continuum target (hard):** source a genuinely weak-bare-coupling,
scale-indexed activity or RG contraction estimate that survives
`β(a) → infinity` and supplies a common **physical** decay rate. The
[finite gas perturbation lemma](FINITE_GAS_TRANSFER.md) is algebraically
correct only under fixed admissibility; it supplies no Wilson-activity
coefficient or volume/spacing-uniform majorant.

**Fail-stop:** Reject any claim that a fixed-`β` Dobrushin/KP estimate,
short-distance OPE, selected scalar channel, or a 4D theorem with logarithmic
coupling closes a 3D continuum gap. Keep the existing 2D-validation
meta-guard and all original `program.yaml` states.

## 6. Checkable scope

The adjacent [obligation ledger](mass_gap_obligations.json) records exact
rational examples of the coupling mismatch and the still-open proof
requirements. The independent
[`check_mass_gap_obligations.py`](../../tools/check_mass_gap_obligations.py)
recomputes these arithmetic examples and rejects false success flags;
[`test_mass_gap_obligations.py`](../../tests/test_mass_gap_obligations.py)
includes negative controls. These tools do **not** verify the spectral
theorem, the cited Dobrushin theorem or the physics of the proposed transfer.

**Primary references:** [original 4D Lean release](https://github.com/yang-mills-group/OpenAI-YM-20261028),
[Lüscher transfer matrix (1977)](https://doi.org/10.1007/BF01614090),
[Rebeschini–van Handel comparison theorem](https://arxiv.org/abs/1308.4117),
and the two 3D repository lanes linked above.
