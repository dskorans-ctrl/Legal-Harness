#!/bin/bash
CAP=52428800                      # 50 MiB of combined stdout and stderr
ROOT="$(cd -P "$(dirname "$0")/.." && pwd -P)" || exit 95
TOOLCHAIN="${CASEFILE_TOOLCHAIN:-$HOME/.casefile-dev}/$(basename "$ROOT")"
case "$TOOLCHAIN" in /*) ;; *) TOOLCHAIN="$PWD/$TOOLCHAIN" ;; esac
[ "$#" -ge 1 ] || { echo "run.sh: usage: scripts/run.sh <cmd> [args]" >&2; exit 96; }
# One identity guard (D24) judges the override and every child path exported below.
verdict="$(python3 -I "$ROOT/src/casefile/pathguard.py" "$ROOT" "$TOOLCHAIN" "$TOOLCHAIN/python" \
    "$TOOLCHAIN/cache" "$TOOLCHAIN/venv" "$TOOLCHAIN/venv/bin" 2>&1)"
# The token is the last line; an interpreter may print a warning above it.
case "${verdict##*$'\n'}" in
    "pathguard outside "*) ;;
    "pathguard inside "*) echo "run.sh: toolchain must be outside the checkout; exit 95" >&2; exit 95 ;;
    *) echo "run.sh: cannot verify toolchain path: ${verdict:-no verdict}; exit 95" >&2; exit 95 ;;
esac
export UV_PYTHON_INSTALL_DIR="$TOOLCHAIN/python" UV_CACHE_DIR="$TOOLCHAIN/cache" UV_PROJECT_ENVIRONMENT="$TOOLCHAIN/venv"
[ -d "$TOOLCHAIN/venv/bin" ] && PATH="$TOOLCHAIN/venv/bin:$PATH"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/casefile-run.XXXXXX")" \
  || { echo "run.sh: cannot create capture dir under ${TMPDIR:-/tmp}; exit 98" >&2; exit 98; }
exec python3 "$ROOT/scripts/run_capture.py" "$CAP" "$tmp" "$@"
