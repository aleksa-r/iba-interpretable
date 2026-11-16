"""The acceptance test on SYNTHETIC returns without any signal (SPEC-2026-11-14-abc-v2, sections 0
and 4): for the first study's ABC (A) and the four whole-space searches, the winner's gain over
the prior on the whole outer fold and on its clean rows, and how often each version of the test
passes it. With no signal an honest test passes about one winner in six and the gain is not positive.

  for a in 0 4 8 12 16 20 24 28; do .venv/bin/python scripts/check_acceptance_synthetic.py $a $((a+4)) & done; wait
  .venv/bin/python scripts/check_acceptance_synthetic.py summary"""
import copy, glob, os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import pandas as pd

OUT = os.path.join(HERE, "..", "artifacts", "timing")
if sys.argv[1] == "summary":
    d = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(OUT, "abc2_acceptance_synthetic_*.csv"))])
    print(len(d), "searches")
    print(d.groupby("search").mean(numeric_only=True).round(4).loc[["A", "W", "V", "G", "Z"]].to_string())
    sys.exit()
exec(open(os.path.join(HERE, "calibrate_abc2_synthetic.py")).read().split("SETTINGS = ")[0])     # make_panel and the imports
rows = []
for dseed in range(int(sys.argv[1]), int(sys.argv[2])):
    panel = make_panel(500 + dseed, 0.0)
    for b, ctx in block_contexts(panel, Task("T", "return", 4), WEEKLY):
        base = FitnessEvaluator(ctx, SearchSpace(ctx.ds.group_cols, ctx.prior), mode="A")
        for name in ("A", "W", "V", "G", "Z"):
            ev = copy.copy(base); ev.cache, ev.n_evals, ev._prior_fit = {}, 0, None
            if name != "A":
                ev.space = SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None, allow_empty=name != "W")
            ev.clean_outer = True
            res = {"A": lambda: abc(ev, ev.space, budget=2000, seed=0), "W": lambda: abc_full(ev, ev.space, budget=2000, seed=0),
                   "V": lambda: abc_vector(ev, ev.space, budget=2000, seed=0, mr=1.0),
                   "G": lambda: abc_graded(GradedEvaluator(ev), budget=2000, seed=0, start="spread", mr=1.0),
                   "Z": lambda: abc_graded(GradedEvaluator(ev), budget=2000, seed=0, start="zero", mr=1.0)}[name]()
            d = res.diag
            ev.clean_outer = False
            whole = (GradedEvaluator(ev).acceptance(res.best) if name in "GZ" else ev.acceptance(res.best))["accepted"]
            rows.append({"search": name, "inner_gain": 1 - d["inner_best"] / d["inner_prior"], "whole_fold_gain": 1 - d["outer_best"] / d["outer_prior"],
                         "clean_gain": 1 - d["clean_best"] / d["clean_prior"], "accepted_clean": res.accepted, "accepted_whole": whole, "clean_rows": d["clean_rows"]})
os.makedirs(OUT, exist_ok=True)
pd.DataFrame(rows).to_csv(os.path.join(OUT, f"abc2_acceptance_synthetic_{sys.argv[1]}.csv"), index=False)
