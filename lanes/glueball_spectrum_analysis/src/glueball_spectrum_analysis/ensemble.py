"""Prepare real periodic operator measurements; numerical diagnostics only."""
import numpy as np
from glueball_spectroscopy.spectrum import number, real_array


def configuration_correlators(samples, max_lag):
    """Average every periodic time origin, then symmetrize operator indices.

    samples axes: configuration, Euclidean time, operator. No centering here:
    the ensemble mean outer product is subtracted downstream, also in replicas.
    """
    products = []
    for lag in range(max_lag + 1):
        shifted = np.roll(samples, -lag, axis=1)
        matrix = np.einsum('cti,ctj->cij', samples, shifted) / samples.shape[1]
        products.append((matrix + matrix.swapaxes(1, 2)) / 2)
    return np.stack(products, axis=1)


def chain_diagnostics(values, block_size, max_lag):
    """Descriptive within-chain autocorrelation; no automatic correlation time."""
    values = np.asarray(values)
    centered = values - values.mean(axis=0)
    variance = np.mean(centered ** 2, axis=0)
    rho = []
    for lag in range(1, min(max_lag, len(values) - 1) + 1):
        cov = np.mean(centered[:-lag] * centered[lag:], axis=0)
        rho.append([float(cov[i] / variance[i]) if variance[i] > 0 else None
                    for i in range(values.shape[1])])
    blocks = values.reshape(-1, block_size, values.shape[1]).mean(axis=1)
    block_centered = blocks - blocks.mean(axis=0)
    block_var = np.mean(block_centered ** 2, axis=0)
    adjacent = np.mean(block_centered[:-1] * block_centered[1:], axis=0)
    return {
        'mean': values.mean(axis=0).tolist(),
        'within_chain_variance': variance.tolist(),
        'autocorrelation_lags_in_saved_configurations': list(range(1, len(rho) + 1)),
        'autocorrelation': rho,
        'adjacent_block_correlation': [float(adjacent[i] / block_var[i])
                                       if block_var[i] > 0 else None
                                       for i in range(values.shape[1])],
        'constant_monitors': np.flatnonzero(variance == 0).tolist(),
    }


def prepare_ensemble(data, block_size, replica_count=200, seed=0,
                     discard_per_chain=0, max_lag=None, diagnostic_max_lag=16):
    """Stratified nonoverlapping-block bootstrap, never joining chains.

    Configuration IDs must have the same positive spacing in every chain.
    Complete equal blocks are required; no tail is dropped or wrapped.
    """
    if not isinstance(data, dict) or data.get('schema_version') != 'ym3d.glueball_operator_samples.v1':
        raise ValueError('Unsupported operator-sample schema.')
    if data.get('gauge_group') != 'SU(2)' or data.get('spacetime_dimensions') != 3:
        raise ValueError('Only 2+1-dimensional SU(2) samples are supported.')
    if data.get('boundary') != 'periodic_time':
        raise ValueError('Preparation currently requires periodic time.')
    if data.get('operator_normalization') != 'spatial_sum_div_sqrt_volume':
        raise ValueError('Measurements must already use spatial_sum_div_sqrt_volume normalization.')
    volume = data.get('spatial_volume')
    extent = data.get('time_extent')
    if type(volume) is not int or volume < 1 or type(extent) is not int or extent < 6:
        raise ValueError('Positive spatial_volume and integer time_extent >= 6 are required.')
    spacing = number(data.get('temporal_spacing'))
    if spacing <= 0 or not isinstance(data.get('time_unit'), str) or not data['time_unit'].strip():
        raise ValueError('Declare positive temporal_spacing and a time_unit.')
    names = data.get('operators')
    if not isinstance(names, list) or not names or any(not isinstance(v, str) or not v.strip() for v in names) or len(set(names)) != len(names):
        raise ValueError('Supply unique nonempty operator names.')
    if data.get('data_kind') not in ('sampled_ensemble', 'synthetic_operator_fixture'):
        raise ValueError('Declare data_kind sampled_ensemble or synthetic_operator_fixture.')
    for value, label, minimum in ((block_size, 'block_size', 1), (replica_count, 'replica_count', 2),
                                  (seed, 'seed', 0), (discard_per_chain, 'discard_per_chain', 0),
                                  (diagnostic_max_lag, 'diagnostic_max_lag', 1)):
        if type(value) is not int or value < minimum:
            raise ValueError(f'{label} must be an integer >= {minimum}.')
    if max_lag is None:
        max_lag = extent // 2
    if type(max_lag) is not int or not 3 <= max_lag <= extent // 2:
        raise ValueError('max_lag must lie between 3 and floor(time_extent/2).')
    chains = data.get('chains')
    if not isinstance(chains, list) or not chains:
        raise ValueError('Supply at least one ordered measurement chain.')
    ids_seen = set()
    saved_spacing = None
    block_means, block_products, records = [], [], []
    monitors = ([f'time_average:{name}' for name in names] +
                [f'raw_equal_time_square:{name}' for name in names])
    with np.errstate(over='raise', invalid='raise', divide='raise'):
        for chain in chains:
            if not isinstance(chain, dict):
                raise ValueError('Each chain must be an object.')
            chain_id = chain.get('chain_id')
            if not isinstance(chain_id, str) or not chain_id.strip() or chain_id in ids_seen:
                raise ValueError('Supply unique nonempty chain_id values.')
            ids_seen.add(chain_id)
            ids = chain.get('configuration_ids')
            if not isinstance(ids, list) or len(ids) < 2 or any(type(i) is not int or i < 0 for i in ids):
                raise ValueError('Each chain requires nonnegative integer configuration IDs.')
            steps = [b - a for a, b in zip(ids, ids[1:])]
            if min(steps) <= 0 or len(set(steps)) != 1:
                raise ValueError('Configuration IDs must increase with uniform spacing; split gaps into separate chains.')
            if saved_spacing is not None and steps[0] != saved_spacing:
                raise ValueError('All chains must have the same saved-configuration spacing.')
            saved_spacing = steps[0]
            x = real_array(chain.get('measurements'))
            if x.shape != (len(ids), extent, len(names)):
                raise ValueError('Measurements must have [configuration][time_extent][operator] shape.')
            x = x[discard_per_chain:]
            kept_ids = ids[discard_per_chain:]
            if len(x) < 2 * block_size:
                raise ValueError('Every retained chain needs at least two complete blocks.')
            if len(x) % block_size:
                raise ValueError('Retained chain length must be divisible by block_size; no tail is silently discarded.')
            nblocks = len(x) // block_size
            means = x.mean(axis=1)
            products = configuration_correlators(x, max_lag)
            block_means.append(means.reshape(nblocks, block_size, len(names)).mean(axis=1))
            block_products.append(products.reshape(nblocks, block_size, max_lag + 1, len(names), len(names)).mean(axis=1))
            monitored = np.concatenate((means, np.mean(x ** 2, axis=1)), axis=1)
            records.append({
                'chain_id': chain_id, 'input_configuration_count': len(ids),
                'discarded_configuration_ids': ids[:discard_per_chain],
                'retained_configuration_ids': kept_ids, 'block_count': nblocks,
                'block_configuration_ids': [kept_ids[i:i + block_size] for i in range(0, len(x), block_size)],
                'diagnostics': chain_diagnostics(monitored, block_size, diagnostic_max_lag),
            })

        total_blocks = sum(len(b) for b in block_means)
        central_means = sum(b.sum(axis=0) for b in block_means) / total_blocks
        central_products = sum(b.sum(axis=0) for b in block_products) / total_blocks
        rng = np.random.Generator(np.random.PCG64(seed))
        replicas, draws = [], []
        for _ in range(replica_count):
            selected = [rng.integers(0, len(b), size=len(b)) for b in block_means]
            mean = sum(b[s].sum(axis=0) for b, s in zip(block_means, selected)) / total_blocks
            product = sum(b[s].sum(axis=0) for b, s in zip(block_products, selected)) / total_blocks
            replicas.append({'operator_means': mean.tolist(), 'correlators': product.tolist()})
            draws.append([s.tolist() for s in selected])

    result = {key: data[key] for key in ('data_kind', 'gauge_group', 'spacetime_dimensions',
              'operator_normalization', 'spatial_volume', 'time_extent', 'temporal_spacing',
              'time_unit', 'operators', 'boundary')}
    result.update(schema_version='ym3d.glueball_correlators.v1', times=list(range(max_lag + 1)),
                  correlators=central_products.tolist(), operator_means=central_means.tolist(),
                  vacuum_subtracted=False,
                  bootstrap={'block_size': block_size, 'resampling_unit': 'nonoverlapping configuration blocks within each chain',
                             'replicas': replicas})
    result['ensemble_preparation'] = {
        'schema_version': 'ym3d.glueball_ensemble_preparation.v1',
        'status': 'NUMERICAL_DIAGNOSTIC', 'seed': seed, 'random_generator': 'PCG64',
        'numpy_version': np.__version__, 'block_size': block_size, 'replica_count': replica_count,
        'configuration_id_spacing': saved_spacing, 'discard_per_chain': discard_per_chain,
        'retained_configuration_count': total_blocks * block_size, 'total_block_count': total_blocks,
        'weighting': 'equal retained configuration weight; fixed sample count within every chain',
        'time_origins': 'all periodic origins, with symmetric operator-index average',
        'vacuum_estimator': 'raw ensemble product minus ensemble mean outer product; refitted in every replica downstream',
        'finite_sample_bias': 'Plug-in vacuum subtraction is not bias-corrected for correlated finite samples.',
        'monitor_names': monitors, 'chains': records,
        'bootstrap_block_indices': draws,
        'qualifications': [
            'Block length and thermalization discard are explicit user choices; adequacy is not automatically established.',
            'Autocorrelations describe the declared monitors within each chain; no integrated correlation time or effective sample size is inferred.',
            'Assumes stationary retained chains sampling the same target distribution; chain counts are fixed during resampling.',
            'No gauge links are generated and SU(2) origin of scalar input measurements is not independently checked.',
            'No physical mass, continuum limit or analytic proof claim is made.',
        ],
    }
    if 'ensemble_metadata' in data:
        result['ensemble_preparation']['ensemble_metadata'] = data['ensemble_metadata']
    return result
