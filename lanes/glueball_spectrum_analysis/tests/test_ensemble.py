"""Numerical estimator regressions; not independent proof checkers."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tools'), str(ROOT.parent / 'glueball_spectroscopy' / 'src')]
from glueball_spectrum_analysis.ensemble import prepare_ensemble, configuration_correlators, chain_diagnostics
from glueball_spectrum_analysis.analysis import analyze
from glueball_spectroscopy.spectrum import connected_input
from build_ensemble_example import example


def fixture():
    rng = np.random.default_rng(441)
    return {
        'schema_version': 'ym3d.glueball_operator_samples.v1', 'data_kind': 'synthetic_operator_fixture',
        'gauge_group': 'SU(2)', 'spacetime_dimensions': 3,
        'operator_normalization': 'spatial_sum_div_sqrt_volume', 'spatial_volume': 12,
        'time_extent': 8, 'temporal_spacing': '1/2', 'time_unit': 'lattice_time',
        'operators': ['a', 'b'], 'boundary': 'periodic_time',
        'chains': [{'chain_id': name, 'configuration_ids': list(range(0, 10 * n, 10)),
                    'measurements': (rng.normal(size=(n, 8, 2)) + np.array([2., -1.])).tolist()}
                   for name, n in [('short', 8), ('long', 12)]],
    }


def direct(samples, max_lag):
    """Explicit time-origin/operator-index formula, separate from einsum code."""
    n, extent, count = samples.shape
    answer = np.zeros((max_lag + 1, count, count))
    for lag in range(max_lag + 1):
        for c in range(n):
            for t in range(extent):
                for i in range(count):
                    for j in range(count):
                        answer[lag, i, j] += (samples[c, t, i] * samples[c, (t + lag) % extent, j] +
                                              samples[c, t, j] * samples[c, (t + lag) % extent, i]) / (2 * n * extent)
    return answer


class EnsembleChecks(unittest.TestCase):
    def test_periodic_origin_average_and_equal_configuration_weight(self):
        data = fixture()
        result = prepare_ensemble(data, 2, 6)
        samples = np.concatenate([np.asarray(c['measurements']) for c in data['chains']])
        np.testing.assert_allclose(result['correlators'], direct(samples, 4), atol=1e-13)
        np.testing.assert_allclose(result['operator_means'], samples.mean(axis=(0, 1)))
        self.assertEqual(result['ensemble_preparation']['retained_configuration_count'], 20)
        self.assertFalse(result['vacuum_subtracted'])

    def test_bootstrap_draws_reconstruct_raw_products_and_own_means(self):
        data = fixture()
        result = prepare_ensemble(data, 2, 8, seed=19)
        records = result['ensemble_preparation']
        for rep, draws in zip(result['bootstrap']['replicas'], records['bootstrap_block_indices']):
            selected = []
            for chain, indices in zip(data['chains'], draws):
                samples = np.asarray(chain['measurements']).reshape(-1, 2, 8, 2)
                self.assertEqual(len(indices), len(samples))
                selected.append(samples[indices].reshape(-1, 8, 2))
            combined = np.concatenate(selected)
            np.testing.assert_allclose(rep['correlators'], direct(combined, 4), atol=1e-13)
            np.testing.assert_allclose(rep['operator_means'], combined.mean(axis=(0, 1)))
        self.assertNotEqual(result['operator_means'], result['bootstrap']['replicas'][0]['operator_means'])

    def test_constant_operator_offsets_cancel_in_central_and_replicas(self):
        data = fixture()
        shifted = deepcopy(data)
        for chain in shifted['chains']:
            chain['measurements'] = (np.asarray(chain['measurements']) + [7., -4.]).tolist()
        a = prepare_ensemble(data, 2, 6, seed=9)
        b = prepare_ensemble(shifted, 2, 6, seed=9)
        for left, right in [(a, b)] + list(zip(a['bootstrap']['replicas'], b['bootstrap']['replicas'])):
            ca = np.asarray(left['correlators']) - np.outer(left['operator_means'], left['operator_means'])
            cb = np.asarray(right['correlators']) - np.outer(right['operator_means'], right['operator_means'])
            np.testing.assert_allclose(ca, cb, atol=1e-13)

    def test_time_origin_shift_and_backward_lag_symmetry(self):
        samples = np.asarray(fixture()['chains'][0]['measurements'])
        a = configuration_correlators(samples, 7)
        b = configuration_correlators(np.roll(samples, 3, axis=1), 7)
        np.testing.assert_allclose(a, b, atol=1e-13)
        np.testing.assert_allclose(a[:, 1], a[:, 7], atol=1e-13)

    def test_discard_is_recorded_and_blocks_never_join_chains(self):
        data = fixture()
        result = prepare_ensemble(data, 2, 4, discard_per_chain=2)
        p = result['ensemble_preparation']
        self.assertEqual(p['retained_configuration_count'], 16)
        for chain in p['chains']:
            self.assertEqual(chain['discarded_configuration_ids'], [0, 10])
            self.assertEqual(chain['block_configuration_ids'][0], [20, 30])
            self.assertEqual(sum(chain['block_configuration_ids'], []), chain['retained_configuration_ids'])
        samples = np.concatenate([np.asarray(c['measurements'])[2:] for c in data['chains']])
        np.testing.assert_allclose(result['correlators'], direct(samples, 4), atol=1e-13)

    def test_seed_reproducibility_and_changed_draws(self):
        data = fixture()
        a = prepare_ensemble(data, 2, 6, seed=2)
        self.assertEqual(a, prepare_ensemble(data, 2, 6, seed=2))
        self.assertNotEqual(a['bootstrap'], prepare_ensemble(data, 2, 6, seed=3)['bootstrap'])

    def test_chain_validation_and_no_silent_tail_drop(self):
        invalid = []
        a = fixture(); a['chains'][1]['chain_id'] = 'short'; invalid.append(a)
        a = fixture(); a['chains'][0]['configuration_ids'][2] = 11; invalid.append(a)
        a = fixture(); a['chains'][1]['configuration_ids'] = list(range(0, 240, 20)); invalid.append(a)
        a = fixture(); a['chains'][0]['measurements'].pop(); invalid.append(a)
        a = fixture(); a['chains'][0]['configuration_ids'].pop(); a['chains'][0]['measurements'].pop(); invalid.append(a)
        for data in invalid:
            with self.subTest(data=data['chains'][0]['chain_id']):
                with self.assertRaises(ValueError): prepare_ensemble(data, 2, 4)
        with self.assertRaisesRegex(ValueError, 'two complete blocks'): prepare_ensemble(fixture(), 8, 4)

    def test_metadata_and_controls_rejected(self):
        for key, value in [('boundary', 'zero_temperature'), ('operator_normalization', 'spatial_average'),
                           ('data_kind', 'unknown'), ('temporal_spacing', 'inf'), ('operators', ['a', 'a']),
                           ('spatial_volume', True), ('time_extent', 5)]:
            data = fixture(); data[key] = value
            with self.assertRaises(ValueError): prepare_ensemble(data, 2, 4)
        for controls in [{'block_size': 0}, {'replica_count': 1}, {'seed': True},
                         {'discard_per_chain': -1}, {'max_lag': 5}, {'diagnostic_max_lag': 0}]:
            args = {'block_size': 2, 'replica_count': 4}; args.update(controls)
            with self.assertRaises(ValueError): prepare_ensemble(fixture(), **args)
        data = fixture(); data['chains'][0]['measurements'][0][0][0] = float('nan')
        with self.assertRaises(ValueError): prepare_ensemble(data, 2, 4)

    def test_monitor_autocorrelation_is_explicit_and_constant_safe(self):
        values = np.column_stack((np.arange(8.), np.ones(8)))
        result = chain_diagnostics(values, 2, 3)
        centered = values[:, 0] - 3.5
        self.assertAlmostEqual(result['autocorrelation'][0][0],
                               np.mean(centered[:-1] * centered[1:]) / np.mean(centered ** 2))
        self.assertEqual(result['constant_monitors'], [1])
        self.assertIsNone(result['autocorrelation'][0][1])
        json.dumps(result, allow_nan=False)

    def test_samples_to_spectrum_pipeline_and_provenance(self):
        prepared = prepare_ensemble(example(), 8, 24, seed=29, discard_per_chain=8)
        times, _, connected, _ = connected_input(prepared)
        self.assertEqual(times, list(range(9)))
        self.assertGreater(connected[0, 0, 0], 0)
        result = analyze(prepared, windows=[(1, 4)])
        self.assertIn('mass', result['fits'][0])
        self.assertIn('bootstrap_mass_samples', result['fits'][0])
        self.assertEqual(result['ensemble_preparation'], prepared['ensemble_preparation'])
        self.assertEqual(result['data_kind'], 'synthetic_operator_fixture')
        self.assertIsNone(result['selected_window'])
        json.dumps(result, allow_nan=False)

    def test_cli_hash_and_input_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'samples.json'; output = Path(tmp) / 'correlators.json'
            source.write_text(json.dumps(fixture()))
            command = [sys.executable, str(ROOT / 'tools' / 'prepare_ensemble.py'), str(source),
                       '--block-size', '2', '--replicas', '4', '--discard-per-chain', '0']
            run = subprocess.run(command + ['--output', str(output)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_text())
            self.assertEqual(result['ensemble_preparation']['input_sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
            before = source.read_bytes()
            rejected = subprocess.run(command + ['--output', str(source)], capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
