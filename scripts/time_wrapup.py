"""Compute measurement for SPEC-2026-11-14-wrapup (section 8), made before the freeze. Runs a few real
development cells of stage 7 and one pool-block of stage 8 and reports SECONDS ONLY: forecasts and search
results are discarded unread, nothing is evaluated, nothing is written to the registry."""
import os, sys, time, json
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import warnings; warnings.filterwarnings("ignore")
from iba.data.panel import load_panel
from iba.protocol.dataset import Task
from iba.protocol.study import POOLED_STAGES, STAGES, pool_units, prior_file, stage_tasks
from iba.protocol.walkforward import block_contexts, protocol_for, run_cell
from iba.search.pooled import pooled_search_block

st = STAGES[7]
tasks = stage_tasks(7)
pick = {}
for t in tasks:                                               # the first cell of each (frequency, kind, horizon)
    pick.setdefault((t.frequency, t.kind, t.h), t)
out = {"stage7": {}, "stage8": {}}
for pset in ("K1", "Kc", "G"):
    panels = {f: load_panel(f, formulas=prior_file(pset)) for f in ("weekly", "monthly")}
    methods = st["methods"] + st["extra"].get(pset, [])
    for key, t in pick.items():
        t0 = time.perf_counter()
        run_cell(panels[t.frequency], t, methods, estimators=st["estimators"], seeds=st["seeds"], with_garch=st["garch"])
        out["stage7"][f"{pset}:{t.frequency}:{t.name}"] = round(time.perf_counter() - t0, 1)
        print(pset, t.frequency, t.name, out["stage7"][f"{pset}:{t.frequency}:{t.name}"], flush=True)
n = {(f, k, h): sum(1 for t in tasks if (t.frequency, t.kind, t.h) == (f, k, h)) for (f, k, h) in pick}
tot = {p: sum(out["stage7"][f"{p}:{t.frequency}:{t.name}"] * n[key] for key, t in pick.items()) for p in ("K1", "Kc", "G")}
core_h7 = (tot["G"] + 2 * tot["Kc"] + 15 * tot["K1"]) / 3600
print(f"stage 7: one plain set {tot['K1'] / 3600:.2f} core-h, one consensus set {tot['Kc'] / 3600:.2f}, G {tot['G'] / 3600:.2f}; all 18 sets {core_h7:.1f} core-h", flush=True)

panels = {f: load_panel(f, formulas=prior_file("Kc")) for f in ("weekly", "monthly")}
units = pool_units(all_pool=False)
seen, core_s8 = {}, 0.0
for u in units:
    freq, kind, q, h, name, pool, targets = u
    k = (freq, "tail" if kind.startswith("tail") else "reg")
    if k not in seen and len(targets) in (5, 11):
        cfg = protocol_for(freq)
        ctxs = [next(c for b, c in block_contexts(panels[freq], Task(tgt, kind, h, q, freq), cfg) if b == 3) for tgt in targets]
        t0 = time.perf_counter()
        pooled_search_block(ctxs, STAGES[9]["seeds"], cfg.search_budget, cfg.colony, arms=POOLED_STAGES[8]["arms"])
        seen[k] = (time.perf_counter() - t0) / len(targets)
        print("stage 8", freq, name, pool, f"{seen[k]:.1f} s per member", flush=True)
for u in units:
    core_s8 += 4 * len(u[6]) * seen[(u[0], "tail" if u[1].startswith("tail") else "reg")]
out["stage8"] = {f"{a}:{b}": round(v, 1) for (a, b), v in seen.items()}
out["core_hours"] = {"stage7": round(core_h7, 1), "stage8": round(core_s8 / 3600, 1)}
print(f"stage 8: {core_s8 / 3600:.1f} core-h", flush=True)
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "timing"), exist_ok=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "timing", "wrapup.json"), "w"), indent=1)
print("TIMING DONE")
