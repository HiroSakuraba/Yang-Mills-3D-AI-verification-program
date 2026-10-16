"""Exact spatial SU(2) scalar-loop definitions for 2+1 dimensions."""
from collections import Counter
from fractions import Fraction as F
from itertools import permutations, product


def canonical(path):
    path=tuple(path)
    if not path or any(type(d) is not int or d not in (-2,-1,1,2) for d in path):
        raise ValueError('A path must contain spatial directions +/-1, +/-2.')
    if any(sum((1 if d>0 else -1) for d in path if abs(d)==axis) for axis in (1,2)):
        raise ValueError('The spatial path is not closed.')
    backward=tuple(-d for d in reversed(path))
    return min(word[i:]+word[:i] for word in (path,backward) for i in range(len(word)))


def square_group():
    """Eight signed 2x2 permutation matrices; time is never transformed."""
    matrices=[]
    for p in permutations((0,1)):
        for signs in product((-1,1),repeat=2):
            m=[[0,0],[0,0]]
            for col in range(2):m[p[col]][col]=signs[col]
            matrices.append(m)
    return matrices


def transform(path,matrix):
    result=[]
    for d in path:
        col=abs(d)-1;sign=1 if d>0 else -1
        row=next(i for i in range(2) if matrix[i][col])
        result.append((row+1)*sign*matrix[row][col])
    return canonical(result)


def anchored_vertices(path):
    vertices=[(0,0)]
    for d in path:
        p=list(vertices[-1]);p[abs(d)-1]+=1 if d>0 else -1;vertices.append(tuple(p))
    if vertices[-1]!=vertices[0]:raise ValueError('Open path.')
    shift=[min(p[i] for p in vertices) for i in range(2)]
    return [tuple(p[i]-shift[i] for i in range(2)) for p in vertices]


def edge_multiplicities(path):
    points=anchored_vertices(path);edges=Counter()
    for p,q in zip(points,points[1:]):edges[tuple(sorted((p,q)))]+=1
    return edges


def scalar_operator(name,path):
    orbit=sorted({transform(canonical(path),m) for m in square_group()})
    edges=Counter()
    for word in orbit:
        for edge,n in edge_multiplicities(word).items():edges[edge]+=F(2*n,len(orbit))
    return {'id':name,'spacetime_dimensions':3,'spatial_dimensions':2,
            'gauge_group':'SU(2)','trace':'Tr(U)/2','spatial_irrep':'A1',
            'parity':'+','charge_conjugation':'+',
            'symmetry_projection_scope':'zero momentum; loops canonicalized modulo translation',
            'continuum_spin':'scalar candidate; A1 also contains spins 4, 8, ...',
            'local_definition':'P(x,t) = 1 - mean_orbit ReTr U_loop(x,t)/2',
            'centered_definition':'P(x,t) - <P(x,t)>',
            'zero_momentum_definition':'O(t) = sum_x [P(x,t)-<P(x,t)>]',
            'correlator_normalization':'Cov(O(t),O(0))/spatial_volume',
            'orbit_paths':[list(p) for p in orbit],
            'orbit_weight':str(F(1,len(orbit))),
            'link_oscillation_upper_bounds':[
                {'edge':[list(a),list(b)],'bound':str(v)} for (a,b),v in sorted(edges.items())],
            'oscillation_l1_upper_bound':str(sum(edges.values(),F(0)))}


def operator_registry():
    rectangles=[('plaquette',1,1),('rectangle_1x2',1,2),('square_2x2',2,2),
                ('rectangle_1x3',1,3),('rectangle_2x3',2,3)]
    return {'schema_version':'ym3d.scalar_operators.v1',
            'scope':'combinatorial definitions; no physical particle identification',
            'spatial_group':square_group(),
            'operators':[scalar_operator(name,[1]*w+[2]*h+[-1]*w+[-2]*h)
                         for name,w,h in rectangles]}
