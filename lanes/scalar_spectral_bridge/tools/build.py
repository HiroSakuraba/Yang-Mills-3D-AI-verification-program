#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from scalar_bridge import build
if __name__=='__main__':
    (ROOT/'artifacts'/'constants.json').write_text(json.dumps(build(),sort_keys=True,indent=2)+'\n')
    print('Generated spectral-note constants; no analytic gate decision.')
