# Canonical JSON Schemas

Single source of truth for ledger-row structure (JSON Schema Draft 2020-12).
The discriminator null-test gate validates `atom.schema.json` against the
fixtures in `bundles/YM3D_M1A_SCHEMA_DISCRIMINATOR_NULL_TEST_1/tests/`.

`atom.schema.json` discriminates by `if/then/else` on `schema_stage`
(`combinatorial`, `gauge_geometric`, `analytic`). Combinatorial and
gauge-geometric branches set `additionalProperties: false` and therefore
**forbid** analytic certificate fields by omission, not by nullability.
