#!/usr/bin/env python3
"""Validate the actual mounted DMG and extracted CLI before any Release write."""
from pathlib import Path
import hashlib
import json
import os
import plistlib
import subprocess
import tempfile
import zipfile

root = Path(__file__).resolve().parents[2]
spec = json.loads((root/'packaging/fork/release-inputs.json').read_text())
dist = root/'dist/release'
stem = spec['app'].lower()
version = spec['version']
dmg = dist/f'{stem}-{version}-macos-aarch64.dmg'
archive = dist/f'{stem}-cli-{version}-macos-aarch64.zip'
def run(*args):
    return subprocess.check_output(args, text=True).strip()
def signature(path):
    subprocess.run(['codesign', '--verify', '--strict', '--deep', '--verbose=2', str(path)], check=True)
    info = subprocess.run(['codesign', '-d', '--verbose=4', str(path)], text=True, capture_output=True, check=True).stderr
    assert 'Signature=adhoc' in info, str(path)+' is not ad-hoc signed'
def binaries(directory):
    found = []
    for path in directory.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        if 'Mach-O' in run('file', '-b', str(path)):
            assert run('lipo', '-archs', str(path)) == 'arm64', str(path)
            signature(path)
            # A Homebrew absolute dependency would work on the runner but not a user's Mac.
            for line in run('otool', '-L', str(path)).splitlines()[1:]:
                lib = line.strip().split(' (', 1)[0]
                assert not lib.startswith(('/opt/homebrew/', '/usr/local/', '/Users/runner/')), (path, lib)
            found.append(path)
    assert found, 'no Mach-O executables found'
    return found
def licences(directory):
    for name in ('LICENSE-MIT', 'LICENSE-APACHE', 'NOTICE'):
        assert (directory/name).is_file(), name
    assert list(directory.rglob('OFL-*.txt')), 'missing embedded font licences'

assert dmg.is_file() and archive.is_file()
signature(dmg)
with tempfile.TemporaryDirectory(prefix='fork-verify-') as temporary:
    work = Path(temporary)
    mount = work/'mount'
    mount.mkdir()
    subprocess.run(['hdiutil', 'attach', '-nobrowse', '-readonly', '-mountpoint', str(mount), str(dmg)], check=True)
    try:
        app = mount/(spec['app']+'.app')
        signature(app)
        binaries(app)
        plist = plistlib.loads((app/'Contents/Info.plist').read_bytes())
        assert plist['CFBundleName'] == spec['app']
        assert plist['CFBundleExecutable'] == spec['app']
        assert plist['CFBundleShortVersionString'] == version
        assert plist['CFBundleVersion'] == version
        assert plist['CFBundleIconName'] == spec['app']
        key = {'pdfcraft': 'PdfCraft', 'photocraft': 'PhotoCraft', 'vectorcraft': 'VectorCraft'}[spec['command']]
        assert plist[key+'BuildCommit'] == os.environ['EXPECTED_SHA']
        resources = app/'Contents/Resources'
        assert (resources/'Assets.car').stat().st_size > 0
        assert (resources/(spec['app']+'.icns')).read_bytes() == (root/'assets/app-icon'/(spec['command']+'.icns')).read_bytes()
        assert (resources/'LICENSE-ribbon.txt').is_file()
        licences(resources)
        if spec['command'] == 'pdfcraft':
            for name, sha in [('text-detection.onnx', 'a917b23dbd9524b465df7e922641b3ff2981623df4ded5a0234004ef2fee7cfe'), ('text-recognition.onnx', '86c145c2edb96c8caed5b1ebb8f44d706408922211451c309c625157dd6061c5')]:
                assert hashlib.sha256((resources/'models'/name).read_bytes()).hexdigest() == sha
            assert (resources/'models/ATTRIBUTION.txt').is_file()
        # Verify a real copy installed from the image retains a valid signature.
        installed = work/(spec['app']+'.app')
        subprocess.run(['ditto', str(app), str(installed)], check=True)
        signature(installed)
    finally:
        subprocess.run(['hdiutil', 'detach', str(mount)], check=True)
    cli_dir = work/'cli'
    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.namelist():
            assert not member.startswith('/') and '..' not in Path(member).parts
    subprocess.run(['ditto', '-x', '-k', str(archive), str(cli_dir)], check=True)
    files = binaries(cli_dir)
    cli = next(p for p in files if p.name == spec['command']+'-cli')
    licences(cli.parent)
    assert version in run(str(cli), '--version')

checksums = []
for asset in (dmg, archive):
    sha = hashlib.sha256(asset.read_bytes()).hexdigest()
    checksums.append(f'{sha}  {asset.name}\n')
    print(asset.name, asset.stat().st_size, sha)
(dist/'SHA256SUMS.txt').write_text(''.join(checksums))
print('Verified thin ARM executables, strict ad-hoc signatures, installed copy, version, icons, licences and hashes')
