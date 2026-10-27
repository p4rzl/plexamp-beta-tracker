# Plexamp Beta Tracker

**Follow the official Plexamp Android beta channel with Obtainium.**

[English](README.md) · [Italiano](docs/README.it.md) · [APK releases](https://github.com/p4rzl/plexamp-beta-tracker/releases) · [Official downloads](https://plexamp.plex.tv/downloads.html)

[![Tracker](https://github.com/p4rzl/plexamp-beta-tracker/actions/workflows/update-plexamp.yml/badge.svg)](https://github.com/p4rzl/plexamp-beta-tracker/actions/workflows/update-plexamp.yml)
[![CI](https://github.com/p4rzl/plexamp-beta-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/p4rzl/plexamp-beta-tracker/actions/workflows/ci.yml)

This community project mirrors the unmodified Android APK linked by Plex's **beta manifest** to GitHub Releases. Obtainium can then find new versions even when the APK filename changes. It is **not an official Plex project** and does not build, modify, or re-sign Plexamp.

## Install with Obtainium

### Quick setup

1. Install [Obtainium](https://github.com/ImranR98/Obtainium/releases) on your Android device.
2. Open this README in your browser and tap the button below.
3. Review the imported configuration, confirm, and run an update check in Obtainium.
4. Tap **Install** and allow Obtainium to install unknown apps if Android asks. Confirm the Android installation prompt.

[![Add to Obtainium](assets/add-to-obtainium.svg)](https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22tv.plex.labs.plexamp%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2Fp4rzl%2Fplexamp-beta-tracker%22%2C%22author%22%3A%22Plex%2C%20Inc.%20%28unofficial%20mirror%20by%20p4rzl%29%22%2C%22name%22%3A%22Plexamp%20Beta%22%2C%22additionalSettings%22%3A%22%7B%5C%22includePrereleases%5C%22%3Atrue%2C%5C%22includeDrafts%5C%22%3Afalse%2C%5C%22verifyLatestTag%5C%22%3Afalse%2C%5C%22apkFilterRegEx%5C%22%3A%5C%22%5EPlexamp-.%2A%5C%5C%5C%5C.apk%24%5C%22%2C%5C%22sortMethodChoice%5C%22%3A%5C%22date%5C%22%7D%22%7D)

The button includes **prereleases enabled** and an APK filter. It opens Obtainium through its [documented redirect service](https://wiki.obtainium.imranr.dev/deep_links/); it does not silently install anything. The redirect is hosted by the Obtainium community and receives the public configuration in the link. If your browser blocks it, use the manual steps below.

### Manual setup

1. Open Obtainium → **Add app**.
2. Paste the **repository URL**, not a link to one APK:

   ```text
   https://github.com/p4rzl/plexamp-beta-tracker
   ```

3. In the GitHub source options, enable **Include prereleases**. Leave **Include drafts** and **Verify latest tag** disabled.
4. Optional APK filename filter: `^Plexamp-.*\.apk$`.
5. Add the app, check for updates, and install the offered APK. Settings labels may vary by Obtainium version or language.

The same configuration is available in [obtainium.json](obtainium.json). It is a single-app config for tools that support Obtainium app-config imports, not a complete Obtainium backup. The JSON string inside `additionalSettings` is intentional and follows Obtainium's export format.

## Updates and channel behavior

- The tracker checks every **two hours**. GitHub scheduled jobs may run late; Obtainium also has its own checking interval.
- The source of truth is [Plex's Android beta manifest](https://plexamp.plex.tv/mobile/android-update-beta.json), not forum post order or the desktop version.
- Every mirrored build is a GitHub **prerelease**. The beta channel may temporarily point to a version without a `-beta` suffix; it is still mirrored as the current beta-channel build.
- Only the current version at each check is mirrored. Builds replaced between checks may be missed.
- It uses the real Plexamp package, `tv.plex.labs.plexamp`, so it cannot be installed alongside another version of that same package. Android only accepts an in-place update when signing certificates and version codes are compatible.
- A newer Play Store installation may prevent installing an older beta. Wait for a newer beta; do not uninstall unless you accept losing local app data/downloads.
- Betas may have bugs. Existing Plex account, server, and feature requirements still apply. This tracker grants no Plex access or subscriptions.

## Download integrity

Each new release contains:

| File | Purpose |
| --- | --- |
| `Plexamp-<version>.apk` | Original APK fetched over HTTPS from `plexamp.plex.tv` |
| `SHA256SUMS` | SHA-256 of the mirrored APK |
| `upstream.json` | Snapshot of the official manifest, including version code and notes |

Before uploading, the tracker checks ZIP integrity, the embedded APK signature with Android `apksigner`, and the package/version with `aapt`. APK bytes remain unchanged. Signature validity does **not** independently establish Plex's signing identity: this project does not pin a separately verified Plex certificate. Checksums detect file differences, not publisher identity. Android enforces certificate continuity for updates of an installed app.

To check a downloaded file on Linux:

```sh
sha256sum -c SHA256SUMS
```

## Troubleshooting

| Problem | What to check |
| --- | --- |
| No releases found | Enable **Include prereleases** and disable **Verify latest tag**. Look at the repository's Releases and Actions tabs. |
| Button does nothing | Open it from a browser on Android with Obtainium installed, or use manual setup. GitHub clients may block app links. |
| Android refuses the update | Check installed version code and signing compatibility. Do not delete app data as a first step. |
| GitHub rate limit | Wait for the limit to reset or configure your own GitHub token in Obtainium. Never share your token in an issue. |
| Mirror is behind | Check the latest tracker run. Upstream outages and GitHub scheduling delays can postpone publication. Official downloads remain available above. |

## Development and running your own tracker

Python **3.11+** is required; there are no third-party Python dependencies.

```sh
python -m unittest discover -s tests -v
python scripts/track_beta.py --metadata-only
```

The metadata command makes a read-only request and validates the live manifest without publishing. Full publishing also requires GitHub CLI, Android SDK build tools (`aapt` and `apksigner`), and `GH_TOKEN`, `GITHUB_REPOSITORY`, and `GITHUB_SHA`. The workflow discovers the tools in the GitHub runner's Android SDK.

Fork this repo, enable Actions, and run **Track Plexamp Android beta → Run workflow** manually once. Scheduled publishing is intentionally restricted to this original repository to avoid accidental duplicate mirrors; change the workflow repository guard to your fork to enable its schedule. Update the README links and `obtainium.json` for your fork too. Public repositories with no activity may have scheduled workflows disabled by GitHub; re-enable them in Actions when needed.

Publishing uses the workflow's `GITHUB_TOKEN` with write access only to repository contents. Pull-request CI has read access and never publishes. Concurrent publisher runs are serialized. New releases stay in draft until assets finish uploading; retries repair missing assets and refuse to replace an existing APK whose digest differs. Authentication and API errors fail the run instead of masquerading as a missing release. A complete existing release is skipped without downloading it again.

To report a bug, [open an issue](https://github.com/p4rzl/plexamp-beta-tracker/issues/new/choose) with the workflow URL or Obtainium error, your Android/Obtainium versions, and the affected Plexamp version. Remove tokens and personal information. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License and attribution

Tracker code and documentation are licensed under [MIT](LICENSE). Plexamp binaries, names, and trademarks belong to their respective owners and are **not** covered by this repository's license. Plexamp is proprietary software; its own terms apply. Prefer the [official download page](https://plexamp.plex.tv/downloads.html) whenever you do not need the GitHub mirror.
