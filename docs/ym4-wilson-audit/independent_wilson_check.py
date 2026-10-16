#!/usr/bin/env python3
"""Exact cube contraction and conservative Wilson Dobrushin coefficients.
Standard library only. The analytic uniqueness/clustering argument is in the note;
this checker certifies the finite combinatorics and arithmetic used there.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
from frontier_certificate import (I, S, ONE, enclose, exp_positive, negative_log_at,
                                  formatted_interval)

class DSU:
    def __init__(self,n): self.p=list(range(n))
    def root(self,a):
        while self.p[a]!=a:
            self.p[a]=self.p[self.p[a]];a=self.p[a]
        return a
    def join(self,a,b): self.p[self.root(a)]=self.root(b)

def cube_contraction(dimension=2):
    """Contract ordinary oriented traces using int U_ij conjugate(U_kl)=delta/dim."""
    vertices=list(product(range(2),repeat=3))
    faces=[]
    for fixed in range(3):
        free=[i for i in range(3) if i!=fixed]
        for side in range(2):
            loop=[]
            for u,v in [(0,0),(1,0),(1,1),(0,1)]:
                x=[0,0,0];x[fixed]=side;x[free[0]]=u;x[free[1]]=v
                loop.append(tuple(x))
            # The forward free-axis loop normal is (-1)^fixed times fixed axis.
            if (-1)**fixed != (-1 if side==0 else 1): loop.reverse()
            faces.append(loop)
    incidences=defaultdict(list)
    for fi,loop in enumerate(faces):
        for k in range(4):
            u,v=loop[k],loop[(k+1)%4]
            key=tuple(sorted((u,v)))
            # Matrix indices of U for positive traversal, conjugate(U) for negative.
            row,col=4*fi+k,4*fi+(k+1)%4
            if u<v:incidences[key].append((1,row,col))
            else:incidences[key].append((-1,col,row))
    uf=DSU(24)
    active_degree=Counter()
    for (u,v),rows in incidences.items():
        assert len(rows)==2 and rows[0][0]==-rows[1][0]
        uf.join(rows[0][1],rows[1][1]);uf.join(rows[0][2],rows[1][2])
        active_degree[u]+=1;active_degree[v]+=1
    loops=len({uf.root(i) for i in range(24)})
    integral=F(dimension**loops,dimension**len(incidences))
    return {'surface':'oriented boundary of one elementary 3-cube embedded in Z^4',
            'faces':len(faces),'edges':len(incidences),'vertices':len(vertices),
            'index_loops_after_haar_pairing':loops,
            'active_edge_degrees':sorted(active_degree.values()),
            'ordinary_character_haar_integral':str(integral),
            'normalized_character_haar_integral':str(integral/F(dimension**6)),
            'omitted_wilson_dimension_factor_for_six_faces':dimension**6}

def link_incidence_row(d=4):
    """Reconstruct every plaquette through one link and all its other edges."""
    zero=(0,)*d;one=(1,)+(0,)*(d-1)
    e=tuple(sorted((zero,one)))
    def step(v,axis,n):
        w=list(v);w[axis]+=n;return tuple(w)
    neighbours=Counter()
    plaquettes=[]
    for axis in range(1,d):
        for sign in [-1,1]:
            loop=[zero,one,step(one,axis,sign),step(zero,axis,sign)]
            edges=[tuple(sorted((loop[k],loop[(k+1)%4]))) for k in range(4)]
            assert e in edges
            plaquettes.append(edges)
            for f in edges:
                if f!=e:neighbours[f]+=1
    return {'dimension':d,'plaquettes_through_link':len(plaquettes),
            'other_link_incidences':sum(neighbours.values()),
            'distinct_other_links':len(neighbours),
            'max_shared_plaquette_multiplicity':max(neighbours.values())}

def dobrushin(x,d=4):
    x=F(x);assert x>0
    e2=exp_positive(2*x)
    numerator=I(e2.lo-S,e2.hi-S)
    denominator=I(e2.lo+S,e2.hi+S)
    tanh=numerator.div(denominator)
    alpha=tanh.scale(6*(d-1))
    result={'wilson_x':str(x),'dimension':d,
            'scope':'arithmetic for the analytically derived influence bound; not the 0.6273 activity budget',
            'alpha':formatted_interval(alpha.lo,alpha.hi),
            'passes':alpha.hi<S}
    if result['passes']:
        rate_low=negative_log_at(F(alpha.hi,S))
        rate_high=negative_log_at(F(alpha.lo,S))
        result['graph_distance_decay_rate']=formatted_interval(rate_low.lo,rate_high.hi)
    return result

def main():
    cube=cube_contraction()
    geometry=link_incidence_row()
    rows=[dobrushin(x) for x in ['0.01','0.04','0.05','0.055','0.0556128','0.0556129','0.06']]
    assert cube['ordinary_character_haar_integral']=='1/16'
    assert cube['active_edge_degrees']==[3]*8
    assert geometry['other_link_incidences']==18
    assert rows[4]['passes'] and not rows[5]['passes']
    output={'cube_counterexample':cube,'wilson_link_geometry':geometry,'influence_bounds':rows,
            'threshold_exact':'atanh(1/18) = (1/2) log(19/17)',
            'threshold_bracket':['0.0556128','0.0556129']}
    Path('independent-results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(cube,indent=2))
    print(json.dumps(geometry,indent=2))
    for r in rows:print(r['wilson_x'],r['alpha']['lower'][:24],r['passes'])

if __name__=='__main__':main()
