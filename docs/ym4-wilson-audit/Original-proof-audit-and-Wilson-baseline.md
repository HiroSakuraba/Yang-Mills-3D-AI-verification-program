# Original-note audit and an independent Wilson baseline

16 October 2026 · follow-up to the YM4 coefficient audit

The earlier activity calculation remains correct for its explicitly defined sums. The question here is whether recovered project files justify applying those sums to the physical lattice model. They do not yet supply that identification. An early proof note also contains a definite incorrect parity lemma. This report supplies an exact counterexample and a separate conservative uniqueness-and-correlation theorem for the actual Wilson measure.

## 1. What was recovered, and what was not

The recovered files include:

- `FALLBACK_LOWER_ORDER_ACTIVITY_1_proof_v1.md` and its script;
- the `ym_mass_gap_v1_16_bundle.zip` archive, including the v1.15a and v1.15b normalization audits;
- the v7 continuum-bridge design bundle;
- the v57 strip-ladder bundle;
- the v156 activity-generator completeness audit.

The exact named `STRONG_COUPLING_FRAGMENT_PAPER_1`, `CUTOFF_REMOVAL_FALLBACK_1`, `FULL_FALLBACK_ASSEMBLY_2` and `OS_TRANSFER_GAP_BRIDGE_1` bundles were not located by the searches used here. Finding related project history does not establish that those later fragments repeat an early error. The audit below applies to the actual recovered statements, not to unseen later proofs.

The v1.15a audit already distinguishes the scalar spin-network envelope from the full Wilson transfer matrix. The v1.15b update claims a conditional domination result; comparing scanned projector ranks to a large envelope, by itself, does not prove the global tensor-network domination with all index contractions and normalizations. The v1.16 continuation remains explicitly a skeleton.

The v156 report independently identifies activity completeness as open: its higher connected cumulants, localization and small/large-field compiler are not all controlled. Its report of an exhaustive third-order check was read, but that 56-million-triple run was not independently rerun here. The v57 ladder applies to its restricted strip-generated envelope, not to arbitrary four-dimensional blocking.

## 2. A cube refutes the early vertex-parity lemma

The early proof note's Lemma 2.3 asserts that every surviving two-face surface has an even number of incident active edges at each interior surface vertex. Its proof replaces the actual local contraction by an invariant space with one fundamental representation per incident active edge.

Take the six faces of a single elementary three-dimensional cube embedded in the four-dimensional lattice. Each active edge belongs to two active faces. There is no surface boundary, and every one of its eight vertices has three incident active edges.

Orient the six faces outward. In the ordinary-character convention, expand each fundamental trace into matrix indices. Each of the twelve link integrations uses

    ∫ U_ij conjugate(U_kl) dU = δ_ik δ_jl / 2.

After those identifications there are eight free index loops. Thus

    ∫ ∏_(six faces) χ_(1/2)(U_face) ∏_(twelve edges) dU_e
      = 2^8 / 2^12 = 1/16 ≠ 0.

`independent_wilson_check.py` constructs the oriented faces, checks opposite traversal of every edge, performs the index identifications, and counts the eight remaining loops. It uses exact integer combinatorics and rational arithmetic. This directly refutes the stated vertex-parity claim.

The correct elementary vanishing statement is at a LINK: an odd number of fundamental representation factors on one integrated link has zero Haar integral. An even face incidence at links does not force an even count of distinct active edges at vertices. Closure modulo two follows from even face incidence at links; no vertex-degree rule is needed. This refutation does not invalidate the dangling-edge vanishing lemma, the Bessel ratio bound, or every coarse entropy upper bound; those must be assessed separately.

## 3. The character normalization must also be repaired

Let χ_a denote the ordinary irreducible character with χ_a(1)=a+1. For normalized Wilson trace tr=Tr/2,

    exp[x tr U] = Σ_a c_a(x) χ_a(U),
    c_a(x) = 2(a+1) I_(a+1)(x)/x.

Define t_a=I_(a+1)/I_1. After vacuum normalization, the ordinary-character coefficient is (a+1)t_a, not t_a.

The early note prints coefficients 2 I_(a+1)/x multiplying its characters and uses a per-face weight t_a. If its characters are ordinary characters, it is missing the dimension factor. For the fundamental cube, this changes the coefficient product by 2^6=64. The correct ordinary-character cube activity is

    (2t_1)^6 · (1/16) = 4 t_1^6.

The early formula with ordinary characters gives t_1^6/16 instead.

An unstated dimension-weighted character convention does not rescue all the formulas: if the character is 2χ_(1/2), the same cube Haar integral is 64/16=4, contradicting the note's separate bound |I_Haar|≤1. The weight and Haar normalization must be fixed together.

For a connected orientable closed two-dimensional manifold surface tiled by faces, with every integrated edge incident to exactly two faces and with the same representation a on every face, index contraction gives d_a^(χ(S)-F) for ordinary characters. Its correctly normalized Wilson activity is d_a^χ(S)t_a^F. For the fundamental representation this is at most 4t_1^F, so a repaired estimate on this family needs a prefactor four rather than the early note’s per-polymer t_1^F bound. A geometric-series convergence ratio may survive that repair; the printed activity normalization does not. This supplies a repair on that explicitly restricted surface family. Singular supports, branching links, insertions and the full polymer incompatibility problem still need their own treatment.

## 4. A projector norm does not bound an arbitrary closed contraction by one

An invariant-space projector has operator norm at most one, but a closed index contraction can take its trace. The invariant subspace of four fundamental SU(2) representations has dimension two, so its orthogonal projector has operator norm one and trace two. Equivalently ∫χ_(1/2)(U)^4 dU=2: use χ_(1/2)^2=χ_0+χ_1 and character orthogonality.

This example does not assert that a specific ordinary-character plaquette surface violates the early bound. It shows why multiplying local projector norms is an incomplete proof unless all contractions, index dimensions and boundary norms have been specified. The cube calculation makes the normalization issue concrete.

## 5. Independent theorem for the actual Wilson measure

This is a conservative application of the established Dobrushin comparison theorem, not a new strong-coupling discovery. It avoids the disputed surface grammar entirely.

Consider SU(2) link variables on the hypercubic lattice in d dimensions, with finite-volume measure

    μ_Λ(dU) ∝ exp[x Σ_p tr U_p] ∏_e dU_e,
    tr=Tr/2,  x>0.

Use ordinary boxes with fixed boundary links, or standard periodic boxes with side lengths at least three. Let two links be adjacent in the influence graph when they belong to a common plaquette. Define δ_eF as the supremum change in a bounded real observable F when only link e is changed.

**Theorem.** If

    α = 6(d-1)tanh x < 1,

the infinite-volume Gibbs measure is unique. Finite-volume expectations of local observables converge independently of the fixed boundary conditions. For bounded real local F and G, in finite or infinite volume,

    |Cov(F,G)| <= [1/4] Σ_(e,f) δ_eF D_ef δ_fG,
    D = Σ_(n>=0) Cbar^n,
    Cbar_ef = m_ef tanh x,

where m_ef is the number of plaquettes containing both distinct links. For supports separated by influence-graph distance r,

    |Cov(F,G)| <= ||δF||_1 ||δG||_1 α^r / [4(1-α)].

In four dimensions, the explicit domain is

    0 < x < atanh(1/18) = (1/2)log(19/17),
    0.0556128 < atanh(1/18) < 0.0556129.

### Proof of the influence estimate

One link is contained in 2(d-1) plaquettes, each involving three other links. Thus

    Σ_(f≠e) m_ef = 6(d-1).

This is independently reconstructed by the geometry checker; in d=4 there are six plaquettes and eighteen other-link incidences.

Changing one neighboring link alters one plaquette term from x tr(U_e A) to x tr(U_e A'). Both normalized traces lie in [-1,1]. The log-density change as a function of U_e consequently has oscillation at most 4x per shared plaquette.

For any probability measure, tilting by exp(h) changes it in total variation by at most tanh(osc(h)/4). This follows by optimizing the normalized likelihood ratio over an interval whose endpoint ratio is exp(osc(h)): the maximal variation is (sqrt(R)-1)/(sqrt(R)+1). Therefore the one-plaquette influence is at most tanh x. Changing several terms and applying the triangle inequality gives C_ef≤m_ef tanh x. The row sum is at most α.

Compactness and continuity of the local specification give existence of a Gibbs measure. The Dobrushin comparison theorem with the discrete metric, whose Wasserstein distance is total variation, applies because the influence row norm is strictly below one. It gives uniqueness and boundary comparison.

### Proof of the covariance estimate

In finite volume, tilt μ by exp(tG). At site f its conditional distribution changes in total variation by at most tanh(|t|δ_fG/4). Apply the comparison theorem with the untilted μ as the reference specification, divide the resulting expectation bound by |t|, and let t tend to zero. Differentiating μ_t(F) gives Cov(F,G), and tanh(|t|δ_fG/4)/|t| tends to δ_fG/4. This proves the matrix bound above.

The matrix Cbar has range one and row norm at most α. If graph distance(e,f)≥r, (Cbar^n)_ef vanishes for n<r, while its entries are at most α^n. Summation gives D_ef≤α^r/(1-α). Summing the oscillations proves the displayed decay estimate. Infinite-volume covariance follows by convergence of local expectations.

Boundary comparisons have the same path interpretation: changes farther than r influence-graph steps from an observable contribute at most a constant times α^r/(1-α). This gives a direct quantitative thermodynamic Cauchy estimate.

### Numerical example and scope

At x=0.05 the certificate gives

    0.89925074924183949 < α < 0.89925074924183951.

The graph-distance decay rate is -log α, enclosed in `independent-results.json`. This is a rate for the specified link-influence graph. Converting it to a physical transfer-Hamiltonian gap requires the transfer-space and time-step identifications stated in the earlier note. This report does not claim those identifications have been fully checked.

The bound reaches a smaller domain than the Shen–Zhu–Zhu result cited in the map. It is useful here as an independent normalization check and a complete, conservative uniqueness/clustering route. Its threshold is not a revision of the 0.6273001 coefficient certificate: they are bounds for different objects.

## 6. What now has to happen before promoting the larger frontier

1. Obtain the actual full-fragment proofs named in the coherence map; the recovered early note is not a substitute.
2. Rebuild the physical polymer weights from one fixed character convention, with all dimension factors and invariant-space multiplicities retained.
3. Replace the false vertex rule with actual link admissibility. Check all entropy claims against the corrected support class.
4. Define the full polymer family, activities, incompatibility relation and size penalty. Verify an actual cluster-expansion criterion, not merely finiteness of a selected activity sum or a connected-walk proxy.
5. Prove the full tensor contraction is dominated by the particular scalar budget, including vacuum normalization and observable insertions.
6. Only then promote the coefficient bound near x=0.6273 to a physical Wilson clustering or gap claim.

The first audited obstruction is now concrete: physical activity normalization and contractions, rather than the arithmetic size of the reported coefficient budget.

## Primary comparison source

Patrick Rebeschini and Ramon van Handel, *Comparison Theorems for Gibbs Measures*, Journal of Statistical Physics 157, 234–281 (2014), arXiv:1308.4117. Corollary 2.6 gives the single-site comparison with D=ΣC^n; the discrete-metric discussion and Corollary 2.8 give the row-norm uniqueness specialization. The Wilson influence and covariance estimates above are derived here from that theorem.

https://arxiv.org/abs/1308.4117

https://web.math.princeton.edu/~rvan/dobrushin130819.pdf
