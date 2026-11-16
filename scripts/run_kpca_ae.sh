#!/usr/bin/env bash
# SPEC-2026-11-14-benchmarks-kpca-ae end to end: stage 10 (kernel PCA and the autoencoder on the 458
# development cells, three estimators), a retry pass, then the pre-written report, which needs the
# finished wrap-up run. With WAIT_FOR=<log file> it first waits until that log says ALL DONE.
set -u
cd "$(dirname "$0")/.."
S=SPEC-2026-11-14-benchmarks-kpca-ae
PY=.venv/bin/python
W=${WORKERS:-8}
if [ -n "${WAIT_FOR:-}" ]; then
  echo "=== $(date '+%F %T') waiting for $WAIT_FOR"
  until grep -q "ALL DONE\|: stop" "$WAIT_FOR"; do sleep 30; done
fi
echo "=== $(date '+%F %T') hashes of the fingerprint cell"
$PY - <<'PYEOF' || { echo "a hash differs from the spec: stop"; exit 1; }
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, "src")
from iba.eval.fingerprint import fingerprint_benchmarks, fingerprint_xgb
from iba.protocol.spec import read_front_matter
fm = read_front_matter("SPEC-2026-11-14-benchmarks-kpca-ae")
got = {"bench_hash": fingerprint_benchmarks(), "xgb_hash": fingerprint_xgb()}
print(got); sys.exit(0 if all(fm[k] == v for k, v in got.items()) else 1)
PYEOF
echo "=== $(date '+%F %T') stage 10 (kernel PCA, autoencoder)"
$PY scripts/run_study.py --spec $S --stage 10 --workers $W 2>&1 | grep --line-buffered -v -i warning
echo "=== $(date '+%F %T') stage 10 retry pass"
$PY scripts/run_study.py --spec $S --stage 10 --workers $W 2>&1 | grep --line-buffered -v -i warning | tail -4
echo "=== $(date '+%F %T') report"
$PY scripts/make_kpca_ae_report.py > artifacts/logs/kpca_ae_report.txt 2>&1; echo "report exit $?"
echo "=== $(date '+%F %T') ALL DONE"
