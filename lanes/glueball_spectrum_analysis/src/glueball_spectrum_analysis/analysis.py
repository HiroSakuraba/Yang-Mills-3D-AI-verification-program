"""Numerical-only orchestration: tracked modes, fixed projections and fit windows."""
import itertools,math
import numpy as np
import scipy
from glueball_spectroscopy.spectrum import number,real_array
from .modes import solve
from .fits import fit_curve


def make_windows(times,reference_time,windows=None,scan_min_points=None):
    allowed=[t for t in times if t>=reference_time]
    if windows is not None and scan_min_points is not None:raise ValueError('Choose explicit windows or a scan, not both.')
    if scan_min_points is not None:
        if type(scan_min_points) is not int or scan_min_points<3:raise ValueError('Window scan requires at least three points.')
        windows=[(allowed[i],allowed[j]) for i in range(len(allowed)) for j in range(i+scan_min_points-1,len(allowed))]
    elif windows is None:
        windows=[(allowed[0],allowed[-1])]
    if not windows or len(windows)>128:raise ValueError('Supply between one and 128 fit windows.')
    result=[]
    for window in windows:
        if len(window)!=2 or any(type(t) is not int for t in window):raise ValueError('Window endpoints must be integer time indices.')
        start,stop=window
        if start not in allowed or stop not in allowed or start>=stop:raise ValueError('Window endpoints must be available times at/after reference_time.')
        indices=[i for i,t in enumerate(times) if start<=t<=stop]
        if len(indices)<3:raise ValueError('Every fit window needs at least three points.')
        if (start,stop) not in [v[:2] for v in result]:result.append((start,stop,indices))
    return result


def effective_masses(solution,boundary):
    times=solution['times'];curves=solution['projected'];a_t=solution['a_t'];values=[];out_times=[]
    if boundary=='zero_temperature':indices=range(len(times)-1)
    else:indices=range(1,len(times)-1)
    for i in indices:
        row=[]
        for state in range(solution['rank']):
            value=None
            if boundary=='zero_temperature':
                left,right=curves[i,state],curves[i+1,state]
                if left>0 and right>0:
                    m=math.log(left/right)/((times[i+1]-times[i])*a_t)
                    if math.isfinite(m) and m>=0:value=m
            else:
                left,mid,right=curves[i-1,state],curves[i,state],curves[i+1,state]
                if min(left,mid,right)>0:
                    arg=(left+right)/(2*mid)
                    if arg>=1:value=math.acosh(arg)/a_t
            row.append(value)
        values.append(row);out_times.append(times[i])
    return {'times':out_times,'values':values,'basis':'fixed_reference_time_variational_projection'}


def bootstrap_solutions(data,central,t0,reference_time,rank_cutoff):
    boot=data.get('bootstrap')
    if boot is None:return []
    if not isinstance(boot,dict) or type(boot.get('block_size')) is not int or boot['block_size']<1 or not isinstance(boot.get('resampling_unit'),str) or not boot['resampling_unit'].strip():
        raise ValueError('Bootstrap requires positive block_size and resampling_unit metadata.')
    replicas=boot.get('replicas')
    if not isinstance(replicas,list) or len(replicas)<2:raise ValueError('Supply at least two bootstrap replicas.')
    output=[]
    for index,rep in enumerate(replicas):
        if not isinstance(rep,dict) or 'correlators' not in rep:raise ValueError('Invalid bootstrap replica.')
        item={k:v for k,v in data.items() if k!='bootstrap'};item['correlators']=rep['correlators']
        if not data['vacuum_subtracted']:
            if 'operator_means' not in rep:raise ValueError('Each raw replica needs its own operator_means.')
            item['operator_means']=rep['operator_means']
        result=solve(item,t0,reference_time,rank_cutoff,central)
        if any(v['kind']=='AMBIGUOUS_BOOTSTRAP_ALIGNMENT' for v in result['issues']):
            raise ValueError(f'Bootstrap replica {index} has ambiguous mode alignment; no mass uncertainty summary emitted.')
        output.append(result)
    return output


def paired_window_stability(fits,threshold=2.):
    output=[]
    states=sorted({f['state'] for f in fits})
    for state in states:
        usable=[f for f in fits if f['state']==state and 'mass' in f]
        pairs=[];warning=False
        for a,b in itertools.combinations(usable,2):
            ra=a.get('bootstrap_mass_samples');rb=b.get('bootstrap_mass_samples')
            entry={'windows':[a['window'],b['window']],'mass_difference':a['mass']-b['mass'],
                   'paired_bootstrap_standard_error':None,'diagnostic_z':None}
            if ra is not None and rb is not None and len(ra)==len(rb) and all(v is not None for v in ra+rb):
                sigma=float(np.std(np.array(ra)-np.array(rb),ddof=1));entry['paired_bootstrap_standard_error']=sigma
                delta=abs(entry['mass_difference'])
                z=delta/sigma if sigma>0 else None
                entry['diagnostic_z']=z
                entry['flagged']=bool(z>threshold) if z is not None else bool(delta>1e-7*max(1.,abs(a['mass']),abs(b['mass'])))
                warning|=entry['flagged']
            pairs.append(entry)
        masses=[f['mass'] for f in usable]
        output.append({'state':state,'usable_windows':len(usable),'mass_span':max(masses)-min(masses) if masses else None,
                       'paired_comparisons':pairs,'issues':['WINDOW_DEPENDENCE'] if warning else [],
                       'qualification':'Paired-bootstrap shift diagnostic only; overlapping windows and multiple comparisons do not establish a plateau.'})
    return output


def analyze(data,t0=0,reference_time=1,windows=None,scan_min_points=None,mass_bounds=(1e-6,5.),
            rank_cutoff=1e-10,covariance_cutoff=1e-10,shrinkage=0.,states=None):
    lo,hi=map(number,mass_bounds);cut=number(covariance_cutoff);shrink=number(shrinkage)
    if not 0<lo<hi or not 0<cut<1 or not 0<=shrink<=1:raise ValueError('Invalid mass bounds/covariance controls.')
    central=solve(data,t0,reference_time,rank_cutoff)
    selected_states=list(range(central['rank'])) if states is None else list(states)
    if not selected_states or len(set(selected_states))!=len(selected_states) or any(type(i) is not int or not 0<=i<central['rank'] for i in selected_states):
        raise ValueError('State indices must be unique retained-mode indices.')
    fit_windows=make_windows(central['times'],reference_time,windows,scan_min_points)
    replicas=bootstrap_solutions(data,central,t0,reference_time,rank_cutoff)
    covariance=None;source='identity_diagnostic'
    if 'projected_covariances' in data:
        if data.get('covariance_basis')!='fixed_reference_modes' or data.get('covariance_kind')!='covariance_of_mean':
            raise ValueError('Declare fixed_reference_modes covariance_of_mean metadata.')
        covariance=real_array(data['projected_covariances'])
        size=len(central['times'])
        if covariance.shape!=(central['rank'],size,size):raise ValueError('Projected covariance shape mismatch.')
        source='user_supplied_covariance_of_mean'
    elif replicas:
        curves=np.asarray([s['projected'] for s in replicas])
        covariance=np.asarray([np.cov(curves[:,:,state],rowvar=False,ddof=1) for state in range(central['rank'])])
        source='bootstrap_estimator_covariance_not_divided_by_replica_count'
    elif shrink:raise ValueError('Shrinkage requires covariance information.')
    fits=[]
    for state in selected_states:
        for start,stop,indices in fit_windows:
            times=[central['times'][i] for i in indices]
            cov=covariance[state][np.ix_(indices,indices)] if covariance is not None else None
            record={'state':state,'window':[start,stop],'times':times,'covariance_source':source}
            try:
                result=fit_curve(times,central['projected'][indices,state],central['a_t'],data['boundary'],(lo,hi),cov,
                                 data.get('time_extent'),cut,shrink)
                record.update(result)
            except ValueError as exc:
                record.update(window_status='REJECTED',reason=str(exc));fits.append(record);continue
            if replicas:
                masses=[];failures=[]
                for index,rep in enumerate(replicas):
                    try:
                        r=fit_curve(times,rep['projected'][indices,state],central['a_t'],data['boundary'],(lo,hi),cov,
                                    data.get('time_extent'),cut,shrink)
                        if 'MASS_AT_SEARCH_BOUND' in r['issues'] or not r['optimizer_success']:raise ValueError('Replica fit reached search bound or failed optimization.')
                        masses.append(r['mass'])
                    except ValueError as exc:
                        masses.append(None);failures.append({'replica':index,'reason':str(exc)})
                record['bootstrap_mass_samples']=masses;record['bootstrap_fit_failures']=failures
                if failures:
                    record['mass_standard_error_bootstrap']=None;record['mass_percentile_16_84']=None
                    record['issues'].append('BOOTSTRAP_FIT_FAILURE');record['window_status']='FLAGGED'
                else:
                    record['mass_standard_error_bootstrap']=float(np.std(masses,ddof=1))
                    record['mass_percentile_16_84']=np.quantile(masses,[.16,.84]).tolist()
            fits.append(record)
    report={'schema_version':'ym3d.glueball_spectrum_analysis.v2','status':'NUMERICAL_DIAGNOSTIC',
            'data_kind':data.get('data_kind','user_supplied'),'gauge_group':'SU(2)','spacetime_dimensions':3,
            't0':t0,'reference_time':reference_time,'temporal_spacing':central['a_t'],'time_unit':data['time_unit'],
            'mass_unit':'1/'+data['time_unit'],'spatial_volume':data['spatial_volume'],
            'operator_normalization':data['operator_normalization'],'metric_rank':central['rank'],
            'rank_cutoff':rank_cutoff,'reference_condition_number':central['reference_condition_number'],
            'tracking':{'times':central['tracked_times'],'principal_correlators':central['tracked_principal'].tolist(),
                        'squared_overlaps':central['matching_overlaps'].tolist(),'permutations':central['mode_permutations'].tolist(),
                        'issues':central['issues']},
            'fixed_projection':{'times':central['times'],'vectors':central['basis'].tolist(),'correlators':central['projected'].tolist(),
                                'label_qualification':central['basis_labels']},
            'effective_masses':effective_masses(central,data['boundary']),'fits':fits,
            'window_stability':paired_window_stability(fits),'selected_window':None,'plateau_status':'NOT_AUTOMATICALLY_SELECTED',
            'backend':{'numpy':np.__version__,'scipy':scipy.__version__},
            'non_claims':['No proof-gate decision, certified mass interval or isolated-particle identification',
                          'No removal of finite-volume, excited-state or discretization effects',
                          'Periodic cosh model assumes vacuum dominance; thermal transitions are omitted',
                          'Mode overlap tracks numerical vectors and cannot resolve genuinely degenerate physical states']}
    if replicas:
        report['bootstrap']={'replica_count':len(replicas),'block_size':data['bootstrap']['block_size'],
                             'resampling_unit':data['bootstrap']['resampling_unit'],
                             'basis_strategy':'refit at reference_time in each replica, align in central C(t0) metric, then freeze over time',
                             'qualification':'Sampling/autocorrelation adequacy is user supplied. Weights stay fixed across replica fits; failed or boundary-censored fits withhold the uncertainty summary.'}
    if not any('mass' in f for f in fits):report['analysis_issue']='NO_USABLE_FITS'
    if 'ensemble_preparation' in data:
        report['ensemble_preparation']=data['ensemble_preparation']
    return report
