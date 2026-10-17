"""Generalized-eigenvalue diagnostics and fixed variational projections."""
import numpy as np
from scipy.optimize import linear_sum_assignment
from glueball_spectroscopy.spectrum import connected_input,number


def assignment(reference,candidates,metric=None):
    """Match columns by maximum total normalized squared overlap."""
    if reference.shape!=candidates.shape:raise ValueError('Mode shapes differ.')
    if metric is None:metric=np.eye(reference.shape[0])
    left=np.einsum('ik,ij,jk->k',reference,metric,reference)
    right=np.einsum('ik,ij,jk->k',candidates,metric,candidates)
    if np.any(left<=0) or np.any(right<=0):raise ValueError('Nonpositive mode matching norm.')
    signed=(reference.T@metric@candidates)/np.sqrt(left[:,None]*right[None,:])
    scores=np.abs(signed)**2
    rows,columns=linear_sum_assignment(scores,maximize=True)
    if not np.array_equal(rows,np.arange(reference.shape[1])):raise ValueError('Incomplete mode assignment.')
    phases=np.where(signed[rows,columns]<0,-1.,1.)
    return columns,phases,scores[rows,columns]


def track_frames(values,vectors,anchor,reference_index=0,overlap_warning=.65,degeneracy_tolerance=1e-5):
    """Track labels away from anchor, exempting the degenerate t0 identity frame."""
    values=np.asarray(values,dtype=float);vectors=np.asarray(vectors,dtype=float)
    tracked_values=values.copy();tracked_vectors=vectors.copy()
    count,rank=values.shape
    overlaps=np.ones((count,rank));permutations=np.tile(np.arange(rank),(count,1));issues=[]
    anchor_scale=max(float(np.max(np.abs(values[anchor]))),np.finfo(float).tiny)
    if rank>1 and np.any(np.abs(np.diff(np.sort(values[anchor])))<=degeneracy_tolerance*anchor_scale):
        issues.append({'kind':'NEAR_DEGENERATE_MODES','frame':anchor})
    for indices in (range(anchor+1,count),range(anchor-1,-1,-1)):
        previous=anchor
        for i in indices:
            if i==reference_index:
                tracked_values[i]=np.ones(rank);tracked_vectors[i]=tracked_vectors[anchor]
                continue
            order,phase,score=assignment(tracked_vectors[previous],vectors[i])
            tracked_values[i]=values[i,order];tracked_vectors[i]=vectors[i][:,order]*phase
            overlaps[i]=score;permutations[i]=order
            if np.any(score<overlap_warning):issues.append({'kind':'LOW_MODE_OVERLAP','frame':i,'minimum':float(score.min())})
            scale=max(float(np.max(np.abs(values[i]))),np.finfo(float).tiny)
            if rank>1 and np.any(np.abs(np.diff(np.sort(values[i])))<=degeneracy_tolerance*scale):
                issues.append({'kind':'NEAR_DEGENERATE_MODES','frame':i})
            previous=i
    return tracked_values,tracked_vectors,overlaps,permutations,issues


def solve(data,t0=0,reference_time=1,rank_cutoff=1e-10,central=None):
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            times,a_t,c,asymmetry=connected_input(data)
    except (FloatingPointError,OverflowError) as exc:raise ValueError('Numerical overflow during input normalization.') from exc
    if not np.isfinite(c).all():raise ValueError('Connected matrices must be finite.')
    if type(t0) is not int or type(reference_time) is not int or t0 not in times or reference_time not in times or reference_time<=t0:
        raise ValueError('Choose available integer times reference_time > t0.')
    cutoff=number(rank_cutoff)
    if not 0<cutoff<1:raise ValueError('rank_cutoff must lie between zero and one.')
    i0=times.index(t0);anchor=times.index(reference_time)-i0;metric=c[i0]
    ev,u=np.linalg.eigh(metric)
    if ev[-1]<=0 or ev[0]<-1e-10*ev[-1]:raise ValueError('Invalid reference metric.')
    keep=ev>cutoff*ev[-1];w=u[:,keep]/np.sqrt(ev[keep])[None,:]
    eigenvalues=[];frames=[]
    for matrix in c[i0:]:
        reduced=w.T@matrix@w;reduced=(reduced+reduced.T)/2
        vals,vec=np.linalg.eigh(reduced);order=np.argsort(vals)[::-1]
        eigenvalues.append(vals[order]);frames.append(vec[:,order])
    eigenvalues=np.asarray(eigenvalues);frames=np.asarray(frames)
    alignment=np.ones(int(keep.sum()))
    if central is not None:
        if int(keep.sum())!=central['rank']:raise ValueError('Bootstrap replica changes retained metric rank.')
        order,phase,alignment=assignment(central['basis'],w@frames[anchor],central['metric'])
        frames[anchor]=frames[anchor][:,order]*phase;eigenvalues[anchor]=eigenvalues[anchor,order]
    tracked,tracked_frames,overlap,orders,issues=track_frames(eigenvalues,frames,anchor)
    basis=w@tracked_frames[anchor]
    projected=np.einsum('ik,tij,jk->tk',basis,c,basis)
    if not np.isfinite(projected).all():raise ValueError('Nonfinite fixed-basis projection.')
    if np.any(alignment<.65):issues.append({'kind':'AMBIGUOUS_BOOTSTRAP_ALIGNMENT','minimum':float(alignment.min())})
    if int(keep.sum())<len(ev):issues.append({'kind':'REFERENCE_RANK_REDUCED','discarded':int((~keep).sum())})
    for issue in issues:
        if 'frame' in issue:issue['time']=times[i0+issue['frame']]
    return {'times':times,'a_t':a_t,'connected':c,'metric':metric,'basis':basis,
            'rank':int(keep.sum()),'tracked_times':times[i0:],'tracked_principal':tracked,
            'matching_overlaps':overlap,'mode_permutations':orders,'projected':projected,
            'bootstrap_alignment':alignment,'issues':issues,'input_asymmetry_max':asymmetry,
            'reference_condition_number':float(ev[keep][-1]/ev[keep][0]),
            'basis_labels':'reference-time variational modes; not certified physical state identities'}
