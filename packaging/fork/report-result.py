#!/usr/bin/env python3
"""Publish a small public-runner status record over Git for API-restricted maintainers.

Only this run's public build command output is read. Environment dumps, local cloud
logs, tokens and private inputs are never collected. The branch contains no binaries.
"""
from pathlib import Path
import base64
import datetime
import hashlib
import json
import os
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
spec = json.loads((root/'packaging/fork/release-inputs.json').read_text())
repo = spec['repository']
assert os.environ['GITHUB_REPOSITORY'] == repo and repo.startswith('frangled123/')
branch = 'ci/macos-arm64-results'
sha = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
result = {
    'repository': repo, 'source_sha': sha, 'version': spec['version'],
    'trigger': os.environ['GITHUB_REF'], 'status': os.environ['BUILD_STATUS'],
    'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
    'run_url': f'https://github.com/{repo}/actions/runs/{os.environ["GITHUB_RUN_ID"]}',
    'updated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'steps': {key: {'outcome': value.get('outcome'), 'conclusion': value.get('conclusion')}
              for key, value in json.loads(os.environ.get('BUILD_STEPS', '{}')).items()},
    'assets': [],
}
sums = root/'dist/release/SHA256SUMS.txt'
if sums.is_file():
    for file in [sums, *(sums.parent/line.split('  ', 1)[1] for line in sums.read_text().splitlines())]:
        if file.is_file():
            result['assets'].append({'name': file.name, 'size': file.stat().st_size, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})

diagnostics = []
for file in sorted(Path(os.environ['RUNNER_TEMP']).glob('fork-public-*.log')):
    lines = file.read_text(errors='replace').splitlines()
    errors = [i for i, line in enumerate(lines) if re.search(r'(^error(?:\[|:)|FAILED|^failures:|panicked at|Traceback|AssertionError)', line)]
    chosen = set(range(max(0, len(lines)-60), len(lines)))
    for index in errors:
        chosen.update(range(max(0, index-2), min(len(lines), index+18)))
    excerpt = '\n'.join(lines[i] for i in sorted(chosen))[-24000:]
    token = os.environ.get('GH_TOKEN', '')
    if token:
        excerpt = excerpt.replace(token, '[REDACTED]')
    excerpt = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b', '[REDACTED]', excerpt)
    excerpt = re.sub(r'https://[^\s/@]+:[^\s/@]+@', 'https://[REDACTED]@', excerpt)
    diagnostics.append(file.name+'\n'+excerpt+'\n')

with tempfile.TemporaryDirectory(prefix='fork-result-') as temp:
    work = Path(temp)
    (work/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    (work/'diagnostics.txt').write_text('\n'.join(diagnostics))
    def git(*args):
        return subprocess.check_output(['git', '-C', str(work), *args], text=True).strip()
    git('init', '--quiet')
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git('remote', 'add', 'origin', 'https://github.com/'+repo+'.git')
    # Supply credentials only in the child environment, never in a URL, command or file.
    token = os.environ['GH_TOKEN']
    os.environ['GIT_CONFIG_COUNT'] = '1'
    os.environ['GIT_CONFIG_KEY_0'] = 'http.https://github.com/.extraheader'
    os.environ['GIT_CONFIG_VALUE_0'] = 'AUTHORIZATION: basic '+base64.b64encode(('x-access-token:'+token).encode()).decode()
    ref = git('ls-remote', '--heads', 'origin', 'refs/heads/'+branch)
    parent = []
    if ref:
        git('fetch', '--quiet', '--depth=1', 'origin', 'refs/heads/'+branch)
        parent = ['-p', git('rev-parse', 'FETCH_HEAD')]
    git('add', 'result.json', 'diagnostics.txt')
    tree = git('write-tree')
    commit = git('commit-tree', tree, *parent, '-m', f'{spec["app"]} runner {result["run_id"]}: {result["status"]}')
    git('push', 'origin', commit+':refs/heads/'+branch)
print(result['run_url'])
