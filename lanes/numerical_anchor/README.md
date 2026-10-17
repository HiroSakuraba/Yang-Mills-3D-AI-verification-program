# Numerical comparison lane

The [scalar-glueball analysis tool](../glueball_spectroscopy/README.md) reads real
correlation matrices, subtracts vacuum means when required, solves a generalized
eigenvalue problem and reports effective masses with optional supplied-bootstrap
uncertainties. It includes open zero-temperature and periodic-cosh references.

All included spectra are constructed test data. No physical gauge configurations
or measured Yang–Mills mass estimates are included. The floating-point analysis
is advisory and cannot close an analytic proof gate or become a proof dependency.
Independent external ensemble comparisons remain future work.

## Spectrum analysis extension

The [extended numerical tool](../glueball_spectrum_analysis/README.md) provides
mode tracking, fixed variational projections, correlated exponential/cosh fits,
explicit covariance cutoffs/shrinkage, matched-bootstrap mass errors and paired
fit-window comparisons. It exports JSON and CSV and includes an excited-state
control demonstrating window dependence. All included examples remain synthetic;
no analytic proof gate is added or closed by these fits.
