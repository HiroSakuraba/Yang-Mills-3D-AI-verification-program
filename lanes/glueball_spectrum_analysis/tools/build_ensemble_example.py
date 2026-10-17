#!/usr/bin/env python3
"""Construct synthetic periodic scalar fields, never SU(2) gauge configurations."""
import argparse
import json
from pathlib import Path
import numpy as np


def example():
    extent = 16
    mass = .45
    sites = np.arange(extent)
    lag = np.abs(sites[:, None] - sites[None, :])
    covariance = (np.exp(-mass * lag) + np.exp(-mass * (extent - lag))) / (1 + np.exp(-mass * extent))
    factor = np.linalg.cholesky(covariance)
    rng = np.random.Generator(np.random.PCG64(812))
    chains = []
    for chain_id in ('synthetic_a', 'synthetic_b'):
        current = factor @ rng.normal(size=extent)
        measurements = []
        for _ in range(136):
            current = .6 * current + .8 * (factor @ rng.normal(size=extent))
            measurements.append((current + 2.)[:, None].tolist())
        chains.append({'chain_id': chain_id, 'configuration_ids': list(range(0, 1360, 10)),
                       'measurements': measurements})
    return {
        'schema_version': 'ym3d.glueball_operator_samples.v1',
        'data_kind': 'synthetic_operator_fixture', 'gauge_group': 'SU(2)',
        'spacetime_dimensions': 3, 'operator_normalization': 'spatial_sum_div_sqrt_volume',
        'spatial_volume': 16, 'time_extent': extent, 'temporal_spacing': 1,
        'time_unit': 'lattice_time', 'operators': ['synthetic_scalar'], 'boundary': 'periodic_time',
        'chains': chains,
        'ensemble_metadata': {'fixture': 'Gaussian periodic scalar fields with configuration AR(1) coefficient 0.6',
                              'underlying_covariance_mass': mass, 'vacuum_offset': 2.,
                              'qualification': 'Synthetic scalar samples only; no SU(2) links or Yang-Mills action.'},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(example(), indent=2, allow_nan=False) + '\n')
    print(f'Wrote synthetic scalar operator fixture {args.output}.')


if __name__ == '__main__':
    main()
