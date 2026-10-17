#!/usr/bin/env python3
"""Reproduce two small gauge pilots and four blocked analysis reports, or summarize existing ones."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ANALYSIS=ROOT.parent/'glueball_spectrum_analysis'/'tools'


def execute(script,*arguments):
    subprocess.run([sys.executable,str(script),*map(str,arguments)],check=True)


def summarize(directory):
    results=[]
    for size in (3,4):
        sample_path=directory/f'pilot_L{size}_operator_samples.json'
        samples=json.loads(sample_path.read_text());meta=samples['ensemble_metadata']
        row={'spatial_extent':size,'time_extent':samples['time_extent'],
             'sample_file':sample_path.name,'sample_sha256':hashlib.sha256(sample_path.read_bytes()).hexdigest(),
             'configuration_count':sum(len(c['configuration_ids']) for c in samples['chains']),
             'chains':[{key:c[key] for key in ('chain_id','seed','start','measurement_acceptance',
                        'first_half_plaquette_mean','second_half_plaquette_mean','maximum_final_unit_norm_error')}
                       for c in meta['chain_diagnostics']], 'analysis':[]}
        for block in (4,8):
            path=directory/f'pilot_L{size}_block{block}_report.json';report=json.loads(path.read_text())
            row['analysis'].append({'block_size':block,'report_file':path.name,
                'report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'fit_candidates':sum('mass' in f for f in report['fits']),
                'rejected_windows':[{'window':f['window'],'reason':f.get('reason')} for f in report['fits'] if f['window_status']=='REJECTED'],
                'nonpositive_projected_times':[t for t,curve in zip(report['fixed_projection']['times'],report['fixed_projection']['correlators']) if curve[0]<=0],
                'plateau_status':report['plateau_status']})
        results.append(row)
    return {'schema_version':'ym3d.su2_pilot_summary.v1','status':'EXPLORATORY_MEASURED_GAUGE_DATA',
            'accepted_glueball_mass':None,'volumes':results,
            'qualification':'Reports summarize an exploratory fixed-budget run. No adequacy, accepted mass, finite-volume correction or analytic theorem follows.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--summarize-only',action='store_true')
    a=p.parse_args();directory=a.output_dir.resolve();directory.mkdir(parents=True,exist_ok=True)
    if not a.summarize_only:
        for size in (3,4):
            samples=directory/f'pilot_L{size}_operator_samples.json'
            execute(ROOT/'tools'/'sample.py','--output',samples,'--beta',2,'--spatial-extent',size,'--time-extent',8,
                    '--seed',101,'--start','hot','--seed',202,'--start','cold','--warmup',128,'--samples',64,'--sweeps-between',4)
            for block in (4,8):
                prepared=directory/f'pilot_L{size}_block{block}_correlators.json'
                execute(ANALYSIS/'prepare_ensemble.py',samples,'--output',prepared,'--block-size',block,
                        '--discard-per-chain',0,'--replicas',48,'--seed',902)
                execute(ANALYSIS/'analyze.py',prepared,'--output',directory/f'pilot_L{size}_block{block}_report.json',
                        '--csv',directory/f'pilot_L{size}_block{block}_fits.csv','--window','1:3','--window','1:4')
    result=summarize(directory)
    (directory/'pilot_summary.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(f'Wrote {directory / "pilot_summary.json"}; no mass automatically accepted.')
    return 0
if __name__=='__main__':raise SystemExit(main())
