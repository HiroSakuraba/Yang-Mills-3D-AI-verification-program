# FALLBACK_LOWER_ORDER_ACTIVITY_1 — Proof Note v1

**Status:** first proof draft; one Haar-contraction step uses a conservative bound (flagged §3.1).
**Track:** A1 (polymer / spin-network strong-coupling lane).
**Claim boundary:** SU(2) lattice Yang–Mills, finite volume \(\Lambda\subset\mathbb Z^4\), finite Peter–Weyl cutoff \(J\ge 1/2\), vacuum-normalized expectations. Strong-coupling lattice regime only. **No continuum claim. No mass-gap statement.**
**Author convention:** theorem-gated, claim-boundary-first; matches CONTINUUM_RG_BRIDGE_0 v7.
**Deliverable per design doc §8.2:** *activity table + proof note*. Activity table is `FALLBACK_LOWER_ORDER_ACTIVITY_1_activity_table_v1.csv`; interval-arithmetic certificate is `fallback_lower_order_activity_certificate_v1.py`.

---

## 1. Setting and inputs

### 1.1 Closed reductions

The chain
\[
\text{FV-WT-4}\ \longrightarrow\ \text{BDE-MARKOV-1}\ \longrightarrow\ \text{BDE-CANCEL-1}\ \longrightarrow\ \text{SSE-1}
\]
is closed at finite Peter–Weyl cutoff \(J\). Its output is the vacuum-normalized cluster expansion
\[
\langle O\rangle^{J}_{\Lambda}
=
\sum_{\substack{C\\\text{connected cluster}\\C\,\text{touches }O}}
W(C;\beta,J),
\]
where each cluster \(C\) is a finite multiset of polymers with all link Haar integrations performed and vertex intertwiner contractions absorbed into the cluster weight \(W(C)\). The present note bounds the lower-order **two-face species** contribution to this sum.

### 1.2 Polymer grammar

A *polymer* is a pair \(\Gamma=(S,j)\) where
- \(S\subset\mathcal P(\Lambda)\) is a connected (plaquette-adjacent) finite subset of plaquettes of \(\Lambda\);
- \(j:S\to\{1/2,1,3/2,\dots,J\}\) is an irreducible-representation label on each plaquette.

The activity of \(\Gamma\) is
\[
w(\Gamma;\beta)=\prod_{P\in S} t_{j_P}(\beta)\ \cdot\ I_{\rm Haar}(S,j),
\]
where
\[
t_j(\beta)=\frac{I_{2j+1}(\beta)}{I_1(\beta)},
\qquad
a_j(\beta)=\frac{2}{\beta} I_{2j+1}(\beta),\quad t_j=a_j/a_0,
\]
is the renormalized SU(2) character coefficient (Wilson action with \(S=\beta\sum_P(1-\tfrac12\operatorname{tr}U_P)\); the character expansion is \(e^{\beta\,\operatorname{tr}U/2}=\sum_j a_j(\beta)\chi_j(U)\)), and \(I_{\rm Haar}(S,j)\) is the link Haar integral with the assigned characters, evaluated with vertex intertwiner contractions.

### 1.3 Species decomposition

Polymers partition into species \(\{L_s\}\) under translation, rotation, reflection, and conjugation in \(j\). The **lower-order species** is the union
\[
L_{\rm lo}=\{\Gamma=(S,j)\,:\ j_P=1/2\ \forall P\in S\}.
\]
The **two-face subspecies** is
\[
L_{2f}=\{\Gamma=(S,j)\in L_{\rm lo}\,:\
\forall e\subset\Lambda,\ \#\{P\in S\,:\,e\subset\partial P\}\le 2\}.
\]
That is: each lattice edge is shared by at most two active plaquettes — the "two-face continuation" grammar of design doc v6 §2.3 / v7 §2.3.

\(L_{2f}\) is the dangerous species: smallest Haar suppression (\(j=1/2\)) and largest combinatorial degree among the controllable lower-order grammars.

---

## 2. Endpoint admissibility from Haar integration

### 2.1 Dangling-edge vanishing

**Lemma 2.1** (Dangling vanishing).  *Let \(\Gamma=(S,j\equiv1/2)\) be a polymer in \(L_{\rm lo}\) and let \(e\subset\Lambda\) be a lattice edge with \(\#\{P\in S\,:\,e\subset\partial P\}=1\). Then \(I_{\rm Haar}(S,j)=0\).*

**Proof.**  The variable \(U_e\) appears in exactly one of the characters in the Haar integrand. Factoring out:
\[
I_{\rm Haar}(S,j)
=
\int dU_e\ \chi_{1/2}\!\bigl(U_e^{\pm 1}\cdot X(U_{\setminus e})\bigr)\ \cdot\ \bigl[\text{rest}\bigr].
\]
By Peter–Weyl orthogonality,
\[
\int_{SU(2)} dU\ \chi_j(UA)=\delta_{j,0}\cdot\chi_0(A)=\delta_{j,0},
\]
so for \(j=1/2\) the inner factor is zero. \(\square\)

**Corollary 2.2.**  *Surviving polymers in \(L_{\rm lo}\) have every internal edge of multiplicity \(\ge 2\). Combined with the two-face grammar, surviving polymers in \(L_{2f}\) have every internal edge of multiplicity exactly \(2\).*

### 2.2 Vertex parity

**Lemma 2.3** (Vertex parity).  *Let \(\Gamma\in L_{2f}\) survive Lemma 2.1, and let \(v\in\Lambda\) be an interior vertex (i.e., a vertex incident only to edges fully internal to \(S\)). Let \(n_v\) be the number of edges incident to \(v\) that are internal to \(S\). Then \(n_v\) is even.*

**Proof sketch.**  At \(v\), Haar integration over the incident link variables \(U_{e_1},\dots,U_{e_{n_v}}\) reduces to evaluating the SU(2) intertwiner space \(\operatorname{Hom}\bigl(\mathbf 1,(\tfrac12)^{\otimes n_v}\bigr)\). Schur orthogonality forces this space to be nontrivial only when the tensor product contains the trivial representation, which for SU(2) requires \(n_v\) even (Clebsch–Gordan parity). \(\square\)

**Corollary 2.4** (Closure).  *Two-face polymers \(\Gamma\in L_{2f}\) surviving Haar integration are \(\mathbb Z_2\)-closed: the boundary of the active surface \(S\) in the \(\mathbb Z_2\) chain complex restricted to the interior of \(\Lambda\) vanishes.*

### 2.3 Effect on the entropy bound

Corollaries 2.2 and 2.4 restrict \(L_{2f}\) to closed two-face supports. For the present proof we keep the conservative consequence
\[
\Delta_{2f}\le 39
\quad\text{(maximum plaquette-adjacency degree on closed two-face supports in 4D),}
\]
which is the input used by SURFACE_SPECIES_ENTROPY_1 (closed). Any further reduction is the remit of `SURFACE_SPECIES_CONNECTIVE_CONSTANT_1` (P1).

---

## 3. Per-polymer activity bound

### 3.1 Haar contraction bound

**Lemma 3.1** (Haar contraction).  *For any \(\Gamma=(S,j\equiv1/2)\) with \(|S|=n\),*
\[
\bigl|I_{\rm Haar}(S,j)\bigr|\le 1.
\]

**Proof (conservative).**  Factor \(I_{\rm Haar}\) over interior vertices: at each interior vertex \(v\) the contraction \(I_v\) is a projection of \((\tfrac12)^{\otimes n_v}\) onto its trivial-rep subspace, normalized so that \(\|I_v\|_{\rm op}\le 1\). Multiplying across vertices (with link integrals already absorbed in the vertex factorization)
\[
|I_{\rm Haar}(S,j)|\le \prod_v \|I_v\|_{\rm op}\le 1. \qquad\square
\]

**[Conservative bound]** — Lemma 3.1 is the **only** step of the present proof that is not optimal. The vertex projection norms in fact contract by powers of \(1/d_{1/2}=1/2\) at every interior vertex once the closure condition (Cor. 2.4) is exploited. A sharper bound of the form
\[
|I_{\rm Haar}(S,j)|\le 2^{-V_{\rm int}(\Gamma)}
\]
follows from the 6j-orthogonality and isoperimetric arguments and would substantially widen the certified \(\beta\)-window. This sharper bound is deferred to `ADMISSIBLE_SPINFOAM_SURFACE_TOPOLOGY_2` (P1) and is **not** required for the present claim.

### 3.2 Per-plaquette activity (rigorous Bessel ratio bound)

**Lemma 3.2** (Bessel ratio bound).  *For all \(\beta\ge 0\),*
\[
t_{1/2}(\beta)=\frac{I_2(\beta)}{I_1(\beta)}\ \le\ \frac{\beta}{4},
\]
*with strict inequality for \(\beta>0\).*

**Proof.**  The modified Bessel recurrence \(I_{\nu-1}(\beta)-I_{\nu+1}(\beta)=(2\nu/\beta)I_\nu(\beta)\) at \(\nu=2\) gives
\[
I_1(\beta)-I_3(\beta)=\frac{4}{\beta}\,I_2(\beta),
\quad\text{hence}\quad
4 I_2(\beta)=\beta I_1(\beta)-\beta I_3(\beta).
\]
Since \(I_3(\beta)>0\) for \(\beta>0\), we obtain \(4 I_2(\beta)<\beta I_1(\beta)\), i.e. \(t_{1/2}(\beta)<\beta/4\). Equality holds at \(\beta=0\) (both sides vanish). \(\square\)

**Remark.**  The same recurrence at \(\nu=2j+1\) gives the analogous rigorous bound \(t_j(\beta)<(\beta/2)^{2j}/(2j+1)!\) up to a recurrence-controlled correction, which establishes the strong Haar suppression of higher-spin species. The present note uses only Lemma 3.2.

### 3.3 Combined polymer activity

**Theorem 3.3** (Polymer activity bound).  *For any \(\Gamma=(S,j\equiv1/2)\in L_{2f}\) with \(|S|=n\):*
\[
|w(\Gamma;\beta)|\ \le\ \bigl(t_{1/2}(\beta)\bigr)^n\ \le\ \bigl(\beta/4\bigr)^n.
\]

**Proof.**  Combine \(w(\Gamma)=\prod_{P\in S}t_{1/2}(\beta)\cdot I_{\rm Haar}(S,j)\) with Lemma 3.1 and Lemma 3.2. \(\square\)

---

## 4. Species entropy bound (recall)

**Theorem 4.1** (SURFACE_SPECIES_ENTROPY_1, recalled).  *For every root plaquette \(x\in\Lambda\) and every \(n\ge 1\),*
\[
N_{2f}(n;x):=\#\{\Gamma=(S,j\equiv 1/2)\in L_{2f}\,:\,|S|=n,\,x\in S\}\ \le\ (39\,e)^{\,n-1}.
\]

This is the Penrose tree-of-clusters estimate applied to the closed two-face grammar with the degree bound \(\Delta_{2f}\le 39\). Closed and audited under SURFACE_SPECIES_ENTROPY_1.

---

## 5. Main theorem: certified two-face fallback bound

### 5.1 Statement

**Theorem 5.1** (FALLBACK_LOWER_ORDER_ACTIVITY_1).  *Define*
\[
\boxed{\ \beta_*\ :=\ \frac{4}{39\,e}\ \approx\ 0.0377312\ldots\ }
\]
*Then for every \(\beta\in[0,\beta_*)\), every finite \(\Lambda\subset\mathbb Z^4\), every finite Peter–Weyl cutoff \(J\ge 1/2\), and every root plaquette \(x\in\Lambda\):*
\[
\Sigma_{2f}(\beta;x)
:=
\sum_{\substack{\Gamma\in L_{2f}\\ x\in S(\Gamma)}}
\bigl|w(\Gamma;\beta)\bigr|
\ \le\
\frac{\beta/4}{1-39\,e\cdot\beta/4}\ <\ +\infty,
\]
*and the Dobrushin-form polymer screen passes:*
\[
\rho_{2f}(\beta)\ :=\ 39\,e\cdot t_{1/2}(\beta)\ \le\ 39\,e\cdot\frac{\beta}{4}\ <\ 1.
\]

### 5.2 Proof

By Theorem 3.3 and Theorem 4.1,
\[
\Sigma_{2f}(\beta;x)
\le
\sum_{n=1}^\infty N_{2f}(n;x)\bigl(\beta/4\bigr)^n
\le
\sum_{n=1}^\infty (39e)^{n-1}\bigl(\beta/4\bigr)^n
=
\frac{\beta/4}{1-39e\cdot\beta/4},
\]
finite iff \(39e\cdot\beta/4<1\), i.e. \(\beta<\beta_*\). \(\square\)

This closes FALLBACK_LOWER_ORDER_ACTIVITY_1 under the conservative entropy constant \(\kappa_{2f}=39e\) and the conservative Haar contraction bound \(|I_{\rm Haar}|\le 1\).

---

## 6. Interval-arithmetic certification

The threshold and the safety margin are machine-certifiable by direct rational-interval evaluation. With \(e\) enclosed at \(\ge 15\) digits,
\[
e\in[2.718281828459045,\ 2.718281828459046],
\qquad
39e\in[106.0129913099,\ 106.0129913100],
\]
\[
\beta_*=\dfrac{4}{39e}\in[0.0377312247\ldots,\ 0.0377312248\ldots].
\]
For a safety factor \(\rho_{\rm safe}=0.95\), the certified passing window is
\[
\beta\in\bigl[0,\ \rho_{\rm safe}\cdot\beta_*\bigr]\subset[0,\ 0.0358446635\ldots].
\]
The accompanying script `fallback_lower_order_activity_certificate_v1.py` evaluates \(t_{1/2}(\beta)=I_2(\beta)/I_1(\beta)\) using mpmath at 50-digit precision and bounds the truncation error explicitly, emitting the activity table per design doc §9.3:
\[
\texttt{beta,action\_type,species,activity\_q,entropy\_kappa,rho,passes,notes}
\]

### Comparison to SZZ functional-inequality threshold

The Shen–Zhu–Zhu strong-coupling LSI/Poincaré window for SU(N) in \(d=4\) (Track A2 lane) is
\[
|\beta|<\frac{1}{16(d-1)}=\frac{1}{48}\approx 0.02083.
\]
Therefore
\[
\frac{\beta_*(\text{polymer},\,L_{2f})}{\beta_*(\text{SZZ},\,\text{LSI})}
\ \approx\ \frac{0.0377}{0.0208}\ \approx\ 1.81.
\]
The polymer two-face certificate is **wider** than the SZZ functional-inequality window by ≈ 1.81 at the conservative entropy / Haar-contraction bounds. This is consistent with the design-doc framing that the two lanes are independent strong-coupling routes with non-equivalent thresholds. The comparison feeds `SZZ_CALIBRATION_1` (P1, queued).

---

## 7. Gap-notion compatibility (per `GAP_NOTION_BRIDGE_1`)

| Quantity established here | Operator / object | Bridge needed for physical mass gap? |
|---|---|---|
| Two-face polymer activity sum \(\Sigma_{2f}(\beta;x)<\infty\) | vacuum-normalized cluster expansion (\(L_{2f}\) sector) | yes — must combine with all other species (`FULL_FALLBACK_ASSEMBLY_1`) and then convert via OS / transfer arguments (`LATTICE_GAP_FRAGMENT_1`) |

**This proof does not establish:** any transfer-matrix spectral gap, any Langevin spectral gap, any LSI constant, any exponential clustering rate. The cluster-expansion finiteness obtained here is a *necessary* component of all of those, but is *not* sufficient for any of them in isolation.

---

## 8. What is and is not proved (claim-boundary)

### Proved
- For \(\beta<\beta_*=4/(39e)\approx 0.0377\), the two-face lower-order species satisfies the Dobrushin-form cluster screen \(\kappa_{2f}\,q_{2f}(\beta)<1\).
- The single-root activity sum \(\Sigma_{2f}(\beta;x)\) is finite, with the explicit bound \((\beta/4)/(1-39e\cdot\beta/4)\), uniformly in \(\Lambda\), \(J\), and \(x\).
- All inequalities are machine-checkable in rational / mpmath interval arithmetic at any desired precision.

### Not proved (explicitly out of scope of this obligation)
1. **Full fallback assembly.** This note handles only \(L_{2f}\). Combining all surviving species (higher-spin sectors, multi-loop continuations, etc.) is the open obligation `FULL_FALLBACK_ASSEMBLY_1` (P0).
2. **Higher-order species.** \(t_j(\beta)\sim(\beta/2)^{2j}/(2j+1)!\); these are far smaller than \(t_{1/2}\) in the strong-coupling regime but still require their own activity certificate.
3. **Cutoff removal.** Peter–Weyl cutoff \(J\) is held fixed; removal is `CUTOFF_REMOVAL_STRONG_1`.
4. **Lattice mass gap.** Conversion from cluster convergence to an OS/transfer mass-gap statement is `LATTICE_GAP_FRAGMENT_1`, gated by `GAP_NOTION_BRIDGE_1`.
5. **Sharper Haar contraction.** Lemma 3.1 uses \(|I_{\rm Haar}|\le 1\); the closure condition (Cor. 2.4) implies a stronger \(|I_{\rm Haar}|\le 2^{-V_{\rm int}(\Gamma)}\) bound, deferred to `ADMISSIBLE_SPINFOAM_SURFACE_TOPOLOGY_2`.
6. **Sharper species entropy.** \(39e\) is conservative; tightening is `SURFACE_SPECIES_CONNECTIVE_CONSTANT_1`.
7. **No continuum claim.** All constants depend on the lattice spacing through the bare coupling \(\beta\). No \(a\to 0\) statement is made.

### Claim-boundary statement (mandatory)
> *This result is a strong-coupling lattice activity bound at finite Peter–Weyl cutoff. It closes one P0 obligation in the Track A1 polymer lane of project YANG-MILLS4. It does not by itself prove any mass-gap statement and makes no continuum claim.*

---

## 9. Ledger update (proposed)

| obligation_id | status before | status after this note |
|---|---|---|
| `FALLBACK_LOWER_ORDER_ACTIVITY_1` | open, P0 | **proof-note draft closed**, pending Haar-contraction sharpening flag and FULL_FALLBACK_ASSEMBLY_1 integration |
| `SURFACE_SPECIES_ENTROPY_1` | closed | recalled as Thm 4.1 |
| `ADMISSIBLE_SPINFOAM_SURFACE_TOPOLOGY_2` | open, P1 | feeds Lemma 3.1 sharpening; not blocking |
| `SURFACE_SPECIES_CONNECTIVE_CONSTANT_1` | open, P1 | feeds entropy sharpening; not blocking |
| `SZZ_CALIBRATION_1` | queued P1 | comparison table now available (§6) |
| `FULL_FALLBACK_ASSEMBLY_1` | open, P0 | unblocked; this note supplies \(L_{2f}\) input |

Activity table CSV and interval-arithmetic certificate accompany this note.
