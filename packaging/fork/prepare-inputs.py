#!/usr/bin/env python3
"""Fetch pinned public build inputs and check the supplier's font hashes."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
spec = json.loads((root/'packaging/fork/release-inputs.json').read_text())
destination = Path(sys.argv[1]).resolve()
destination.mkdir(parents=True, exist_ok=True)
def checkout(repository, sha):
    path = destination/repository
    if not (path/'.git').exists():
        subprocess.run(['git', 'init', '--quiet', str(path)], check=True)
        subprocess.run(['git', '-C', str(path), 'remote', 'add', 'origin', 'https://github.com/storytold/'+repository+'.git'], check=True)
    subprocess.run(['git', '-C', str(path), 'fetch', '--depth=1', 'origin', sha], check=True)
    subprocess.run(['git', '-C', str(path), 'checkout', '--detach', sha], check=True)
    actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    assert actual == sha
    assert not subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain'], text=True).strip()
    return path

fonts = checkout('craft-fonts', spec['fonts'])
count = 0
for manifest in ['manifest.txt', 'simplified-chinese-manifest.txt']:
    for line in (fonts/'fonts'/manifest).read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        fields = [p.strip() for p in line.split(' | ')]
        assert len(fields) == 8
        font, licence = (fonts/fields[2]).resolve(), (fonts/fields[5]).resolve()
        assert font.is_relative_to(fonts) and licence.is_relative_to(fonts)
        assert fields[4] == 'OFL-1.1' and licence.is_file()
        assert hashlib.sha256(font.read_bytes()).hexdigest() == fields[6], fields[2]
        count += 1
environment = {'CRAFT_FONTS_DIR': str(fonts), 'CRAFT_FONTS_REQUIRED': '1'}
if spec['i18n']:
    assert (root/'craft-i18n.rev').read_text().strip() == spec['i18n']
    environment['CRAFT_I18N_DIR'] = str(checkout('craft-i18n', spec['i18n']))
    environment['CRAFT_I18N_REQUIRED'] = '1'
with open(os.environ['GITHUB_ENV'], 'a') as out:
    for key, value in environment.items():
        assert '\n' not in value
        out.write(f'{key}={value}\n')
print(f'Verified pinned inputs and {count} font files with OFL notices')
