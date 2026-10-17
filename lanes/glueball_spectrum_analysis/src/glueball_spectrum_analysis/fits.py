"""Correlated single-exponential/cosh fits, with explicit numerical qualifications."""
import math
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import chi2


def covariance_weight(covariance,size,cutoff=1e-10,shrinkage=0.):
    if not 0<cutoff<1 or not 0<=shrinkage<=1:raise ValueError('Invalid covariance cutoff or shrinkage.')
    cov=np.asarray(covariance,dtype=float)
    if cov.shape!=(size,size) or not np.isfinite(cov).all():raise ValueError('Invalid fit covariance dimensions/values.')
    scale=max(float(np.max(np.abs(cov))),np.finfo(float).tiny)
    if np.max(np.abs(cov-cov.T))>1e-10*scale:raise ValueError('Fit covariance is not symmetric.')
    cov=(cov+cov.T)/2
    raw=np.linalg.eigvalsh(cov)
    if raw[-1]<=0 or raw[0]<-1e-10*raw[-1]:raise ValueError('Fit covariance is not positive semidefinite.')
    cov=(1-shrinkage)*cov+shrinkage*np.diag(np.diag(cov))
    ev,u=np.linalg.eigh(cov);keep=ev>cutoff*ev[-1]
    rank=int(keep.sum())
    if rank<=2:raise ValueError('Fit covariance retains too few modes for two fit parameters.')
    w=(u[:,keep]/ev[keep][None,:])@u[:,keep].T
    return w,{'rank':rank,'points':size,'condition_number':float(ev[keep][-1]/ev[keep][0]),
              'relative_cutoff':cutoff,'shrinkage':shrinkage}


def shape_and_derivative(mass,times,a_t,boundary,extent=None):
    times=np.asarray(times,dtype=float)
    if boundary=='zero_temperature':
        shifted=(times-times[0])*a_t;f=np.exp(-mass*shifted)
        return f,-shifted*f
    if boundary!='periodic_time' or extent is None:raise ValueError('Unknown fit time boundary.')
    forward=np.exp(-mass*a_t*times);backward=np.exp(-mass*a_t*(extent-times))
    g=forward+backward;derivative=-a_t*(times*forward+(extent-times)*backward)
    if g[0]<=0 or not np.isfinite(g).all():raise ValueError('Periodic model underflow/overflow.')
    f=g/g[0];df=(derivative-f*derivative[0])/g[0]
    return f,df


def fit_curve(times,y,a_t,boundary,mass_bounds,covariance=None,extent=None,covariance_cutoff=1e-10,shrinkage=0.):
    times=np.asarray(times,dtype=float);y=np.asarray(y,dtype=float)
    if len(times)<3 or y.shape!=times.shape or not np.isfinite(y).all() or np.any(y<=0):
        raise ValueError('Fits require at least three finite positive projected correlators.')
    if np.any(np.diff(times)<=0) or not math.isfinite(a_t) or a_t<=0:raise ValueError('Invalid fit time coordinates.')
    lo,hi=mass_bounds
    if not (math.isfinite(lo) and math.isfinite(hi) and 0<lo<hi):raise ValueError('Finite positive ordered mass bounds required.')
    known_covariance=covariance is not None
    if known_covariance:w,info=covariance_weight(covariance,len(y),covariance_cutoff,shrinkage)
    else:w=np.eye(len(y));info={'rank':len(y),'points':len(y),'condition_number':1.,'relative_cutoff':None,'shrinkage':0.}
    def profile(m):
        try:
            f,_=shape_and_derivative(m,times,a_t,boundary,extent)
            denominator=float(f@w@f)
            if denominator<=0:return math.inf,None
            amplitude=float(f@w@y)/denominator
            if amplitude<=0:return math.inf,None
            residual=y-amplitude*f;value=float(residual@w@residual)
            return max(0.,value),amplitude
        except (ValueError,FloatingPointError):return math.inf,None
    grid=np.linspace(lo,hi,65);scores=[profile(m)[0] for m in grid]
    best=int(np.argmin(scores))
    left=grid[max(0,best-1)];right=grid[min(len(grid)-1,best+1)]
    result=minimize_scalar(lambda m:profile(m)[0],bounds=(left,right),method='bounded',options={'xatol':1e-12,'maxiter':500})
    candidates=[(float(grid[best]),scores[best]),(lo,profile(lo)[0]),(hi,profile(hi)[0])]
    if result.success:candidates.append((float(result.x),profile(float(result.x))[0]))
    mass,value=min(candidates,key=lambda item:item[1]);amplitude=profile(mass)[1]
    if not math.isfinite(value) or amplitude is None:raise ValueError('Mass fit did not find a finite positive-amplitude solution.')
    f,df=shape_and_derivative(mass,times,a_t,boundary,extent)
    j=np.column_stack((f,amplitude*df));information=j.T@w@j
    standard_error=None
    if known_covariance:
        ev=np.linalg.eigvalsh(information)
        if ev[0]>ev[-1]*1e-12:
            standard_error=math.sqrt(max(0.,float(np.linalg.inv(information)[1,1])))
    dof=info['rank']-2;issues=[]
    pvalue=float(chi2.sf(value,dof)) if known_covariance and dof>0 else None
    if not result.success:issues.append('OPTIMIZER_NOT_CONVERGED')
    if min(mass-lo,hi-mass)<=1e-4*(hi-lo):issues.append('MASS_AT_SEARCH_BOUND')
    if pvalue is not None and pvalue<.01:issues.append('POOR_SINGLE_STATE_FIT')
    if info['rank']<len(y):issues.append('COVARIANCE_RANK_REDUCED')
    if info['condition_number']>1e8:issues.append('ILL_CONDITIONED_COVARIANCE')
    if not known_covariance:issues.append('UNWEIGHTED_DIAGNOSTIC')
    if shrinkage:issues.append('SHRUNK_COVARIANCE')
    return {'mass':mass,'amplitude_at_window_start':amplitude,'mass_standard_error_linearized':standard_error,
            'chi_square':value if known_covariance else None,'unweighted_residual_sum_squares':value if not known_covariance else None,
            'degrees_of_freedom':dof if known_covariance else None,'p_value_diagnostic':pvalue,
            'covariance':info,'optimizer_success':bool(result.success),'mass_bounds':[lo,hi],
            'model':'single_exponential' if boundary=='zero_temperature' else 'vacuum_dominated_periodic_cosh',
            'issues':issues,'window_status':'FLAGGED' if issues else 'CANDIDATE_FOR_REVIEW',
            'qualification':'Estimated or regularized covariance p-values and linearized errors are diagnostics; fit-window selection and omitted states are not included.'}
