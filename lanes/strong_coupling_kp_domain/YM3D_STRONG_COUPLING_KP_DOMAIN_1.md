# YM3D_STRONG_COUPLING_KP_DOMAIN_1 — the strong-coupling gas in three dimensions

27 October 2026 · 3D SU(2) lattice gauge theory · input to the fallback-basin row (design §10)

## Short version

- In 3D every link lies in four plaquettes (in 4D, six). The tools built for the
  4D fragment repair carry over unchanged with that one number swapped, and
  every constant improves.
- **Proved here, with interval arithmetic:** the strong-coupling polymer gas of
  the 3D SU(2) Wilson action satisfies the Kotecký–Preiss condition for
  **β ≤ 0.185** (heat-kernel action: τ ≥ 8.19). The gas of closed two-face
  surfaces alone satisfies it up to **β ≤ 1** (τ ≥ 3.8).
- β is the YM3D design's coupling: the weight is exp(β/2 · Re Tr U_p).
- The gap between 0.185 and 1 is the same obstruction as in 4D. Branched
  supports (links with three or four faces) are counted at 7.16 per face
  instead of 3, and spin-1 faces on them are bounded only through Finner's
  inequality, which loses about a factor 2 per face. The exact data say they are
  tiny: at β = 0.5 they are 0.02% of the exact two-face sum, at β = 1 about 1%.
- This is not a mass gap and not yet the fallback-basin certification. It
  supplies the row's convergence domain for single-plaquette actions; the
  overlap with an RG-produced effective action is the missing piece.

## 1. The objects

The setup is the one in TWO_FACE_EXACT_SURFACES_1 and BRANCHED_SUPPORTS_EXACT_1,
with Z^3 in place of Z^4. Write the plaquette weight as 1 + f with
f = Σ_{a≥1} r_a χ_a. For the Wilson action r_a = (a+1) I_{a+1}(β)/I_1(β), and
for the heat kernel r_a = (a+1) e^{−τ a(a+2)/8}. Put t_a = r_a/(a+1).

- **Polymers:** link-connected plaquette sets X in which every link lies in 0 or
  at least 2 plaquettes of X. These are the surviving supports; a link in exactly
  one active face integrates to zero.
- **Activity:** w(X) = ∫ Π_{p∈X} f(U_p) dU, which sums over all labellings.
- **Compatibility:** two polymers are incompatible when they share a link.

A link of Z^3 lies in 4 plaquettes and a polymer through it contains at least 2
of them, so the KP condition is 4R(c) ≤ c, where R(c) = Σ_{X∋root} |w(X)| e^{cF(X)}.

## 2. Exact data (checked independently)

**Closed two-face surfaces through a plaquette, F ≤ 22:**

| F | 6 | 10 | 14 | 16 | 18 | 20 | 22 |
|---|---:|---:|---:|---:|---:|---:|---:|
| N(F) | 2 | 10 | 70 | 16 | 498 | 320 | 3,520 |

- All are spheres; no tori, nonorientable or pinched surfaces occur yet.
- Every weight is |W| = 2^{χ−F} = 2^{2−F}.
- The growth is about 1.6 per face, against the proved cap of 3.
- Checker: PASS.

**All surviving supports through a plaquette, F ≤ 18:**

| F | 6 | 10 | 11 | 12 | 14 | 15 | 16 | 17 | 18 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 2 | 10 | 11 | 24 | 70 | 150 | 352 | 272 | 906 |
| branched | 0 | 0 | 11 | 24 | 0 | 150 | 336 | 272 | 408 |

The smallest branched shapes are:
- **F = 11:** two cubes sharing a face.
- **F = 12:** two cubes touching along a link.

All weights with spin ½ and spin 1 were computed exactly, up to eight spin-1
faces per support. Every one is positive.

The single-link factorisation lemma (Lemma G) shows up throughout. The all-spin-½
weights of the branched supports are exactly products of cube and box weights:
1/256 = (1/16)² at F = 12, and 1/4096 = (1/16)³ or (1/16)(1/256) at F = 16, 18.

Checker: PASS.
- It re-enumerates with the opposite rule and gets the identical set: 1,797
  supports, 1,201 of them branched.
- It recomputes 3,433 labellings exactly with the Weingarten formula (every
  labelling with at most six spin-1 faces).
- It confirms Theorem C, and Lemma G on 784 single-link splits.
- The 3,979 labellings with more than six spin-1 faces are not recomputed.
  Their weights carry r₂⁷ or smaller and are covered by Finner anyway.

## 3. Proved statements

**Counting (potential method, interval-certified).** Through a plaquette of Z^3,
the number of supports grows at most like:

| class | per-face rate in 3D | in 4D |
|---|---:|---:|
| closed two-face surfaces (Lemma A, rate 2d − 3) | 3 | 5 |
| every link valence even | 3.47 | 6.83 |
| even, weighted by Π Cat(k_e/2) | 4.62 | 10.35 |
| all surviving supports | 7.16 | 14.94 |

**Haar bounds** (unchanged from the 4D notes):
- Two-face surfaces: |W| = d_a^{χ−F} for every spin.
- All-spin-½ supports (Theorem C): |W| ≤ 2^{−F} Π_e Cat(k_e/2) 4^{⌊F/6⌋}.
- Any support (Finner's inequality): |w(X)| ≤ Π_p ‖f‖_{q_p}, with q_p = 4 when p
  touches a link of valence 3 or 4, else 2.

**Kotecký–Preiss.** R(c) is bounded by three pieces:
- the exact two-face sum to F = 22 for every spin, with the rate-3 bound beyond;
- the branched list to F = 18, each support bounded by Finner;
- the all-support counting with ‖f‖₄ on every face for F > 18.

Results:

| statement | Wilson β | heat kernel τ |
|---|---|---|
| whole gas: KP (certified at 37/200 and 819/100, extends by monotonicity) | **β ≤ 0.185** | **τ ≥ 8.19** |
| all-spin-½ branched sector: root sum finite (Theorem C + counting) | β < 0.70 | τ > 4.70 |
| two-face gas alone: KP (certified at 1 and 19/5) | **β ≤ 1** | **τ ≥ 3.8** |

**Monotonicity.** Every term of the bound used at the endpoints increases with
the character ratios. Those increase with β and decrease with τ, so each
endpoint statement covers all smaller β and all larger τ.

**For comparison.** The Shen–Zhu–Zhu condition, |β_SZZ| < 1/(16(d−1)), converts
to β < 1/8 in these units for d = 3, by the same conversion used for 4D (which
gave 1/12). SZZ prove more there, though: a mass gap.

## 4. What this gives the fallback-basin row

Design §10 lists the fields a fallback certification must carry. Status of each:

| field | status |
|---|---|
| `fallback_method` | polymer (character/defect) expansion: done |
| `convergence_criterion` | Kotecký–Preiss with explicit c: done |
| `volume_uniformity_row` | KP for a translation-invariant gas is volume-uniform: done for the gas; observables not treated |
| `input_activity_vector` | the domain is stated through the character ratios r_a of a single-plaquette weight; no RG ladder exists to supply one |
| `overlap_or_majorization_check` | missing: an RG step produces larger-loop terms, not a single-plaquette weight |
| `mass_scale_bound` | missing: needs observable insertions (the cluster expansion of a connected correlation), not done |

So this is a precursor to the certification: the domain D_fallback for
single-plaquette actions, with certified constants.

**Physical scale.** At weak coupling the 3D lattice coupling runs like
β ≈ 4/(g₃² a) (Wilson normalisation; the design's §1.1 states only β ≍ 1/(g₃² a),
so treat the factor as approximate). β ≤ 0.185 then means a coarse spacing of
roughly a ≳ 22/g₃². Reaching that from the UV is exactly what the one-step-rung
gates are meant to supply, but only if the effective action stays close to a
single-plaquette form.

## 5. Proposed registration

As a gate this would be `schema_stage: analytic` and held by the
2D-validation meta-guard. Two options:

1. **Register it as a research lane now** (like the glueball lane), with
   `claim_strength: fallback_domain_only` and no dependents. Nothing it states
   would be claimed in the manuscript until a program gate closes.
2. **Remove the dependency of `YM2D_SUN_EXACT_VALIDATION_LANE_0` on the Milestone
   1A orbit audit.** I see no mathematical reason for it, and the 2D lane already
   has an independent audit. Then close the 2D lane, then add this as an analytic
   gate.

Draft stanza for option 1:

```yaml
  - id: YM3D_STRONG_COUPLING_KP_DOMAIN_1
    title: Strong-coupling KP domain for single-plaquette actions (3D SU(2))
    milestone: fallback_domain
    schema_stage: analytic
    workdir: lanes/strong_coupling_kp_domain
    checker_cmd: "python tools/decide.py"
    decision_glob: "artifacts/decision.json"
    decision_status_key: status
    independence: strict
    meta_requires: [ym2d_validation_passed]
    depends_on: []
    timeout_s: 3600
    claims_unlocked: ["KP for the 3D SU(2) Wilson polymer gas for beta <= 37/200"]
    claim_strength: fallback_domain_only
```

`decide.py` reads the two checker reports and re-runs only the
interval-arithmetic decision. A control with one checker report set to FAIL makes
it write `status: FAIL` and exit 1 (`artifacts/neg_decision_checker_fail.json`). The generator and checkers are separate scripts,
as the harness requires; the two checkers import nothing from the generator.

## 6. What would move the number

1. **Branched counting near the two-face rate.** Lemma G strips single-link
   contacts exactly (they are products), so what remains is counting the
   irreducible blocks. In 3D that is far more tractable than in 4D: the
   enumeration already reaches F = 18 in minutes.
2. **A Haar bound for spin-1 faces on branched supports that keeps 1/d per
   face.** If it matched Theorem C, the whole-gas threshold would move toward
   the all-spin-½ value, β ≈ 0.7.
3. **Observable insertions**, to turn KP into exponential clustering with an
   explicit mass, which fills `mass_scale_bound`.

## 7. Non-claims

- No mass gap, no clustering of observables, no transfer-matrix statement.
- Not the fallback-basin certification: single-plaquette class-function actions
  only, with no overlap with an RG-produced effective action.
- Nothing continuum or lattice-spacing-uniform.
- Branched supports carrying spin-1 faces are controlled only through Finner's
  inequality.
