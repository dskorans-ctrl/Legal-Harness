#!/bin/bash
CAP=52428800                      # 50 MiB of combined stdout and stderr
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLCHAIN="${CASEFILE_TOOLCHAIN:-$HOME/.casefile-dev}/$(basename "$ROOT")"
export UV_PYTHON_INSTALL_DIR="$TOOLCHAIN/python" UV_CACHE_DIR="$TOOLCHAIN/cache" UV_PROJECT_ENVIRONMENT="$TOOLCHAIN/venv"
[ -d "$TOOLCHAIN/venv/bin" ] && PATH="$TOOLCHAIN/venv/bin:$PATH"
[ "$#" -ge 1 ] || { echo "run.sh: usage: scripts/run.sh <cmd> [args]" >&2; exit 96; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/casefile-run.XXXXXX")" \
  || { echo "run.sh: cannot create capture dir under ${TMPDIR:-/tmp}; exit 98" >&2; exit 98; }
exec python3 "$ROOT/scripts/run_capture.py" "$CAP" "$tmp" "$@"
