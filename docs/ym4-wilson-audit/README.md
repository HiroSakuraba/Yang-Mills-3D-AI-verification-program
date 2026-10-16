> Repository scope: this directory is a four-dimensional comparison research
> archive, separate from the 3D proof program. Its scripts are consistency checks
> and do not satisfy the repository's independent-checker contract or close any
> gate in `program.yaml`. Results here are not 3D proof dependencies.

# YM4 coefficient-audit bundle

Open `YM4-Coherence-Map.html` for the updated map. It includes a new audit section and revised proof-status language. The unedited attachment is retained as `original-map.html`.

Start with `Original-proof-audit-and-Wilson-baseline.md` for the recovered-source audit, exact cube counterexample, normalization repair and independent conservative Wilson uniqueness/clustering theorem.

Read `Wilson-comparison-and-gap-lemma.md` for definitions, proofs of the coefficient and tail bounds, the conditional spectral-gap lemma, and remaining obligations.

Run with Python 3.10 or newer; no packages or network access required:

```sh
python3 frontier_certificate.py --output results.json
python3 independent_wilson_check.py
python3 -m unittest discover -p 'test_*.py' -v
```

The script writes exact outward enclosures for the stated infinite activity sums. It verifies opposite sides of the Wilson crossing at 0.6273001 and 0.6273002. All eleven consistency tests passed in this run. Results are included so the HTML can be read on a phone without running anything.

The code certifies arithmetic for the explicitly defined admissibility grammar, including infinite tails. It does not certify the original polymer counting argument, a full Wilson clustering theorem, the intermediate renormalization flow, or a continuum Yang–Mills mass gap. Related earlier proof notes and later audits were recovered. The exact full-fragment proofs cited in the map remain unlocated. The new Dobrushin baseline applies directly to the physical Wilson measure; it is a conservative application of a standard theorem and does not identify the larger coefficient frontier with a physical gap.

`source-check.json` records hashes of the public draft snapshots inspected and the literal search terms used. The large source files are not included; their public URLs are recorded. This was a targeted source check, not an audit of all 26 MB of companion TeX.

`evidence/` preserves the inspected early proof note and three normalization-audit notes. `followup-source-check.json` records archive hashes and the primary comparison-paper snapshot.
