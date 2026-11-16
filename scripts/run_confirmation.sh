#!/usr/bin/env bash
# SPEC-2026-11-14-confirmation, once: the hashes of the machine, the one download of the 21 confirmation series,
# stage 11 (every cell with the frozen method, the benchmarks and the controls), a pass that re-runs cells that
# failed for a technical reason, then the pre-written report. Refuses unless the spec is frozen and committed.
set -u
cd "$(dirname "$0")/.."
S=SPEC-2026-11-14-confirmation
PY=.venv/bin/python
W=${WORKERS:-8}
echo "=== $(date '+%F %T') hashes of the fingerprint cell"
$PY - <<'PYEOF' || { echo "the spec is not frozen or a hash differs: stop"; exit 1; }
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "src")
from iba.eval.fingerprint import fingerprint_benchmarks, fingerprint_xgb
from iba.protocol.spec import require_frozen
fm = require_frozen("SPEC-2026-11-14-confirmation")
got = {"bench_hash": fingerprint_benchmarks(), "xgb_hash": fingerprint_xgb()}
print("fingerprint", fm["fingerprint"], got); sys.exit(0 if all(fm[k] == v for k, v in got.items()) else 1)
PYEOF
if [ ! -f data/panels/weekly_confirmation/manifest.json ]; then
  echo "=== $(date '+%F %T') download of the confirmation series"
  $PY scripts/download_confirmation.py 2>&1 | grep -v -i warning || true
  [ -f data/panels/weekly_confirmation/manifest.json ] || { echo "download failed: stop"; exit 1; }
fi
echo "=== $(date '+%F %T') stage 11 (confirmation cells)"
$PY scripts/run_study.py --spec $S --stage 11 --workers $W 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 11, second pass for cells that failed"
$PY scripts/run_study.py --spec $S --stage 11 --workers $W 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') report"
$PY scripts/make_confirmation_report.py > artifacts/logs/confirmation_report.txt 2>&1; echo "report exit $?"
echo "=== $(date '+%F %T') ALL DONE"
