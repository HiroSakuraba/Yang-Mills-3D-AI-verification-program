# Wilson comparison and the transfer-gap lemma

Benjamin John Schulz research working notes · 16 October 2026

**Follow-up:** related source history has now been recovered and audited in `Original-proof-audit-and-Wilson-baseline.md`. Its exact cube counterexample and normalization findings concern the recovered early note. The coefficient certificates below remain valid; the named full-fragment bundles are still unlocated.

This note verifies a coefficient calculation and states the hypotheses needed to use it. It does not claim a four-dimensional continuum mass-gap theorem. The original strong-coupling proof bundles named in the uploaded map were not supplied; their combinatorial bounds remain inputs requiring inspection.

## 1. Conventions fixed before comparison

The gauge group is SU(2), with normalized trace tr(1)=1. The Wilson single-plaquette weight, after removing its configuration-independent factor, is

    w_x(U) = exp(x tr U),  x > 0.

With doubled-spin label a=0,1,..., dimension d_a=a+1 and ordinary irreducible character χ_a,

    w_x = Σ c_a(x) χ_a,
    c_a(x) = 2(a+1) I_(a+1)(x)/x,
    r_a(x) = c_a/c_0 = (a+1) I_(a+1)(x)/I_1(x),
    ξ_a(x) = r_a(x)^2,  a >= 1.

For this note the heat kernel is defined explicitly by

    h_τ(U) = Σ (a+1) exp[-τ a(a+2)/8] χ_a(U),
    ξ_a(τ) = (a+1)^2 exp[-τ a(a+2)/4].

The parameter τ is therefore twice the time in the convention exp[-t j(j+1)]. This convention reproduces the uploaded map's numbers. A different heat-kernel time convention changes the parameter values; there is no exact identity between the heat-kernel and Wilson actions.

The Wilson coefficient formula follows from SU(2) class-angle integration: normalized Haar class measure is (2/π) sin²θ dθ, χ_a(θ)=sin((a+1)θ)/sinθ, and the Bessel recurrence converts I_a-I_(a+2) to 2(a+1)I_(a+1)/x. The constant exp(-x) from the action cancels from all ratios.

The normalized Wilson inverse coupling x agrees with the x in the publicly posted Theorem 0 draft (its §1.4, one-loop normalization). This is a matching of Wilson conventions. It does not place an effective action containing additional interactions on a one-parameter Wilson curve.

## 2. Positive coefficients and an explicit ratio bound

For integer n>=0 and x>0,

    I_n(x) = Σ_{k>=0} (x/2)^(2k+n) / [k! (k+n)!] > 0.

Termwise comparison gives

    I_(n+1)(x) <= [x / (2(n+1))] I_n(x).

Consequently

    ξ_(a+1)(x)/ξ_a(x) <= x²/[4(a+1)²].

In particular ξ_a decreases for all a>=1 throughout the computed range 0<x<=0.7. Coefficients are positive and their tails are summable. Nonnegative character coefficients also give the standard lattice reflection-positivity construction, when plaquette reflection and boundary conditions are chosen in the usual compatible way. Reflection positivity for a proposed coarse-graining still needs its own proof; it does not follow merely from the microscopic Wilson coefficients.

Strict increase of each ξ_a with x can be proved without a numerical derivative. For ν>=1, I_(ν+1)/I_ν is the mean of t under the probability density proportional to exp(xt)(1-t²)^(ν-1/2) on (-1,1). Its derivative is the strictly positive variance of t. The ratio I_(a+1)/I_1 is the product of these adjacent ratios for ν=1,...,a. Hence ξ_a, and the positive activity sums below, increase strictly with x. Heat-kernel weights and their activity sums decrease strictly with τ. These facts justify interpreting the endpoint calculations as brackets for the respective activity crossings.

## 3. The exact sums being enclosed

All representation labels below are nonzero. Define the SU(2) channel set

    C(a,b) = {|a-b|, |a-b|+2, ..., a+b}.

Then the reconstructed grammar is

    Q₂ = Σ_a ξ_a²,
    Q₃ = Σ_(a,b,c) 1[c in C(a,b)] ξ_a ξ_b ξ_c,
    Q₄ = Σ_(a,b,c,d) 1[C(a,b) intersects C(c,d)] ξ_a ξ_b ξ_c ξ_d,
    ρ_act = e [39 Q₂ + 95 (Q₃+Q₄)].

Tuples are ordered. In Q₄ a tuple is counted once when a common channel exists. It is NOT multiplied by the number of common channels. For example (1,1,1,1) has common channels 0 and 2 but contributes once. This convention reproduces the uploaded numbers. Before applying a polymer theorem, check that its treatment of recoupling multiplicities matches this convention, or that those multiplicities have already been absorbed into its constants. Reproducing a number does not verify that choice for the physical expansion.

The coefficients 39 and 95 are inherited from the uploaded map. This note does not derive their lattice entropy estimates, verify coverage of all allowed surfaces and defects, or establish the corresponding convergence criterion.

## 4. How the runnable bounds work

`frontier_certificate.py` uses only Python's standard library. Every floating quantity is represented by a closed interval with integer endpoints divided by 10^100. There is no binary floating-point arithmetic in the certificate. Products and divisions round outward using integer floor and ceiling.

Bessel coefficients use the positive series above. After a retained term, let b be the first omitted term and q an upper bound, less than one, on every subsequent term ratio. The omitted series lies between zero and b/(1-q). The exponential is bounded by its positive Taylor series on [0,1], then argument doubling with outward rounding. Reciprocal intervals give negative exponentials.

Let the spin cutoff be M, and let T bound Σ_(a>M) ξ_a. The Wilson ratio lemma yields

    T <= ξ_(M+1) / [1 - x²/(4(M+2)²)].

For heat-kernel weights, replace the denominator's ratio by

    [(M+3)/(M+2)]² exp[-τ(2M+5)/4].

This dominates every subsequent ratio. Let S_all bound Σ_(a>=1) ξ_a. Omitting admissibility constraints only increases positive sums, so the discarded contributions satisfy

    Q₂ tail <= T²,
    Q₃ tail <= 3 T S_all²,
    Q₄ tail <= 4 T S_all³.

The last two are union bounds over the position of an omitted label; overcounting is harmless. Therefore the resulting intervals enclose the uncut infinite sums rather than merely a finite truncation.

When ρ_act<1, the code also encloses -log ρ_act using

    -log r = 2 Σ_(k>=0) q^(2k+1)/(2k+1),  q=(1-r)/(1+r),

with a geometric bound on the remainder. This is an activity decay rate until a valid clustering and transfer theorem identifies it with a physical spectral bound.

## 5. Results

At doubled-spin cutoff M=14 the exact arithmetic proves:

| Action and parameter | Enclosure, rounded outward for display | Arithmetic conclusion |
|---|---:|---|
| Heat kernel, τ=5 | 0.96119017435077955 < ρ_act < 0.96119017435077957 | Below one |
| Heat kernel, τ=4.9742 | 1.0001025323 < ρ_act < 1.0001025324 | Above one |
| Heat kernel, τ=4.9743 | 0.9999486323 < ρ_act < 0.9999486324 | Below one |
| Wilson, x=0.623 | 0.97272237442298917 < ρ_act < 0.97272237442298919 | Below one |
| Wilson, x=0.6273 | 0.99999879664408829 < ρ_act < 0.99999879664408831 | Below one |
| Wilson, x=0.6273001 | 0.99999943774994316 < ρ_act < 0.99999943774994318 | Below one |
| Wilson, x=0.6273002 | 1.00000007885611460 < ρ_act < 1.00000007885611462 | Above one |

Thus the unique crossing for the specified Wilson activity budget lies in (0.6273001,0.6273002). This certifies ρ_act<1 for 0<x<=0.6273001 for these sums. It does not identify the edge of the physical massive phase. Failure of a sufficient expansion bound is not evidence of a phase transition.

For τ=5,

    0.03958299744550050 < -log ρ_act < 0.03958299744550051.

For Wilson x=0.6273,

    0.00000120335663573 < -log ρ_act < 0.00000120335663575.

The near-frontier Wilson rate is tiny. A display that shows only ρ<1 conceals that loss of margin. These rates remain conditional physical gap bounds.

`results.json` contains full endpoints. The six automated checks exercise the Bessel recurrence, reciprocal exponentials, a logarithm identity, admissibility conventions, overlapping bounds at two cutoffs, and opposite signs at the Wilson crossing endpoints. They check implementation consistency; they do not verify the original polymer proof.

## 6. What the density lemma does establish

**Finite graph lemma.** For a finite graph Γ and compact gauge group G, finite linear combinations of matrix coefficients are uniformly dense in continuous functions on G^E by Peter–Weyl. Average over G^V using Haar measure. This averaging is a bounded projection onto gauge-invariant functions, and it maps representation matrix products to contracted intertwiners: spin networks. Therefore finite linear combinations of spin networks are uniformly dense in the gauge-invariant continuous functions.

For any gauge-invariant finite Borel probability measure on G^E, they are consequently dense in its gauge-invariant L² space. They are orthonormal for the conventional Haar kinematic inner product after choosing orthonormal intertwiner bases; they need not be orthonormal for the interacting physical measure. Density, rather than orthonormality, is the relevant property here.

**Infinite spatial lattice.** Bounded cylinder functions are dense in L² of a countable product probability space. Conditional expectation onto increasing finite-edge sigma-algebras converges in L². Gauge invariance of the measure makes these conditional expectations commute with gauge transformations. On each finite subgraph, gauge averaging and the preceding lemma approximate the resulting function by spin networks. Thus local spin networks are dense in the gauge-invariant time-zero L² space of the given state.

**Remaining identification.** One must identify that time-zero space with the full physical transfer Hilbert space used in the claimed gap bridge, or prove its images dense there. At fixed lattice spacing a suitable Markov transfer representation can supply this identification. A time-zero lemma alone does not establish density in an arbitrary continuum Osterwalder–Schrader Hilbert space, or control sectors invisible to the chosen observables.

## 7. Conditional spectral-gap lemma

Suppose T is a bounded self-adjoint positive contraction on a Hilbert space H, TΩ=Ω, and D is dense in H. Write Q=1-|Ω><Ω| with ||Ω||=1. Assume the actual clustering theorem supplies, for every ψ in D and every integer n>=0,

    0 <= <Qψ, T^n Qψ> <= C_ψ exp(-m n),  m>0,

with one common m; C_ψ may depend on ψ but not n.

Let μ_ψ be the spectral measure of Qψ for T. If it had positive mass in [r,1] for any r>exp(-m), then its n-th moment would be at least μ_ψ([r,1]) r^n, contradicting the displayed upper bound as n tends to infinity. Hence the spectral projection onto (exp(-m),1] annihilates QD. Density makes that projection zero on Ω-perp. Thus T restricted to Ω-perp has norm at most exp(-m), and Ω is the unique invariant vector. If T is injective, H_phys=-log T is defined by spectral calculus and has spectrum at least m on Ω-perp. Without injectivity, the transfer-operator conclusion still holds; a densely defined Hamiltonian requires removing the kernel or proving injectivity.

If the available decay statement instead concerns <ψ,T^(2n)ψ>, the same argument must match its exponent to 2n. If one time step has physical length A_t, the physical lower bound is m/A_t. The spatial block distance in an activity estimate is not automatically this time step.

This proves the abstract implication under explicit hypotheses. To close the original R06 entry, inspect its actual observable class, transfer representation, common decay rate, and time normalization.

## 8. Conditions still required for the proposed bridge

1. Verify that the original expansion proves a volume-uniform connected-correlation estimate from precisely the Q₂,Q₃,Q₄ sums and constants used here, including recoupling multiplicities, boundary defects and observable insertions.
2. Show that the coefficient dependence in every proof step uses only the positive coefficients, ratio bounds and tails established above. No heat-kernel semigroup identity or other special property may be silently imported into the Wilson proof.
3. Check the transfer-space and density identifications in §6 and the hypotheses of §7. Treat infinite-volume Gibbs-state uniqueness and uniqueness of a vacuum in a chosen reconstruction as distinct claims.
4. Supply an actual coarse-graining map and a uniform estimate placing its full effective action in that basin. A scalar running coupling is insufficient: blocking generates multi-plaquette interactions.
5. State MIDDLE-1 with the order of quantifiers: for each fixed allowed reference coupling, there must be a finite k* and ρ*<1 independent of the ultraviolet cutoff and relevant volumes. Uniformity as that reference coupling tends to zero would be an extra demand.
6. For rotational invariance, check the exact far-sphere flux hypothesis and ultraviolet control of renormalized stress-tensor insertions. A gap for bounded lattice Wilson loops alone does not establish those estimates.
7. For any zero-free computation, bound every boundary segment and every truncation remainder. Small boxes do not prove a volume-uniform zero-free region. Analyticity alone does not imply a mass gap or entry into a specific polymer basin.

## 9. Source check in this pass

The public Theorem 0 PDF was downloaded and inspected at §1.4 and §9.4; the latter describes the finite-size criterion without its exact functional or threshold. All three posted companion TeX files were downloaded and searched for that criterion. No match was found for the four literal phrases recorded in `source-check.json`; this is a search result, not proof that no equivalent statement occurs. The outstanding-proof list in part III explicitly includes large-field positivity. Snapshot hashes are recorded for reproducibility. No correspondence was sent to the authors.

Primary sources:

- https://github.com/ethanwsussman/Yang--Mills-LLM-experiment
- https://github.com/ethanwsussman/Yang--Mills-LLM-experiment/blob/main/ym4_manuscript_zeroth_draft.pdf
- https://github.com/ethanwsussman/Yang--Mills-LLM-experiment/blob/main/theorem_0_complete_account_raw_III.tex
- Shen, Zhu and Zhu, *A stochastic analysis approach to lattice Yang–Mills at strong coupling*, https://arxiv.org/abs/2204.12737. Its stated SU(N) domain is a separate established result; its normalization was not rederived from the full paper in this pass.
