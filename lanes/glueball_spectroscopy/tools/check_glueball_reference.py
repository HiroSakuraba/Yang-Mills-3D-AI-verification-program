#!/usr/bin/env python3
"""Independent exact combinatorial/reference checker. Never imports src or NumPy.
PASS concerns spatial operator geometry and rational reference identities only.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]


def require(value,message):
    if not value:raise ValueError(message)


def loop_word(word):
    # Independently collect all starts/traversals on the polygon.
    word=tuple(word);require(word and all(type(d) is int and abs(d) in (1,2) for d in word),'bad direction')
    vertices=[(0,0)]
    for d in word:
        x,y=vertices[-1];vertices.append((x+(d==1)-(d==-1),y+(d==2)-(d==-2)))
    require(vertices[-1]==vertices[0],'open loop')
    choices=[]
    for direction in (1,-1):
        for start in range(len(word)):
            choices.append(tuple(word[(start+k)%len(word)] for k in range(len(word))) if direction==1
                           else tuple(-word[(start-k-1)%len(word)] for k in range(len(word))))
    return min(choices)


def orbit(word):
    result=set()
    # Generate by four rotations composed with an optional reflection.
    for reflect in (False,True):
        for turns in range(4):
            path=[]
            for d in word:
                x,y=(1 if d==1 else -1 if d==-1 else 0),(1 if d==2 else -1 if d==-2 else 0)
                if reflect:x=-x
                for _ in range(turns):x,y=-y,x
                path.append(x if x else 2*y)
            result.add(loop_word(path))
    return result


def check_operators(data):
    matrices=data['spatial_group']
    expected=set()
    for a,b,c,d in product((-1,0,1),repeat=4):
        if a*a+c*c==1 and b*b+d*d==1 and a*b+c*d==0:expected.add((a,b,c,d))
    require(len(matrices)==8 and {tuple(v for row in m for v in row) for m in matrices}==expected,'square group')
    dimensions=[('plaquette',1,1),('rectangle_1x2',1,2),('square_2x2',2,2),('rectangle_1x3',1,3),('rectangle_2x3',2,3)]
    require(len(data['operators'])==len(dimensions),'operator count')
    for op,(name,w,h) in zip(data['operators'],dimensions):
        require(op['id']==name and op['spatial_irrep']=='A1','operator identity')
        require(op['spacetime_dimensions']==3 and op['spatial_dimensions']==2,'dimension')
        require(op['trace']=='Tr(U)/2' and op['gauge_group']=='SU(2)','trace normalization')
        paths=[tuple(p) for p in op['orbit_paths']]
        require(len(paths)==len(set(paths)) and set(paths)==orbit([1]*w+[2]*h+[-1]*w+[-2]*h),'scalar orbit')
        require(F(op['orbit_weight'])==F(1,len(paths)),'orbit weight')
        edges=Counter()
        for path in paths:
            require(loop_word(path)==path,'path representative')
            points=[(0,0)]
            for d in path:
                x,y=points[-1];points.append((x+(d==1)-(d==-1),y+(d==2)-(d==-2)))
            xmin=min(x for x,y in points);ymin=min(y for x,y in points)
            points=[(x-xmin,y-ymin) for x,y in points]
            for a,b in zip(points,points[1:]):edges[tuple(sorted((a,b)))]+=F(2,len(paths))
        actual={tuple(tuple(v) for v in row['edge']):F(row['bound']) for row in op['link_oscillation_upper_bounds']}
        require(actual==dict(edges) and len(actual)==len(op['link_oscillation_upper_bounds']),'link oscillation envelope')
        require(F(op['oscillation_l1_upper_bound'])==4*(w+h),'oscillation l1')


def det2(m):return m[0][0]*m[1][1]-m[0][1]*m[1][0]


def check_reference(data,periodic):
    z=[[F(1),F(1,2)],[F(1,3),F(1)]];qs=[F(1,2),F(1,4)];means=[F(2),F(-1)]
    require(data['vacuum_subtracted'] is False and [F(x) for x in data['operator_means']]==means,'vacuum metadata')
    require(data['boundary']==('periodic_time' if periodic else 'zero_temperature'),'time boundary')
    require(data['data_kind']=='synthetic_exact_reference','synthetic provenance')
    require(data['operator_normalization']=='spatial_sum_div_sqrt_volume' and data['spatial_volume']==1 and data['time_unit']=='lattice_time','normalization metadata')
    require(data['times']==list(range(9)) and (data['time_extent']==16 if periodic else data['time_extent'] is None),'time grid')
    matrices=[]
    require(len(data['correlators'])==9,'time count')
    for t,raw in zip(data['times'],data['correlators']):
        require(len(raw)==2 and all(len(row)==2 for row in raw),'matrix dimensions')
        c=[[F(raw[i][j])-means[i]*means[j] for j in range(2)] for i in range(2)]
        for i in range(2):
            for j in range(2):
                wanted=sum(z[i][k]*z[j][k]*(qs[k]**t+(qs[k]**(16-t) if periodic else 0)) for k in range(2))
                require(c[i][j]==wanted,'reference matrix reconstruction')
        matrices.append(c)
    c0=matrices[0];require(c0[0][0]>0 and det2(c0)>0,'positive reference metric')
    for t,c in enumerate(matrices):
        for q in qs:
            eigenvalue=(q**t+q**(16-t))/(1+q**16) if periodic else q**t
            require(det2([[c[i][j]-eigenvalue*c0[i][j] for j in range(2)] for i in range(2)])==0,'exact GEVP root')


def check_budget(data):
    x=F(data['wilson_x']);alpha=F(data['alpha_upper']);q=F(data['pure_exponential_base'])
    require(x==F(1,20) and alpha==12*x and q==(1+alpha)/2 and 0<alpha<q<1,'review budget parameters')
    def bracket(t):return (2*t+3)**2+8*alpha*((t+2)/(1-alpha)+alpha/(1-alpha)**2)
    coefficients=[bracket(0),bracket(1)-bracket(0)-4,F(4)]
    require([F(v) for v in data['polynomial_coefficients']]==coefficients,'spatial polynomial')
    r=alpha/q
    # Finite differences rather than the generator's power-moment formula.
    total=bracket(0)/(1-r)+(bracket(1)-bracket(0))*r/(1-r)**2+8*r*r/(1-r)**3
    require(F(data['pure_exponential_prefactor'])==16*total/(1-alpha),'exponential envelope constant')
    require(F(data['local_covariance_prefactor'])==16/(1-alpha),'local support factor')
    require(data['status']=='EXACT_FORMULA_EVALUATION_ANALYTIC_DERIVATION_FOR_REVIEW','analytic scope')


def reject_mutation(check,data,mutator):
    changed=deepcopy(data);mutator(changed)
    try:check(changed)
    except (ValueError,KeyError,TypeError,IndexError):return
    raise ValueError('Negative control was incorrectly accepted.')


def main():
    out=ROOT/'artifacts'
    operators=json.loads((out/'operators.json').read_text())
    budget=json.loads((out/'scalar_decay_budget.json').read_text())
    zero=json.loads((ROOT/'examples/two_state_zero_temperature.json').read_text())
    periodic=json.loads((ROOT/'examples/two_state_periodic.json').read_text())
    decision={'status':'FAIL','closed_obligations':[],
              'non_claims':['No analytic or physical mass-gap gate closed','No isolated glueball pole',
                            'No continuum result','Floating-point spectroscopy not certified by this checker'],
              'next_obligation':'Review analytic correlation derivation and establish physical transfer identification'}
    try:
        check_operators(operators);check_budget(budget)
        check_reference(zero,False);check_reference(periodic,True)
        reject_mutation(check_operators,operators,lambda d:d['spatial_group'].pop())
        reject_mutation(check_operators,operators,lambda d:d['operators'][0].update(orbit_weight='2'))
        reject_mutation(lambda d:check_reference(d,False),zero,lambda d:d['correlators'][2][0].__setitem__(0,'99'))
        reject_mutation(check_budget,budget,lambda d:d.update(pure_exponential_prefactor='1'))
        decision.update(status='PASS',closed_obligations=[
            'D4 spatial scalar-loop orbits and link-oscillation envelope coefficients reconstructed',
            'Two-state rational GEVP reference pencils and vacuum subtraction reconstructed',
            'Rational spatial-sum formula constants reconstructed; analytic hypotheses not certified'],
            negative_controls_rejected=4,operator_count=5,reference_time_slices=18)
    except Exception as exc:
        decision['error']=str(exc);(out/'decision.json').write_text(json.dumps(decision,indent=2)+'\n');raise
    (out/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    print('PASS: exact geometry/reference arithmetic only; four negative controls rejected.')
if __name__=='__main__':main()
