"""Numerical regression tests, not exact proof-gate checkers."""
from copy import deepcopy
from pathlib import Path
import json,math,sys,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT.parent/'glueball_spectroscopy'/'src')]
from glueball_spectrum_analysis.analysis import analyze,make_windows
from glueball_spectrum_analysis.fits import fit_curve,covariance_weight
from glueball_spectrum_analysis.modes import assignment,track_frames,solve


def dataset(curves=None,periodic=False):
    times=list(range(9))
    if curves is None:
        masses=[math.log(2),math.log(4)]
        curves=np.array([[math.exp(-m*t)+(math.exp(-m*(16-t)) if periodic else 0) for m in masses] for t in times])
    curves=np.asarray(curves)
    rank=curves.shape[1]
    return {'schema_version':'ym3d.glueball_correlators.v1','data_kind':'synthetic_test',
            'gauge_group':'SU(2)','spacetime_dimensions':3,'operator_normalization':'spatial_sum_div_sqrt_volume',
            'spatial_volume':1,'time_unit':'lattice_time','operators':[f'o{i}' for i in range(rank)],
            'times':times,'correlators':[np.diag(v).tolist() for v in curves],
            'vacuum_subtracted':True,'boundary':'periodic_time' if periodic else 'zero_temperature',
            'time_extent':16 if periodic else None,'temporal_spacing':1}


def with_covariance(d,variance=1e-6):
    rank=len(d['operators']);n=len(d['times'])
    d.update(projected_covariances=[(np.eye(n)*variance).tolist() for _ in range(rank)],
             covariance_basis='fixed_reference_modes',covariance_kind='covariance_of_mean')
    return d


class SpectrumAnalysisChecks(unittest.TestCase):
    def test_assignment_ignores_permutation_and_sign(self):
        a=np.eye(3);b=a[:,[2,0,1]]*np.array([-1,1,-1])
        order,phase,score=assignment(a,b)
        np.testing.assert_array_equal(order,[1,2,0]);np.testing.assert_allclose(score,1)
        np.testing.assert_allclose(b[:,order]*phase,a)

    def test_tracked_frames_preserve_labels(self):
        vals=np.array([[1,1],[.5,.25],[.0625,.25],[.125,.015625]])
        vec=np.array([np.eye(2),np.eye(2),np.array([[0,-1],[1,0]]),np.eye(2)])
        tracked,_,scores,_,_=track_frames(vals,vec,1)
        np.testing.assert_allclose(tracked[2],[.25,.0625]);np.testing.assert_allclose(scores,1)

    def test_crossing_tracks_vectors_instead_of_sorted_values(self):
        t=np.arange(9);curves=np.column_stack((.1*.99**t+.9*.2**t,.6**t))
        result=solve(dataset(curves));tracked=result['tracked_principal']
        self.assertLess(tracked[5,0],tracked[5,1])
        np.testing.assert_allclose(result['projected'][:,0],.6**t,atol=1e-12)
        self.assertEqual(result['mode_permutations'][5].tolist(),[1,0])

    def test_degenerate_reference_is_flagged(self):
        t=np.arange(9);result=solve(dataset(np.column_stack((.5**t,.5**t))))
        self.assertTrue(any(i['kind']=='NEAR_DEGENERATE_MODES' and i['time']==1 for i in result['issues']))

    def test_zero_temperature_correlated_reference_fits(self):
        result=analyze(with_covariance(dataset()),windows=[(1,5),(2,6)])
        self.assertIsNone(result['selected_window'])
        for f in result['fits']:
            self.assertAlmostEqual(f['mass'],[math.log(2),math.log(4)][f['state']],places=6)
            self.assertGreater(f['degrees_of_freedom'],0)
            self.assertIsNotNone(f['mass_standard_error_linearized'])
        json.dumps(result,allow_nan=False)

    def test_periodic_cosh_fit_and_time_units(self):
        d=with_covariance(dataset(periodic=True));d['temporal_spacing']='1/2'
        result=analyze(d,windows=[(2,7)],mass_bounds=(.01,4))
        for f in result['fits']:
            self.assertAlmostEqual(f['mass'],2*[math.log(2),math.log(4)][f['state']],places=6)
            self.assertEqual(f['model'],'vacuum_dominated_periodic_cosh')

    def test_fixed_projection_invariant_under_basis_change(self):
        d=with_covariance(dataset());a=np.array([[2.,.3],[-.2,1.]])
        d['correlators']=[(a@np.asarray(c)@a.T).tolist() for c in d['correlators']]
        result=analyze(d,windows=[(1,5)])
        for f in result['fits']:self.assertAlmostEqual(f['mass'],[math.log(2),math.log(4)][f['state']],places=6)

    def test_offdiagonal_covariance_is_used(self):
        t=np.arange(1,7);cov=1e-5*.7**np.abs(t[:,None]-t[None,:])
        y=1.3*np.exp(-.65*(t-t[0]))+np.array([.0002,-.0001,.0003,-.0002,.0001,-.0001])
        result=fit_curve(t,y,1,'zero_temperature',(.01,2),cov)
        residual=y-result['amplitude_at_window_start']*np.exp(-result['mass']*(t-t[0]))
        wanted=float(residual@np.linalg.inv(cov)@residual)
        self.assertAlmostEqual(result['chi_square'],wanted,places=9)
        self.assertAlmostEqual(result['mass'],.65,places=2)

    def test_unweighted_fits_do_not_get_statistical_errors(self):
        result=analyze(dataset(),windows=[(1,5)],states=[0])
        f=result['fits'][0]
        self.assertIsNone(f['p_value_diagnostic']);self.assertIsNone(f['mass_standard_error_linearized'])
        self.assertIn('UNWEIGHTED_DIAGNOSTIC',f['issues'])

    def test_covariance_rank_and_indefiniteness(self):
        with self.assertRaisesRegex(ValueError,'too few modes'):covariance_weight(np.ones((4,4)),4)
        c=np.eye(4);c[0,1]=c[1,0]=2
        with self.assertRaisesRegex(ValueError,'semidefinite'):covariance_weight(c,4)
        c=np.diag([1.,1.,1.,0.]);_,info=covariance_weight(c,4)
        self.assertEqual(info['rank'],3)
        _,shrunk=covariance_weight(np.full((4,4),.99)+.01*np.eye(4),4,shrinkage=.2)
        self.assertEqual(shrunk['rank'],4)

    def test_bound_censoring_is_flagged(self):
        t=np.arange(5);f=fit_curve(t,np.exp(-.6*t),1,'zero_temperature',(.01,.2))
        self.assertIn('MASS_AT_SEARCH_BOUND',f['issues'])

    def test_invalid_controls_rejected(self):
        with self.assertRaises(ValueError):analyze(dataset(),mass_bounds=(0,2))
        with self.assertRaises(ValueError):analyze(dataset(),windows=[(1,2)])
        with self.assertRaises(ValueError):analyze(dataset(),reference_time=0)
        with self.assertRaises(ValueError):analyze(dataset(),shrinkage=.1)
        d=with_covariance(dataset());del d['covariance_kind']
        with self.assertRaises(ValueError):analyze(d)
        self.assertEqual(len(make_windows(list(range(7)),1,scan_min_points=4)),6)

    def test_raw_replica_means_and_fit_bootstrap(self):
        d=with_covariance(dataset());d['vacuum_subtracted']=False;mean=np.array([.2,-.1])
        d['correlators']=[(np.asarray(c)+np.outer(mean,mean)).tolist() for c in d['correlators']]
        d['operator_means']=mean.tolist();replicas=[];qs=np.linspace(.48,.52,8)
        for index,q in enumerate(qs):
            m=np.array([.01*index,-.1]);curves=np.column_stack((q**np.arange(9),.25**np.arange(9)))
            replicas.append({'correlators':[(np.diag(c)+np.outer(m,m)).tolist() for c in curves],
                             'operator_means':m.tolist()})
        d['bootstrap']={'replicas':replicas,'block_size':8,'resampling_unit':'configuration blocks'}
        result=analyze(d,windows=[(1,5)],states=[0]);f=result['fits'][0]
        self.assertAlmostEqual(f['mass_standard_error_bootstrap'],float(np.std(-np.log(qs),ddof=1)),places=5)
        bad=deepcopy(d);del bad['bootstrap']['replicas'][0]['operator_means']
        with self.assertRaisesRegex(ValueError,'own operator_means'):analyze(bad,windows=[(1,5)])

    def test_bootstrap_covariance_not_divided_by_replica_count(self):
        rng=np.random.default_rng(911);d=dataset();replicas=[]
        for _ in range(24):
            curves=np.column_stack((.5**np.arange(9),.25**np.arange(9)))*(1+rng.normal(0,.001,(9,2)))
            replicas.append({'correlators':[np.diag(row).tolist() for row in curves]})
        d['bootstrap']={'replicas':replicas,'block_size':4,'resampling_unit':'configuration blocks'}
        result=analyze(d,windows=[(1,5)],states=[0])
        self.assertIn('not_divided_by_replica_count',result['fits'][0]['covariance_source'])
        self.assertGreater(result['fits'][0]['mass_standard_error_bootstrap'],0)

    def test_rank_change_in_bootstrap_is_rejected(self):
        d=with_covariance(dataset());rep=deepcopy(d['correlators']);rep[0]=[[1,0],[0,0]]
        d['bootstrap']={'block_size':1,'resampling_unit':'configurations',
                        'replicas':[{'correlators':rep},{'correlators':d['correlators']}]}
        with self.assertRaisesRegex(ValueError,'changes retained metric rank'):analyze(d,windows=[(1,5)])

    def test_paired_window_shift_flags_excited_state_contamination(self):
        rng=np.random.default_rng(15);t=np.arange(9);curve=.8*np.exp(-.4*t)+.2*np.exp(-1.4*t)
        d=with_covariance(dataset(curve[:,None]),variance=1e-10)
        replicas=[]
        for _ in range(12):
            c=curve*(1+rng.normal(0,1e-5,len(t)));replicas.append({'correlators':[[[float(v)]] for v in c]})
        d['bootstrap']={'replicas':replicas,'block_size':4,'resampling_unit':'configuration blocks'}
        result=analyze(d,windows=[(1,4),(4,8)],states=[0])
        self.assertIn('WINDOW_DEPENDENCE',result['window_stability'][0]['issues'])

if __name__=='__main__':unittest.main()
