"""Spec section 8, the tests that complement the map. Written after the map had been seen
(recorded in docs/DEVIATIONS.md); definitions as in the spec, open choices listed there.

1. Per (frequency, task), pooled over ALL development series of that frequency (same dates):
   paired date-block-bootstrap differences in the primary loss for the comparisons behind Q1–Q4,
   and SPA for "does any of the 12 IBA variants beat the benchmark" (type reference; group PCA).
2. Per cell (series): Diebold–Mariano (HAC lag h − 1, HLN) and, for returns, Clark–West against
   the historical mean, as descriptives, with a Holm cross-check inside each target type.
3. Walk-throughs: per target type the map unit where the first headline configuration (iba_e1|lin)
   is most and least favourable against the best benchmark (standardised difference).
4. Registry counts."""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.eval.bootstrap import default_block, paired_block_test
from iba.eval.dm import clark_west, dm_test, holm
from iba.eval.map import HEADLINE, REFERENCE, base_name, configs_of, is_benchmark, pointwise
from iba.eval.mcs import spa_test
from iba.protocol.study import development_tasks, stratum_of

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
spec = sys.argv[1]
out = os.path.join(REPO, "docs", "results", spec)
PAIRS = [("iba_e1|lin", "gpca|lin"), ("iba_a|lin", "iba_e1|lin"), ("iba_d|lin", "iba_a|lin"), ("iba_b", "iba_a|lin"),
         ("iba_b", "iba_e1|lin"), ("iba_b", "gpca|lin"), ("iba_c", "iba_e1|lin"), ("iba_x|lin", "iba_e1|lin"),
         ("iba_e1|lin", "REF"), ("iba_b", "REF"), ("gpca|lin", "REF")]
IBA12 = ["iba_e1|lin", "iba_e1|gbt", "iba_a|lin", "iba_a|gbt", "iba_d|lin", "iba_d|gbt", "iba_x|lin", "iba_x|gbt",
         "iba_xlo|lin", "iba_xlo|gbt", "iba_b", "iba_c"]
DM_PAIRS = [("iba_e1|lin", "REF"), ("iba_b", "REF"), ("gpca|lin", "REF"), ("iba_e1|lin", "gpca|lin"), ("iba_b", "gpca|lin")]
CW_MODELS = ["gpca|lin", "iba_e1|lin", "iba_a.s0|lin", "iba_b.s0", "iba_c.s0"]
strata = stratum_of()
by = {}
for t in development_tasks():
    preds = []
    for d in sorted(glob.glob(os.path.join(REPO, "artifacts", spec, "stage*", t.frequency, t.name, t.target.replace("^", "_")))):
        preds.append(pd.read_csv(os.path.join(d, "predictions.csv"), parse_dates=["date"]))
    pred = preds[0]
    for p in preds[1:]:
        pred = pd.concat([pred, p[[c for c in p.columns if c not in pred.columns]]], axis=1)
    by.setdefault((t.frequency, t.name, t.kind, t.h), []).append((t.target, pred))
rows, spa, dm, cw, per_block = [], [], [], [], {}
for (freq, task, kind, h), cells in sorted(by.items()):
    preds = [p for _, p in cells]
    common = sorted(set.intersection(*[set(configs_of(p)) for p in preds]))
    bases = sorted({base_name(c) for c in common})
    L = {b: np.mean([np.column_stack([pointwise(p, kind, m) for p in preds]) for m in common if base_name(m) == b], axis=0) for b in bases}
    T = L[bases[0]].shape[0]; block = default_block(h, T)
    for a, b in PAIRS:
        bb = REFERENCE[kind] if b == "REF" else b
        r = paired_block_test(L[a] - L[bb], block=block, reps=2000, seed=h)
        rows.append({"frequency": freq, "task": task, "kind": kind, "a": a, "b": b, "series": len(preds),
                     "rel_diff": r.mean / L[bb].mean(), "ci_low": r.ci_low / L[bb].mean(), "ci_high": r.ci_high / L[bb].mean(), "p": r.p_value})
    models = pd.DataFrame({c: L[c].mean(axis=1) for c in IBA12 if c in L})
    for bench in (REFERENCE[kind], "gpca|lin"):
        s = spa_test(pd.Series(L[bench].mean(axis=1)), models, block=block, reps=2000, seed=h)
        spa.append({"frequency": freq, "task": task, "kind": kind, "benchmark": "REF" if bench == REFERENCE[kind] else bench,
                    "variants": s["k"], "best_variant": models.mean().idxmin(), "p_consistent": s["consistent"], "p_lower": s["lower"], "p_upper": s["upper"]})
    for i, (target, p) in enumerate(cells):
        for a, b in DM_PAIRS:
            bb = REFERENCE[kind] if b == "REF" else b
            r = dm_test(L[a][:, i], L[bb][:, i], h)
            dm.append({"frequency": freq, "task": task, "kind": kind, "target": target, "a": a, "b": b, "stat": r["stat"], "p": r["p"]})
        if kind == "return":
            for m in CW_MODELS:
                r = clark_west(p["y"].values, p["bench|mean"].values, p[m].values, h)
                cw.append({"frequency": freq, "task": task, "target": target, "model": base_name(m), "stat": r["stat"], "p": r["p"]})
        blocks = p["block"].values
        for c in list(HEADLINE) + [x for x in bases if is_benchmark(x)]:
            for bl in np.unique(blocks):
                per_block.setdefault((freq, task, strata[target], c, int(bl)), []).append(float(L[c][blocks == bl, i].mean()))
P, S, D, C = pd.DataFrame(rows), pd.DataFrame(spa), pd.DataFrame(dm), pd.DataFrame(cw)
D["p_holm"] = D.groupby(["kind", "a", "b"])["p"].transform(lambda p: holm(p.values))
C["p_holm"] = C.groupby("model")["p"].transform(lambda p: holm(p.values))
P.to_csv(os.path.join(out, "paired_tests.csv"), index=False); S.to_csv(os.path.join(out, "spa_tests.csv"), index=False)
D.to_csv(os.path.join(out, "dm_tests.csv"), index=False); C.to_csv(os.path.join(out, "clark_west.csv"), index=False)
pd.set_option("display.width", 230)
md = [f"# Tests for {spec} (section 8; written after the map was seen, see docs/DEVIATIONS.md)", ""]
P["verdict"] = np.where(P.ci_high < 0, "a better", np.where(P.ci_low > 0, "a worse", "n.s."))
g = P.groupby(["a", "b", "kind"], sort=False).agg(tasks=("task", "count"), a_better=("verdict", lambda v: (v == "a better").sum()), ns=("verdict", lambda v: (v == "n.s.").sum()),
                                                  a_worse=("verdict", lambda v: (v == "a worse").sum()), mean_rel_diff=("rel_diff", "mean")).round(4).reset_index()
md += ["## Paired date-block-bootstrap tests per task (all development series of the frequency pooled; 95 % interval)", "",
       "Relative difference in the primary loss, a minus b (negative = a better). REF = historical mean / HAR / base rate.", "", g.to_markdown(index=False), ""]
s1 = S.assign(sig=S.p_consistent < 0.05).groupby(["benchmark", "kind"]).agg(tasks=("task", "count"), significant=("sig", "sum"), median_p=("p_consistent", "median")).round(4).reset_index()
s2 = S[S.benchmark == "REF"].groupby(["kind", "best_variant"]).size().unstack(fill_value=0).reset_index()
md += ["## SPA: does any of the 12 IBA variants beat the benchmark? (consistent p-value; tasks with p < 0.05)", "", s1.to_markdown(index=False), "",
       "Variant with the lowest pooled loss per task:", "", s2.to_markdown(index=False), ""]
D["fav"] = (D.stat < 0)
d1 = D.groupby(["a", "b", "kind"], sort=False).apply(lambda x: pd.Series({"cells": len(x), "a_better_5pct": int(((x.p < 0.05) & x.fav).sum()), "a_worse_5pct": int(((x.p < 0.05) & ~x.fav).sum()),
                                                                           "a_better_holm": int(((x.p_holm < 0.05) & x.fav).sum()), "a_worse_holm": int(((x.p_holm < 0.05) & ~x.fav).sum())})).reset_index()
md += ["## Diebold–Mariano per series (descriptive; HAC lag h − 1, HLN; Holm inside target type and comparison)", "", d1.to_markdown(index=False), ""]
c1 = C.groupby("model", sort=False).apply(lambda x: pd.Series({"cells": len(x), "p_below_5pct": int((x.p < 0.05).sum()), "holm_below_5pct": int((x.p_holm < 0.05).sum()), "median_p": round(float(x.p.median()), 3)})).reset_index()
md += ["## Clark–West against the historical mean, return cells (descriptive, one-sided; seeded methods: first seed)", "", c1.to_markdown(index=False), ""]

# walk-throughs
M = pd.read_csv(os.path.join(out, "map.csv"))
E = M[M.config == HEADLINE[0]].copy()
E["z"] = E.diff_to_best_benchmark / ((E.ci_high - E.ci_low) / 3.92)
md += ["## Walk-throughs: per target type the unit where iba_e1|lin is most and least favourable against the best benchmark", ""]
for kind in ("return", "logrv", "tail_loss", "tail_gain"):
    e = E[E.kind == kind]
    for label, r in (("most favourable", e.loc[e.z.idxmin()]), ("least favourable", e.loc[e.z.idxmax()])):
        u = M[(M.frequency == r.frequency) & (M.task == r.task) & (M.stratum == r.stratum)].set_index("config")
        best = r.best_benchmark
        md += [f"### {kind}, {label}: {r.frequency} {r.task}, {r.stratum} ({int(r.cells)} series)", "",
               f"Best benchmark {best}, skill against the reference {u.loc[best, 'skill_vs_reference']:+.4f}.", ""]
        t = []
        for c in HEADLINE:
            x = u.loc[c]
            blocks = sorted(k[4] for k in per_block if k[:4] == (r.frequency, r.task, r.stratum, c))
            rel = [np.mean(per_block[(r.frequency, r.task, r.stratum, c, b)]) / np.mean(per_block[(r.frequency, r.task, r.stratum, best, b)]) - 1 for b in blocks]
            t.append({"config": c, "skill": round(x.skill_vs_reference, 4), "rank": f"{int(x.rank_among_benchmarks)}/{int(x.n_benchmarks)}",
                      "rel. diff to best": round(x.diff_to_best_benchmark / u.loc[best, "mean_loss"], 4),
                      "95 % interval": f"[{x.ci_low / u.loc[best, 'mean_loss']:+.4f}, {x.ci_high / u.loc[best, 'mean_loss']:+.4f}]",
                      "per block (rel. loss vs best benchmark)": "  ".join(f"{v:+.3f}" for v in rel),
                      "search accepted": "" if pd.isna(x.get("search_accept_rate")) else f"{x.search_accept_rate:.0%}"})
        md += [pd.DataFrame(t).to_markdown(index=False), ""]

# registry counts
cnt = collections.Counter()
with open(os.path.join(REPO, "registry", "trials.jsonl")) as f:
    for line in f:
        r = json.loads(line)
        if r.get("spec_id") == spec:
            cfg = r["config"]
            cnt[(cfg.get("stage"), r.get("split"), cfg.get("fingerprint"))] += 1
md += ["## Registry", "", f"{sum(cnt.values())} rows for this spec in `registry/trials.jsonl`:", ""]
md += [pd.DataFrame([{"stage": k[0], "split": k[1], "fingerprint": k[2], "rows": v} for k, v in sorted(cnt.items())]).to_markdown(index=False), ""]
open(os.path.join(out, "tests.md"), "w").write("\n".join(md))
print("\n".join(md))
