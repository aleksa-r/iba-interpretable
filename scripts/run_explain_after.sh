#!/usr/bin/env bash
# Runs the explanation step once the log named in WAIT_FOR says ALL DONE: a dry run (inputs only), then the requests.
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
if [ -n "${WAIT_FOR:-}" ]; then
  echo "=== $(date '+%F %T') waiting for $WAIT_FOR"
  until grep -q "ALL DONE\|: stop" "$WAIT_FOR"; do sleep 30; done
fi
[ -f docs/results/SPEC-2026-11-14-wrapup/final_method.json ] || { echo "no final_method.json: the wrap-up run did not finish; stop"; exit 1; }
echo "=== $(date '+%F %T') dry run"
$PY scripts/explain.py --dry-run > artifacts/logs/explain_dry.txt 2>&1 || { echo "dry run failed: stop"; tail -3 artifacts/logs/explain_dry.txt; exit 1; }
head -2 artifacts/logs/explain_dry.txt
echo "=== $(date '+%F %T') requests"
$PY scripts/explain.py 2>&1 | grep -v -i warning
echo "=== $(date '+%F %T') ALL DONE"
