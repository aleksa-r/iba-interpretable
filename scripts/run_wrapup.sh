#!/usr/bin/env bash
# SPEC-2026-11-14-wrapup end to end: stage 7 (every formula set as a fixed formula, three estimators, the
# no-search colonies, the benchmarks with XGBoost), part A of the report (the choice of the formula set),
# stage 8 (five algorithms on the pooled fitness with the chosen set), stage 9 (forecasts from the pooled ABC),
# then the full pre-written report. Each stage has a second pass that retries failures. Resumable.
set -u
cd "$(dirname "$0")/.."
S=SPEC-2026-11-14-wrapup
PY=.venv/bin/python
W=${WORKERS:-8}
echo "=== $(date '+%F %T') XGBoost hash of the fingerprint cell"
$PY - <<'PYEOF' || { echo "XGBoost hash differs from the spec: stop"; exit 1; }
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "src")
from iba.eval.fingerprint import fingerprint_xgb
from iba.protocol.spec import read_front_matter
got, want = fingerprint_xgb(), read_front_matter("SPEC-2026-11-14-wrapup")["xgb_hash"]
print("xgb hash", got, "spec", want); sys.exit(0 if got == want else 1)
PYEOF
echo "=== $(date '+%F %T') stage 7 (formula sets)"
$PY scripts/run_study.py --spec $S --stage 7 --workers $W 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 7 retry pass"
$PY scripts/run_study.py --spec $S --stage 7 --workers $W 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') report, part A (choice of the formula set)"
$PY scripts/make_wrapup_report.py --part A > artifacts/logs/wrapup_report_A.txt 2>&1 || { echo "part A failed: stop"; tail -5 artifacts/logs/wrapup_report_A.txt; exit 1; }
tail -1 artifacts/logs/wrapup_report_A.txt
echo "=== $(date '+%F %T') stage 8 (five algorithms, pooled fitness)"
$PY scripts/run_pooled_search.py --spec $S --stage 8 --workers $W 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 8 retry pass"
$PY scripts/run_pooled_search.py --spec $S --stage 8 --workers $W 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') stage 9 (forecasts from the pooled ABC)"
$PY scripts/run_study.py --spec $S --stage 9 --workers $W 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 9 retry pass"
$PY scripts/run_study.py --spec $S --stage 9 --workers $W 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') report"
$PY scripts/make_wrapup_report.py > artifacts/logs/wrapup_report.txt 2>&1; echo "report exit $?"
echo "=== $(date '+%F %T') ALL DONE"
