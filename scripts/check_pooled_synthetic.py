"""SPEC-2026-11-14-abc-v3 on SYNTHETIC data only: what pooling and noise-aware replacement do when
the truth is known. A weekly panel of the real shape (956 weeks, 8 groups x 4 factors, two
windows) with EIGHT targets that share the factors; returns with no signal, or with one weak
signal common to all targets that the prior only partly describes (h = 4). For each arm
(anchored / spread start, greedy / noise-aware) on one series and on the pool of eight: gain on
the fitness folds, gain of the winner on the clean outer rows, acceptance, size, seconds.

  for r in 0 1; do for d in 0 1 2; do .venv/bin/python scripts/check_pooled_synthetic.py $r $d & done; done; wait
  .venv/bin/python scripts/check_pooled_synthetic.py summary"""
import glob, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
import numpy as np, pandas as pd

OUT = os.path.join(HERE, "..", "artifacts", "timing")
if sys.argv[1] == "summary":
    d = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(OUT, "abc3_pooled_synthetic_*.csv"))])
    pd.set_option("display.width", 200)
    print(len(d), "searches")
    print(d.groupby(["signal", "pool", "arm"])[["inner_gain", "clean_gain", "accepted", "literals", "seconds"]].mean().round(4).to_string())
    sys.exit()
from scipy.stats import norm
from iba.data.panel import Panel
from iba.protocol.dataset import Task
from iba.protocol.walkforward import WEEKLY, block_contexts
from iba.search.pooled import ARMS, make_evaluator, run_arm

K = 8
signal, dseed = bool(int(sys.argv[1])), int(sys.argv[2])
rng = np.random.default_rng(900 + dseed)
n = 956
idx = pd.date_range("2008-06-06", periods=n, freq="W-FRI")
groups = {g: [f"{g}{i}" for i in range(4)] for g in ("IR", "B", "V", "AP", "ST", "FX", "COM", "MC")}
f = pd.DataFrame(rng.normal(size=(n, 32)), index=idx, columns=[c for v in groups.values() for c in v])
f = f.rolling(8, min_periods=1).mean() * np.sqrt(8)
u = pd.DataFrame(norm.cdf(f.values), index=idx, columns=f.columns)
sig = (2 * u["IR0"] * (1 - u["IR2"]) + (1 - u["V1"]) + u["COM3"]).shift(1).fillna(1.5).values
targets = [f"S{k}" for k in range(K)]
r, rv = {}, {}
for t in targets:
    vol = np.exp(0.3 * np.cumsum(rng.normal(0, 0.04, n))) * 0.02
    r[t] = (0.004 if signal else 0.0) * (sig - sig.mean()) + rng.normal(0, 1, n) * vol
    rv[t] = (vol * (1 + 0.2 * np.abs(rng.normal(size=n)))) ** 2
formulas = {"groups": {**{g: [[c[0], "high"], [c[1], "not_high"]] for g, c in groups.items()}, "ENDG": [["__target__", "high"]]}}
panel = Panel("weekly", f, groups, pd.DataFrame(r, index=idx), pd.DataFrame(rv, index=idx), None, formulas, 52)
by_block = {}
for t in targets:
    for b, ctx in block_contexts(panel, Task(t, "return", 4), WEEKLY):
        by_block.setdefault(b, []).append(ctx)
rows = []
for b, ctxs in by_block.items():
    for pool, members in (("one series", ctxs[:1]), ("eight series", ctxs)):
        built = None
        for arm in ARMS:
            ev = make_evaluator(members, arm, built); built = ev.members
            t0 = time.perf_counter()
            res = run_arm(ev, arm, 2000, 0, 20)
            d = res.diag
            rows.append({"signal": signal, "pool": pool, "arm": arm, "inner_gain": 1 - d["inner_best"] / d["inner_prior"],
                         "clean_gain": 1 - d["clean_best"] / d["clean_prior"], "accepted": res.accepted, "literals": d["literals"],
                         "moved": res.best != ev.space.prior, "seconds": time.perf_counter() - t0})
    print("block", b, "done", flush=True)
os.makedirs(OUT, exist_ok=True)
pd.DataFrame(rows).to_csv(os.path.join(OUT, f"abc3_pooled_synthetic_{int(signal)}_{dseed}.csv"), index=False)
