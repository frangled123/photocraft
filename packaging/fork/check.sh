#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 packaging/fork/verify-source.py
python3 packaging/fork/audit-i18n.py
cargo fmt --all -- --check
cargo xtask ci
