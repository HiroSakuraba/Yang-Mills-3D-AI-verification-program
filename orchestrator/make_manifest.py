#!/usr/bin/env python3
"""Generate a deterministic SHA-256 manifest for a bundle.

Excludes volatile / non-source files (__pycache__, *.pyc, the manifest itself,
.DS_Store) so the manifest is reproducible and reviewable. Run from anywhere:

    python orchestrator/make_manifest.py bundles/YM3D_M1A_OH_GROUP_GENERATOR_1
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache"}
EXCLUDE_SUFFIX = {".pyc", ".pyo"}
EXCLUDE_NAMES = {"manifest.json", ".DS_Store"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: make_manifest.py <bundle_dir>")
        return 2
    root = Path(sys.argv[1]).resolve()
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix in EXCLUDE_SUFFIX or p.name in EXCLUDE_NAMES:
            continue
        files.append({
            "path": str(p.relative_to(root)),
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
        })
    manifest = {
        "bundle": root.name,
        "version": "1",
        "determinism": "exact integer/rational arithmetic; sorted JSON; no floats in decisions",
        "files": files,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {root.name}/manifest.json ({len(files)} files, no .pyc)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
