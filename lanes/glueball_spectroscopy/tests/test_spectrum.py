"""Numerical self-tests for advisory spectroscopy; not proof-gate checkers."""
from copy import deepcopy
from pathlib import Path
from fractions import Fraction as F
import json,math,sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from glueball_spectroscopy.operators import operator_registry,canonical
from glueball_spectroscopy.spectrum import analyze,evaluate_operator,connected_input


def load(periodic=False):
    return json.loads((ROOT/'examples'/('two_state_periodic.json' if periodic else 'two_state_zero_temperature.json')).read_text())


class NumericalSpectroscopyChecks(unittest.TestCase):
    def assert_known_masses(self,result):
        for row in result['effective_masses']['values']:
            np.testing.assert_allclose(row,[math.log(2),math.log(4)],atol=2e-8,rtol=2e-8)

    def test_exact_two_state_reference(self):
        result=analyze(load());self.assert_known_masses(result)
        self.assertEqual(result['vacuum_subtraction'],'subtracted_operator_mean_outer_product')
        self.assertLess(result['projected_eigen_residual_max'],1e-12)

    def test_periodic_cosh_reference(self):
        result=analyze(load(True));self.assert_known_masses(result)
        self.assertTrue(any(v['kind']=='PERIODIC_COSH_ASSUMPTION' for v in result['issues']))

    def test_nonzero_t0_and_time_spacing(self):
        d=load();d['temporal_spacing']='1/2';r=analyze(d,t0=2)
        for row in r['effective_masses']['values']:
            np.testing.assert_allclose(row,[2*math.log(2),2*math.log(4)],atol=2e-8,rtol=2e-8)

    def test_nonsingular_operator_basis_change(self):
        d=load();a=np.array([[2.,-.5],[.25,1.]])
        raw=np.array([[[float(F(v)) for v in row] for row in c] for c in d['correlators']])
        d['correlators']=[(a@c@a.T).tolist() for c in raw]
        d['operator_means']=(a@np.array([2.,-1.])).tolist()
        self.assert_known_masses(analyze(d))

    def test_rank_reduction_for_redundant_operator(self):
        d=load();a=np.array([[1.,0.],[0.,1.],[1.,1.]])
        raw=np.array([[[float(F(v)) for v in row] for row in c] for c in d['correlators']])
        d['correlators']=[(a@c@a.T).tolist() for c in raw]
        d['operator_means']=(a@np.array([2.,-1.])).tolist();d['operators'].append('redundant')
        r=analyze(d);self.assertEqual(r['metric_rank'],2);self.assert_known_masses(r)

    def test_bootstrap_raw_means_are_recomputed(self):
        d=load();replicas=[]
        for q,shift in [(F(49,100),F(1)),(F(1,2),F(2)),(F(51,100),F(3))]:
            z=[[F(1),F(1,2)],[F(1,3),F(1)]];mean=[shift,F(-1)]
            raw=[[[str(sum(z[i][k]*z[j][k]*([q,F(1,4)][k]**t) for k in range(2))+mean[i]*mean[j])
                   for j in range(2)] for i in range(2)] for t in range(9)]
            replicas.append({'correlators':raw,'operator_means':[str(v) for v in mean]})
        d['bootstrap']={'block_size':8,'resampling_unit':'configuration blocks','replicas':replicas}
        r=analyze(d);expected=np.std([-math.log(.49),-math.log(.5),-math.log(.51)],ddof=1)
        self.assertAlmostEqual(r['bootstrap']['effective_mass_uncertainties'][0][0]['standard_error'],expected,places=10)
        self.assertAlmostEqual(r['effective_masses']['values'][0][0],math.log(2),places=10)
        bad=deepcopy(d);del bad['bootstrap']['replicas'][0]['operator_means']
        with self.assertRaisesRegex(ValueError,'own operator_means'):analyze(bad)

    def test_invalid_metadata_and_metric_rejected(self):
        mutations=[lambda d:d.update(vacuum_subtracted=None),lambda d:d.pop('operator_means'),
                   lambda d:d.update(temporal_spacing='nan'),lambda d:d.update(times=[0,1,1]),
                   lambda d:d.update(boundary='unspecified'),
                   lambda d:d['correlators'][0].__setitem__(0,['-999','0'])]
        for mutate in mutations:
            d=load();mutate(d)
            with self.assertRaises(ValueError):analyze(d)
        with self.assertRaises(ValueError):analyze(load(),rank_cutoff=0)

    def test_negative_late_modes_flagged_not_logged(self):
        d=load();d['correlators'][3]=[[3, -2],[-2,0]]  # connected metric at t=3 is -I.
        r=analyze(d)
        self.assertTrue(any(v is None for row in r['effective_masses']['values'] for v in row))
        self.assertTrue(any(i['kind']=='INVALID_LOG_MASS' for i in r['issues']))
        json.dumps(r,allow_nan=False)

    def test_connected_flag_avoids_double_subtraction(self):
        d=load();_,_,c,_=connected_input(d)
        d['correlators']=c.tolist();d['vacuum_subtracted']=True
        self.assert_known_masses(analyze(d))

    def test_loop_gauge_invariance_and_identity_links(self):
        rng=np.random.default_rng(143)
        def su2():
            a,b,c,d=rng.normal(size=4);norm=math.sqrt(a*a+b*b+c*c+d*d)
            return np.array([[a+1j*b,c+1j*d],[-c+1j*d,a-1j*b]])/norm
        for op in operator_registry()['operators']:
            keys=[];vertices=set()
            for row in op['link_oscillation_upper_bounds']:
                a,b=map(tuple,row['edge']);axis=0 if a[0]!=b[0] else 1
                keys.append((*a,axis));vertices.update([a,b])
            links={k:su2() for k in keys};g={v:su2() for v in vertices}
            rotated={}
            for k,u in links.items():
                x,y,axis=k;a=(x,y);b=(x+(axis==0),y+(axis==1))
                rotated[k]=g[a]@u@g[b].conj().T
            self.assertAlmostEqual(evaluate_operator(op,links),evaluate_operator(op,rotated),places=12)
            self.assertAlmostEqual(evaluate_operator(op,{k:np.eye(2) for k in keys}),0.,places=12)
        with self.assertRaises(ValueError):canonical([1,2,-1])

if __name__=='__main__':unittest.main()
