#!/usr/bin/env bash
# Run a noisy command, store the full log in $TMPDIR, print only relevant signal.
# Usage: tools/q.sh <command...>
log="${TMPDIR:-/tmp}/adaptpulse-last.log"
"$@" >"$log" 2>&1
code=$?
lines=$(wc -l <"$log" | tr -d ' ')
bytes=$(wc -c <"$log" | tr -d ' ')
echo "exit=$code lines=$lines bytes=$bytes log=$log"
grep -nEi 'error|fail|traceback|warning|assert|exception' "$log" | head -n 25 | cut -c1-240
echo "--- tail ---"
tail -n 15 "$log" | cut -c1-240
exit $code

