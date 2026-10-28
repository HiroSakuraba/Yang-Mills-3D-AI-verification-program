# Exact two-source marked polymer identity — with convergence scope kept separate

For finite **closed** normalized SU(2) Wilson loops C,D set
\[
Z(s,t)=\int\exp\left(\beta\sum_{p}\phi_p+sW_C+tW_D\right)dH(U),\quad
 Z_{00}=Z(0,0)>0.
\]
For real s,t, the measure is positive; for complex s,t, these are entire finite-dimensional integrals. In a sufficiently small neighborhood of (0,0), Z is nonzero and a unique analytic log branch normalized by its real value at zero exists. Exactly,
\[
\left.\partial_s\partial_t\log Z(s,t)\right|_{0,0}=\langle W_C W_D\rangle_\beta-\langle W_C\rangle_\beta\langle W_D\rangle_\beta.
\]

## A hard-core augmented gas without a false plaquette-only assumption

Write \(z_\beta=\int e^{\beta\phi(U)}dH(U)\), \(f_p(U)=e^{\beta\phi_p(U)}/z_\beta-1\), \(h_C=e^{sW_C}-1\), \(h_D=e^{tW_D}-1\). On each link configuration, identically
\[
Z(s,t)=z_\beta^{|P|}\int\prod_{p\in P}(1+f_p(U))\,(1+h_C(U))(1+h_D(U))\,dH(U).
\]
Give each vertex of the finite hypergraph \(P\sqcup\{\mathbf C,\mathbf D\}\) its **link support**: four links for a plaquette, the *entire set of distinct links* of C or D for the respective marked vertex. In a selected subset A of these vertices, join two vertices precisely when they share a link. The connected components \(\gamma\) have link support \(S(\gamma)\) and exact weight
\[
 w_{s,t}(\gamma)=\int_{SU(2)^{S(\gamma)}}
 \prod_{p\in\gamma\cap P} f_p(U)
 \prod_{i\in\gamma\cap\{\mathbf C,\mathbf D\}}h_i(U)\,\prod_{e\in S(\gamma)}dH(U_e).
\]
Selected components have disjoint link supports, so their Haar integrals factor **exactly**. Summing over hard-core compatible components gives an exact finite-volume representation \(Z(s,t)=z_\beta^{|P|}\Xi_{\rm aug}(s,t)\). Components without marks and with any singly covered link vanish, because their single-link integral of \(f_p\) is zero. **With a Wilson mark this valence-one rule changes**: a face touching a contour link may survive, and one cannot reuse the plaquette-only F≥5 bound for such a marked component. This is the principal combinatorial extension.

The logarithm of \(\Xi_{\rm aug}\) admits the standard **formal** Mayer/Ursell expansion at \(\beta=s=t=0\), and the coefficient of st is assembled from connected incompatibility clusters that collectively involve both marked vertices. For link-disjoint C,D, any such cluster must connect their supports via plaquette factors, because the marks do not themselves share a link. This explains geometric source localization and the dependence on the length of each contour, but **does not** establish an absolutely convergent KP majorant for the augmented activities at β=3/25. The unconditional absolute convergence of the source-marked Mayer series at that endpoint is an **open analytic obligation**. Do not replace it with the plaquette-only KP certificate at β=9/100.

The separate Dobrushin analysis in `README.md` is an independent, rigorous-in-principle route to the exponential covariance estimate at β≤3/25, conditional only on auditing its local influence proof and invoking the published covariance theorem. It does not justify termwise source differentiation of a nonconvergent augmented-polymer cluster sum.

## A normalised source comparison that survives differentiation

For \(|s|,|t|<\log2\), \(|\mathbb E_\beta e^{sW_C}|\ge2-e^{|s|}>0\) and similarly for D, since \(|W|\le1\). Define the exact connected ratio
\[
R(s,t)=\frac{Z(s,t)Z(0,0)}{Z(s,0)Z(0,t)}
 =1+\frac{\operatorname{Cov}_\beta(e^{sW_C},e^{tW_D})}{\langle e^{sW_C}\rangle_\beta\langle e^{tW_D}\rangle_\beta}.
\]
No unnormalized numerator may replace the covariance on the right. The derivative at the origin of \(\log R\) reproduces \(\operatorname{Cov}(W_C,W_D)\). This identity is independent of the choice of polymer expansion and is a useful acceptance test for a future absolute source-weighted KP argument. When the two observables are well separated, the Dobrushin covariance bound for their source exponentials supplies exponential separation as well; the denominator is nonzero for the displayed small source disks. A *volume-uniform complex-source KP norm*, however, has not been established here.

The contrast with the 4D Wilson-loop program is deliberate: V5's outgoing observable is a Radon–Nikodym derivative of an **inserted** measure with respect to a **vacuum** measure, whereas its continuum comparison uses a *centred numerator/denominator mark*. Neither is equivalent to simply inserting one extra plaquette factor in the vacuum polymer expansion.
