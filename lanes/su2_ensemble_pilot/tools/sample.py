#!/usr/bin/env python3
"""Generate a small actual SU(2) Wilson pilot with explicit sampling controls."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from su2_pilot.sampler import run


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--beta',type=float,required=True)
    p.add_argument('--time-extent',type=int,default=8);p.add_argument('--spatial-extent',type=int,default=3)
    p.add_argument('--seed',type=int,action='append',required=True)
    p.add_argument('--start',choices=['hot','cold'],action='append',required=True)
    p.add_argument('--warmup',type=int,required=True);p.add_argument('--samples',type=int,required=True)
    p.add_argument('--sweeps-between',type=int,required=True);p.add_argument('--proposal-angle',type=float,default=.6)
    p.add_argument('--haar-probability',type=float,default=.1);p.add_argument('--max-updates',type=int,default=2000000)
    a=p.parse_args()
    try:
        result=run(a.beta,(a.time_extent,a.spatial_extent,a.spatial_extent),a.seed,a.start,
                   a.warmup,a.samples,a.sweeps_between,a.proposal_angle,a.haar_probability,a.max_updates)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    except (ValueError,TypeError,OSError,ArithmeticError) as exc:
        print(f'Sampling rejected: {exc}',file=sys.stderr);return 2
    print(f'Wrote {a.output}; {len(a.seed)*a.samples} sampled gauge configurations. Exploratory pilot only.')
    return 0
if __name__=='__main__':raise SystemExit(main())
