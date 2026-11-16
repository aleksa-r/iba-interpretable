#!/usr/bin/env bash
# The frozen development study, end to end: stage 1 (benchmarks, E1, exhaustive references),
# stage 2 (ABC variants, 3 seeds), stage 3 (search comparison), then the map. Resumable: finished
# cells are skipped, so each stage is simply called twice (the second call retries failures).
set -u
cd "$(dirname "$0")/.."
S=SPEC-2026-11-13-multitarget-study
PY=.venv/bin/python
for st in 1 2; do
  echo "=== $(date '+%F %T') stage $st"
  $PY scripts/run_study.py --spec $S --stage $st --workers 8 2>&1 | grep --line-buffered -v -i warning
  echo "=== $(date '+%F %T') stage $st retry pass"
  $PY scripts/run_study.py --spec $S --stage $st --workers 8 2>&1 | grep --line-buffered -v -i warning | tail -4
done
echo "=== $(date '+%F %T') stage 3"
$PY scripts/run_search_comparison.py --spec $S --workers 8 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') map"
$PY scripts/make_map.py $S > artifacts/logs/map.txt 2>&1; echo "map exit $?"
echo "=== $(date '+%F %T') ALL STAGES DONE"
