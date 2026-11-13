#!/usr/bin/env python3
"""Write only this fork's tag/Release; verify uploaded bytes before publishing Latest."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
spec = json.loads((root/'packaging/fork/release-inputs.json').read_text())
repo, sha, tag = spec['repository'], os.environ['EXPECTED_SHA'], 'v'+spec['version']
assert os.environ['GITHUB_REPOSITORY'] == repo and repo.startswith('frangled123/')
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == sha
assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], text=True).strip(), 'release source changed during the build'
def gh(*args):
    return subprocess.check_output(['gh', *args], text=True).strip()

ref = subprocess.run(['gh', 'api', f'repos/{repo}/git/ref/tags/{tag}'], text=True, capture_output=True)
if ref.returncode:
    assert '404' in ref.stderr, ref.stderr
    gh('api', '--method', 'POST', f'repos/{repo}/git/refs', '-f', 'ref=refs/tags/'+tag, '-f', 'sha='+sha)
else:
    target = json.loads(ref.stdout)['object']
    assert target['type'] == 'commit' and target['sha'] == sha, 'existing tag points elsewhere'

dist = root/'dist/release'
assets = [dist/name for name in [*(line.split('  ', 1)[1] for line in (dist/'SHA256SUMS.txt').read_text().splitlines()), 'SHA256SUMS.txt']]
assert len(assets) == 3 and all(p.is_file() for p in assets)
existing = subprocess.run(['gh', 'release', 'view', tag, '--repo', repo, '--json', 'isDraft'], text=True, capture_output=True)
if existing.returncode == 0:
    assert json.loads(existing.stdout)['isDraft'], 'refusing to replace an existing published Release'
else:
    notes = (root/'docs/fork-release-notes.md').read_text()
    notes += f'\n\nSource: `{sha}`\n\nUpstream merged: `{spec["upstream"]}`\n\nBuild and package checks: https://github.com/{repo}/actions/runs/{os.environ["GITHUB_RUN_ID"]}\n'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md') as body:
        body.write(notes)
        body.flush()
        gh('release', 'create', tag, '--repo', repo, '--verify-tag', '--draft', '--title', spec['app']+' '+spec['version'], '--notes-file', body.name)
gh('release', 'upload', tag, '--repo', repo, '--clobber', *(str(p) for p in assets))
metadata = json.loads(gh('release', 'view', tag, '--repo', repo, '--json', 'assets'))
assert sorted(x['name'] for x in metadata['assets']) == sorted(p.name for p in assets), 'unexpected Release attachments'
with tempfile.TemporaryDirectory(prefix='fork-download-') as folder:
    gh('release', 'download', tag, '--repo', repo, '--dir', folder)
    for path in assets:
        downloaded = Path(folder)/path.name
        assert downloaded.stat().st_size == path.stat().st_size
        assert hashlib.sha256(downloaded.read_bytes()).digest() == hashlib.sha256(path.read_bytes()).digest()
if os.environ.get('PUBLISH_RELEASE') == 'true':
    gh('release', 'edit', tag, '--repo', repo, '--draft=false', '--latest')
    latest = json.loads(gh('api', f'repos/{repo}/releases/latest'))
    assert latest['tag_name'] == tag and not latest['draft'] and not latest['prerelease']
    print(latest['html_url'])
else:
    print('Verified draft created; publication was not requested in this dispatch.')
