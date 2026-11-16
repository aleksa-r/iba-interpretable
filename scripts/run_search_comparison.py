"""Stage 3 of a FROZEN spec: search algorithms at equal budget on the fixed comparison sample.

For every cell of the sample and every re-selection block: ABC, GA, binary PSO and simulated
annealing with the same fitness, budget (distinct evaluations) and acceptance test, 20 seeds each,
plus ABC with "global validation" (select on the outer fold) as the labelled secondary variant.
Only search diagnostics are produced (inner fitness, outer-fold loss, optimism, acceptance);
no forecast. Analysis (pre-written): per algorithm the mean over (cell, block) units of the
seed-averaged inner and outer scores relative to the prior, Friedman test across algorithms and
Wilcoxon tests of ABC against each comparator with Holm adjustment."""
import argparse, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ALGOS = [("abc", "inner"), ("ga", "inner"), ("pso", "inner"), ("sa", "inner"), ("abc", "outer")]
SEEDS = list(range(20))


def _work(task, panel=None):
    import warnings; warnings.filterwarnings("ignore")
    from iba.data.panel import load_panel
    from iba.protocol.walkforward import block_contexts
    from iba.search.run import search
    panel = panel or load_panel(task.frequency)
    rows = []
    for b, ctx in block_contexts(panel, task):
        for algo, select in ALGOS:
            for seed in SEEDS:
                res, space = search(ctx, algo, "A", seed, select)
                d = res.diag
                rows.append({"target": task.target, "task": task.name, "block": b, "algorithm": algo + ("_gv" if select == "outer" else ""),
                             "seed": seed, "n_evals": res.n_evals, "accepted": res.accepted, "inner_best": d["inner_best"],
                             "outer_best": d["outer_best"], "inner_prior": d["inner_prior"], "outer_prior": d["outer_prior"],
                             "optimism": d["optimism"], "distance": d["distance"], "literals": d["literals"], "seconds": d["seconds"]})
    return rows


def analyse(df: pd.DataFrame) -> str:
    from scipy import stats
    df = df.assign(inner_gain=1 - df.inner_best / df.inner_prior, outer_gain=1 - df.outer_best / df.outer_prior)
    unit = df.groupby(["target", "task", "block", "algorithm"])[["inner_gain", "outer_gain", "optimism", "accepted", "n_evals"]].mean().reset_index()
    summ = unit.groupby("algorithm")[["inner_gain", "outer_gain", "optimism", "accepted", "n_evals"]].mean()
    lines = ["## Search comparison at equal budget (units = cell x block, seed-averaged)\n", summ.round(5).to_markdown(), ""]
    for metric in ("inner_gain", "outer_gain"):
        W = unit.pivot_table(index=["target", "task", "block"], columns="algorithm", values=metric)
        main = [a for a in ("abc", "ga", "pso", "sa") if a in W]
        if len(main) >= 3:
            fr = stats.friedmanchisquare(*[W[a].values for a in main])
            lines.append(f"- {metric}: Friedman chi2 = {fr.statistic:.2f}, p = {fr.pvalue:.4f} over {len(W)} units")
        ps = {}
        for a in [c for c in W.columns if c != "abc"]:
            d = W["abc"] - W[a]
            if np.allclose(d, 0):
                ps[a] = (float("nan"), 0, 0)
            else:
                ps[a] = (float(stats.wilcoxon(d).pvalue), int((d > 0).sum()), int((d < 0).sum()))
        order = sorted([a for a in ps if np.isfinite(ps[a][0])], key=lambda a: ps[a][0])
        adj, run = {}, 0.0
        for i, a in enumerate(order):
            run = max(run, min(1.0, ps[a][0] * (len(order) - i))); adj[a] = run
        for a in ps:
            lines.append(f"  - ABC vs {a}: wins {ps[a][1]}, losses {ps[a][2]}, Wilcoxon p = {ps[a][0]:.4f}, Holm p = {adj.get(a, float('nan')):.4f}")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    from iba.eval.registry import TrialRegistry
    from iba.protocol.spec import require_frozen
    from iba.protocol.study import search_comparison_cells
    fm = require_frozen(a.spec)
    out = os.path.join(REPO, "artifacts", a.spec, "stage3"); os.makedirs(out, exist_ok=True)
    cells = search_comparison_cells()
    t0 = time.perf_counter(); rows = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for i, r in enumerate(ex.map(_work, cells)):
            rows += r; print(f"[{i + 1}/{len(cells)}] {cells[i].name} {cells[i].target} ({time.perf_counter() - t0:.0f}s)", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(out, "search_comparison.csv"), index=False)
    reg = TrialRegistry(os.path.join(REPO, "registry", "trials.jsonl"))
    for (alg, task), g in df.groupby(["algorithm", "task"]):
        reg.record(a.spec, "development", {"stage": 3, "algorithm": alg, "task": task, "seeds": len(SEEDS), "fingerprint": fm["fingerprint"]},
                   {"inner_gain": float((1 - g.inner_best / g.inner_prior).mean()), "outer_gain": float((1 - g.outer_best / g.outer_prior).mean()),
                    "optimism": float(g.optimism.mean()), "accepted": float(g.accepted.mean()), "runs": int(len(g))})
    text = analyse(df)
    res = os.path.join(REPO, "docs", "results", a.spec); os.makedirs(res, exist_ok=True)
    open(os.path.join(res, "search_comparison.md"), "w").write(text + "\n")
    print(text); print("STAGE 3 DONE")
