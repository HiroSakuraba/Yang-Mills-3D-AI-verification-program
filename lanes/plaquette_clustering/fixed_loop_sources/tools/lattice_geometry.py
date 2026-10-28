"""Finite cubic-torus geometry for independent influence graph checks.

The graph is only a local combinatorial check; it does not verify Haar integrals.
"""
from itertools import combinations, product

def positive_links(n: int):
    if n < 4: raise ValueError('nondegenerate test lattice needs n >= 4')
    return [(x,y,z,axis) for x,y,z in product(range(n),repeat=3) for axis in range(3)]

def shift(xyz, axis, n):
    q=list(xyz);q[axis]=(q[axis]+1)%n;return tuple(q)

def face_links(n: int):
    if n<4: raise ValueError('nondegenerate test lattice needs n >= 4')
    output=[]
    for xyz in product(range(n),repeat=3):
        for a,b in combinations(range(3),2):
            # Orientation does not affect incidence.
            output.append(frozenset([
                (*xyz,a),(*xyz,b),(*shift(xyz,a,n),b),(*shift(xyz,b,n),a)]))
    return output

def incidence(n:int):
    l2f={link:[] for link in positive_links(n)}
    for fid,face in enumerate(face_links(n)):
        assert len(face)==4
        for link in face: l2f[link].append(fid)
    return l2f

def local_geometry(n:int)->dict:
    faces=face_links(n); l2f=incidence(n)
    degree=[];max_shared=0
    for link, fids in l2f.items():
        linked=set()
        for f in fids: linked.update(faces[f])
        linked.remove(link)
        degree.append(len(linked))
        for other in linked:
            overlap=len(set(fids).intersection(l2f[other]))
            max_shared=max(max_shared,overlap)
    return {'n':n,'face_count':len(faces),'link_count':len(l2f),
            'min_link_faces':min(map(len,l2f.values())),
            'max_link_faces':max(map(len,l2f.values())),
            'min_neighbor_links':min(degree),'max_neighbor_links':max(degree),
            'max_shared_faces_per_link_pair':max_shared}
