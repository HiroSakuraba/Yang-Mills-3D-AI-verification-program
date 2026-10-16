# Scalar glueball observables and spectroscopy

This lane defines five SU(2) spatial-loop operators for **2+1 dimensions** and
supplies a small analysis tool for real correlation matrices. It runs on a CPU;
no GPU or simulation data is needed for the supplied reference cases.

The single new harness result, `YM3D_GLUEBALL_OBSERVABLE_REFERENCE_1`, checks
**spatial geometry and exact rational reference arithmetic only**. It does not
close an analytic gate, bypass the required 2D validation, or become a dependency
of the constructive-RG proof lane.

## What is implemented

- Plaquette, 1×2, 2×2, 1×3 and 2×3 loop definitions with normalized trace Tr/2.
- Eight-element spatial square symmetry group D4. This is different from the
  existing three-dimensional Euclidean cubic group O_h.
- Zero-momentum A1 scalar-candidate projection, vacuum subtraction, and explicit
  per-link oscillation bounds. A1 also contains continuum spins 4,8,...; it does
  not certify spin zero or a single-particle glueball.
- An analytic **derivation for review** for the connected elementary-plaquette
  correlator, including a volume-uniform spatial sum. See
  [the full derivation](SCALAR_CORRELATION_DERIVATION.md).
- A numerical generalized eigenvalue analysis using reference-metric whitening,
  a reported rank cutoff and projected eigenvalue residuals.
- Log effective masses for zero-temperature input and acosh effective masses for
  consecutive periodic-time input. The latter uses a vacuum-dominated cosh ansatz;
  it does not model general finite-temperature transitions.
- Optional uncertainty summaries from user-supplied bootstrap replicas, with
  replica-specific vacuum means, declared block size and resampling unit. Invalid
  replica cells are reported, not silently omitted from error estimates.

No Monte Carlo sampler, physical gauge configurations, automated plateau
acceptance or continuum extrapolation is supplied. The reference spectra are
constructed inputs, not Yang–Mills measurements.

## Run the exact reference gate

From the repository root, with the ordinary harness dependencies installed:

```sh
make up-to GATE=YM3D_GLUEBALL_OBSERVABLE_REFERENCE_1
```

Or regenerate and independently check the files directly:

```sh
python lanes/glueball_spectroscopy/tools/build.py
python lanes/glueball_spectroscopy/tools/check_glueball_reference.py
```

The checker does not import `src/` or NumPy. It reconstructs loop orbits, link
oscillation coefficients, every rational reference matrix, vacuum subtraction,
exact roots of the 2×2 generalized eigenvalue pencils, and the spatial-sum formula
constants. Four deliberately corrupted inputs must be rejected. Its decision's
`non_claims` remain part of the result. Floating-point spectroscopy has separate
numerical self-tests and is not certified by this exact checker.

## Run numerical analysis

Install the additional analysis dependency if needed:

```sh
python -m pip install -r lanes/glueball_spectroscopy/requirements.txt
python lanes/glueball_spectroscopy/tools/analyze.py \
  lanes/glueball_spectroscopy/examples/two_state_zero_temperature.json \
  --output /tmp/glueball-zero-temperature-report.json
python lanes/glueball_spectroscopy/tools/analyze.py \
  lanes/glueball_spectroscopy/examples/two_state_periodic.json \
  --output /tmp/glueball-periodic-report.json
python -m unittest discover -s lanes/glueball_spectroscopy/tests -v
```

Both exact two-state references have transfer eigenvalues 1/2 and 1/4, hence
masses log(2) and log(4) in inverse lattice-time units. The analysis returns
`NUMERICAL_DIAGNOSTIC`, with reference provenance retained. It does not output a
proof-gate decision or claim a measured glueball mass.

## Input conventions

See the example JSON files for a complete payload. Required fields include:

| Field | Meaning |
|---|---|
| `schema_version` | `ym3d.glueball_correlators.v1` |
| `gauge_group`, `spacetime_dimensions` | `SU(2)`, `3` |
| `operator_normalization` | `spatial_sum_div_sqrt_volume` |
| `spatial_volume` | Number of spatial sites, a positive integer |
| `operators`, `times` | Unique operator names; increasing nonnegative integer time indices |
| `correlators` | Real symmetric matrices, one per time; rational strings are allowed |
| `vacuum_subtracted` | Explicit boolean; raw matrices require `operator_means` |
| `operator_means` | Expectations of the normalized operators ΣP/√V, not per-site means |
| `boundary` | `zero_temperature` or `periodic_time` |
| `time_extent` | Required for periodic time; measured time indices must be below it |
| `temporal_spacing`, `time_unit` | Positive time step and its declared unit; no GeV calibration is inferred |

For raw input, the tool computes C_ij(t)=R_ij(t)-mean_i mean_j. For already
connected matrices it does not subtract again. A non-positive reference metric,
nonfinite values, or materially asymmetric matrices are rejected. Near-null
reference directions are removed only through the declared cutoff and reported.
Invalid late-time log/acosh values become JSON nulls with explicit issues.

To attach bootstrap replicas, add:

```json
"bootstrap": {
  "block_size": 8,
  "resampling_unit": "configuration blocks",
  "replicas": [
    {"correlators": "replace with matrix arrays", "operator_means": [2, -1]},
    {"correlators": "replace with matrix arrays", "operator_means": [2, -1]}
  ]
}
```

The placeholders in this fragment illustrate structure, not executable data.
Provide full arrays shaped like the main `correlators`. Each raw replica needs
its own means. The tool rejects changing retained rank and withholds a cell's
uncertainty summary if any supplied replica has an invalid effective mass there.
It cannot validate whether the chosen block size removes sampling autocorrelation.

Eigenmodes are sorted independently at each time. Near-degenerate modes and
crossings need subsequent overlap tracking. Effective-mass plateaus, finite-volume
stability, extra states and thermal contamination remain research checks.

## Next useful extension

Supply actual gauge-field ensembles or validated correlator matrices, add an
operator-overlap tracking and correlated-fit analysis, and test volume and basis
stability. The mathematical next step is review of the comparison hypotheses
and the transfer-space identification, following the repository's analytic
validation prerequisites. An isolated glueball particle requires additional
spectral evidence beyond an exponential upper bound on a correlator.
