#!/usr/bin/env python3
"""Produce all necessary generator artifacts, without consulting checkers."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
ART.mkdir(exist_ok=True)
for script, args in (
    ('generator/two_face_surfaces.py', ['--fmax', '22', '--output', str(ART / 'two_face_f22.json')]),
    ('generator/branched_supports.py', ['--fmax', '18', '--output', str(ART / 'branched_f18.json')]),
):
    subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT, check=True)
