# Iride: independent macOS ARM fork

This fork is maintained in `macos-arm64`, based on [storytold/photocraft](https://github.com/storytold/photocraft). `main`, the original contributor credits, licences, command names and document formats are retained. The original ribbon artwork identifies this independent distribution; it is not an official ArtCraft distribution.

## Reproducible inputs

`packaging/fork/release-inputs.json` records the previous fork commit, exact upstream commit, Rust version, public font/translation input revisions, and protected artwork Git blobs. `python3 packaging/fork/verify-source.py` checks the worktree artwork; the release workflow additionally proves both commits are ancestors of the exact reviewed source SHA. Attribution and code changes are reviewed separately from those artwork bytes.

The UI supports 35 languages including English. Simplified and Traditional Chinese follow the system display language or the application's explicit language setting. PDF and Photo translations are compiled from their pinned `craft-i18n.rev` plus the committed `crates/ui-egui/src/i18n/fork/*.tsv`; the external checkout is never modified. Vector translations remain in its own catalogs. The build and runtime tests verify the actual embedded Chinese rows, including placeholders and plural forms. Software names, authors and licence texts retain their proper identities; source and update links use this fork.

## Free GitHub build and release

The only active workflow is `.github/workflows/macos-arm64-release.yml`. It accepts a deliberate push of `fork-release/v<version>-attempt.<N>` pointing at a reviewed commit already in `macos-arm64`. Such a push runs the complete build and publishes Latest after verification. Ordinary branch pushes, schedules and pull requests do not trigger it. It also supports `workflow_dispatch` on `macos-arm64`, with:

- `source_sha`: the full reviewed 40-character commit, which must equal the dispatched branch HEAD.
- `publish`: `false` creates a verified draft; `true` publishes Latest only after verification and download comparison.

It uses the public repository's **standard `macos-26` ARM runner**, two Cargo jobs, one run at a time per repository, and a 180-minute limit. The three-repository maintenance is bounded to one run per repository (at most three standard runners); retry only after the previous run has finished. There are no paid larger runners, cache uploads, persistent Actions artifacts, Apple accounts, certificates or notarization. Existing upstream workflows are retained under `.github/upstream-workflows/`, where GitHub cannot trigger them. In particular, never reactivate the shared upstream release workflow's paid `macos-15-xlarge` job.

Enable Actions only after this reviewed workflow and the inactive upstream workflows have reached the fork's default branch. All inherited workflows must stay disabled. A maintainer with Git push access can trigger a build without access to api.github.com. The runner writes a small `result.json` plus sanitized excerpts of its own public build output to the separate `ci/macos-arm64-results` branch; fetch that branch to follow the run URL, source SHA, step outcomes and verified asset hashes. No cloud-session private logs or environment dumps are collected. For a failed run, correct the source and push a fresh attempt tag; never move an existing public release tag. GitHub's own `GITHUB_TOKEN` creates the tag and Release on this fork only.

The workflow fetches exact public input revisions, verifies the font manifest's SHA-256 values and licences, runs formatting and embedded-language/branding tests, then invokes `packaging/macos/build-arm-local.sh`. Only `aarch64-apple-darwin` is built. LTO is disabled and codegen units are set to 16 for the standard runner's memory budget; app features remain enabled. Iride includes its existing HEIF feature; Aevum requires embedded translations and stages its SHA-256-pinned OCR models.

Before uploading, `verify-package.py` mounts the actual DMG read-only, checks every Mach-O executable is thin arm64, verifies strict ad-hoc signatures and an installed copy, rejects runner-local dynamic dependencies, checks version/commit/native icon/legacy ICNS/licences, extracts and runs the CLI, and writes **`SHA256SUMS.txt`**. Release attachment names are `iride-0.23.2-macos-aarch64.dmg`, `iride-cli-0.23.2-macos-aarch64.zip` and `SHA256SUMS.txt`. The upload is downloaded again and checked byte-for-byte before publication. Published existing Releases and tags pointing elsewhere are never overwritten.

The packages are ad-hoc signed and not notarized. macOS may require its explicit Open Anyway confirmation for the downloaded app. Native icons retain the accepted light, dark and system-tinted ribbon layers; old macOS versions use the existing ICNS. About uses the transparent shared three-color ribbon. File formats and executable command names retain upstream identifiers for compatibility.

## Manual build

On an Apple Silicon Mac with Xcode 26 and the pinned Rust version, set absolute `CRAFT_FONTS_DIR` and (for PDF/Photo) `CRAFT_I18N_DIR` paths to the verified pinned checkouts. Set `CRAFT_FONTS_REQUIRED=1` and `CRAFT_I18N_REQUIRED=1`, then run `packaging/macos/build-arm-local.sh`. No build on the user's Mac is required for this release workflow.

## Future updates

Merge a fixed upstream SHA into `macos-arm64` without replacing the fork tree. Review conflicts by function, retain artwork blob hashes, check new UI strings and run the repository gates. Increase the Cargo application SemVer above both the installed fork and merged upstream; build metadata alone is not an update. Preserve the fork repository and accepted renamed artifact stems in `UPDATE_APP`. Never push or send automated messages to upstream as part of this workflow.
