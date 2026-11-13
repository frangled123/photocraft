#!/usr/bin/env python3
"""Verify fixed merge inputs and each approved artwork blob, independently of metadata."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib

root = Path(__file__).resolve().parents[2]
os.chdir(root)
spec = json.loads((root/'packaging/fork/release-inputs.json').read_text())
def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

version = tomllib.loads((root/'Cargo.toml').read_text())['workspace']['package']['version']
assert version == spec['version'], (version, spec['version'])
assert re.fullmatch(r'\d+\.\d+\.\d+', version)
assert git('remote', 'get-url', 'origin').rstrip('/').removesuffix('.git').endswith('/'+spec['repository'])
if '--release' in sys.argv:
    expected = os.environ['EXPECTED_SHA']
    assert re.fullmatch('[0-9a-f]{40}', expected), 'source_sha must be a complete reviewed commit'
    assert git('rev-parse', 'HEAD') == expected == os.environ['GITHUB_SHA']
    assert os.environ['GITHUB_REPOSITORY'] == spec['repository']
    ref = os.environ['GITHUB_REF']
    if ref.startswith('refs/tags/fork-release/'):
        assert re.fullmatch('refs/tags/fork-release/v'+re.escape(version)+r'-attempt\.[1-9][0-9]*', ref), ref
        subprocess.run(['git', 'merge-base', '--is-ancestor', 'HEAD', 'origin/macos-arm64'], check=True)
    else:
        assert ref == 'refs/heads/macos-arm64', ref
    assert not git('status', '--porcelain', '--untracked-files=no'), 'modified release source'
    for sha in (spec['upstream'], spec['baseline']):
        subprocess.run(['git', 'merge-base', '--is-ancestor', sha, 'HEAD'], check=True)
for entry in spec['artwork']:
    path = root/entry['path']
    content = path.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    assert blob == entry['sha'], 'protected artwork changed: '+entry['path']
# A new upstream logo under a different filename must not bypass the protected-file check.
expected_artwork = {entry['path'] for entry in spec['artwork']}
actual_artwork = set()
for folder in ['assets/app-icon', 'docs/brand', 'packaging/macos/dmg']:
    for path in (root/folder).rglob('*'):
        if path.is_file() and (path.suffix.lower() in {'.svg', '.png', '.icns', '.ico', '.tiff', '.tif', '.jpg', '.jpeg'} or path.name.endswith('.DS_Store') or path.name in {'icon.json', 'DS_Store'}):
            actual_artwork.add(str(path.relative_to(root)))
assert actual_artwork == expected_artwork, ('unexpected/missing branding artwork', actual_artwork ^ expected_artwork)
active = sorted(p.name for p in (root/'.github/workflows').iterdir() if p.suffix in ('.yml', '.yaml'))
assert active == ['macos-arm64-release.yml'], active
ui = (root/'crates/ui-egui/src/lib.rs').read_text()
assert f'repo: "{spec["repository"]}"' in ui
assert f'name: "{spec["app"]}"' in ui
print(f'{spec["app"]} {version}: source, update repository and {len(spec["artwork"])} protected artwork blobs verified')
