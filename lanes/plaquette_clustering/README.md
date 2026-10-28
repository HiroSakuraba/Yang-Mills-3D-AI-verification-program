# Plaquette clustering / finite Wilson-loop correlations (3D SU(2))

**Research lane, not a closed analytic gate.** Conservative, independently derived estimates at fixed lattice spacing and `0 <= beta <= 3/200`, with exact-rational numerical checks. The beta<=0.185 imported strong-coupling domain is intentionally **not** a dependency: its previously imported branched checker still needs a fresh verified report.

## Results proposed for independent analytic review

- **Two distinct plaquettes:** `|Cov(phi_p,phi_q)| < 5373.78 exp[-dist_plaquette(p,q)/10]`, with `phi_p=Tr_F(U_p)/2`. See `THEOREM.md` for the local-coupling derivative, complex-source normalization, Finner activity bound and rooted KP argument.
- **Two fixed finite Wilson loops:** `|Cov(W_C,W_D)| <= (188/11)*len(C)*len(D)*(36/47)**dist_link(C,D)`. The source is the original normalized Wilson action and the link-level Dobrushin–Föllmer covariance theorem; see `WILSON_LOOP_EXTENSION.md`.
- **Perturbative diagnostic:** two different faces of the same cube have a one-cube contribution `beta**4 / 1024` to the mixed local-coupling derivative. This is **not** an exhaustive expansion coefficient unless other diagrams are separately checked.

All distances are graph distances on the **lattice**, not physical distances after taking the continuum limit. Constants are conservative; neither result is competitive with the sharper published small-coupling bounds or a continuum theorem.

## Run

```sh
python tools/certificate.py
python tools/dobrushin.py
python -m unittest discover -s tools -p 'test_*.py' -v
```

`artifacts/certificate.json` and `artifacts/dobrushin.json` contain exact rational bounds. The scripts require only Python 3.11+ standard library. The recorded `pass` applies to arithmetic and geometry; it does not replace independent scrutiny of the invoked analytic theorems.

## Integrity / claim controls

No output from this lane changes `program.yaml` or closes `YM3D_FALLBACK_BASIN_CERTIFICATION_1`, `YM3D_ONE_STEP_RG_RUNG_SCALE_INDEXED_1`, or any other proof gate. There is no claimed continuum clustering or positive physical glueball mass. See `COMPARISON_4D.md` for a scoped cross-project comparison against the latest 4D Wilson-loop fork.
