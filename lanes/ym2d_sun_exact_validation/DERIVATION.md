# SU(2) open-boundary reference: definitions and derivation

This is an exact reference benchmark with a separately implemented arithmetic
and geometry audit. It is not a completed validation of the future 3D ledger
pipeline. The program milestone remains blocked; no analytic waiver is used.

## Measure and normalization

Use normalized Haar measure on every link of a finite open rectangular square
lattice, with density proportional to

    exp[beta sum_p t(U_p)],  t(U) = Tr(U)/2,  beta >= 0.

Here beta multiplies the normalized fundamental trace. This is the Wilson
plaquette action, not the heat-kernel action. Additive constants in the action
cancel from normalized observables. A spin-j Wilson observable is
chi_j(U_loop)/(2j+1); n=2j labels the representation.

For a class function of SU(2), t=cos(theta) has normalized density
2 sqrt(1-t^2)/pi on [-1,1]. Its moments are

    mu_(2k) = binomial(2k,k) / [(k+1) 4^k],   mu_(2k+1) = 0.

They follow by the substitution t=cos(theta) and the beta integral, or the
semicircle-moment recurrence. In particular mu_0=1, mu_2=1/4, mu_4=1/8.
The first three normalized characters are 1, t, and (4t^2-1)/3.

Define K_n(beta) as the Haar integral of exp(beta*t) times the normalized
spin-n/2 character. Expanding the exponential and inserting these moments gives,
for n=0,1,2,

    K_n(beta) = sum_(k>=0) beta^(2k+n) /
                         [2^(2k+n) k! (k+n+1)!].

For n=2 the cancellation of its constant term and the identity
(4 mu_(2k+2)-mu_(2k))/3 give the displayed positive coefficients after reindexing.
For n=1 use mu_(2k+2)/(2k+1)!. These factorial identities hold for every k;
they are not inferred from a numerical fit or a finite set of coefficients.
Termwise integration is valid by absolute uniform convergence on t in [-1,1].

The single-plaquette partition factor is Z=K_0. The mean normalized character is
r_n=K_n/K_0. Equivalently r_n=I_(n+1)(beta)/I_1(beta) for positive beta, with I
being the modified Bessel function; no Bessel evaluation library is used here.
At beta=0 the trivial mean is one and the other two vanish. The leading
fundamental coefficient is beta/4; the leading adjoint coefficient is beta^2/24.
These detect missing trace and representation-dimension factors.

## Why the open lattice reduces to independent plaquettes

Take the comb spanning tree: every horizontal link plus the leftmost vertical
column. A root-fixed tree gauge sets those links to identity. For a gauge-invariant
observable, the corresponding changes of link variables preserve normalized Haar
measure. Tree-gauge variables integrate to one; no background-dependent determinant
is introduced by this finite-tree construction.

Write V(x,y) for an upward vertical link in this gauge, with V(0,y)=1. The
positively traversed plaquette is

    P(x,y) = V(x+1,y) V(x,y)^(-1).

The inverse triangular change of variables is

    V(x,y) = P(x-1,y) ... P(0,y).

Each step is multiplication by an already fixed group element. Haar invariance
therefore makes the plaquette variables independent under the ungauged product
measure as well as under their product Wilson weights after normalization. For
N_p plaquettes the unnormalized lattice partition function is K_0(beta)^N_p.
Open boundaries are essential here: no periodic global holonomy constraint is
being silently discarded.

Because the plaquette density is conjugation invariant, Schur's lemma gives
E[D_j(P)] = r_n identity. SU(2) characters are real, so the same holds for P^(-1).
For a rectangular loop, every interior plaquette occurs exactly once in its
ordered axial-gauge boundary word. Integrate those independent variables one at
a time. Each inserts a scalar r_n; all remaining exterior words cancel in their
original noncommutative order. Hence

    E[chi_j(U_rectangle)/(2j+1)] = r_n^A,

where A is the number of enclosed plaquettes. At positive finite beta, 0<r_n<1
for the two nontrivial representations, so this is the discrete area law. The
code exports bounded Wilson expectations, not floating logarithms of a string
tension. It checks every rectangle on a 4-by-3 plaquette grid, in both traversal
directions: 120 ordered loops, including translated loops whose raw axial words
contain exterior variables. An explicit free-word stack retains order; commuting
plaquettes to simplify their counts would be invalid.

## Exact outward error bounds

The generator uses the positive factorial series above. The checker instead
integrates the normalized character polynomials using Catalan Haar moments.
Both use Python integers and fractions.Fraction, with no binary floating-point
or external interval backend in the audit.

Retain k=0 through K=24. If a_k denotes a positive term, then

    a_(k+1)/a_k = beta^2 / [4(k+1)(k+n+2)].

This ratio decreases as k increases. With b=a_(K+1) and
rho=beta^2/[4(K+2)(K+n+3)]<1, the omitted tail is between zero and b/(1-rho).
The checker obtains b and the next-term ratio from its own Haar coefficients.
The couplings are exactly 0, 1/2, 2 and 4; all satisfy this condition.

For positive Z intervals and nonnegative numerator intervals, ratio and power
bounds are

    r_n in [K_n.lower/Z.upper, K_n.upper/Z.lower],
    r_n^A in [r_n.lower^A, r_n.upper^A].

Every endpoint is rounded outward to a dyadic rational with denominator dividing
2^96. The checker reconstructs the enclosures and requires the exact rounding
and absolute width <=2^(-80). It validates 12 one-plaquette cases and 64 area-law
cases, with 88 intervals in total. The action, boundary, representations, coupling
schedule and precision are pinned; altered conventions and weakened precision
are rejected. These are rational enclosures of generally irrational expectations,
not assertions that the exact expectations are rational numbers.

## Scope and primary reference

The finite measure reduction uses standard Haar invariance and representation
theory, with the open-grid specialization derived above. The executable audit
checks the finite geometry, character-moment arithmetic and tail bounds. It is
not a proof-assistant formalization of Haar integration or Schur's lemma.

Aroca and Kubyshin, *Calculation of Wilson loops in 2-dimensional Yang-Mills
theories*, Annals of Physics 283 (2000), 11-56, section 4 and its lattice
character-expansion construction:
https://arxiv.org/abs/hep-th/9901155;
https://doi.org/10.1006/aphy.2000.6044.
Our action, normalized-character convention, open-boundary specialization and
rational truncation schedule are explicit here; no compact-surface or continuum
heat-kernel formula is substituted for this Wilson-lattice benchmark.
