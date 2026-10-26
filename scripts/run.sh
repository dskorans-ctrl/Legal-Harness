#!/bin/bash
CAP=52428800                      # 50 MiB of combined stdout and stderr
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLCHAIN="${CASEFILE_TOOLCHAIN:-$HOME/.casefile-dev}/$(basename "$ROOT")"
export UV_PYTHON_INSTALL_DIR="$TOOLCHAIN/python" UV_CACHE_DIR="$TOOLCHAIN/cache" UV_PROJECT_ENVIRONMENT="$TOOLCHAIN/venv"
[ -d "$TOOLCHAIN/venv/bin" ] && PATH="$TOOLCHAIN/venv/bin:$PATH"
[ "$#" -ge 1 ] || { echo "run.sh: usage: scripts/run.sh <cmd> [args]" >&2; exit 96; }
tmp="$(mktemp -d "${TMPDIR:-/tmp}/casefile-run.XXXXXX")" \
  || { echo "run.sh: cannot create capture dir under ${TMPDIR:-/tmp}; exit 98" >&2; exit 98; }
set -o pipefail
"$@" 2>&1 | head -c "$((CAP + 1))" | tee "$tmp/out" | head -c "$CAP"
st=("${PIPESTATUS[@]}")
bytes="$(wc -c < "$tmp/out" 2>/dev/null | tr -d ' ')"
rm -rf "$tmp"
case "$bytes" in ''|*[!0-9]*)
  echo "run.sh: capture file unreadable (stages ${st[*]}); exit 98" >&2; exit 98;; esac
if [ "$bytes" -gt "$CAP" ]; then
  echo "run.sh: output cap $CAP bytes hit (child status ${st[0]}); exit 97" >&2
  exit 97
fi
if [ "${st[1]}" != 0 ] || [ "${st[2]}" != 0 ] || [ "${st[3]}" != 0 ]; then
  echo "run.sh: capture stage failed (stages ${st[*]}); exit 98" >&2
  exit 98
fi
exit "${st[0]}"
