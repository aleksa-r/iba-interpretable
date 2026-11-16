"""The pooled searches: stage 5 of SPEC-2026-11-14-abc-v3 and stage 8 of SPEC-2026-11-14-wrapup (five
algorithms on the asset-class pools, with the chosen formula set as the prior). Resumable; one process per
(task, pool, block).

  .venv/bin/python scripts/run_pooled_search.py --spec SPEC-2026-11-14-abc-v3 --workers 8
  .venv/bin/python scripts/run_pooled_search.py --spec SPEC-2026-11-14-wrapup --stage 8 --workers 8
For every task of the spec, every pool (each asset class; "ALL" = every development series of the
frequency) and every re-selection block: the four arms (anchored / spread start, greedy /
noise-aware replacement) with three seeds on the pooled fitness, using only rows admissible at the
block origin. Output: the winner, whether it passed the pooled acceptance test on clean rows, and
the final colony, in generic column names, under artifacts/<spec>/stage5/. No forecast is made
here; stage 6 turns the formulas into forecasts per series. Every search is a registry row."""
import argparse, json, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from concurrent.futures import ProcessPoolExecutor, as_completed

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
_PANELS = {}


def _work(args):
    base, unit, block, stage, prior = args
    freq, kind, q, h, name, pool, targets = unit
    import warnings; warnings.filterwarnings("ignore")
    from iba.data.panel import load_panel
    from iba.protocol.dataset import Task
    from iba.protocol.study import POOLED_STAGES, STAGES, prior_file
    from iba.protocol.walkforward import block_contexts, protocol_for
    from iba.search.pooled import pooled_search_block, store_path
    t0 = time.perf_counter()
    try:
        if freq not in _PANELS:
            _PANELS[freq] = load_panel(freq, formulas=prior_file(prior))
        cfg = protocol_for(freq)
        ctxs = []
        for tgt in targets:
            for b, ctx in block_contexts(_PANELS[freq], Task(tgt, kind, h, q, freq), cfg):
                if b == block:
                    ctxs.append(ctx)
                    break
        if len(ctxs) != len(targets):
            raise ValueError(f"block {block} missing for some member")
        ps = POOLED_STAGES[stage]
        res = pooled_search_block(ctxs, STAGES[ps["forecast_stage"]]["seeds"], cfg.search_budget, cfg.colony, arms=ps["arms"])
        res["_meta"] = {"frequency": freq, "task": name, "pool": pool, "block": block, "members": targets, "train_rows": int(len(ctxs[0].rows)), "prior_set": prior,
                        "seconds": time.perf_counter() - t0}
        path = store_path(freq, name, pool, block, base)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".tmp", "w") as fh:
            json.dump(res, fh, indent=1)
        os.replace(path + ".tmp", path)                       # written last: marks the unit as done
        return ("OK", unit, block, time.perf_counter() - t0, "")
    except Exception as exc:
        import traceback
        return ("FAIL", unit, block, time.perf_counter() - t0, f"{exc}\n{traceback.format_exc()[-1500:]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--stage", type=int, default=5)
    a = ap.parse_args()
    from iba.eval.registry import TrialRegistry
    from iba.protocol.spec import require_frozen
    from iba.protocol.study import POOLED_STAGES, STAGES, pool_units, stage_priors
    from iba.search.pooled import store_path
    fm = require_frozen(a.spec)
    ps = POOLED_STAGES[a.stage]
    if STAGES[ps["forecast_stage"]].get("spec") != a.spec:
        sys.exit(f"the pooled searches of stage {a.stage} belong to {STAGES[ps['forecast_stage']].get('spec')}, not to {a.spec}")
    prior = stage_priors(ps["forecast_stage"])[0]              # None for the earlier spec; the chosen formula set for the wrap-up
    with open(os.path.join(REPO, "docs", "DEVIATIONS.md")) as fh:
        n_dev = sum(1 for line in fh if line.startswith("|") and len(line.split("|")) > 2 and line.split("|")[2].strip().startswith(a.spec))
    base = os.path.join(REPO, "artifacts", a.spec, f"stage{a.stage}", *([f"prior_{prior}"] if prior else []))
    units = [(u, b) for u in pool_units(all_pool=ps["all_pool"]) for b in range(4)]
    todo = [(u, b) for u, b in units if not os.path.exists(store_path(u[0], u[4], u[5], b, base))]
    todo.sort(key=lambda ub: -len(ub[0][6]) * (3 if ub[0][1].startswith("tail") else 1))       # largest first
    print(f"spec {a.spec} (frozen, fingerprint {fm['fingerprint']}), stage {a.stage}{', prior ' + prior if prior else ''}: {len(units)} pool-blocks, {len(todo)} to run", flush=True)
    reg = TrialRegistry(os.path.join(REPO, "registry", "trials.jsonl"))
    try:
        os.nice(10)
    except OSError:
        pass
    done = 0
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(_work, (base, u, b, a.stage, prior)) for u, b in todo]
        for f in as_completed(futs):
            status, unit, block, secs, err = f.result(); done += 1
            if status == "OK":
                with open(store_path(unit[0], unit[4], unit[5], block, base)) as fh:
                    res = json.load(fh)
                for arm, by_seed in res.items():
                    if arm.startswith("_"):
                        continue
                    for seed, r in by_seed.items():
                        reg.record(a.spec, "development", {"stage": a.stage, "frequency": unit[0], "task": unit[4], "pool": unit[5], "block": block, "arm": arm,
                                                           "seed": int(seed), "members": r["members"], "fingerprint": fm["fingerprint"], "deviations": n_dev,
                                                           **({"prior": prior} if prior else {})},
                                   {"accepted": float(r["accepted"]), "n_evals": r["n_evals"], **r["diag"]})
            print(f"[{done}/{len(todo)}] {status} {unit[0]} {unit[4]} {unit[5]} block {block} ({len(unit[6])} series) {secs:.0f}s {err}", flush=True)
    print("STAGE DONE", flush=True)
