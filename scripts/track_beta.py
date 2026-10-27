"""Track the official Plexamp Android beta manifest. Python standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile

MANIFEST_URL = 'https://plexamp.plex.tv/mobile/android-update-beta.json'
PACKAGE = 'tv.plex.labs.plexamp'
VERSION = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+(?:-beta\.[0-9]+)?')
MAX_APK = 512 * 1024 * 1024


def fetch(url, destination=None, token=None):
    """Retry transient failures, bound downloads, and keep HTTP errors visible."""
    headers = {'User-Agent': 'plexamp-beta-tracker', 'Accept': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers), timeout=60) as response:
                if not response.url.startswith('https://'):
                    raise ValueError('Refusing a non-HTTPS redirect')
                limit = MAX_APK if destination else 1024 * 1024
                if destination:
                    with open(destination, 'wb') as output:
                        count = 0
                        while chunk := response.read(1024 * 1024):
                            count += len(chunk)
                            if count > limit:
                                raise ValueError('APK exceeds size limit')
                            output.write(chunk)
                    return None
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError('JSON exceeds size limit')
                return json.loads(data)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError('Manifest must be an object')
    version = data.get('version')
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError('Unsupported version format')
    code = data.get('versionCode')
    if type(code) is not int or code <= 0:
        raise ValueError('Invalid Android versionCode')
    url = f'https://plexamp.plex.tv/mobile/Plexamp-{version}.apk'
    if data.get('url') != url:
        raise ValueError('APK URL does not match the official host and version')
    if not isinstance(data.get('notes', ''), str):
        raise ValueError('Invalid release notes')
    return data


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}): {result.stderr.strip()}')
    return result.stdout


def validate_apk(path, manifest):
    with zipfile.ZipFile(path) as archive:
        if 'AndroidManifest.xml' not in archive.namelist() or archive.testzip():
            raise ValueError('Invalid or corrupt APK archive')
    # Verify the embedded signature without modifying/re-signing the APK.
    run(os.environ.get('APKSIGNER', 'apksigner'), 'verify', '--verbose', str(path))
    badging = run(os.environ.get('AAPT', 'aapt'), 'dump', 'badging', str(path))
    match = re.search(r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'", badging)
    if not match or match.groups() != (PACKAGE, str(manifest['versionCode']), manifest['version']):
        raise ValueError('APK package/version does not match the manifest')
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def get_release(repo, tag):
    try:
        return fetch(f'https://api.github.com/repos/{repo}/releases/tags/{tag}',
                     token=os.environ['GH_TOKEN'])
    except HTTPError as error:
        if error.code == 404:
            return None
        raise


def asset_names(release):
    return {a['name'] for a in release.get('assets', []) if a.get('state') == 'uploaded'}


def complete(release, required):
    return bool(release and not release['draft'] and release['prerelease']
                and required <= asset_names(release))


def publish(repo, manifest, directory, release):
    version = manifest['version']
    tag = f'v{version}'
    apk = directory / f'Plexamp-{version}.apk'
    fetch(manifest['url'], apk)
    digest = validate_apk(apk, manifest)
    checksum = directory / 'SHA256SUMS'
    checksum.write_text(f'{digest}  {apk.name}\n', encoding='utf-8')
    metadata = directory / 'upstream.json'
    metadata.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    notes = directory / 'release-notes.md'
    notes.write_text(
        f"Unofficial mirror of the official Plexamp Android **beta channel**.\n\n"
        f"- Upstream APK: {manifest['url']}\n- Manifest: {MANIFEST_URL}\n"
        f"- Android package: `{PACKAGE}`\n- Version code: `{manifest['versionCode']}`\n"
        f"- SHA-256: `{digest}`\n\nThe APK is unmodified. Its embedded signature and "
        f"package/version were checked before upload. The signature check is not an "
        f"independent verification of Plex's signing identity.\n\n"
        f"## Upstream notes\n\n{manifest.get('notes', '')}\n\n"
        f"[Obtainium setup](https://github.com/{repo}#install-with-obtainium)\n",
        encoding='utf-8')
    if release:
        # A retry must never silently replace an existing APK with different bytes.
        for asset in release.get('assets', []):
            if asset['name'] == apk.name:
                if asset.get('state') != 'uploaded' or asset.get('digest') != f'sha256:{digest}':
                    raise ValueError('Existing APK differs or has no verifiable digest; manual review required')
    else:
        run('gh', 'release', 'create', tag, '--repo', repo, '--target',
            os.environ['GITHUB_SHA'], '--draft', '--prerelease', '--title',
            f'Plexamp v{version}', '--notes-file', str(notes))
    existing = asset_names(release or {})
    missing = [str(p) for p in (apk, checksum, metadata) if p.name not in existing]
    if missing:
        run('gh', 'release', 'upload', tag, *missing, '--repo', repo)
    # Publication happens only after every required asset has been uploaded.
    run('gh', 'release', 'edit', tag, '--repo', repo, '--draft=false',
        '--prerelease', '--latest=false', '--notes-file', str(notes))
    print(f'Published {tag}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata-only', action='store_true', help='Validate live manifest without downloading or publishing')
    args = parser.parse_args()
    manifest = validate_manifest(fetch(MANIFEST_URL))
    print(f"Official Android beta channel: {manifest['version']} ({manifest['versionCode']})")
    if args.metadata_only:
        return
    repo = os.environ['GITHUB_REPOSITORY']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Invalid repository name')
    tag = f"v{manifest['version']}"
    release = get_release(repo, tag)
    required = {f"Plexamp-{manifest['version']}.apk", 'SHA256SUMS', 'upstream.json'}
    if complete(release, required):
        print(f'{tag} is already complete; nothing to do')
        return
    with tempfile.TemporaryDirectory() as temporary:
        publish(repo, manifest, Path(temporary), release)


if __name__ == '__main__':
    main()
