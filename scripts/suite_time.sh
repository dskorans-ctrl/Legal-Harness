#!/bin/bash
# T-11: every suite must pass and finish strictly below the budget.
set -u
export LC_ALL=C
ROOT="$(cd -P "$(dirname "$0")/.." && pwd -P)" || exit 1
cd "$ROOT" || exit 1
runs="${1:-3}"
budget="${SUITE_BUDGET:-90}"
if [ "$#" -gt 1 ] || ! [[ "$runs" =~ ^[1-9][0-9]*$ ]] ||
    ! awk -v b="$budget" 'BEGIN { exit !(b ~ /^[0-9]+([.][0-9]+)?$/ && b > 0) }'; then
    echo "suite_time: usage: SUITE_BUDGET=<positive seconds> scripts/suite_time.sh [positive runs]" >&2
    exit 1
fi
capture="$(mktemp "${TMPDIR:-/tmp}/suite-time.XXXXXX")" || exit 1
trap 'rm -f "$capture"' EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
failed=0
maximum=0
for ((i=1; i<=runs; i++)); do
    if [ "${SUITE_CMD+x}" = x ]; then
        bash -c "$SUITE_CMD" >"$capture" 2>&1
    else
        /usr/bin/time -p scripts/run.sh pytest -q >"$capture" 2>&1
    fi
    command_exit=$?
    cat "$capture"
    seconds="$(awk '
        $1 == "real" {
            if (NF != 2 || $2 !~ /^[0-9]+([.][0-9]+)?$/) bad=1
            else { count++; if (count == 1 || $2+0 > maximum+0) maximum=$2 }
        }
        END { if (!count || bad) print "missing"; else print maximum }
    ' "$capture")"
    verdict=PASS
    if [ "$seconds" = missing ]; then
        verdict=FAIL
        maximum=missing
    else
        if [ "$maximum" != missing ]; then
            maximum="$(awk -v a="$maximum" -v b="$seconds" 'BEGIN { print (a+0 > b+0 ? a : b) }')"
        fi
        if ! awk -v s="$seconds" -v b="$budget" 'BEGIN { exit !(s < b) }'; then
            verdict=FAIL
        fi
    fi
    if [ "$command_exit" -ne 0 ]; then verdict=FAIL; fi
    if [ "$verdict" = FAIL ]; then failed=1; fi
    echo "suite_time run=$i real=$seconds budget=$budget verdict=$verdict"
done
verdict=PASS
if [ "$failed" -ne 0 ]; then verdict=FAIL; fi
echo "suite_time runs=$runs max=$maximum verdict=$verdict"
exit "$failed"
