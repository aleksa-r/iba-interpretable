"""SPEC-2026-11-15-ablations: the component contribution analysis on the development series. Resumable.

  .venv/bin/python scripts/run_ablations.py --workers 8
For every development cell of the wrap-up spec and the method's formula set: the fixed-formula linear forecasts
with one component changed (a group's formula removed, one literal per group, empirical-distribution scaling,
no HAR stage for volatility). The unchanged variant must equal the stored forecast of the wrap-up run; a cell
where it does not is a failure. Every variant of every cell is a registry row."""
import argparse, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from concurrent.futures import ProcessPoolExecutor, as_completed

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SPEC, SET, STAGE = "SPEC-2026-11-15-ablations", "Kc", 12
_PANELS = {}


def cell_dir(t):
    return os.path.join(REPO, "artifacts", SPEC, f"stage{STAGE}", t.frequency, t.name, t.target.replace("^", "_"))


def _work(t):
    import warnings; warnings.filterwarnings("ignore")
    import numpy as np, pandas as pd
    from iba.data.panel import load_panel
    from iba.explain.ablate import variant_forecasts
    from iba.protocol.study import WRAPUP, prior_file
    t0 = time.perf_counter()
    try:
        if t.frequency not in _PANELS:
            _PANELS[t.frequency] = load_panel(t.frequency, formulas=prior_file(SET))
        stored = pd.read_csv(os.path.join(REPO, "artifacts", WRAPUP, "stage7", f"prior_{SET}", t.frequency, t.name, t.target.replace("^", "_"), "predictions.csv"))
        v = variant_forecasts(_PANELS[t.frequency], t)
        gap = float(np.max(np.abs(v["base"] - stored["iba_e1|lin"].values)))
        if gap > 1e-9:
            raise ValueError(f"the unchanged variant differs from the stored forecast by {gap:.2e}")
        keep = [c for c in stored.columns if c in ("date", "y", "y_eval", "block", "threshold") or (c.startswith("bench|") and "::" not in c)]
        out = stored[keep].copy()
        for k, f in v.items():
            out[f"abl_{k}|lin"] = f
        d = cell_dir(t); os.makedirs(d, exist_ok=True)
        out.to_csv(os.path.join(d, "predictions.csv.tmp"), index=False)
        os.replace(os.path.join(d, "predictions.csv.tmp"), os.path.join(d, "predictions.csv"))
        return ("OK", t, time.perf_counter() - t0, "")
    except Exception as exc:
        import traceback
        return ("FAIL", t, time.perf_counter() - t0, f"{exc}\n{traceback.format_exc()[-800:]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    import pandas as pd
    from iba.eval.map import REFERENCE, pointwise
    from iba.eval.registry import TrialRegistry
    from iba.protocol.spec import require_frozen
    from iba.protocol.study import stage_tasks
    fm = require_frozen(SPEC)
    tasks = stage_tasks(7)
    todo = [t for t in tasks if not os.path.exists(os.path.join(cell_dir(t), "metrics.csv"))]
    print(f"spec {SPEC} (frozen, fingerprint {fm['fingerprint']}): {len(tasks)} cells, {len(todo)} to run", flush=True)
    reg = TrialRegistry(os.path.join(REPO, "registry", "trials.jsonl"))
    try:
        os.nice(10)
    except OSError:
        pass
    done = 0
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for f in as_completed([ex.submit(_work, t) for t in todo]):
            status, t, secs, err = f.result(); done += 1
            if status == "OK":
                pred = pd.read_csv(os.path.join(cell_dir(t), "predictions.csv"))
                ref = float(pointwise(pred, t.kind, REFERENCE[t.kind]).mean())
                rows = []
                for c in [c for c in pred.columns if c.startswith("abl_")]:
                    loss = float(pointwise(pred, t.kind, c).mean())
                    rows.append({"target": t.target, "task": t.name, "config": c, "loss": loss, "rel_to_reference": loss / ref - 1})
                    reg.record(SPEC, "development", {"target": t.target, "task": t.name, "frequency": t.frequency, "config": c, "prior": SET, "stage": STAGE,
                                                     "fingerprint": fm["fingerprint"]}, {"loss": loss, "rel_to_reference": loss / ref - 1})
                pd.DataFrame(rows).to_csv(os.path.join(cell_dir(t), "metrics.csv"), index=False)
            print(f"[{done}/{len(todo)}] {status} {t.frequency} {t.name} {t.target} {secs:.0f}s {err}", flush=True)
    print("STAGE DONE", flush=True)
