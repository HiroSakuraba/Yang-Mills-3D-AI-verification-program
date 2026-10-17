# Glueball spectrum analysis — numerical extension

This tool extends the original scalar-loop analysis with **mode tracking,
fixed-basis correlated mass fits, and fit-window diagnostics**. It consumes the
same `ym3d.glueball_correlators.v1` real-matrix format. Input definitions and
normalization are documented in the [original lane](../glueball_spectroscopy/README.md).

For per-configuration operator measurements, use the new
[ensemble preparation workflow](ENSEMBLES.md). It constructs periodic
correlators and chain-aware block-bootstrap replicas, retaining sample IDs,
vacuum means, dependence diagnostics and provenance through the final report.

This is a separate numerical comparison module. The code and artifacts belonging
to the CLOSED `YM3D_GLUEBALL_OBSERVABLE_REFERENCE_1` result remain unchanged.
There is no new proof gate, analytic waiver, measured Yang–Mills mass or continuum
claim. The supplied data are explicitly constructed test spectra.

## Quick start

From the repository root:

```sh
python -m pip install -r lanes/glueball_spectrum_analysis/requirements.txt
python lanes/glueball_spectrum_analysis/tools/analyze.py \
  lanes/glueball_spectrum_analysis/examples/two_state_zero_temperature.json \
  --output /tmp/glueball-fits.json --csv /tmp/glueball-fits.csv \
  --t0 0 --reference-time 1 --window 1:5 --window 2:6
```

The two masses should be approximately **0.69314718** and **1.38629436**, in
inverse lattice-time units. These are log(2) and log(4) from the constructed
reference spectrum. The JSON records the input SHA-256 and NumPy/SciPy versions.

For periodic time:

```sh
python lanes/glueball_spectrum_analysis/tools/analyze.py \
  lanes/glueball_spectrum_analysis/examples/two_state_periodic.json \
  --output /tmp/glueball-periodic-fits.json --window 2:7
```

The periodic model includes forward and backward propagation through a cosh form.
It assumes vacuum dominance; general finite-temperature transition terms remain
outside the model.

To demonstrate an unstable fit window:

```sh
python lanes/glueball_spectrum_analysis/tools/analyze.py \
  lanes/glueball_spectrum_analysis/examples/excited_state_control.json \
  --output /tmp/glueball-window-control.json --csv /tmp/glueball-window-control.csv \
  --window 1:4 --window 4:8
```

This one-operator input contains states of mass 0.4 and 1.4. A single-state fit
should show `POOR_SINGLE_STATE_FIT` and the paired-bootstrap comparison should
flag `WINDOW_DEPENDENCE`. Its bootstrap perturbations and covariance are synthetic,
not sampled lattice configurations.

## How the basis and tracking work

1. Subtract the vacuum mean outer product when the input is raw. Each bootstrap
   replica must supply its own means in that case.
2. Diagonalize C(t0), report its retained rank, and whiten using an explicit
   relative eigenvalue cutoff.
3. Solve the generalized eigenvalue problem at `reference_time > t0`. The modes
   are initially labeled in decreasing eigenvalue order there.
4. Track generalized-eigenvalue modes forward and backward in time by maximum
   total squared-overlap assignment. Align signs and record the permutation and
   overlap score at every time. The exactly degenerate t0 identity frame is exempt
   from tracking. Near-degenerate reference/other frames are explicitly flagged.
5. **Freeze the reference-time variational vectors for mass fits.** Fit the
   projected curves v_i^T C(t) v_i, rather than fitting a sequence of differently
   optimized eigenvectors. Tracked principal correlators remain available as a
   separate diagnostic.

For bootstrap replicas, the reference-time basis is refitted, aligned against the
central basis using the central C(t0) metric, then frozen over time. A changed
retained rank or ambiguous bootstrap alignment rejects the uncertainty analysis.
Vector overlap is a numerical label; it does not prove a physical state identity
at a genuine degeneracy or crossing.

## Correlated fits

Each requested window fits amplitude and mass in either

- zero temperature: A exp[-m a_t (t-t_start)]; or
- periodic time: the corresponding normalized forward/backward exponential sum.

The amplitude is solved analytically for each trial mass. Mass minimization uses
an explicit finite range, a 65-point coarse scan and bounded local refinement.
The result is a numerical fit, not a certified global optimum. The default mass
range is 10^-6 to 5 in the declared inverse time unit; change it with `--mass-min`
and `--mass-max`. Fits reaching a search bound are flagged.

There are three covariance modes:

| Available input | Fit weights and qualifications |
|---|---|
| `projected_covariances` | User-supplied covariance **of the mean/estimator**, in the fixed reference-mode basis |
| Bootstrap replicas only | Covariance of the replica projected-curve estimates, **without dividing by replica count** |
| Neither | Identity-weight descriptive fit; statistical errors and p-values are withheld |

For explicit covariance, add these fields:

```json
"covariance_basis": "fixed_reference_modes",
"covariance_kind": "covariance_of_mean",
"projected_covariances": "replace with [retained_mode][time][time] arrays"
```

The covariance includes correlations between times for each mode. This release
fits modes individually; it does not fit a cross-mode covariance block. If both
explicit covariance and replicas are supplied, the explicit covariance determines
weights and replica fits determine bootstrap errors.

`--covariance-cutoff` controls the retained covariance eigenspace.
`--shrinkage DELTA` optionally mixes the covariance with its diagonal. Rank loss,
conditioning and shrinkage are all reported. Degrees of freedom are the retained
covariance rank minus the two fit parameters. P-values from estimated or
regularized covariance are diagnostic and do not establish fit validity.

The report gives linearized mass errors when identifiable and bootstrap standard
errors/16–84 percentiles when replicas are available. Replica fit weights are kept
fixed. Failed or search-bound-censored replicas are retained as explicit failures;
**any such failure withholds that fit's bootstrap uncertainty summary**.

## Window sensitivity

Repeat `--window START:STOP` for explicit inclusive windows, or use
`--scan-min-points N` for all contiguous available windows with at least N points
at/after the reference time. At most 128 windows are allowed per run. `--state I`
selects retained reference-mode indices; repeated uses select several modes.

The report gives the mass span across windows. When matched bootstrap fit samples
exist, it computes the standard error of their **paired mass differences**, which
retains correlations between overlapping windows. Shifts exceeding two such
standard errors are flagged as a diagnostic. Multiple-window comparisons and
selection biases remain uncorrected.

Every report has `selected_window: null` and
`plateau_status: NOT_AUTOMATICALLY_SELECTED`. A fit marked `CANDIDATE_FOR_REVIEW`
still requires review of excited-state contamination, operator basis, covariance,
volume and lattice spacing. A low chi-square alone cannot identify a glueball pole.

## Output

JSON includes tracked principal correlators, overlap scores, permutations, fixed
projection vectors/curves, effective masses, fit results, uncertainty summaries
and paired-window comparisons. CSV provides a compact fit table. JSON rejects
nonfinite numbers, and output paths may not overwrite the input data.

Input remains restricted to the current lane's **2+1-dimensional SU(2), real
symmetric matrices** and its declared spatial-volume/time-unit conventions.
General complex channels, multi-state fits, gauge-ensemble generation and continuum
extrapolation are future work.

## Validation

```sh
python -m unittest discover -s lanes/glueball_spectrum_analysis/tests -v
python lanes/glueball_spectrum_analysis/tools/build_examples.py
```

Twenty-seven numerical regression tests cover sign/permutation matching, eigenvalue
crossings, degeneracy flags, fixed-basis invariance, log/cosh references, off-diagonal
covariance, covariance rank and shrinkage, missing uncertainty information,
bound-censored fits, raw replica means, bootstrap covariance normalization,
bootstrap rank changes and paired-window sensitivity to excited-state contamination.
The eleven ensemble-preparation checks additionally cover direct estimator sums,
chain weighting, replica replay, vacuum-offset cancellation, time-translation
symmetry, sample discards, input validation, seed replay, monitor diagnostics,
the samples-to-spectrum pipeline and CLI provenance/input protection.
They are numerical self-tests, not independent exact proof checkers.

## Primary references

- Blossier et al., generalized eigenvalue methods and excited-state contamination:
  https://arxiv.org/abs/0902.1265.
- Athenodorou and Teper, glueball operator and spectral practice in 2+1 dimensions:
  https://arxiv.org/abs/1609.03873.
- SciPy maximum-weight assignment:
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html.
- SciPy bounded scalar minimization and its local-optimization limits:
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html.
