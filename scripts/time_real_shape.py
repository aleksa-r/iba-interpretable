"""Timing on a SYNTHETIC weekly panel of the real shape (956 weeks, 8 groups x 4 factors), with the
real protocol and search budget. No real series is touched; only seconds are reported."""
import os, sys, time, json
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.data.panel import Panel
from iba.protocol.dataset import Task
from iba.protocol.study import STAGES
from iba.protocol.walkforward import WEEKLY, run_cell

rng = np.random.default_rng(1)
n = 956
idx = pd.date_range("2008-06-06", periods=n, freq="W-FRI")
groups = {g: [f"{g}{i}" for i in range(4)] for g in ("IR", "B", "V", "AP", "ST", "FX", "COM", "MC")}
f = pd.DataFrame(rng.normal(size=(n, 32)), index=idx, columns=[c for v in groups.values() for c in v])
vol = np.exp(0.3 * np.cumsum(rng.normal(0, 0.04, n))) * 0.02
r = pd.DataFrame({"T": 0.001 + rng.normal(0, 1, n) * vol}, index=idx)
rv = pd.DataFrame({"T": (vol * (1 + 0.2 * np.abs(rng.normal(size=n)))) ** 2}, index=idx)
days = pd.bdate_range(idx[0] - pd.Timedelta(days=400), idx[-1])
daily = pd.DataFrame({"T": rng.normal(0, 0.01, len(days))}, index=days)
formulas = {"groups": {**{g: [[c[0], "high"], [c[1], "not_high"]] for g, c in groups.items()}, "ENDG": [["__target__", "high"]]}}
panel = Panel("weekly", f, groups, r, rv, daily, formulas, 52)
out = {}
for stage in (1, 2):
    st = STAGES[stage]
    for task in (Task("T", "return", 4), Task("T", "logrv", 1), Task("T", "tail_loss", 4, 0.10)):
        t0 = time.perf_counter()
        pred, meta = run_cell(panel, task, st["methods"], estimators=st["estimators"], seeds=st["seeds"], with_garch=st["garch"])
        secs = time.perf_counter() - t0
        b = {}
        for blk in meta["blocks"]:
            for k, v in blk["seconds"].items():
                b[k] = b.get(k, 0.0) + v
        out[f"stage{stage}:{task.name}"] = {"seconds": round(secs, 1), "configs": int(sum("|" in c or c.startswith("iba_") for c in pred.columns)),
                                           "top": {k: round(v, 1) for k, v in sorted(b.items(), key=lambda kv: -kv[1])[:6]}}
        print(f"stage{stage} {task.name}: {secs:.1f}s", out[f"stage{stage}:{task.name}"]["top"], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "timing", "real_shape.json"), "w"), indent=1)
print("TIMING DONE")
