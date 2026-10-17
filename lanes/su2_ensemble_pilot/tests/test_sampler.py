"""Numerical sampler regressions with an independent complex-matrix oracle."""
from pathlib import Path
import sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT.parent/'glueball_spectrum_analysis'/'src'),str(ROOT.parent/'glueball_spectroscopy'/'src')]
from su2_pilot.sampler import Lattice,multiply,conjugate,haar,normalize,run
from glueball_spectrum_analysis.ensemble import prepare_ensemble


def matrix(q):
    w,x,y,z=q
    return np.array([[w+1j*x,y+1j*z],[-y+1j*z,w-1j*x]])


def independent_trace_sum(lattice):
    shape=lattice.shape;answer=0.
    for coord in np.ndindex(shape):
        for a in range(3):
            for b in range(a+1,3):
                ca=list(coord);ca[a]=(ca[a]+1)%shape[a]
                cb=list(coord);cb[b]=(cb[b]+1)%shape[b]
                u=matrix(lattice.links[3*lattice.index[coord]+a])
                v=matrix(lattice.links[3*lattice.index[tuple(ca)]+b])
                r=matrix(lattice.links[3*lattice.index[tuple(cb)]+a])
                s=matrix(lattice.links[3*lattice.index[coord]+b])
                answer+=float(np.trace(u@v@r.conj().T@s.conj().T).real/2)
    return answer


class SamplerChecks(unittest.TestCase):
    def test_quaternions_match_complex_matrices(self):
        rng=np.random.default_rng(77)
        for _ in range(20):
            a,b=haar(rng),haar(rng)
            np.testing.assert_allclose(matrix(multiply(a,b)),matrix(a)@matrix(b),atol=1e-14)
            np.testing.assert_allclose(matrix(conjugate(a)),matrix(a).conj().T,atol=1e-14)
            np.testing.assert_allclose(matrix(a).conj().T@matrix(a),np.eye(2),atol=1e-14)

    def test_action_and_local_difference_against_matrix_oracle(self):
        rng=np.random.default_rng(21);lattice=Lattice((3,3,3),rng)
        self.assertAlmostEqual(lattice.trace_sum(),independent_trace_sum(lattice),places=12)
        for index in (0,15,80):
            before=independent_trace_sum(lattice)
            local_before=sum(lattice.plaquette(p) for p in lattice.incident[index])
            lattice.links[index]=haar(rng)
            change=sum(lattice.plaquette(p) for p in lattice.incident[index])-local_before
            self.assertAlmostEqual(change,independent_trace_sum(lattice)-before,places=12)

    def test_gauge_invariance_of_action_and_measured_operator(self):
        rng=np.random.default_rng(33);lattice=Lattice((3,3,3),rng)
        action=lattice.trace_sum();operator=lattice.scalar_operator();g=[haar(rng) for _ in lattice.coordinates]
        lattice.links=[multiply(multiply(g[s],lattice.links[3*s+a]),conjugate(g[lattice.plus[a][s]]))
                       for s in range(len(lattice.coordinates)) for a in range(3)]
        self.assertAlmostEqual(action,lattice.trace_sum(),places=12)
        np.testing.assert_allclose(operator,lattice.scalar_operator(),atol=1e-13)

    def test_beta_zero_accepts_every_proposal_and_preserves_group(self):
        rng=np.random.default_rng(19);lattice=Lattice((3,3,3),rng,'cold')
        self.assertEqual(lattice.sweep(0.,rng,.6,1.),len(lattice.links))
        np.testing.assert_allclose(np.sum(np.asarray(lattice.links)**2,axis=1),1,atol=1e-14)

    def test_seed_replay_and_samples_feed_preparation(self):
        controls=dict(beta=1.,shape=(6,3,3),seeds=(9,),starts=('hot',),warmup=0,samples=8,sweeps_between=1)
        a=run(**controls);b=run(**controls);self.assertEqual(a,b)
        self.assertEqual(a['data_kind'],'sampled_ensemble')
        self.assertEqual(a['chains'][0]['configuration_ids'],list(range(1,9)))
        prepared=prepare_ensemble(a,2,4,seed=8,discard_per_chain=0)
        self.assertFalse(prepared['vacuum_subtracted'])
        self.assertEqual(prepared['ensemble_preparation']['ensemble_metadata']['wilson_beta'],1.)

    def test_controls_and_resource_cap(self):
        for changes in ({'beta':float('nan')},{'beta':-1},{'step':0},{'shape':(8,2,3)},
                        {'seeds':(1,1)},{'max_updates':10},{'samples':True},{'global_probability':0}):
            controls={'beta':1.};controls.update(changes)
            with self.assertRaises((ValueError,TypeError)):run(**controls)
if __name__=='__main__':unittest.main()
