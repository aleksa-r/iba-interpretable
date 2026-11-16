#!/usr/bin/env bash
# SPEC-2026-11-14-abc-v2 end to end: stage 4 (ABC over the whole space, 458 development cells,
# 3 seeds), a second pass that retries failures, then the pre-written report. Resumable.
set -u
cd "$(dirname "$0")/.."
S=SPEC-2026-11-14-abc-v2
PY=.venv/bin/python
echo "=== $(date '+%F %T') stage 4"
$PY scripts/run_study.py --spec $S --stage 4 --workers 8 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 4 retry pass"
$PY scripts/run_study.py --spec $S --stage 4 --workers 8 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') report"
$PY scripts/make_abc2_report.py > artifacts/logs/abc2_report.txt 2>&1; echo "report exit $?"
echo "=== $(date '+%F %T') ALL DONE"
