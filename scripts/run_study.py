"""Run a stage of a FROZEN spec on the development series (stage 11: the confirmation series, once). Resumable; one process per cell.

  .venv/bin/python scripts/run_study.py --spec SPEC-2026-11-13-multitarget-study --stage 1 --workers 8
Refuses to start unless the spec is frozen, committed and its fingerprint reproduces here.
Every finished cell is evaluated and written to the trial registry by this (single) parent process."""
import argparse, json, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
_PANELS = {}


def cell_dir(spec, stage, task, prior=None):
    """``prior``: the formula set of the cell (stages of SPEC-2026-11-14-wrapup); one directory level per set."""
    parts = [REPO, "artifacts", spec, f"stage{stage}"] + ([f"prior_{prior}"] if prior else [])
    return os.path.join(*parts, task.frequency, task.name, task.target.replace("^", "_"))


def _work(args):
    spec, stage, task, prior = args
    import warnings; warnings.filterwarnings("ignore")
    from iba.data.panel import load_panel
    from iba.protocol.study import STAGES, prior_file
    from iba.protocol.walkforward import run_cell
    st = STAGES[stage]
    if (task.frequency, prior) not in _PANELS:
        _PANELS[(task.frequency, prior)] = load_panel(task.frequency, formulas=prior_file(prior),
                                                      confirmation_run=spec if st.get("split") == "confirmation" else None)
    methods = st["methods"] + st.get("extra", {}).get(prior, [])
    if st.get("pooled_stage"):                                # pooled formulas found by an earlier stage of the same spec
        from iba.protocol.study import stratum_of
        from iba.search import pooled
        if pooled.STORE_DIR is None:
            pooled.STORE_DIR = os.path.join(REPO, "artifacts", spec, f"stage{st['pooled_stage']}", *([f"prior_{prior}"] if prior else []))
            pooled.POOL_OF = stratum_of()
    if st.get("pooled_store"):                                # formulas found by another spec's pooled searches (the development colonies)
        from iba.protocol.study import stratum_of
        from iba.search import pooled
        if pooled.STORE_DIR is None:
            sp, stg, pset = st["pooled_store"]
            pooled.STORE_DIR = os.path.join(REPO, "artifacts", sp, f"stage{stg}", f"prior_{pset}")
            pooled.POOL_OF = stratum_of()
    out = cell_dir(spec, stage, task, prior)
    t0 = time.perf_counter()
    try:
        pred, meta = run_cell(_PANELS[(task.frequency, prior)], task, methods, estimators=st["estimators"], seeds=st["seeds"],
                              with_garch=st["garch"] or prior in st.get("garch_sets", ()))
        os.makedirs(out, exist_ok=True)
        meta["seconds_total"] = time.perf_counter() - t0
        meta["prior_set"] = prior
        with open(os.path.join(out, "meta.json"), "w") as fh:
            json.dump(meta, fh, indent=1, default=str)
        pred.to_csv(os.path.join(out, "predictions.csv.tmp"), index=False)
        os.replace(os.path.join(out, "predictions.csv.tmp"), os.path.join(out, "predictions.csv"))     # written last and atomically: marks the forecasts as made
        return ("OK", task, prior, time.perf_counter() - t0, "")
    except Exception as exc:
        import traceback
        return ("FAIL", task, prior, time.perf_counter() - t0, f"{exc}\n{traceback.format_exc()[-1200:]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--stage", type=int, required=True)
    ap.add_argument("--workers", type=int, default=8); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--frequency", choices=["weekly", "monthly"]); ap.add_argument("--kind")
    ap.add_argument("--priors", help="comma-separated formula sets (stages that run over formula sets); default: all of the stage")
    a = ap.parse_args()
    from iba.eval.registry import TrialRegistry
    from iba.protocol.spec import require_frozen
    from iba.protocol.study import STAGES, development_tasks
    from iba.protocol.walkforward import evaluate, protocol_for
    fm = require_frozen(a.spec)
    from iba.protocol.study import FIRST_SPEC
    if STAGES[a.stage].get("spec", FIRST_SPEC) != a.spec:
        sys.exit(f"stage {a.stage} belongs to {STAGES[a.stage].get('spec', FIRST_SPEC)}, not to {a.spec}")
    with open(os.path.join(REPO, "docs", "DEVIATIONS.md")) as fh:          # deviations recorded for this spec so far
        n_dev = sum(1 for line in fh if line.startswith("|") and len(line.split("|")) > 2 and line.split("|")[2].strip().startswith(a.spec))
    from iba.protocol.study import stage_priors, stage_tasks
    priors = [p for p in stage_priors(a.stage) if not a.priors or p in a.priors.split(",")]
    tasks = [(t, p) for p in priors for t in stage_tasks(a.stage) if (not a.frequency or t.frequency == a.frequency) and (not a.kind or t.kind == a.kind)]
    todo = [(t, p) for t, p in tasks if not os.path.exists(os.path.join(cell_dir(a.spec, a.stage, t, p), "predictions.csv"))]
    unevaluated = [(t, p) for t, p in tasks if (t, p) not in set(todo) and not os.path.exists(os.path.join(cell_dir(a.spec, a.stage, t, p), "metrics.csv"))]
    if a.limit:
        todo = todo[: a.limit]
    print(f"spec {a.spec} (frozen, fingerprint {fm['fingerprint']}), stage {a.stage}: {len(tasks)} cells, {len(todo)} to run", flush=True)
    reg = TrialRegistry(os.path.join(REPO, "registry", "trials.jsonl"))
    try:
        os.nice(10)
    except OSError:
        pass
    first = priors[0]

    def record(task, prior):
        """Evaluate a finished cell and write its registry rows. In a stage that runs over formula sets the benchmarks and
        references are the same in every set: they are registered with the first set only (IBA configurations with every set)."""
        d = cell_dir(a.spec, a.stage, task, prior)
        pred = pd.read_csv(os.path.join(d, "predictions.csv"), parse_dates=["date"])
        ev = evaluate(pred, task, protocol_for(task.frequency).periods_per_year, reg, a.spec, STAGES[a.stage].get("split", "development"),
                      {"stage": a.stage, "fingerprint": fm["fingerprint"], "deviations": n_dev, **({"prior": prior} if prior else {})},
                      register=None if prior == first else (lambda c: c.startswith("iba_")))
        ev.to_csv(os.path.join(d, "metrics.csv.tmp"), index=False)
        os.replace(os.path.join(d, "metrics.csv.tmp"), os.path.join(d, "metrics.csv"))

    for task, prior in unevaluated:                              # forecasts made by an interrupted run: evaluate, do not recompute
        record(task, prior)
    if unevaluated:
        print(f"evaluated {len(unevaluated)} cells whose forecasts existed without an evaluation", flush=True)
    done = 0
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(_work, (a.spec, a.stage, t, p)) for t, p in todo]
        for f in as_completed(futs):
            status, task, prior, secs, err = f.result(); done += 1
            if status == "OK":
                record(task, prior)
            print(f"[{done}/{len(todo)}] {status} {prior or ''} {task.frequency} {task.name} {task.target} {secs:.0f}s {err}", flush=True)
    print("STAGE DONE", flush=True)
