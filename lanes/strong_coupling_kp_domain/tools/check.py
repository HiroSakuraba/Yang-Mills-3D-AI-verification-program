#!/usr/bin/env python3
"""Run independent checks on freshly generated outputs, then decide."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
for script, args in (
    ('checker/check_two_face.py', ['--fmax', '22', '--generator-json', str(ART / 'two_face_f22.json'), '--output', str(ART / 'check_two_face_f22.json')]),
    ('checker/check_branched.py', ['--fmax', '18', '--generator-json', str(ART / 'branched_f18.json'), '--output', str(ART / 'check_branched_f18.json')]),
    ('tools/decide.py', []),
):
    subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT, check=True)
