# From sampled operators to spectrum fits

`tools/prepare_ensemble.py` prepares the correlator input consumed by
`tools/analyze.py`. Supply the scalar, zero-spatial-momentum operator value on
every Euclidean time slice of each saved configuration. Gauge-link generation,
loop measurement and checking that measurements originate in SU(2) gauge fields
remain the responsibility of the simulation producing the input.

This release accepts real 2+1-dimensional SU(2) metadata with **periodic time**.
The converter does not reweight ensembles or infer physical units.

## Run the complete synthetic example

From the repository root, after installing the lane's requirements:

```sh
python lanes/glueball_spectrum_analysis/tools/build_ensemble_example.py \
  --output /tmp/operator-samples.json
python lanes/glueball_spectrum_analysis/tools/prepare_ensemble.py \
  /tmp/operator-samples.json --output /tmp/operator-correlators.json \
  --block-size 8 --discard-per-chain 8 --replicas 64 --seed 29
python lanes/glueball_spectrum_analysis/tools/analyze.py \
  /tmp/operator-correlators.json --output /tmp/operator-spectrum.json \
  --csv /tmp/operator-fits.csv --window 1:4 --window 2:5
```

The fixture contains two configuration chains of Gaussian scalar fields, with
periodic Euclidean covariance of mass 0.45 and a vacuum offset of 2.0. Successive
configurations have an autoregressive coefficient of 0.6. These are constructed
scalar measurements, **not simulated Yang–Mills configurations**. SU(2) metadata
is present only to exercise the existing input interface.

The explicit discard leaves 256 configurations in 32 blocks. With NumPy 2.3.5,
the two mass fits are about 0.43165 and 0.42502, with bootstrap standard errors
0.03858 and 0.05267 respectively. These finite-sample results need not equal the
underlying covariance mass exactly. They establish that the preparation and
analysis interfaces work together; they are not a coverage study or a block-size
recommendation. Reports still select no plateau automatically.

## Input contract

The input is a JSON object with these fields:

| Field | Required value or meaning |
|---|---|
| `schema_version` | `ym3d.glueball_operator_samples.v1` |
| `data_kind` | `sampled_ensemble` or `synthetic_operator_fixture` |
| `gauge_group` / `spacetime_dimensions` | `SU(2)` / `3` |
| `operator_normalization` | `spatial_sum_div_sqrt_volume` |
| `spatial_volume` | Positive integer number of spatial sites |
| `time_extent` | Integer Euclidean time extent, at least 6 |
| `temporal_spacing` / `time_unit` | Positive finite time spacing and nonempty unit string |
| `operators` | Ordered unique operator names |
| `boundary` | `periodic_time` |
| `chains` | Nonempty list of chain objects described below |
| `ensemble_metadata` | Optional JSON metadata retained verbatim, e.g. action, coupling, lattice geometry and measurement-code revision |

Each chain contains:

| Field | Meaning |
|---|---|
| `chain_id` | Unique nonempty string |
| `configuration_ids` | Strictly increasing nonnegative integer trajectory/configuration IDs at uniform spacing |
| `measurements` | Finite real array with axes `[configuration][Euclidean_time][operator]` |

All chains must have the same configuration-ID spacing, recorded in the output.
A gap or a change in sampling stride must be handled explicitly; split gaps into
separate chain segments and preserve their provenance. The statistical procedure
assumes independent stationary chains sampling the same distribution. Merely
splitting one dependent run into segments does not establish their independence.

Inputs must **already** be spatial sums divided by the square root of spatial
volume. They must include their vacuum offsets; do not center each configuration
or each block separately. No normalization is inferred from array dimensions.
IDs are scoped to their chain and may repeat across different chains.

## Correlator estimator

Let Q[c,t,i] be operator i at Euclidean time t on configuration c after the
explicit initial discard. For N retained configurations and time extent T:

```text
mu[i] = sum_c,t Q[c,t,i] / (N T)
R[lag,i,j] = sum_c,t (Q[c,t,i] Q[c,t+lag,j]
                    + Q[c,t,j] Q[c,t+lag,i]) / (2 N T)
C[lag,i,j] = R[lag,i,j] - mu[i] mu[j]
```

Time indices in the products wrap modulo T. All periodic time origins are
averaged, and operator-index symmetrization is explicit. Chains of different
lengths retain equal weight per configuration. Output stores R and mu with
`vacuum_subtracted: false`; the spectrum analyzer performs the subtraction.
The plug-in mean product has finite-sample bias; no unbiased correction is
claimed for correlated input samples.

The converter retains consecutive lags 0 through `--max-lag`, defaulting to
floor(T/2); the chosen maximum must be between 3 and floor(T/2). It avoids
duplicating the backward half of the periodic correlator. The analyzer fits
the forward/backward cosh model with the declared full time extent.

## Resampling and diagnostics

`--block-size` is required. After `--discard-per-chain` (also required, including
an explicit zero), every chain must contain at least two complete blocks and its
retained length must be divisible by block size. An incomplete tail is rejected,
never silently discarded or wrapped into another chain. The same initial discard
count applies to each chain; prepare data explicitly if chains need different
thermalization cuts.

The implementation uses a **stratified nonoverlapping-block bootstrap**. It draws
the original number of blocks with replacement separately within each chain,
retaining each chain's sample count and all operators/time lags together. Blocks
never cross chain boundaries. This is not a moving-block or circular bootstrap.
Every replica reconstructs both raw correlator products and operator means from
its selected blocks. The downstream analyzer then subtracts that replica's own
vacuum mean product and refits its variational basis.

`--replicas` defaults to 200 and must be at least two. More replicas do not add
independent configurations or rescue too few blocks. Use explicit `--seed` for
reproducibility. Output records PCG64, the seed, NumPy version, retained and
discarded IDs, block membership and every replica's block indices (indexed from
zero in input-chain order). The CLI hashes the original input bytes. These
preparation records are carried into the final spectrum report, which also
hashes the prepared correlator file. Output size grows with replica count and
number of blocks; measurement arrays are not duplicated in the report.

Per-chain monitors are each operator's time average and its raw equal-time
square averaged over time. For each monitor, diagnostics provide the mean,
within-chain variance, saved-configuration-lag autocorrelations, and adjacent
block correlation. `--diagnostic-max-lag` defaults to 16. Correlations use the
within-chain centered series, pair-count-normalized covariance at each lag,
divided by the lag-zero variance. Block correlations use the same convention
on block means. Constant monitors have null correlation values and are listed
explicitly. These descriptive estimates can be noisy and are not clipped.

**No integrated autocorrelation time, effective sample size, equilibration test
or automatic block length is inferred.** Monitors can miss slow modes relevant
to fitted masses. Compare block lengths and thermalization cuts, review chain
consistency, and assess dependence for the observables of interest before
interpreting fit errors. The tool does not certify these choices.

## Validation and references

Eleven additional numerical regression tests cover direct time-origin sums,
unequal-chain weighting, replayed replica draws and vacuum means, constant-offset
cancellation, time translation and backward-lag symmetry, explicit discards,
seed reproducibility, malformed chains, dependence diagnostics, the complete
samples-to-fit workflow, input hashing and overwrite protection. Run all 27 lane
tests with the command in the [main README](README.md#validation).

Relevant primary sources:

- Künsch, *The Jackknife and the Bootstrap for General Stationary Observations*
  (1989), https://doi.org/10.1214/aos/1176347265. Foundational dependent-data
  resampling reference; this implementation uses the explicitly described
  nonoverlapping variant and does not claim that paper validates a particular
  finite block choice here.
- Wolff, *Monte Carlo errors with less errors* (2004; revised version includes
  erratum), https://arxiv.org/abs/hep-lat/0306017. Discusses observable-dependent
  autocorrelation/error assessment and independent runs. The full method is not
  implemented by the descriptive monitor diagnostics here.
