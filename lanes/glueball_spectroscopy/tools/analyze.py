#!/usr/bin/env python3
"""Analyze supplied real correlator matrices; no simulation or theorem closure."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from glueball_spectroscopy.spectrum import analyze


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--t0',type=int,default=0);parser.add_argument('--rank-cutoff',type=float,default=1e-10)
    args=parser.parse_args()
    try:
        report=analyze(json.loads(args.input.read_text()),args.t0,args.rank_cutoff)
        encoded=json.dumps(report,indent=2,allow_nan=False)+'\n'
    except (ValueError,ArithmeticError,KeyError,TypeError) as exc:
        print(f'Analysis rejected: {exc}',file=sys.stderr);return 2
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(encoded)
    print(f'Wrote {args.output}; NUMERICAL_DIAGNOSTIC only.');return 0
if __name__=='__main__':raise SystemExit(main())
