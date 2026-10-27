import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import zipfile

from scripts import track_beta as tracker


def manifest(version='4.50.21-beta.3'):
    return {'version': version, 'versionCode': 324004163,
            'url': f'https://plexamp.plex.tv/mobile/Plexamp-{version}.apk', 'notes': 'Changes'}


class TrackerTests(unittest.TestCase):
    def test_beta_manifest(self):
        self.assertEqual(tracker.validate_manifest(manifest())['versionCode'], 324004163)

    def test_beta_channel_can_point_at_stable_build(self):
        tracker.validate_manifest(manifest('4.50.21'))

    def test_untrusted_urls_and_invalid_versions_are_rejected(self):
        for field, value in [('url', 'https://example.com/app.apk'),
                             ('url', 'http://plexamp.plex.tv/mobile/app.apk'),
                             ('version', '../app'), ('version', '4.50.21;echo test'),
                             ('versionCode', True), ('versionCode', 0),
                             ('versionCode', '123'), ('notes', {})]:
            with self.subTest(field=field, value=value):
                data = manifest()
                data[field] = value
                with self.assertRaises(ValueError):
                    tracker.validate_manifest(data)
        for data in ([], None, {}):
            with self.assertRaises(ValueError):
                tracker.validate_manifest(data)

    def test_only_404_means_release_absent(self):
        with patch.dict('os.environ', {'GH_TOKEN': 'test'}):
            for status in (404, 401, 403, 500):
                with self.subTest(status=status), patch.object(tracker, 'fetch', side_effect=HTTPError('url', status, 'error', {}, None)):
                    if status == 404:
                        self.assertIsNone(tracker.get_release('owner/repo', 'v1'))
                    else:
                        with self.assertRaises(HTTPError):
                            tracker.get_release('owner/repo', 'v1')

    def test_incomplete_and_draft_releases_are_not_skipped(self):
        release = {'draft': False, 'prerelease': True,
                   'assets': [{'name': n, 'state': 'uploaded'} for n in ('app.apk', 'SHA256SUMS')]}
        required = {'app.apk', 'SHA256SUMS'}
        self.assertTrue(tracker.complete(release, required))
        self.assertFalse(tracker.complete(release, required | {'upstream.json'}))
        for key in ('draft', 'prerelease'):
            changed = copy.deepcopy(release)
            changed[key] = not changed[key]
            self.assertFalse(tracker.complete(changed, required))
        release['assets'][0]['state'] = 'starter'
        self.assertFalse(tracker.complete(release, required))

    def test_apk_package_version_and_signature_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            apk = Path(directory) / 'app.apk'
            with zipfile.ZipFile(apk, 'w') as archive:
                archive.writestr('AndroidManifest.xml', b'fixture')
            good = "package: name='tv.plex.labs.plexamp' versionCode='324004163' versionName='4.50.21-beta.3'"
            with patch.object(tracker, 'run', side_effect=['Verified', good]):
                self.assertEqual(len(tracker.validate_apk(apk, manifest())), 64)
            for bad in (good.replace('tv.plex.labs.plexamp', 'other.app'),
                        good.replace('324004163', '1'), good.replace('beta.3', 'beta.2')):
                with patch.object(tracker, 'run', side_effect=['Verified', bad]):
                    with self.assertRaises(ValueError):
                        tracker.validate_apk(apk, manifest())
            with patch.object(tracker, 'run', side_effect=RuntimeError('Invalid signature')):
                with self.assertRaises(RuntimeError):
                    tracker.validate_apk(apk, manifest())

    def test_html_and_zip_without_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            apk = Path(directory) / 'app.apk'
            apk.write_text('<html>error</html>')
            with self.assertRaises(zipfile.BadZipFile):
                tracker.validate_apk(apk, manifest())
            with zipfile.ZipFile(apk, 'w') as archive:
                archive.writestr('other', 'not an APK')
            with self.assertRaises(ValueError):
                tracker.validate_apk(apk, manifest())

    def test_release_published_only_after_upload(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'GITHUB_SHA': 'abc'}):
            with patch.object(tracker, 'fetch'), patch.object(tracker, 'validate_apk', return_value='a' * 64), patch.object(tracker, 'run') as run:
                tracker.publish('owner/repo', manifest(), Path(directory), None)
                calls = [call.args for call in run.call_args_list]
                self.assertEqual([c[2] for c in calls], ['create', 'upload', 'edit'])
                self.assertIn('--draft', calls[0])
                self.assertIn('--draft=false', calls[-1])
                run.reset_mock()
                run.side_effect = [None, RuntimeError('Upload failed')]
                with self.assertRaises(RuntimeError):
                    tracker.publish('owner/repo', manifest(), Path(directory), None)
                self.assertEqual(run.call_count, 2)

    def test_existing_apk_repair_and_digest_mismatch(self):
        release = {'draft': False, 'assets': [
            {'name': 'Plexamp-4.50.21-beta.3.apk', 'state': 'uploaded', 'digest': 'sha256:' + 'a' * 64}]}
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(tracker, 'fetch'), patch.object(tracker, 'validate_apk', return_value='a' * 64), patch.object(tracker, 'run') as run:
                tracker.publish('owner/repo', manifest(), Path(directory), release)
                self.assertEqual(run.call_args_list[0].args[2], 'upload')
                self.assertFalse(any(str(arg).endswith('.apk') for arg in run.call_args_list[0].args))
                run.reset_mock()
                release['assets'][0]['digest'] = 'sha256:wrong'
                with self.assertRaises(ValueError):
                    tracker.publish('owner/repo', manifest(), Path(directory), release)
                run.assert_not_called()

    def test_obtainium_config_and_buttons(self):
        from urllib.parse import unquote
        import re
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / 'obtainium.json').read_text())
        settings = json.loads(config['additionalSettings'])
        self.assertEqual(config['id'], tracker.PACKAGE)
        self.assertTrue(settings['includePrereleases'])
        self.assertFalse(settings['verifyLatestTag'])
        self.assertIsNotNone(re.search(settings['apkFilterRegEx'], 'Plexamp-4.50.21-beta.3.apk'))
        self.assertIsNone(re.search(settings['apkFilterRegEx'], 'SHA256SUMS'))
        for doc in ('README.md', 'docs/README.it.md'):
            content = (root / doc).read_text()
            payload = re.search(r'redirect\?r=obtainium://app/([^\s)]+)', content).group(1)
            self.assertEqual(json.loads(unquote(payload)), config)


if __name__ == '__main__':
    unittest.main()
