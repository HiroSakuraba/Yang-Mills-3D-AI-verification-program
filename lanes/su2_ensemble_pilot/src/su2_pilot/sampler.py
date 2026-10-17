"""Quaternion Metropolis sampler with an auditable full-plaquette local action."""
import hashlib
from itertools import combinations, product
import math
from pathlib import Path
import numpy as np


def multiply(a,b):
    w,x,y,z=a;v,i,j,k=b
    return (w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v)


def conjugate(q):return (q[0],-q[1],-q[2],-q[3])


def normalize(q):
    norm=math.sqrt(sum(float(v)**2 for v in q))
    if not math.isfinite(norm) or norm<=0:raise ValueError('Invalid quaternion norm.')
    return tuple(float(v)/norm for v in q)


def haar(rng):return normalize(rng.normal(size=4))


def proposal(rng,step,global_probability):
    if rng.random()<global_probability:return haar(rng)
    direction=rng.normal(size=3);norm=float(np.linalg.norm(direction))
    if norm==0:return (1.,0.,0.,0.)
    scale=math.sin(step)/norm
    return (math.cos(step),*(float(v)*scale for v in direction))


class Lattice:
    def __init__(self,shape,rng,start='hot'):
        if len(shape)!=3 or any(type(n) is not int or n<3 for n in shape):raise ValueError('Three periodic extents >=3 are required.')
        if start not in ('hot','cold'):raise ValueError('Choose hot or cold start.')
        self.shape=tuple(shape);self.coordinates=list(product(*(range(n) for n in shape)))
        self.index={x:i for i,x in enumerate(self.coordinates)}
        self.plus=[[self.index[tuple((x[j]+(1 if j==a else 0))%shape[j] for j in range(3))] for x in self.coordinates] for a in range(3)]
        self.links=[haar(rng) if start=='hot' else (1.,0.,0.,0.) for _ in range(3*len(self.coordinates))]
        self.plaquettes=[];self.incident=[[] for _ in self.links];self.spatial=[]
        for site in range(len(self.coordinates)):
            for a,b in combinations(range(3),2):
                edges=((3*site+a,1),(3*self.plus[a][site]+b,1),
                       (3*self.plus[b][site]+a,-1),(3*site+b,-1))
                p=len(self.plaquettes);self.plaquettes.append(edges)
                for link,_ in edges:self.incident[link].append(p)
                if (a,b)==(1,2):self.spatial.append((self.coordinates[site][0],p))
        if any(len(set(v))!=4 for v in self.incident):raise ValueError('Unexpected Wilson incidence geometry.')

    def plaquette(self,p):
        q=(1.,0.,0.,0.)
        for index,orientation in self.plaquettes[p]:
            link=self.links[index];q=multiply(q,link if orientation==1 else conjugate(link))
        return q[0]

    def trace_sum(self):return sum(self.plaquette(p) for p in range(len(self.plaquettes)))

    def update(self,index,beta,rng,step,global_probability):
        old=self.links[index];before=sum(self.plaquette(p) for p in self.incident[index])
        self.links[index]=normalize(multiply(proposal(rng,step,global_probability),old))
        after=sum(self.plaquette(p) for p in self.incident[index])
        delta=beta*(after-before)
        accepted=bool(rng.random()<math.exp(min(0.,delta)))
        if not accepted:self.links[index]=old
        return accepted

    def sweep(self,beta,rng,step,global_probability):
        return sum(self.update(i,beta,rng,step,global_probability) for i in range(len(self.links)))

    def scalar_operator(self):
        values=np.zeros(self.shape[0]);volume=self.shape[1]*self.shape[2]
        for time,p in self.spatial:values[time]+=1-self.plaquette(p)
        return (values/math.sqrt(volume)).tolist()


def run(beta,shape=(8,3,3),seeds=(101,202),starts=('hot','cold'),warmup=64,
        samples=32,sweeps_between=2,step=.6,global_probability=.1,max_updates=2000000):
    if isinstance(beta,bool) or not math.isfinite(float(beta)) or beta<0:raise ValueError('beta must be finite and nonnegative.')
    if not math.isfinite(step) or not 0<step<math.pi or not math.isfinite(global_probability) or not 0<global_probability<=1:
        raise ValueError('Require 0<step<pi and 0<global_probability<=1.')
    if len(shape)!=3 or any(type(v) is not int or v<3 for v in shape) or shape[0]<6:raise ValueError('Use periodic [time>=6,space>=3,space>=3].')
    for value,minimum in ((warmup,0),(samples,2),(sweeps_between,1),(max_updates,1)):
        if type(value) is not int or value<minimum:raise ValueError('Invalid integer sampling control.')
    if not seeds or len(seeds)!=len(starts) or len(set(seeds))!=len(seeds) or any(type(s) is not int or s<0 for s in seeds):
        raise ValueError('Supply unique nonnegative integer seeds and one start for each.')
    if any(v not in ('hot','cold') for v in starts):raise ValueError('Choose hot or cold starts.')
    updates=len(seeds)*3*math.prod(shape)*(warmup+samples*sweeps_between)
    if updates>max_updates:raise ValueError(f'Requested {updates} updates exceeds max_updates={max_updates}.')
    chains=[];diagnostics=[]
    for seed,start in zip(seeds,starts):
        rng=np.random.Generator(np.random.PCG64(seed));lattice=Lattice(shape,rng,start)
        warm_accept=sum(lattice.sweep(beta,rng,step,global_probability) for _ in range(warmup))
        accepted=0;measurements=[];plaquettes=[];ids=[]
        for index in range(samples):
            accepted+=sum(lattice.sweep(beta,rng,step,global_probability) for _ in range(sweeps_between))
            measurements.append([[v] for v in lattice.scalar_operator()])
            plaquettes.append(lattice.trace_sum()/len(lattice.plaquettes))
            ids.append(warmup+(index+1)*sweeps_between)
        values=np.asarray(lattice.links,dtype='<f8')
        diagnostics.append({'chain_id':f'seed_{seed}','seed':seed,'start':start,
                            'warmup_acceptance':warm_accept/(warmup*len(lattice.links)) if warmup else None,
                            'measurement_acceptance':accepted/(samples*sweeps_between*len(lattice.links)),
                            'saved_mean_plaquette':plaquettes,
                            'first_half_plaquette_mean':float(np.mean(plaquettes[:samples//2])),
                            'second_half_plaquette_mean':float(np.mean(plaquettes[samples//2:])),
                            'maximum_final_unit_norm_error':float(np.max(np.abs(np.sum(values**2,axis=1)-1))),
                            'final_configuration_sha256_float64_little_endian':hashlib.sha256(values.tobytes()).hexdigest()})
        chains.append({'chain_id':f'seed_{seed}','configuration_ids':ids,'measurements':measurements})
    return {'schema_version':'ym3d.glueball_operator_samples.v1','data_kind':'sampled_ensemble',
            'gauge_group':'SU(2)','spacetime_dimensions':3,'boundary':'periodic_time',
            'spatial_volume':shape[1]*shape[2],'time_extent':shape[0],'temporal_spacing':1,
            'time_unit':'lattice_time','operator_normalization':'spatial_sum_div_sqrt_volume',
            'operators':['spatial_plaquette_1_minus_normalized_trace'],'chains':chains,
            'ensemble_metadata':{'schema_version':'ym3d.su2_wilson_pilot.v1',
                'status':'EXPLORATORY_GAUGE_ENSEMBLE_NOT_A_MASS_MEASUREMENT',
                'action':'exp(beta*sum_plaquettes(Tr(U_p)/2))','wilson_beta':float(beta),
                'lattice_shape_time_x_y':list(shape),'boundary_all_axes':'periodic',
                'algorithm':'sequential-link Metropolis; symmetric fixed-angle/Haar-mixture left multiplication',
                'proposal_angle_radians':step,'haar_proposal_probability':global_probability,
                'warmup_sweeps_omitted':warmup,'saved_samples_per_chain':samples,
                'sweeps_between_saved_configurations':sweeps_between,'requested_link_updates':updates,
                'random_generator':'PCG64','numpy_version':np.__version__,
                'sampler_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'chain_diagnostics':diagnostics,
                'qualifications':['Actual sampled finite-volume SU(2) links; no constructed spectral input.',
                                  'Warmup, mixing, autocorrelation and finite-volume adequacy are not established by this pilot.',
                                  'A successful fit is not an accepted glueball mass; no continuum/analytic claim.']}}
