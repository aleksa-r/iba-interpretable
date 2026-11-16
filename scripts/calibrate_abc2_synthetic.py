"""Optimiser settings of SPEC-2026-11-14-abc-v2, chosen on SYNTHETIC data only (no real series):
a weekly panel of the real shape (956 weeks, 8 groups x 4 factors, two z-score windows) whose
return carries a weak planted signal that the prior formula only partly describes. For every
candidate setting: inner-fitness gain over the prior at the study's budget, outer-fold gain,
acceptance, seconds. Only the modification rate of the vector moves is chosen here."""
import os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import copy
import numpy as np, pandas as pd
from scipy.stats import norm
from iba.data.panel import Panel
from iba.protocol.dataset import Task
from iba.protocol.walkforward import WEEKLY, block_contexts
from iba.search.algorithms import abc
from iba.search.fitness import FitnessEvaluator
from iba.search.space import SearchSpace
from iba.search.vector import GradedEvaluator, abc_full, abc_graded, abc_vector


def make_panel(seed, strength):
    rng = np.random.default_rng(seed)
    n = 956
    idx = pd.date_range("2008-06-06", periods=n, freq="W-FRI")
    groups = {g: [f"{g}{i}" for i in range(4)] for g in ("IR", "B", "V", "AP", "ST", "FX", "COM", "MC")}
    f = pd.DataFrame(rng.normal(size=(n, 32)), index=idx, columns=[c for v in groups.values() for c in v])
    f = f.rolling(8, min_periods=1).mean() * np.sqrt(8)                     # persistent factors, as z-scored levels are
    u = pd.DataFrame(norm.cdf(f.values), index=idx, columns=f.columns)
    # truth: IR0 high AND IR2 not high (prior says IR0 high AND IR1 not high); V1 not high (prior: V0 high AND V1 not high);
    # COM3 high (prior: COM0 high AND COM1 not high); the other five groups carry nothing
    sig = (2 * u["IR0"] * (1 - u["IR2"]) + (1 - u["V1"]) + u["COM3"]).shift(1).fillna(1.5).values
    vol = np.exp(0.3 * np.cumsum(rng.normal(0, 0.04, n))) * 0.02
    r = pd.DataFrame({"T": strength * (sig - sig.mean()) + rng.normal(0, 1, n) * vol}, index=idx)
    rv = pd.DataFrame({"T": (vol * (1 + 0.2 * np.abs(rng.normal(size=n)))) ** 2}, index=idx)
    formulas = {"groups": {**{g: [[c[0], "high"], [c[1], "not_high"]] for g, c in groups.items()}, "ENDG": [["__target__", "high"]]}}
    return Panel("weekly", f, groups, r, rv, None, formulas, 52)


SETTINGS = [("A (ball)", "a", {}), ("W", "w", {})] + [(f"V mr={m}", "v", {"mr": m}) for m in (0.05, 0.1, 0.3, 1.0)] \
    + [(f"G mr={m}", "g", {"mr": m}) for m in (0.1, 0.3, 1.0)] + [(f"Z mr={m}", "z", {"mr": m}) for m in (0.1, 0.3, 1.0)]
rows = []
for strength in (0.0, 0.004):
    for dseed in range(3):
        panel = make_panel(100 + dseed, strength)
        for task in (Task("T", "return", 4), Task("T", "tail_loss", 4, 0.10)):
            for b, ctx in block_contexts(panel, task, WEEKLY):
                if b not in (0, 3):
                    continue
                base = FitnessEvaluator(ctx, SearchSpace(ctx.ds.group_cols, ctx.prior), mode="A")
                for name, kind, kw in SETTINGS:
                    for seed in range(2):
                        ev = copy.copy(base); ev.cache, ev.n_evals, ev._prior_fit = {}, 0, None
                        if kind != "a":
                            ev.space = SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None, allow_empty=kind != "w")
                        t0 = time.perf_counter()
                        if kind == "a":
                            res = abc(ev, ev.space, budget=2000, seed=seed)
                        elif kind == "w":
                            res = abc_full(ev, ev.space, budget=2000, seed=seed)
                        elif kind == "v":
                            res = abc_vector(ev, ev.space, budget=2000, seed=seed, **kw)
                        else:
                            res = abc_graded(GradedEvaluator(ev), budget=2000, seed=seed, start="spread" if kind == "g" else "zero", **kw)
                        d = res.diag
                        rows.append({"signal": strength > 0, "task": task.kind, "setting": name, "inner_gain": 1 - d["inner_best"] / d["inner_prior"],
                                     "outer_gain": 1 - d["outer_best"] / d["outer_prior"], "accepted": res.accepted, "evals": res.n_evals,
                                     "literals": d["literals"], "groups": d.get("groups", np.nan), "seconds": time.perf_counter() - t0})
    print("strength", strength, "done", flush=True)
df = pd.DataFrame(rows)
pd.set_option("display.width", 200)
order = [s[0] for s in SETTINGS]
print(df.groupby(["signal", "setting"])[["inner_gain", "outer_gain", "accepted", "evals", "literals", "groups", "seconds"]].mean().round(4)
      .reindex([(s, o) for s in (False, True) for o in order]).to_string())
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "timing"), exist_ok=True)
df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "timing", "abc2_synthetic_calibration.csv"), index=False)
