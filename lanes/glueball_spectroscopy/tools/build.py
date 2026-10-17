#!/usr/bin/env python3
"""Generate exact definitions and spectral reference data; not a physical simulation."""
from fractions import Fraction as F
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from glueball_spectroscopy.operators import operator_registry
from glueball_spectroscopy.bounds import scalar_budget


def reference(periodic=False):
    z=[[F(1),F(1,2)],[F(1,3),F(1)]];q=[F(1,2),F(1,4)];means=[F(2),F(-1)]
    times=list(range(9));extent=16
    matrices=[]
    for t in times:
        matrix=[[sum(z[i][k]*z[j][k]*(q[k]**t+(q[k]**(extent-t) if periodic else 0))
                     for k in range(2))+means[i]*means[j] for j in range(2)] for i in range(2)]
        matrices.append([[str(a) for a in row] for row in matrix])
    return {'schema_version':'ym3d.glueball_correlators.v1','data_kind':'synthetic_exact_reference',
            'gauge_group':'SU(2)','spacetime_dimensions':3,
            'boundary':'periodic_time' if periodic else 'zero_temperature',
            'time_extent':extent if periodic else None,'temporal_spacing':'1',
            'operators':['ref_loop_a','ref_loop_b'],'vacuum_subtracted':False,
            'operator_means':[str(x) for x in means],'times':times,'correlators':matrices,
            'operator_normalization':'spatial_sum_div_sqrt_volume','spatial_volume':1,'time_unit':'lattice_time',
            'reference':{'overlap_matrix':[[str(v) for v in row] for row in z],
                         'transfer_eigenvalues':[str(v) for v in q],
                         'mass_formulas':['log(2)','log(4)'],
                         'warning':'Constructed spectra, not measured Yang-Mills configurations.'}}


def main():
    out=ROOT/'artifacts';out.mkdir(exist_ok=True)
    examples=ROOT/'examples';examples.mkdir(exist_ok=True)
    for p,data in [(out/'operators.json',operator_registry()),(out/'scalar_decay_budget.json',scalar_budget()),
                   (examples/'two_state_zero_temperature.json',reference()),
                   (examples/'two_state_periodic.json',reference(True))]:
        p.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print('Generated operator registry, rational budget, and two exact spectral references.')
if __name__=='__main__':main()
