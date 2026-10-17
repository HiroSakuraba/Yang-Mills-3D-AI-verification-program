#!/usr/bin/env python3
"""Convert periodic operator samples to correlators and chain-aware bootstrap replicas."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT.parent / 'glueball_spectroscopy' / 'src')]
from glueball_spectrum_analysis.ensemble import prepare_ensemble


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--block-size', type=int, required=True)
    parser.add_argument('--replicas', type=int, default=200)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--discard-per-chain', type=int, required=True,
                        help='Explicit number of initial saved configurations to discard, including zero.')
    parser.add_argument('--max-lag', type=int)
    parser.add_argument('--diagnostic-max-lag', type=int, default=16)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Output must not overwrite the operator samples.')
    try:
        raw = args.input.read_bytes()
        result = prepare_ensemble(json.loads(raw), args.block_size, args.replicas, args.seed,
                                  args.discard_per_chain, args.max_lag, args.diagnostic_max_lag)
        result['ensemble_preparation']['input_sha256'] = hashlib.sha256(raw).hexdigest()
        encoded = json.dumps(result, indent=2, allow_nan=False) + '\n'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    except (ValueError, TypeError, KeyError, ArithmeticError, OSError, np.linalg.LinAlgError) as exc:
        print(f'Ensemble preparation rejected: {exc}', file=sys.stderr)
        return 2
    p = result['ensemble_preparation']
    print(f"Wrote {args.output}; {p['retained_configuration_count']} configurations, "
          f"{p['total_block_count']} blocks, {args.replicas} replicas. Block adequacy requires review.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
