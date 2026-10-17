#!/usr/bin/env python3
"""Construct deterministic numerical references; no Yang–Mills ensemble generation."""
import json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'glueball_spectroscopy'/'examples'


def main():
    out=ROOT/'examples';out.mkdir(exist_ok=True)
    for periodic in (False,True):
        name='two_state_periodic.json' if periodic else 'two_state_zero_temperature.json'
        data=json.loads((SOURCE/name).read_text());t=np.array(data['times'])
        covariances=[]
        for q in (.5,.25):
            signal=(q**t+q**(16-t))/(1+q**16) if periodic else q**t
            sigma=.002*signal;sigma[0]=0
            covariances.append((np.outer(sigma,sigma)*.4**np.abs(t[:,None]-t[None,:])).tolist())
        data.update(data_kind='synthetic_correlated_reference',projected_covariances=covariances,
                    covariance_basis='fixed_reference_modes',covariance_kind='covariance_of_mean',
                    covariance_note='Constructed relative-error covariance; not measured sampling errors.')
        (out/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    t=np.arange(9);curve=.8*np.exp(-.4*t)+.2*np.exp(-1.4*t)
    control={'schema_version':'ym3d.glueball_correlators.v1','data_kind':'synthetic_excited_state_control',
             'gauge_group':'SU(2)','spacetime_dimensions':3,'operators':['two_state_mixture'],
             'operator_normalization':'spatial_sum_div_sqrt_volume','spatial_volume':1,
             'times':t.tolist(),'temporal_spacing':1,'time_unit':'lattice_time','vacuum_subtracted':True,
             'boundary':'zero_temperature','time_extent':None,'correlators':[[[float(v)]] for v in curve],
             'projected_covariances':[(np.eye(9)*1e-10).tolist()],
             'covariance_basis':'fixed_reference_modes','covariance_kind':'covariance_of_mean',
             'reference':{'masses':[.4,1.4],'weights':[.8,.2],
                          'expected_diagnostic':'WINDOW_DEPENDENCE for windows 1:4 and 4:8'},
             'bootstrap':{'block_size':1,'resampling_unit':'constructed perturbations, not gauge configurations','replicas':[]}}
    rng=np.random.default_rng(15)
    for _ in range(12):
        c=curve*(1+rng.normal(0,1e-5,len(t)))
        control['bootstrap']['replicas'].append({'correlators':[[[float(v)]] for v in c]})
    (out/'excited_state_control.json').write_text(json.dumps(control,indent=2,allow_nan=False)+'\n')
    print('Wrote three synthetic numerical inputs; no physical gauge ensembles.')
if __name__=='__main__':main()
