# YM3D_STRONG_COUPLING_KP_DOMAIN_1

The strong-coupling polymer gas of 3D SU(2) lattice gauge theory, built exactly
and bounded with proofs: the three-dimensional version of
TWO_FACE_EXACT_SURFACES_1 and BRANCHED_SUPPORTS_EXACT_1. It defines, with
certified constants, the convergence domain that the design's fallback-basin
row (§10) asks for, for single-plaquette actions.

Start with `YM3D_STRONG_COUPLING_KP_DOMAIN_1.md`.

## Status

Registered as a research-only analytic gate in `program.yaml`, with no
dependents and with `ym2d_validation_passed` as a required meta-guard. It is
**BLOCKED** until that independent 2D validation lane closes or a documented
waiver exists; this code import does not close any physical or continuum claim.

## Layout (suggested place in the repo: `lanes/strong_coupling_kp_domain/`)

| Path | Role |
|---|---|
| `generator/two_face_surfaces.py` | Closed two-face surfaces in Z^3 through a root plaquette; exact Haar weights |
| `generator/supports.py` | Decision encoding of every surviving support (each exactly once) |
| `generator/haar.py` | Exact Haar integrals (Wick link tensors, symmetriser for spin 1, multi-modular exact contraction) |
| `generator/branched_supports.py` | Branched supports, sheets, labellings, exact weights, Theorem C data |
| `checker/check_two_face.py` | Independent: opposite branching rule, Weingarten contraction, loop formula |
| `checker/check_branched.py` | Independent: own enumeration (opposite rule), Weingarten weights, Lemma G, Theorem C |
| `analysis/entropy.py` | Counting constants in Z^3 (potential method), interval-certified |
| `analysis/kp_3d.py` | Kotecký–Preiss bound for the whole gas and the two-face gas, interval arithmetic, rigorous Bessel enclosures |
| `tools/decide.py` | Requires both checker PASS reports, re-certifies the constants, certifies KP at rational endpoints, writes `artifacts/decision.json` |
| `artifacts/` | Generator outputs, checker reports, KP scan, decision |

The checkers were copied from the 4D bundles with the dimension set to 3, so the
`id` field inside their reports still reads `TWO_FACE_EXACT_SURFACES_1` /
`BRANCHED_SUPPORTS_EXACT_1`; the report files are named for this lane.

Requirements: Python 3.10+, `pip install -r requirements.txt` (numpy, opt_einsum, mpmath). Gate acceptance uses interval endpoint comparisons; rounded floating-point
values in decision.json are diagnostics only.

## Reproduce

    python3 tools/build.py         # full generator runs, may be expensive
    python3 tools/check.py         # independently rerun checkers and decision
    python3 tools/test_integrity.py

Alternatively, run each stage separately:

    python3 generator/two_face_surfaces.py --fmax 22 --output artifacts/two_face_f22.json      # ~1 min
    python3 checker/check_two_face.py --fmax 22 --generator-json artifacts/two_face_f22.json --output artifacts/check_two_face_f22.json
    python3 generator/branched_supports.py --fmax 18 --output artifacts/branched_f18.json      # ~10 min
    python3 checker/check_branched.py --fmax 18 --generator-json artifacts/branched_f18.json --output artifacts/check_branched_f18.json
    python3 analysis/entropy.py > artifacts/entropy_3d.json
    python3 analysis/kp_3d.py artifacts/two_face_f22.json artifacts/branched_f18.json > artifacts/kp_scan.json
    python3 tools/decide.py
    python3 tools/test_integrity.py

## Evidence binding and conservative claims

The independent checker reports now include `generator_sha256` for the precise
input JSON bytes they audited. `tools/decide.py` refuses PASS if either checksum
is absent or differs, if the reported horizon/status is incorrect, or if the
checked counts/weights/profiles do not agree with the JSON. Entropy threshold
comparisons are evaluated with mpmath interval endpoints rather than rounded
float diagnostics. A failed decision overwrites an existing stale PASS artifact
with a FAIL report. Negative controls are in `tools/test_integrity.py`.

This is an *artifact consistency* guard, not a proof that the enumerators or
inequalities are correct, nor protection against malicious replacement of both
code and reports. Rerun the independent checkers after changing any generator
output. The branched checker recomputes exact weights only through its declared
spin-1-face cap; the unverified upper-spin sector remains covered by Finner's
bound. This lane proves no observable clustering, RG-action overlap, mass gap,
or continuum-uniform statement. Until the 2D validation meta-guard is satisfied,
it should be registered as a nonblocking research lane only.
