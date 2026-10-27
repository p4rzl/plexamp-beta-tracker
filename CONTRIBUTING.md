# Contributing

Discuss changes in an issue or pull request. Include the affected Plexamp version and workflow run when reporting tracker failures; include Android and Obtainium versions for setup failures. Never post tokens or account data.

Use Python 3.11+ and run `python -m unittest discover -s tests -v`. Tests do not download or publish APKs. For a read-only live check run `python scripts/track_beta.py --metadata-only`.

Keep the official Android beta manifest as the source of truth, preserve APK bytes, and retain the draft-before-publish behavior. Add regression coverage when changing parsing, validation, or release recovery. Keep English/Italian instructions and Obtainium config links in sync. Do not attach Plex APKs to code-review fixtures.
