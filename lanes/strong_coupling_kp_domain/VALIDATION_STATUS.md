# Verification status — source import, October 27/28, 2026

This lane is **research-only**. Source code is now present in PR #10, but a
completed fresh recheck of the full branched exact-Haar coverage is NOT yet
included in the GitHub branch, and no generator JSON or PASS report is treated
as a closed certificate.

Local work on the supplied ZIP:
- The independent two-face checker was rerun at F <= 22: PASS, with the exact
  generator-input SHA-256 added to its report.
- The full branched checker at F <= 18 and n2_cap=6 remained active for 22
  minutes and was terminated without producing a new report. The supplied
  historical PASS report is not equivalent to a new rerun.
- The hardened decision script intentionally fails closed with no current
  branched checker report. A separate temporary analytic dry run with injected
  matching hashes reproduced the KP endpoint result but is **not** accepted
  as independent verification.
- Seven standalone ZIP-import preflight unit tests passed; the CI job checks
  source syntax and these tests.

To complete evidence:
1. Install `pip install -r requirements.txt` in this lane.
2. Generate artifacts with `python tools/build.py`, or use the original
   generator JSON as input to the independent checkers.
3. Execute `python tools/check.py` for the complete two-face + branched rerun
   and analytic endpoint decision; do not lower `n2_cap`.
4. Execute `python tools/test_integrity.py` for the ten negative controls.
5. Inspect the decision JSON and attach exact SHA-256-bound reports.

Keep the `ym2d_validation_passed` meta-guard and do not promote this research
claim into fallback-basin certification, observable clustering, or a mass gap.
