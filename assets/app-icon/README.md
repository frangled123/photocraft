# Iride ribbon icons

Original editable vectors for the independent macOS ARM fork. See [LICENSE.txt](LICENSE.txt).

- `Iride.icon/`: native Icon Composer source. The transparent light, dark and monochrome SVG layers are in `Assets/`; the system supplies the rounded plate, lighting and appearance treatment.
- `photocraft.svg`: light legacy tile; `photocraft-dark.svg`: dark tile for previews and future consumers. `photocraft-small.svg` uses the same simplified geometry.
- PNG, ICNS, ICO and hicolor files: generated compatibility assets. Run `packaging/icons.sh` with resvg and the Rust toolchain installed; iconutil generates ICNS on macOS.
- `packaging/macos/compile-icon.sh` compiles the native `.icon` using Xcode 26 or newer, writes `Assets.car`, and adds `CFBundleIconName`. It runs automatically during macOS packaging.

The legacy macOS canvas is 1024 × 1024 with an 824 × 824 plate and transparent margins. The foreground has an optical scale of 86% relative to the original ribbon drawing, with extra room around its silhouette. Dark artwork uses a separate, brighter palette rather than a color inversion. The monochrome layer supports system Clear and Tinted treatments. Older macOS versions use the static light ICNS fallback.

The shared three-color ribbon logo lives in `docs/brand/ribbon-mark-*.svg`. It has no background plate.
