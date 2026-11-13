#!/usr/bin/env python3
"""Audit literal UI lookups against the same pinned + committed Chinese inputs as build.rs.

Dynamic menus, engine messages and plural forms are additionally covered by each
repository's Rust i18n report/tests; this scan deliberately reports its narrower scope.
"""
from pathlib import Path
import json
import os
import re

root = Path(__file__).resolve().parents[2]
spec = json.loads((root/'packaging/fork/release-inputs.json').read_text())
app = spec['command']
folder = root/'crates/ui-egui/src/i18n'
allowed = set(json.loads((folder/'fork/untranslated-technical-terms.json').read_text()))
keys = set()
pattern = r'(?:tl!\s*\(|(?:crate::)?i18n::(?:t|words)\s*\(|notify_(?:tr|fmt)\s*\()\s*("(?:[^"\\]|\\.)*")'
source_files = [*(root/'crates/ui-egui/src').rglob('*.rs'), *(root/'apps'/app/'src').rglob('*.rs')]
for file in source_files:
    if 'tests' in file.parts or file.name.endswith('_tests.rs'):
        continue
    # Test-only imports/helpers may precede production UI code; do not cut at their cfg.
    text = re.split(r'#\[cfg\(test\)\]\s*mod\s+\w+\s*\{', file.read_text(), maxsplit=1)[0]
    for match in re.finditer(pattern, text, re.S):
        try:
            keys.add(json.loads(match.group(1)))
        except ValueError:
            continue
def unescape(text):
    return re.sub(r'\\([nt\\])', lambda m: {'n': '\n', 't': '\t', '\\': '\\'}[m[1]], text)

for code in ['zh-hans', 'zh-hant']:
    if app == 'vectorcraft':
        files = [folder/(code+'.tsv')]
    else:
        external = Path(os.environ['CRAFT_I18N_DIR'])/'locales'/code
        files = [external/'common.tsv', external/(app+'.tsv'), folder/'fork'/(code+'.tsv')]
    catalog = {}
    for file in files:
        for line in file.read_text().splitlines():
            if not line or line.startswith('#'):
                continue
            fields = line.split('\t')
            assert len(fields) == 3, (file, line)
            if not fields[0]:
                catalog[unescape(fields[1])] = unescape(fields[2])
    missing = sorted(key for key in keys-allowed if catalog.get(key, key) == key)
    assert not missing, f'{code}: untranslated literal UI keys: {missing}'
    print(f'{code}: {len(keys)} literal UI keys checked, {len(allowed & keys)} explicitly retained technical/product/symbol keys')
