"""Advisory real-correlator spectroscopy. Floating-point estimates, never proof decisions."""
from fractions import Fraction
import math
import numpy as np
from .operators import anchored_vertices


def number(value):
    if isinstance(value,bool):raise ValueError('Boolean is not a numerical measurement.')
    try:out=float(Fraction(value)) if isinstance(value,str) else float(value)
    except (ValueError,TypeError,ZeroDivisionError,OverflowError) as e:raise ValueError('Invalid number.') from e
    if not math.isfinite(out):raise ValueError('Measurements must be finite.')
    return out


def real_array(values):
    try:return np.asarray(np.vectorize(number,otypes=[float])(values),dtype=float)
    except (TypeError,ValueError) as e:raise ValueError('Expected a rectangular array of finite real numbers.') from e


def trace_loop(path,links):
    """Normalized real SU(2) trace of a closed spatial loop.

    links[(x,y,axis)] stores a positive-oriented 2x2 SU(2) matrix, axis=0,1.
    The caller owns link unitarity/gauge-group validation.
    """
    points=anchored_vertices(path);matrix=np.eye(2,dtype=complex)
    for p,q in zip(points,points[1:]):
        axis=0 if p[0]!=q[0] else 1
        positive=q[axis]>p[axis];start=p if positive else q
        u=np.asarray(links[(*start,axis)],dtype=complex)
        if u.shape!=(2,2) or not np.isfinite(u).all():raise ValueError('Invalid link matrix.')
        matrix=matrix@(u if positive else u.conj().T)
    return float(np.trace(matrix).real/2)


def evaluate_operator(op,links):
    """Uncentered local P=1-average(W); ensemble centering is a separate operation."""
    return 1-sum(trace_loop(p,links) for p in op['orbit_paths'])/len(op['orbit_paths'])


def connected_input(data):
    if data.get('schema_version')!='ym3d.glueball_correlators.v1':raise ValueError('Unsupported correlator schema.')
    if data.get('gauge_group')!='SU(2)' or data.get('spacetime_dimensions')!=3:
        raise ValueError('This lane accepts 2+1-dimensional SU(2) metadata only.')
    if data.get('operator_normalization')!='spatial_sum_div_sqrt_volume' or type(data.get('spatial_volume')) is not int or data['spatial_volume']<1:
        raise ValueError('Declare spatial_sum_div_sqrt_volume normalization and positive spatial_volume.')
    if not isinstance(data.get('time_unit'),str) or not data['time_unit'].strip():raise ValueError('Declare time_unit.')
    names=data.get('operators')
    if not isinstance(names,list) or not names or any(not isinstance(v,str) or not v for v in names) or len(set(names))!=len(names):
        raise ValueError('Supply unique operator names.')
    times=data.get('times')
    if not isinstance(times,list) or len(times)<3 or any(type(t) is not int or t<0 for t in times) or any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError('At least three increasing nonnegative integer time indices are required.')
    a_t=number(data.get('temporal_spacing'))
    if a_t<=0:raise ValueError('temporal_spacing must be positive.')
    boundary=data.get('boundary')
    if boundary not in ('zero_temperature','periodic_time'):raise ValueError('Declare the time boundary condition.')
    if boundary=='periodic_time':
        extent=data.get('time_extent')
        if type(extent) is not int or extent<3 or times[-1]>=extent:raise ValueError('Invalid periodic time extent.')
        if any(b-a!=1 for a,b in zip(times,times[1:])):raise ValueError('Periodic acosh masses require consecutive time indices.')
    c=real_array(data.get('correlators'))
    n=len(names)
    if c.shape!=(len(times),n,n):raise ValueError('Correlator dimensions do not match operators/times.')
    flag=data.get('vacuum_subtracted')
    if type(flag) is not bool:raise ValueError('Explicit vacuum_subtracted flag required.')
    if not flag:
        if 'operator_means' not in data:raise ValueError('Raw correlators require operator_means.')
        means=real_array(data['operator_means'])
        if means.shape!=(n,):raise ValueError('operator_means shape mismatch.')
        c=c-np.outer(means,means)[None,:,:]
    asymmetry=float(np.max(np.abs(c-np.swapaxes(c,1,2))))
    if asymmetry>1e-10*max(1.,float(np.max(np.abs(c)))):raise ValueError('Correlator matrices must be symmetric.')
    c=(c+np.swapaxes(c,1,2))/2
    return times,a_t,c,asymmetry


def _solve(data,t0,rank_cutoff):
    times,a_t,c,asymmetry=connected_input(data)
    if type(t0) is not int or t0 not in times or t0==times[-1]:raise ValueError('t0 must be an available non-final integer time.')
    cutoff=number(rank_cutoff)
    if not 0<cutoff<1:raise ValueError('rank_cutoff must be between zero and one.')
    i0=times.index(t0);metric=c[i0]
    eigenvalues,vectors=np.linalg.eigh(metric)
    largest=float(eigenvalues[-1])
    if largest<=0 or float(eigenvalues[0]) < -1e-10*largest:
        raise ValueError('Reference matrix has no valid positive-semidefinite metric.')
    keep=eigenvalues>largest*cutoff
    w=vectors[:,keep]/np.sqrt(eigenvalues[keep])[None,:]
    if not np.isfinite(w).all():raise ValueError('Unstable reference whitening.')
    values=[];residual=0.
    for matrix in c[i0:]:
        reduced=w.T@matrix@w;reduced=(reduced+reduced.T)/2
        vals,vecs=np.linalg.eigh(reduced);order=np.argsort(vals)[::-1]
        vals,vecs=vals[order],vecs[:,order]
        residual=max(residual,float(np.linalg.norm(reduced@vecs-vecs*vals[None,:])))
        values.append(vals)
    principal=np.asarray(values);selected=times[i0:];issues=[]
    if int(keep.sum())<len(keep):issues.append({'kind':'METRIC_RANK_REDUCTION','discarded':int((~keep).sum())})
    masses=[];mass_times=[]
    if data['boundary']=='zero_temperature':
        for i in range(len(selected)-1):
            row=[]
            for state in range(principal.shape[1]):
                a,b=principal[i,state],principal[i+1,state]
                value=None
                if a>0 and b>0:
                    estimate=math.log(a/b)/((selected[i+1]-selected[i])*a_t)
                    if math.isfinite(estimate) and estimate>=0:value=estimate
                if value is None:issues.append({'kind':'INVALID_LOG_MASS','time':selected[i],'state':state})
                row.append(value)
            masses.append(row);mass_times.append(selected[i])
    else:
        issues.append({'kind':'PERIODIC_COSH_ASSUMPTION','detail':'Vacuum-dominated forward/backward ansatz; finite-temperature transitions are not modeled.'})
        for i in range(1,len(selected)-1):
            row=[]
            for state in range(principal.shape[1]):
                left,mid,right=principal[i-1,state],principal[i,state],principal[i+1,state]
                value=None
                if min(left,mid,right)>0:
                    arg=(left+right)/(2*mid)
                    if arg>=1:value=math.acosh(arg)/a_t
                if value is None:issues.append({'kind':'INVALID_ACOSH_MASS','time':selected[i],'state':state})
                row.append(value)
            masses.append(row);mass_times.append(selected[i])
    if not np.isfinite(principal).all():raise ValueError('Nonfinite principal correlator.')
    return {'schema_version':'ym3d.glueball_spectrum_report.v1','status':'NUMERICAL_DIAGNOSTIC',
            'data_kind':data.get('data_kind','user_supplied'),'t0':t0,'times':selected,
            'boundary':data['boundary'],'temporal_spacing':a_t,
            'spatial_volume':data['spatial_volume'],'operator_normalization':data['operator_normalization'],
            'mass_unit':'1/'+data['time_unit'],
            'vacuum_subtraction':'already_connected' if data['vacuum_subtracted'] else 'subtracted_operator_mean_outer_product',
            'metric_rank':int(keep.sum()),'operator_count':len(keep),'rank_cutoff':cutoff,
            'reference_condition_number':float(eigenvalues[keep][-1]/eigenvalues[keep][0]),
            'input_asymmetry_max':asymmetry,'projected_eigen_residual_max':residual,
            'principal_correlators':principal.tolist(),
            'effective_masses':{'times':mass_times,'values':masses},'issues':issues,
            'non_claims':['No automatically accepted plateau or isolated-particle identification',
                          'No certified eigenvalue enclosure or physical gap proof',
                          'Modes are sorted independently at each time; near crossings need operator-overlap tracking',
                          'Finite volume, omitted states and discretization effects are not removed']}


def analyze(data,t0=0,rank_cutoff=1e-10):
    report=_solve(data,t0,rank_cutoff)
    boot=data.get('bootstrap')
    if boot is None:return report
    if not isinstance(boot,dict) or type(boot.get('block_size')) is not int or boot['block_size']<1 or not isinstance(boot.get('resampling_unit'),str) or not boot['resampling_unit'].strip():
        raise ValueError('Bootstrap requires block_size >= 1 and resampling_unit metadata.')
    replicas=boot.get('replicas')
    if not isinstance(replicas,list) or len(replicas)<2:raise ValueError('At least two bootstrap replicas required.')
    values=[]
    for index,replica in enumerate(replicas):
        if not isinstance(replica,dict) or 'correlators' not in replica:raise ValueError('Invalid bootstrap replica.')
        item={k:v for k,v in data.items() if k!='bootstrap'};item['correlators']=replica['correlators']
        if not data['vacuum_subtracted']:
            if 'operator_means' not in replica:raise ValueError('Raw bootstrap replicas require their own operator_means.')
            item['operator_means']=replica['operator_means']
        result=_solve(item,t0,rank_cutoff)
        if result['metric_rank']!=report['metric_rank']:raise ValueError(f'Bootstrap replica {index} changes metric rank; no uncertainty summary emitted.')
        values.append(result['effective_masses']['values'])
    summary=[]
    for ti in range(len(report['effective_masses']['times'])):
        row=[]
        for state in range(report['metric_rank']):
            cell=[v[ti][state] for v in values]
            invalid=sum(v is None for v in cell)
            if invalid:row.append({'standard_error':None,'percentile_16_84':None,'invalid_replicas':invalid})
            else:
                q=np.quantile(cell,[.16,.84]);row.append({'standard_error':float(np.std(cell,ddof=1)),
                                                       'percentile_16_84':q.tolist(),'invalid_replicas':0})
        summary.append(row)
    report['bootstrap']={'replica_count':len(replicas),'block_size':boot['block_size'],
                         'resampling_unit':boot['resampling_unit'],'effective_mass_uncertainties':summary,
                         'qualification':'Uses supplied replicas; block size and autocorrelation adequacy are not independently validated.'}
    return report
