#!/usr/bin/env bash
# SPEC-2026-11-15-confirmation-hf, once: the hashes of the machine, the panel of the BarclayHedge indices built from
# the owner's spreadsheets, stage 12 (every cell with the frozen method, the benchmarks and the controls), a pass that
# re-runs cells that failed for a technical reason, then the pre-written report. Refuses unless the spec is frozen
# and committed.
set -u
cd "$(dirname "$0")/.."
S=SPEC-2026-11-15-confirmation-hf
PY=.venv/bin/python
W=${WORKERS:-8}
echo "=== $(date '+%F %T') hashes of the fingerprint cell"
$PY - <<'PYEOF' || { echo "the spec is not frozen or a hash differs: stop"; exit 1; }
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "src")
from iba.eval.fingerprint import fingerprint_benchmarks, fingerprint_xgb
from iba.protocol.spec import require_frozen
fm = require_frozen("SPEC-2026-11-15-confirmation-hf")
got = {"bench_hash": fingerprint_benchmarks(), "xgb_hash": fingerprint_xgb()}
print("fingerprint", fm["fingerprint"], got); sys.exit(0 if all(fm[k] == v for k, v in got.items()) else 1)
PYEOF
if [ ! -f data/panels/monthly_confirmation_bh/manifest.json ]; then
  echo "=== $(date '+%F %T') panel of the hedge-fund confirmation series"
  $PY scripts/ingest_barclayhedge.py 2>&1 | grep -v -i warning
  [ -f data/panels/monthly_confirmation_bh/manifest.json ] || { echo "the panel was not built: stop"; exit 1; }
fi
echo "=== $(date '+%F %T') stage 12 (hedge-fund confirmation cells)"
$PY scripts/run_study.py --spec $S --stage 12 --workers $W 2>&1 | grep --line-buffered -v -i warning
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "stage 12 did not finish: stop"; exit 1; }
echo "=== $(date '+%F %T') stage 12, second pass for cells that failed"
$PY scripts/run_study.py --spec $S --stage 12 --workers $W 2>&1 | grep --line-buffered -v -i warning | grep -E "FAIL|cells,|STAGE DONE|evaluated"
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "the second pass did not finish: stop"; exit 1; }
echo "=== $(date '+%F %T') cells"
$PY - <<'PYEOF' || { echo "cells could not be counted: stop"; exit 1; }
import os, sys; sys.path.insert(0, "src")
from iba.protocol import study
tasks, sets = study.hf_confirmation_tasks(), study.STAGES[12]["priors"]
d = lambda t, p: os.path.join("artifacts", "SPEC-2026-11-15-confirmation-hf", "stage12", f"prior_{p}", t.frequency, t.name, t.target)
cells = [(t, p) for t in tasks for p in sets]
no_pred = [(t.target, t.name, p) for t, p in cells if not os.path.exists(os.path.join(d(t, p), "predictions.csv"))]
no_eval = [(t.target, t.name, p) for t, p in cells if not os.path.exists(os.path.join(d(t, p), "metrics.csv"))]
print(f"{len(cells)} cell runs ({len(tasks)} cells x {len(sets)} formula sets); without forecasts: {len(no_pred)}; without evaluation: {len(no_eval)}")
for x in no_eval[:40]:
    print("  incomplete:", *x)
PYEOF
echo "=== $(date '+%F %T') report"
$PY scripts/make_confirmation_hf_report.py > artifacts/logs/confirmation_hf_report.txt 2>&1; RC=$?; echo "report exit $RC"
[ "$RC" -eq 0 ] || { tail -3 artifacts/logs/confirmation_hf_report.txt; echo "=== $(date '+%F %T') THE REPORT FAILED"; exit 1; }
echo "=== $(date '+%F %T') ALL DONE"
