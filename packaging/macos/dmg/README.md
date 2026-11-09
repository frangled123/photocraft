# Iride installer window

`background.svg` is the editable 660 × 400 pt source. It uses the shared ribbon logo, the app accent and the repository’s OFL Inter fonts. `background.tiff` contains 1× and 2× images. The Finder layout positions `Iride.app` at (326, 205) and Applications at (574, 205), with a 128 pt icon size.

The volume name must be `Iride` because the background alias uses that name. Regenerate with `python3 packaging/macos/dmg/generate.py` after installing free build dependencies `pillow>=12`, `ds_store==1.3.3` and `mac_alias==2.2.3`, with resvg on PATH. The generator uses only repository fonts and fixed alias metadata.

The upstream layout and generator are retained. Replacement ribbon artwork, labels and palette are copyright (c) 2026 frangled123, MIT OR Apache-2.0. Original contributor notices remain in the root attribution file.
