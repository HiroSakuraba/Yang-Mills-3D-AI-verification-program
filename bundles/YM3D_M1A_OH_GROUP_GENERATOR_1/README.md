# YM3D_M1A_OH_GROUP_GENERATOR_1

This bundle closes the second executable gate in Milestone A:

\[
\texttt{YM3D\_OH\_SIGNED\_PERMUTATION\_GROUP\_1}.
\]

It generates the full cubic symmetry group \(O_h\) as the set of all \(3\times 3\) signed
permutation matrices over \(\mathbb Z\), and verifies the group laws using exact integer
arithmetic.

## Scope

This bundle proves only the finite group-action seed. It does **not** yet define lattice
links, support lifting, orbit representatives, collision graphs, KP bounds, or analytic
Yang--Mills estimates.

## Mathematical definition

The group is

\[
O_h=\{M\in \mathrm{Mat}_{3\times 3}(\mathbb Z): M^T M=I,\; M e_i=\pm e_j\}.
\]

Equivalently, each matrix is determined by a permutation \(\pi\in S_3\) and signs
\(\sigma_i\in\{\pm 1\}\), with

\[
M_{i,\pi(i)}=\sigma_i.
\]

The checker verifies:

1. exactly 48 unique elements are generated;
2. every element is an integer signed-permutation matrix;
3. every element satisfies \(M^TM=I\);
4. the identity is present;
5. the set is closed under multiplication;
6. every element has an inverse in the generated set;
7. determinant distribution is 24 proper rotations and 24 orientation-reversing elements.

## Files

- `src/ym3d/group_oh.py`: pure-Python exact integer generator.
- `tools/build.py`: runs the generator, writes artifacts.
- `tools/check_oh_group.py`: **independent** checker (re-derives O_h; no generator import).
- `artifacts/oh_group_elements.json`: canonical element export.
- `artifacts/oh_group_report.json`: detailed report.
- `artifacts/decision.json`: pass/fail decision.
- `manifest.json`: SHA-256 manifest.

## Usage

The generator and the checker are separate processes (the checker is
**independent**: it re-derives `O_h` from scratch and never imports the
generator package `ym3d`).

```bash
python tools/build.py            # generator: writes artifacts/oh_group_*.json
python tools/check_oh_group.py   # independent checker: re-derives + audits export
```

Or via the harness from the repo root:

```bash
python orchestrator/run.py gate YM3D_OH_SIGNED_PERMUTATION_GROUP_1
```

Expected result:

```text
PASS: YM3D_OH_SIGNED_PERMUTATION_GROUP_1
```
