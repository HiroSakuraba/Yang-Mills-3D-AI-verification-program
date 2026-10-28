# YM3D strong-coupling KP-domain handoff (2026-10-27)

**Status:** research-only evidence; not a closed program gate or a mass-gap theorem.

A supplied 3D SU(2) Wilson-action research bundle reports a whole-polymer-gas
Kotecký–Preiss bound for beta <= 37/200 (0.185), and separately reports a
closed two-face-surface-gas bound for beta <= 1. The corresponding heat-kernel
endpoints are tau >= 819/100 and tau >= 19/5. Reported exact enumerations
reach F <= 18 for surviving supports and F <= 22 for closed two-face surfaces.

The strongest omitted obligations are **not** just arithmetic: (a) a majorization
from a genuinely RG-produced effective action, including larger-loop terms, into
the single-plaquette KP domain; (b) observables inserted into the expansion to
obtain exponential clustering; and (c) volume- and lattice-spacing-uniform
continuum arguments. The supplied 3D note is not the complete fallback-basin
certification in design section 10.

## Certificate-integrity defect and import barrier

The original archived decision script accepted stored checker reports that
said PASS without verifying which exact generator JSON bytes they checked.
Changing a six-face count while keeping the stale report could still produce
PASS. The remedy is to make both **independent** checkers include the SHA-256
of their exact input JSON, and to reject missing/changed fingerprints, wrong
checker IDs, horizons, statuses, and incompatible aggregate counts.

The dependency-free `tools/verify_kp_bundle.py` preflight checks this
import/evidence boundary for ZIP files or extracted directories. The original
October 27 ZIP intentionally **fails** this preflight because its reports have
no hashes. A corrected source bundle, with regenerated checkers, can pass.
The preflight does not prove the combinatorial or analytic lemmas and does not
replace the interval decision or rerunning the independent checkers.

```sh
python tools/verify_kp_bundle.py path/to/YM3D_STRONG_COUPLING_KP_DOMAIN_1.zip
python -m unittest discover -s tests -p test_kp_bundle_preflight.py
```

## Gate policy

The external full-source research bundle is **not imported by this PR**.
Do not register an executable `program.yaml` gate until the actual generator,
checker, and analysis sources plus correct reproduction artifacts have been
added and the repository's independent-checker harness has been exercised.
When it is registered, use `schema_stage: analytic`,
`claim_strength: fallback_domain_only`, no dependents, and retain the
`ym2d_validation_passed` meta-guard. Do not unlock a continuum or mass-gap
claim.

Next: reproduce and audit the source bundle; test observable insertions; then
bound the overlap of a multi-loop RG effective action with the KP domain.
