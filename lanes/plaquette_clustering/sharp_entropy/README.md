# Entropy-witness extension: explicit β≤0.09 plaquette clustering

The **proposed** refinement of the baseline 3D SU(2) two-plaquette clustering estimate extends the fixed-lattice coupling range from `0 <= beta <= 0.015` to `0 <= beta <= 0.09` using an independently checkable branching-potential majorant. The decay rate remains `exp(-d_plaquette/10)`, and the new conservative prefactor is `<11153`.

- `SHARP_ENTROPY.md`: mathematical derivation, hypotheses, source-insertion argument, and independent-review obligations.
- `tools/entropy_certificate.py`: exact-rational entropy witness, complex normalization, size-weighted KP inequality, and explicit numerical constants.
- `tools/test_entropy_certificate.py`: 14 positive and negative tests including tampered witness, invalid SU(2) Haar-moment bound, invalid exponential bound, over-range beta/source disks.
- `artifacts/entropy_certificate.json`: machine-generated exact rational numbers.
- `REVIEW_AND_4D_BRIDGE.md`: separation of the fixed-lattice 3D argument from the 4D dressed-loop and cutoff-comparison problem.

Reproduce:

```sh
python lanes/plaquette_clustering/sharp_entropy/tools/entropy_certificate.py
python -m unittest discover -s lanes/plaquette_clustering/sharp_entropy/tools -p 'test_*.py' -v
```

The scripts check arithmetic **only**; they do not formally prove the combinatorial recurrence or KP rooted-cluster theorem. Do not promote this research lane to a closed gate solely on the basis of its test run. It **does not** extend the separate long Wilson-loop Dobrushin result beyond its original beta ≤0.015 range.
