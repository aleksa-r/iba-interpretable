#!/usr/bin/env bash
# SPEC-2026-11-14-abc-v3 end to end: stage 5 (pooled searches, 424 pool-blocks), stage 6 (forecasts
# of every arm on the 458 development cells), each with a second pass that retries failures, then
# the pre-written report. Resumable.
set -u
cd "$(dirname "$0")/.."
S=SPEC-2026-11-14-abc-v3
PY=.venv/bin/python
echo "=== $(date '+%F %T') stage 5 (pooled searches)"
$PY scripts/run_pooled_search.py --spec $S --workers 8 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 5 retry pass"
$PY scripts/run_pooled_search.py --spec $S --workers 8 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') stage 6 (forecasts)"
$PY scripts/run_study.py --spec $S --stage 6 --workers 8 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 6 retry pass"
$PY scripts/run_study.py --spec $S --stage 6 --workers 8 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') report"
$PY scripts/make_abc3_report.py > artifacts/logs/abc3_report.txt 2>&1; echo "report exit $?"
echo "=== $(date '+%F %T') ALL DONE"
