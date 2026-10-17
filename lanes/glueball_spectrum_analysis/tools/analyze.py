#!/usr/bin/env python3
"""Mode tracking and correlated mass fits; numerical diagnostics only."""
import argparse,csv,hashlib,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT.parent/'glueball_spectroscopy'/'src')]
from glueball_spectrum_analysis.analysis import analyze


def window(value):
    try:a,b=map(int,value.split(':'))
    except (ValueError,TypeError):raise argparse.ArgumentTypeError('Use START:STOP integer indices.')
    return a,b


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--csv',type=Path);parser.add_argument('--t0',type=int,default=0)
    parser.add_argument('--reference-time',type=int,default=1)
    group=parser.add_mutually_exclusive_group();group.add_argument('--window',action='append',type=window)
    group.add_argument('--scan-min-points',type=int)
    parser.add_argument('--state',type=int,action='append')
    parser.add_argument('--mass-min',type=float,default=1e-6);parser.add_argument('--mass-max',type=float,default=5.)
    parser.add_argument('--rank-cutoff',type=float,default=1e-10)
    parser.add_argument('--covariance-cutoff',type=float,default=1e-10)
    parser.add_argument('--shrinkage',type=float,default=0.)
    args=parser.parse_args()
    if args.output.resolve()==args.input.resolve() or (args.csv is not None and args.csv.resolve()==args.input.resolve()):
        parser.error('Outputs must not overwrite the input data.')
    if args.csv is not None and args.csv.resolve()==args.output.resolve():parser.error('JSON and CSV outputs must differ.')
    try:
        raw=args.input.read_bytes();data=json.loads(raw)
        result=analyze(data,args.t0,args.reference_time,args.window,args.scan_min_points,
                       (args.mass_min,args.mass_max),args.rank_cutoff,args.covariance_cutoff,args.shrinkage,args.state)
        result['input_sha256']=hashlib.sha256(raw).hexdigest()
        encoded=json.dumps(result,indent=2,allow_nan=False)+'\n'
    except (ValueError,TypeError,KeyError,ArithmeticError,np.linalg.LinAlgError,OSError) as exc:
        print(f'Analysis rejected: {exc}',file=sys.stderr);return 2
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(encoded)
    if args.csv:
        args.csv.parent.mkdir(parents=True,exist_ok=True)
        fields=['state','start','stop','mass','mass_standard_error_bootstrap','mass_standard_error_linearized',
                'chi_square','degrees_of_freedom','p_value_diagnostic','window_status','issues','reason']
        with args.csv.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            for r in result['fits']:
                row={k:r.get(k) for k in fields};row.update(start=r['window'][0],stop=r['window'][1],issues=';'.join(r.get('issues',[])))
                writer.writerow(row)
    print(f"Wrote {args.output}; {sum('mass' in f for f in result['fits'])} fit candidates, no plateau automatically selected.")
    return 0
if __name__=='__main__':raise SystemExit(main())
