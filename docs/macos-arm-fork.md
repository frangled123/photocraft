# Iride

Iride is the user-facing name of this independent PhotoCraft fork. Cargo package names, document formats and repository paths keep their upstream identifiers for compatibility.

# Independent macOS ARM fork

This branch is maintained by frangled123, based on [storytold/photocraft](https://github.com/storytold/photocraft). The original copyright, licence and contributor records are retained. The restricted ArtCraft graphics have been removed and replaced with the original ribbon artwork. This is not an official ArtCraft distribution.

## Build locally without paid services

Requirements: an Apple Silicon Mac, Rust stable, the `aarch64-apple-darwin` target, and Xcode 26 or newer (Icon Composer / actool). The existing font build inputs must be available as documented by the upstream build setup. PdfCraft also uses its pinned `craft-i18n` checkout.

```sh
packaging/macos/build-arm-local.sh
```

The script builds only `aarch64-apple-darwin`, creates the DMG and CLI ZIP in `dist/release`, and uses free ad-hoc signing. It does not notarize, purchase a Developer Program membership, or start GitHub Actions. The packages are for local use; a downloaded copy may require macOS's explicit Open Anyway confirmation because it is not notarized. No Intel or universal executable is included.

Keep Actions disabled on the fork unless you separately audit and approve runner costs. Do not run upstream release workflows as part of routine syncing.

## Icons

`assets/app-icon/Iride.icon` contains true vector foreground layers with distinct light/dark palettes and a monochrome variant for system treatments. Xcode compiles the native catalog; macOS chooses the appearance according to its app-icon settings. Transparency alone does not switch palettes. Older macOS versions fall back to the light ICNS. The shared tri-color ribbon logo is in `docs/brand/`.

## Merge upstream updates

Use `macos-arm64` for this fork and keep upstream history. With `upstream` pointing to `https://github.com/storytold/photocraft.git`:

```sh
git fetch upstream
git switch macos-arm64
git merge upstream/main
```

Resolve conflicts while retaining the ribbon assets, native icon compilation, bundle-icon runtime behavior and the fork update repository. Run the repository quality gates and build locally before pushing. Review upstream changes rather than blindly overwriting this branch. The app checks this fork's releases, so an upstream update cannot silently replace this build.

## Publish an update later

A commit or branch push is not an application update. A new GitHub Release needs a version higher than the installed application and the matching ARM DMG. Increase the application version in the Cargo workspace before compiling; changing only the archive filename is insufficient. The updater accepts the renamed artifact stems (`aevum`, `iride`, `nodus`) and checks only this fork’s repository.
