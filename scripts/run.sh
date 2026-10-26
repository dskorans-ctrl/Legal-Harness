#!/bin/bash
CAP=52428800                      # 50 MiB of combined stdout and stderr
ROOT="$(cd -P "$(dirname "$0")/.." && pwd -P)" || exit 95
TOOLCHAIN="${CASEFILE_TOOLCHAIN:-$HOME/.casefile-dev}/$(basename "$ROOT")"
# Resolve the deepest existing directory without creating toolchain folders.
ancestor="$TOOLCHAIN"
while [ ! -d "$ancestor" ]; do
    if [ -e "$ancestor" ] || [ -L "$ancestor" ]; then
        echo "run.sh: cannot verify toolchain path; exit 95" >&2
        exit 95
    fi
    parent="$(dirname "$ancestor")"
    [ "$parent" != "$ancestor" ] || { echo "run.sh: cannot verify toolchain path; exit 95" >&2; exit 95; }
    ancestor="$parent"
done
physical="$(cd -P "$ancestor" && pwd -P)" \
    || { echo "run.sh: cannot verify toolchain path; exit 95" >&2; exit 95; }
# Check identity along both the typed path and its physical ancestors.
for candidate in "$TOOLCHAIN" "$physical"; do
    while :; do
        if [ "$candidate" -ef "$ROOT" ]; then
            echo "run.sh: toolchain must be outside the checkout; exit 95" >&2
            exit 95
        fi
        parent="$(dirname "$candidate")"
        [ "$parent" != "$candidate" ] || break
        candidate="$parent"
    done
done
export UV_PYTHON_INSTALL_DIR="$TOOLCHAIN/python" UV_CACHE_DIR="$TOOLCHAIN/cache" UV_PROJECT_ENVIRONMENT="$TOOLCHAIN/venv"
[ -d "$TOOLCHAIN/venv/bin" ] && PATH="$TOOLCHAIN/venv/bin:$PATH"
[ "$#" -ge 1 ] || { echo "run.sh: usage: scripts/run.sh <cmd> [args]" >&2; exit 96; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/casefile-run.XXXXXX")" \
  || { echo "run.sh: cannot create capture dir under ${TMPDIR:-/tmp}; exit 98" >&2; exit 98; }
exec python3 "$ROOT/scripts/run_capture.py" "$CAP" "$tmp" "$@"
