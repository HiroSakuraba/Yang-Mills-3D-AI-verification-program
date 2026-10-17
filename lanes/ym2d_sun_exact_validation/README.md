# Exact two-dimensional Wilson reference — initial SU(2) implementation

This lane now contains a runnable **SU(2), open-boundary reference benchmark**.
It independently checks exact rational enclosures of normalized fundamental and
adjoint Wilson-loop expectations. It uses only the Python standard library.

The broader `YM2D_SUN_EXACT_VALIDATION_LANE_0` milestone remains **BLOCKED**.
Its support-lift, orbit and expanded-collision-graph prerequisites are not yet
implemented, and this initial reference does not yet consume their exports.
No analytic 3D permission or waiver is introduced. General SU(N) and periodic
surfaces are outside this reference implementation.

## Run the reference audit

From the repository root:

```sh
python lanes/ym2d_sun_exact_validation/tools/build.py
python lanes/ym2d_sun_exact_validation/tools/check_ym2d_exact.py --report-only
python -m unittest discover -s lanes/ym2d_sun_exact_validation/tests -v
```

The first command exports `artifacts/reference.json`. The second writes
`artifacts/benchmark_report.json` and emits no `decision.json`. The report has
`program_gate_closed: false`, even when the standalone audit passes.

The default checker invocation also evaluates prerequisite readiness and writes
an explicitly BLOCKED program decision. It cannot close the full milestone in
this initial implementation, including if a state file names closed parents:
integration with the shared geometry pipeline is still missing. The scheduler
does not invoke it until its existing dependencies are satisfied. This prevents
an isolated numerical/reference agreement from authorizing analytic 3D work.

## What is checked

- A 4-by-3 open plaquette grid and its 19-edge comb spanning tree.
- All 60 rectangles, at all available positions, with both traversal signs:
  120 ordered boundaries. Axial-gauge words retain noncommutative order.
- Every interior plaquette occurs once; exterior words cancel after interior
  integration, including loops translated away from the gauge-tree boundary.
- Exact SU(2) Haar moments for normalized characters 1, Tr/2 and the adjoint
  character divided by 3, independently of the generator's factorial series.
- Couplings beta=0, 1/2, 2, 4 with action exp[beta sum_p Tr(U_p)/2].
- Twelve one-plaquette cases and 64 area-law cases (88 rational intervals),
  with positive-series tails bounded explicitly and outward dyadic rounding.
- Each reported interval has absolute width at most 2^(-80). No float, SciPy,
  numerical quadrature or uninstalled interval backend participates in the audit.

The exact expectations generally are irrational; the artifacts contain rigorous
rational enclosures, not claims that decimal approximations are exact values.
The checker uses Catalan Haar moments and normalized-character polynomials; it
does not import the generator or re-run its package. See
[DERIVATION.md](DERIVATION.md) for the measure reduction, normalization, area-law
argument, error bounds and primary source.

Seven regression tests include twelve deliberate artifact corruptions. They
exercise trace normalization, representation normalization, ordered words,
rectangle area/completeness, spanning tree, boundary convention and precision.

## What is still required for full pipeline validation

1. Complete the existing directed-link, support-lift, orbit, orbit-closure and
   expanded-graph prerequisites in `program.yaml`.
2. Route the 2D geometry/observable export through the shared machinery and
   independently compare it against this reference without importing generators.
3. Define whether the full milestone accepts an initial SU(2) specialization or
   requires additional SU(N) groups; do not silently broaden this benchmark.
4. Audit the corresponding gauge/observable metadata and negative controls, then
   close the milestone through the harness once those obligations actually pass.

This reference makes no statement about a 3D physical gap, an isolated glueball,
renormalization contraction, continuum limit or general reflection-positivity
transfer. The compact-group integration facts are derived in the note and used
by the arithmetic checker; they are not formalized in a proof assistant.
