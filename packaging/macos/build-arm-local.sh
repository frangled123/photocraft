#!/usr/bin/env bash
# Single-architecture Apple Silicon build, locally or on a standard GitHub macos-26 runner.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
[[ "$(uname -s)" = Darwin && "$(uname -m)" = arm64 ]] || { echo "Run on an Apple Silicon Mac." >&2; exit 1; }
export MACOS_SIGN_IDENTITY=-
export CRAFT_FONTS_REQUIRED=1
export CRAFT_I18N_REQUIRED=1
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-4}"
exec "$ROOT/packaging/macos/package.sh" "$@" --arch aarch64
