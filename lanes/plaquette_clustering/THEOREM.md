# 3D SU(2) connected plaquette clustering: an explicit conservative bound

**Status (27 October 2026):** complete mathematical derivation offered for independent audit; numerical acceptance checks reproducible with Python's `fractions.Fraction`. Not a closed YM3D analytic gate, not a continuum theorem. This standalone argument does **not** consume the imported branched enumeration or its historical checker result.

## 1. Setting and normalization

Fix a finite periodic cubic box of side at least four lattice spacings in each direction. Orient one representative of each geometric plaquette. The Wilson measure is

\[
 d\mu_\beta(U)=Z_\beta^{-1}\prod_{p}\exp(\beta\phi_p(U))\prod_{\ell}dH(U_\ell),\qquad
 \phi_p(U)=\tfrac12\operatorname{Tr}_{\mathbf 2}U(\partial p)\in[-1,1].
\]

Here beta is the coupling used by the YM3D strong-coupling package (`exp(beta/2 Re Tr U_p)`). For distinct plaquettes `p != q`, the covariance is exactly the mixed local-coupling derivative

\[
 \langle\phi_p;\phi_q\rangle_\beta
  =\left.\partial_s\partial_t\log Z(\beta_p+s,\beta_q+t)\right|_{s=t=0}.
\]

The single-face normalization \(z(w)=\int_{SU(2)}e^{w\phi(U)}dH(U)\) is nonzero in the source disk below. Put \(f_w=e^{w\phi}/z(w)-1\). Multiplying by \(\prod_p z(\beta_p)\) changes the log-partition function only by sums of individual-plaquette terms and therefore does not change its mixed derivative at distinct marks.

## 2. Exact Haar input and a complex-source bound

For SU(2), \(\phi=\cos\theta\) under normalized Haar measure; therefore

\[
\int\phi\,dH=0,\qquad \int\phi^4\,dH=\tfrac18,
 \quad\|\phi\|_4=8^{-1/4}<\tfrac35.
\]

Let beta <= 3/200, and allow *independent complex couplings* in the two marked faces with |s|, |t| <= eta = 1/500. Every resulting face coupling obeys |w| <= b = 17/1000. By the exponential power series, |phi| <= 1 and the vanishing first Haar moment,

\[
 |z(w)-1|\le D:=\frac{b^2}{2(1-b)},\quad
 \|e^{w\phi}-1\|_4\le\frac{b}{1-b}\|\phi\|_4.
\]

It follows directly from the triangle inequality that

\[
 \|f_w\|_4\le B:=
 \frac{(b/(1-b))(3/5)+D}{1-D}
 =\frac{20689}{1965711}\ (<0.010525).
\]

These are estimates uniform in the complex source disks, including for the unmarked real couplings. The local normalization is nonzero because D<1. The bound uses no positive-character cancellation at complex coupling.

## 3. Support gas, Finner, and elementary counting

Expand \(\prod_p(1+f_{\beta_p}(U_p))\). If a link belongs to exactly one selected face, its Haar integral vanishes because \(\int f_w=0\). Every surviving selected set splits uniquely into **link-connected** components X whose used links have face valence at least two. Define

\[
 w(X)=\int \prod_{p\in X} f_{\beta_p}(U_p)\prod_{\ell\in E(X)}dH(U_\ell).
\]

Two components are compatible precisely when they share no links. This is the same polymer gas and compatibility convention as the uploaded `YM3D_STRONG_COUPLING_KP_DOMAIN_1` research package. Finner's generalized Hölder inequality, with exponent four assigned to each plaquette function (no link belongs to more than four plaquettes), implies

\[ |w(X)|\le \prod_{p\in X}\|f_{\beta_p}\|_4\le B^{F(X)}.\]

The graph of elementary plaquettes sharing a link has maximum degree 12: four edges per face, at most three alternative faces per edge. Every rooted connected face set of cardinality F can be encoded by a rooted *ordered* spanning tree and a choice of one of at most 12 neighboring faces on each tree edge. There are Catalan(F-1) <= 4^(F-1) tree shapes. Consequently

\[
 N_F(p)\le 48^{F-1}.
\]

For any nonzero support containing p, the four different edges of p must each be shared by an additional plaquette. Distinct elementary plaquettes in the nondegenerate cubic lattice share at most one entire edge. Thus the argument only requires the safe bound **F >= 5** (the uploaded enumeration begins at F=6, but its completeness is not needed here).

## 4. Weighted KP and connected-cluster estimate

Take a=3/10 and delta=1/10, so a+delta=2/5 and exp(2/5)<3/2. The latter upper bound follows, e.g., by the exact-rational geometric tail for the exponential series in `tools/certificate.py`. Put

\[
 M:=\frac32 B=\frac{20689}{1310474},\qquad
 q_0=48M<1,
\]

and bound the rooted sum for *all possible source values* by

\[
 R:=\sup_{p}\sum_{X\ni p}|w(X)|e^{(a+\delta)F(X)}
 \le\sum_{F\ge5}48^{F-1}M^F
 = \frac{M(48M)^4}{1-48M}<0.021496.
\]

If X has F faces, at most 2F distinct links belong to it because every used link has face valence >=2. For any link, the sum of weights of polymers through it is at most twice the rooted face sum R: that link has four plaquettes, and every surviving polymer through the link contains at least two. Therefore

\[
 \sum_{Y\not\sim X}|w(Y)|e^{(a+\delta)F(Y)}\le 4 F(X) R < a F(X),
\]

where the last inequality is an **exact rational** inequality checked by the certificate. This is the KP criterion for the new activities \(\widehat w(Y)=|w(Y)|e^{\delta F(Y)}\), with control function a F(Y).

For these dominated activities, the usual rooted-cluster theorem gives the absolute expansion

\[
 \log\Xi=\sum_{n\ge1}\frac1{n!}
 \sum_{X_1,\ldots,X_n}\varphi^T(X_1,\ldots,X_n)
 \prod_i w(X_i)
\]

and a bound on clusters with a selected first polymer X by \(e^{aF(X)}\) times that root's activity. Here the graph in each nonzero \(\varphi^T\) is connected by polymer incompatibility.

Let d(p,q) be graph distance between the two distinct plaquettes in the link-sharing plaquette graph, including shortest paths through the periodic box. A cluster that meets *both* marked faces contains a link-connected union with at least d(p,q)+1 faces, so \(d(p,q)\le\sum_i F(X_i)\). All clusters not meeting both marks have mixed source derivative zero. For each remaining cluster term, two-variable Cauchy bounds in the disks of radius eta cost eta^-2. Using the strengthened KP root sum and the distance weight then gives

\[
 \boxed{\left|\langle \phi_p;\phi_q\rangle_\beta\right|
 \le \frac{R}{\eta^2}\,e^{-\delta d(p,q)}
 < 5373.78\,e^{-d(p,q)/10}.}
\]

**Scope:** every distinct pair of elementary plaquettes, beta in [0,0.015], every admissible periodic finite box. The bound is independent of volume. For an averaged local scalar operator \(O_x=\sum_{a=1}^3\phi_{x,a}\), applying the triangle inequality to the nine face pairs gives the corresponding sum of nine exponential terms; their distances must be measured facewise rather than silently equated with vertex distance.

## 5. Independent perturbative cross-check

For two distinct faces p,q belonging to the **same cube**, the cube's closed all-fundamental surface contributes exactly 2^(2-6)=1/16 times the product of its six character coefficients \(r_1(\beta_j)=\beta_j/2+O(\beta_j^3)\). Hence its contribution to the mixed local-coupling derivative begins at

\[
 \frac{N_{\mathrm{shared\ cubes}}(p,q)}{1024}\,\beta^4.
\]

`tools/leading_cube.py` checks cube incidence and this coefficient for a test pair of opposite cube faces. This is a **specific lowest-surface contribution**, not a claim that no other diagram or cancellation can affect the first nonzero coefficient without a full independent enumeration of source-decorated graphs.

## 6. Claim boundaries and review checklist

1. The script checks the rational inequalities, not Finner's theorem, the cluster theorem or their correct use in this application. An independent mathematical review of these steps is required before promoting the lane to an analytic program gate.
2. The result is a direct strong-coupling statement. It does **not** use or close the imported beta<=0.185 all-support certificate, whose new independent branched checker was pending at the prior handoff.
3. The result is **not** a lattice-spacing-uniform physical mass, a statement about continuum beta->infinity, a transfer-matrix spectrum result or a 4D result.
4. The exponential is in the **plaquette adjacency graph**. Translating to Euclidean or physical distance requires a separate, stated geometry conversion.
5. The count assumes nondegenerate plaquettes and links; exclude periodic boxes with a dimension shorter than four.
