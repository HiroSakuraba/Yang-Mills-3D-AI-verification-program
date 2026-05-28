# Contributing

This repository advances a proof program **gate by gate**. Please read
`AGENTS.md` — it is the operating contract for humans and coding agents alike.

## Ground rules

1. **One gate per change.** A pull request closes (or builds toward) exactly one
   gate in `program.yaml`.
2. **Independent checkers.** A checker must re-derive its invariant; it must not
   import the generator it audits. The harness lints for this.
3. **Exact arithmetic.** No floating-point comparisons in a gate decision. Use
   `int`, `fractions.Fraction`, or a pinned interval backend.
4. **Never weaken a checker to make it pass.** If a closed result is wrong, open
   a new versioned gate (`..._2`) and supersede the old one in `program.yaml`.
5. **Respect the claim ratchet.** `make claims` must pass; do not assert a
   result whose gate is not closed.
6. **Reproducibility.** `make verify` must reproduce every closed gate from a
   clean checkout. Regenerate manifests with
   `python orchestrator/make_manifest.py <bundle>`.

## Local check before opening a PR

```bash
make setup
make all        # or: make up-to GATE=<the gate you touched>
make claims
make verify
```

By contributing you agree your contributions are licensed under the MIT License.
