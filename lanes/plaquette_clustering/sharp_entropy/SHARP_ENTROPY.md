# Sharper 3D two-plaquette clustering without an enumerated-tail dependency

**Research status (27 October 2026):** proposed mathematical proof for independent review. The attached Python script verifies all displayed **rational inequalities** exactly. It does not formally verify the combinatorial induction, Finner's inequality, the Kotecký–Preiss (KP) cluster theorem, or the use of multivariate Cauchy estimates. It intentionally does **not** use the historical branched-Haar checker or assert that the imported 0.185 KP endpoint is independently verified.

## Statement

Consider Wilson's 3D SU(2) lattice measure on a finite, nondegenerate periodic cubic lattice of side at least four, with

\[
  d\mu_\beta(U)=Z^{-1}\exp\!\left(\beta\sum_f\phi_f(U)\right)\prod_e dH(U_e),\quad
  \phi_f(U)=\tfrac12\operatorname{Tr}U(\partial f)\in[-1,1].
\]

For distinct elementary faces \(p,q\), let \(d_P(p,q)\) be their distance in the graph in which two plaquettes are adjacent iff they share a link. The *proposed* explicit bound is

\[
 \boxed{\left|\langle\phi_p;\phi_q\rangle_\beta\right| \leq
      C_{\rm rat}e^{-d_P(p,q)/10},\quad
      0\leq\beta\leq\frac9{100},\quad
      C_{\rm rat}:=\frac{R_*}{(1/500)^2}<11153.}
\]

The precise rational value \(R_*\) is in `artifacts/entropy_certificate.json`. In particular, the bound is uniform in the finite lattice volume at **fixed lattice spacing**. No continuum spectrum or 4D assertion follows.

## Step 1. Exact local-source normalization

Replace each face coupling by an independent complex value \(v_f\). Only two faces will eventually be perturbed by parameters \(s,t\) with \(|s|,|t|\leq\eta:=1/500\), while the others retain \(\beta\in[0,9/100]\). All \(|v_f|\leq b:=23/250=0.092\). Write

\[
 z(v)=\int_{SU(2)}e^{v\phi(U)}\,dH(U),\quad
 f_v(U)=e^{v\phi(U)}/z(v)-1.
\]

For SU(2), the Haar pushforward of \(\phi\) satisfies \(\int\phi\,dH=0\), \(\int\phi^4\,dH=1/8\), and \(|\phi|\leq1\). The elementary exponential series gives, for any \(|v|\leq b\),

\[
 |z(v)-1|\leq D=\frac{b^2}{2(1-b)}<1,
 \qquad \|f_v\|_{L^4(dH)}\leq
 B=\frac{\frac{b}{1-b}\frac35+D}{1-D}.
\]

This proves that every local normalization is nonzero in the full complex polydisk, *without* appealing to positivity of real-coupling character coefficients at complex sources.

## Step 2. Haar-supported polymer gas

Expanding \(\prod_f[1+f_{v_f}(U_f)]\), any face set containing a link incident to exactly one selected face integrates to zero. The remaining sets decompose into unique components linked by shared links; call them polymers. They are incompatible when they share a link. For a polymer \(X\),

\[
 w_v(X)=\int\prod_{f\in X}f_{v_f}(U_f)\prod_{e\in E(X)}dH(U_e).
\]

Each 3D link occurs in at most four plaquettes. Finner's hypergraph Hölder inequality therefore yields

\[
 |w_v(X)|\leq\prod_{f\in X}\|f_{v_f}\|_{4}\leq B^{|X|}.
\]

If \(p\in X\), each of its four links must belong to another selected face, and two distinct elementary plaquettes share at most one full link. Consequently **\(|X|\geq5\)**; we do not rely on an independently unreviewed improvement to six.

## Step 3. The all-support counting lemma (self-contained decision induction)

Put \(w=3247/10000\) and \(H=13247/10000=1+w\). Consider the rooted generating function over **all** finite link-connected face sets containing root plaquette \(p\) and having no link of selected-face valence one:

\[
 A_p(z):=\sum_{X\ni p\ \text{surviving}} z^{|X|-1}.
\]

**Claim (decision-encoding lemma).** For \(z=z_*:=w/H^3\),

\[
 A_p(z_*)\leq H^4<3.08,\qquad
 z_* > 13967/100000\;(>0.13967).
\]

*Combinatorial proof for independent checking.* Grow a candidate support starting from \(p\) by deciding one touched, undecided link at a time, using a fixed lexicographic choice. If the link is already incident to \(c\in\{1,2,3,4\}\) chosen faces, choose a subset of the at most \(4-c\) other incident faces to add so its final count is at least two; forbid adding any face that touches a previously decided link. This gives a unique history for every fixed surviving support (each face is first added when its first touched link is decided). Every added face introduces **at most** three other undecided link incidences; some may already have been touched, which only makes the potential majorant conservative.

Give each currently touched undecided link with count \(c\) the potential \(h(c)=H^c\), and give each newly added face the weight \(z\). At one decision, the total potential of the children divided by the parent's potential is bounded by

\[
 \frac{g_c(zH^3)}{H^c},\quad
 g_1(w)=(1+w)^3-1,\quad g_2(w)=(1+w)^2,\quad
 g_3(w)=1+w,\quad g_4(w)=1.
\]

At the rational witness \(w=3247/10000\) all four inequalities \(g_c(w)\leq H^c\) hold; `tools/entropy_certificate.py` checks them exactly. The root has four touched links, so its initial potential is \(H^4\); terminal states have no undecided link and contribute their weights \(z^{|X|-1}\). This proves the displayed count provided the uniqueness and potential bookkeeping in this paragraph are valid. The decision-encoding lemma is **not** a claim about verified enumeration counts at every cardinality; it is a bound valid uniformly by an inductive branching argument.

## Step 4. Size-weighted KP condition with geometric decay margin

Set \(a=1/5\), \(\delta=1/10\), and \(E=27/20\). The strictly rational Taylor majorant

\[
 e^{a+\delta}=e^{3/10}\leq1+u+\frac{u^2}{2}+\frac{u^3}{6(1-u/4)}\biggr|_{u=3/10}<\frac{27}{20}=E
\]

uses \(n!\geq 6\,4^{n-3}\) for every integer \(n\geq3\). Let \(M:=EB\) and check \(M<z_*\). The minimum size-five observation together with the counting lemma gives, for every face \(p\) and every complex source choice,

\[
 \begin{split}
 \sum_{X\ni p}|w_v(X)| e^{(a+\delta)|X|}
 &\leq \sum_{X\ni p}M^{|X|}\\
 &=M\sum_{X\ni p}\left(\frac{M}{z_*}\right)^{|X|-1}z_*^{|X|-1}\\
 &\leq M\left(\frac{M}{z_*}\right)^4H^4=:R_*.
 \end{split}
\]

The exact certificate establishes

\[
 R_*<0.044611,\qquad4R_*<0.178443<0.2=a.
\]

If \(X\) has \(F\) faces, it contains at most \(2F\) links, because every used link has face-valence at least two. For each such link, at least two of its four incident faces belong to any incompatible polymer; charging that polymer to its incident face gives a rooted sum at most \(2R_*\) per link. Thus

\[
 \sum_{Y\not\sim X}|w_v(Y)|e^{(a+\delta)|Y|}\leq 4FR_*<aF.
\]

This is the KP criterion for the *distance-weighted* activities \(|w_v(Y)|e^{\delta|Y|}\), with control function \(a|Y|\). The standard rooted KP cluster theorem yields an absolute connected-cluster expansion uniformly over the local source polydisk.

## Step 5. Two marked faces and exponential distance

For distinct faces \(p,q\), use independent sources \(s,t\) at these faces and write \(Z(s,t)=\prod_f z(v_f)\,\Xi(s,t)\). The mixed derivative of \(\sum_f\log z(v_f)\) vanishes, hence

\[
 \langle\phi_p;\phi_q\rangle_\beta=
 \left.\partial_s\partial_t\log\Xi(s,t)\right|_{s=t=0}.
\]

A connected cluster contributing to this derivative must contain a polymer using each marked face (possibly the same polymer). Because the incompatibility connections are shared links, the union of its plaquettes is connected in the plaquette graph. If its total face count (counting repetitions across polymers) is \(F_{\rm total}\), then \(d_P(p,q)\leq F_{\rm total}-1\leq F_{\rm total}\). Therefore the exponential weight \(e^{\delta F_{\rm total}}\) pays \(e^{\delta d_P(p,q)}\).

Anchor each cluster at a polymer containing the first marked face. The rooted cluster theorem, applied to the stronger weights, bounds its total absolute activity by \(R_*\). A two-variable Cauchy estimate on \(|s|,|t|\leq\eta\) then costs \(\eta^{-2}\), giving

\[
 \boxed{\big|\langle\phi_p;\phi_q\rangle_\beta\big|
 \leq R_*\eta^{-2}\,e^{-\delta d_P(p,q)}<11153\,e^{-d_P(p,q)/10}.}
\]

**Audit obligation:** justify precisely that the rooted-cluster theorem's anchored sum is compatible with the two local source derivatives and the distance weight; the rational certificate does not check cluster combinatorics or Cauchy analyticity. The expected bound is stated here as a reviewable *candidate theorem*, not an automated proof.

## Scope and next steps

1. This is independent of the archived branched-Haar report. It uses **only** the decision-encoding potential lemma for all surviving supports. It does not establish the sharper imported β=0.185 endpoint for observables.
2. The earlier Wilson-loop Dobrushin estimate retains its separate domain \(\beta\leq0.015\). **No bound for arbitrarily long Wilson loops at β=0.09 has been established.** Elementary plaquettes are Wilson loops, so the result does cover two unit loops at the stronger coupling.
3. Distances are measured in the plaquette adjacency graph, and uniformity is in volume, not in the ultraviolet lattice spacing or the physical correlation length.
4. Before use as a proof gate, obtain an independent math review of the decision-encoding uniqueness and the analytic polymer-to-derivative step; ideally also give a second independent implementation of the rational branching witness.
5. A natural next extension is a fixed-size, finite-link-support gauge-invariant insertion by a source-weighted expansion, then a genuinely renormalized dressed-loop insertion with explicit numerator/denominator accounting.
