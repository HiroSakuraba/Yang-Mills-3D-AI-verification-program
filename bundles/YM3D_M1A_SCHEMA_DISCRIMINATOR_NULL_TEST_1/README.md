# YM3D Milestone A — Schema Discriminator Null-Test Seed

Bundle: `YM3D_M1A_SCHEMA_DISCRIMINATOR_NULL_TEST_1`

This bundle implements the first executable gate for Milestone A of the 3D Yang--Mills constructive RG program.

## Scope

This bundle checks only the stage-discriminated JSON Schema contract. It does not generate lattice atoms, does not construct the cubic group, and does not make analytic or physical claims.

The gate verifies that a row with

```json
"schema_stage": "combinatorial"
```

accepts only combinatorial/gauge-geometric fields and rejects analytic fields such as:

```json
"primitive_enclosure_ids"
"boundary_surface_multiplier_id"
"determinant_expansion_id"
"ghost_loop_degree"
```

## Run

```bash
python tools/validate_schema_discriminators.py
```

Expected result: all fixtures pass their expected validation outcome. The report is written to:

```text
artifacts/schema_null_test_report.json
```

## Included fixtures

- `valid_combinatorial_atom.json` — must validate.
- `invalid_combinatorial_with_analytic_field.json` — must fail.
- `invalid_missing_required_combinatorial_field.json` — must fail.
- `invalid_bad_schema_stage.json` — must fail.
- `valid_analytic_atom.json` — must validate as a later-stage analytic row.

## Closed gate

If the generated report has

```json
"all_passed": true
```

then the bundle closes:

```text
YM3D_SCHEMA_DISCRIMINATOR_NULL_TEST_1
```

## Non-claims

This bundle does not close Milestone A. It is the first prerequisite before implementing:

1. the signed-permutation representation of `O_h`,
2. oriented link transformations,
3. support lifting,
4. orbit representatives and stabilizers,
5. expanded-graph audits.
