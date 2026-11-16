"""The analysis of SPEC-2026-11-14-abc-v2 (section 6), written BEFORE the run.

  .venv/bin/python scripts/make_abc2_report.py            # writes docs/results/SPEC-2026-11-14-abc-v2/

For every cell of the spec the forecasts of the first study (stage 1 and 2 of
SPEC-2026-11-13-multitarget-study: E1, A, B, group PCA, the type's reference) are joined with the
forecasts of this spec's stage 4 (same dates, same labels). Then:
 1. search diagnostics per search (from the block metadata): inner and outer gain over the prior,
    acceptance rate, size of the winner, colony diversity; unit = (cell, block), seeds averaged;
 2. per (frequency, task), all development series of the frequency pooled on the same dates: paired
    date-block-bootstrap differences in the primary loss for the declared pairs;
 3. SPA: does any of the 12 new configurations beat E1 / B / group PCA / the reference;
 4. unit wins (task x asset class) and seed spread;
 5. the decision rule of the spec, evaluated mechanically."""
import glob, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.eval.bootstrap import default_block, paired_block_test
from iba.eval.map import REFERENCE, base_name, configs_of, pointwise
from iba.eval.mcs import spa_test
from iba.protocol.study import FIRST_SPEC, abc2_tasks, stratum_of

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SPEC = "SPEC-2026-11-14-abc-v2"
SEARCHES = {"w": "W  discrete moves, whole space, spread start", "v": "V  vector moves, crisp formulas",
            "g": "G  vector moves, graded formulas, spread start", "z": "Z  graded formulas, zero start"}
GATED = [f"iba_{k}|lin" for k in SEARCHES]
A_CLEAN = "iba_ac|lin"          # the first study's ABC with the acceptance test on clean rows
RAW = [f"iba_{k}r|lin" for k in SEARCHES]
ENS = [f"iba_{k}b" for k in SEARCHES]
NEW12 = GATED + RAW + ENS
PAIRS = ([(c, "iba_e1|lin") for c in ["iba_a|lin", A_CLEAN] + GATED] + [(c, "iba_e1|lin") for c in ["iba_ar|lin"] + RAW]
         + [("iba_b", "iba_e1|lin")] + [(c, "iba_b") for c in ENS] + [(c, "iba_e1|lin") for c in ENS] + [(c, "gpca|lin") for c in ENS]
         + [(c, "REF") for c in ["iba_e1|lin", "iba_b", "gpca|lin"] + GATED + ENS])
KINDS = ("return", "logrv", "tail_loss", "tail_gain")


def cell_dirs(t):
    name = t.target.replace("^", "_")
    return ([os.path.join(REPO, "artifacts", FIRST_SPEC, f"stage{s}", t.frequency, t.name, name) for s in (1, 2)]
            + [os.path.join(REPO, "artifacts", SPEC, "stage4", t.frequency, t.name, name)])


def load():
    by, diag = {}, []
    for t in abc2_tasks():
        pred = None
        for d in cell_dirs(t):
            p = pd.read_csv(os.path.join(d, "predictions.csv"), parse_dates=["date"])
            if pred is None:
                pred = p
            else:
                if len(p) != len(pred) or (p["date"].values != pred["date"].values).any() or not np.allclose(p["y_eval"].values, pred["y_eval"].values, equal_nan=True):
                    raise ValueError(f"{t.name} {t.target}: stages do not share dates and labels")
                pred = pd.concat([pred, p[[c for c in p.columns if c not in pred.columns]]], axis=1)
            meta = json.load(open(os.path.join(d, "meta.json")))
            for b in meta["blocks"]:
                for name, info in b["methods"].items():
                    m = re.match(r"^iba_(ac|w|v|g|z)\.s(\d+)$", name)
                    if m and isinstance(info, dict) and "inner_best" in info:
                        diag.append({"frequency": t.frequency, "task": t.name, "kind": t.kind, "target": t.target, "block": b["block"],
                                     "search": m.group(1), "seed": int(m.group(2)), "accepted": float(info["accepted"]), "n_evals": info["n_evals"],
                                     "accepted_whole_fold": float(info.get("accepted_whole_fold", np.nan)), "clean_rows": info["clean_rows"],
                                     "clean_gain": 1 - info["clean_best"] / info["clean_prior"] if info["clean_rows"] > 0 else np.nan,
                                     "inner_gain": 1 - info["inner_best"] / info["inner_prior"], "outer_gain": 1 - info["outer_best"] / info["outer_prior"],
                                     "literals": info["literals"], "groups": info.get("groups", np.nan), "empty": info.get("empty", np.nan),
                                     "colony_distinct": info.get("colony_distinct", np.nan), "colony_literals": info.get("colony_literals", np.nan)})
        by.setdefault((t.frequency, t.name, t.kind, t.h), []).append((t.target, pred))
    return by, pd.DataFrame(diag)


def main():
    out = os.path.join(REPO, "docs", "results", SPEC); os.makedirs(out, exist_ok=True)
    by, diag = load()
    strata = stratum_of()
    md = [f"# {SPEC}: ABC over the whole space, development series", "",
          "Configurations: `iba_<s>|lin` the winner of search s if it passed the acceptance test, else the prior; `iba_<s>r|lin` the winner "
          "without the test; `iba_<s>b` the final colony as an ensemble. Searches: " + "; ".join(SEARCHES.values()) +
          ". A, B, E1, group PCA and the references are the first study's forecasts for the same cells.", ""]

    # 1. search diagnostics
    unit = diag.groupby(["kind", "frequency", "task", "target", "block", "search"]).mean(numeric_only=True).reset_index()
    d1 = unit.groupby(["kind", "search"])[["inner_gain", "outer_gain", "clean_gain", "accepted", "accepted_whole_fold", "literals", "groups", "empty",
                                           "colony_distinct", "colony_literals", "clean_rows", "n_evals"]].mean()
    d1 = d1.reindex([(k, s) for k in KINDS for s in ("ac", "w", "v", "g", "z")]).round(4).reset_index()
    diag.to_csv(os.path.join(out, "search_diagnostics.csv"), index=False)
    md += ["## 1. What the searches do (units = cell x block, seeds averaged; gains relative to the prior)", "",
           "inner_gain: fitness folds. outer_gain: the WHOLE outer fold (as in the first study; most of its rows are also validation rows of the "
           "last fitness fold). clean_gain: the outer rows the search has not used, the basis of this spec's acceptance test. All for the winner "
           "before the test. ac = the first study's ABC (same search); accepted_whole_fold = its acceptance rate under the first study's test.", "",
           d1.to_markdown(index=False), ""]

    # 2. paired tests per task, 3. SPA, 4. unit wins and seed spread
    rows, spa, units, sd = [], [], [], []
    for (freq, task, kind, h), cells in sorted(by.items()):
        preds = [p for _, p in cells]
        common = sorted(set.intersection(*[set(configs_of(p)) for p in preds]))
        bases = sorted({base_name(c) for c in common})
        per_seed = {b: [np.column_stack([pointwise(p, kind, m) for p in preds]) for m in common if base_name(m) == b] for b in bases}
        L = {b: np.mean(v, axis=0) for b, v in per_seed.items()}
        T = L[bases[0]].shape[0]; block = default_block(h, T)
        ref = REFERENCE[kind]
        for a, b in PAIRS:
            bb = ref if b == "REF" else b
            r = paired_block_test(L[a] - L[bb], block=block, reps=2000, seed=h)
            rows.append({"frequency": freq, "task": task, "kind": kind, "a": a, "b": b, "series": len(preds), "rel_diff": r.mean / L[bb].mean(),
                         "ci_low": r.ci_low / L[bb].mean(), "ci_high": r.ci_high / L[bb].mean(), "p": r.p_value})
        models = pd.DataFrame({c: L[c].mean(axis=1) for c in NEW12})
        for bench in ("iba_e1|lin", "iba_b", "gpca|lin", ref):
            s = spa_test(pd.Series(L[bench].mean(axis=1)), models, block=block, reps=2000, seed=h)
            spa.append({"frequency": freq, "task": task, "kind": kind, "benchmark": "REF" if bench == ref else bench, "variants": s["k"],
                        "best_variant": models.mean().idxmin(), "p_consistent": s["consistent"]})
        for c in NEW12 + ["iba_a|lin", A_CLEAN, "iba_b"]:
            if len(per_seed[c]) > 1:
                sd.append({"kind": kind, "config": c, "rel_seed_sd": float(np.std([x.mean() for x in per_seed[c]]) / L[c].mean())})
        targets = [t for t, _ in cells]
        for st in sorted({strata[t] for t in targets}):
            idx = [i for i, t in enumerate(targets) if strata[t] == st]
            units.append({"frequency": freq, "task": task, "kind": kind, "stratum": st,
                          **{c: float(L[c][:, idx].mean()) for c in NEW12 + ["iba_e1|lin", "iba_a|lin", "iba_ar|lin", A_CLEAN, "iba_b", "gpca|lin", ref]},
                          "REF": float(L[ref][:, idx].mean())})
    P, S, U, SD = pd.DataFrame(rows), pd.DataFrame(spa), pd.DataFrame(units), pd.DataFrame(sd)
    P.to_csv(os.path.join(out, "paired_tests.csv"), index=False); S.to_csv(os.path.join(out, "spa_tests.csv"), index=False)
    U.to_csv(os.path.join(out, "unit_losses.csv"), index=False)
    P["verdict"] = np.where(P.ci_high < 0, "better", np.where(P.ci_low > 0, "worse", "n.s."))

    def table(pairs, title, note):
        g = P[P.apply(lambda r: (r.a, r.b) in pairs, axis=1)]
        t = g.groupby(["a", "b", "kind"], sort=False).agg(tasks=("task", "count"), better=("verdict", lambda v: (v == "better").sum()),
                                                          ns=("verdict", lambda v: (v == "n.s.").sum()), worse=("verdict", lambda v: (v == "worse").sum()),
                                                          mean_rel_diff=("rel_diff", "mean")).reset_index()
        lines = []
        for (a, b) in pairs:
            row = {"a": a, "b": b}
            for k in KINDS:
                x = t[(t.a == a) & (t.b == b) & (t.kind == k)]
                row[k] = "" if x.empty else f"{100 * x.mean_rel_diff.iloc[0]:+.2f} % ({int(x.better.iloc[0])}b {int(x.worse.iloc[0])}w / {int(x.tasks.iloc[0])})"
            x = t[(t.a == a) & (t.b == b)]
            row["all tasks"] = f"{int(x.better.sum())} better, {int(x.worse.sum())} worse of {int(x.tasks.sum())}"
            lines.append(row)
        return [f"## {title}", "", note, "", pd.DataFrame(lines).to_markdown(index=False), ""]

    cell = "Cell: mean relative difference in the primary loss, a minus b (negative = a better), and the tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse)."
    md += table([(c, "iba_e1|lin") for c in ["iba_a|lin", A_CLEAN] + GATED], "2a. Winner with the acceptance test against the fixed prior formulas (E1); iba_a = first study's test, all others = clean rows", cell)
    md += table([(c, "iba_e1|lin") for c in ["iba_ar|lin"] + RAW], "2b. Winner WITHOUT the acceptance test against E1 (diagnostic: what the search alone does)", cell)
    md += table([("iba_b", "iba_e1|lin")] + [(c, "iba_e1|lin") for c in ENS], "2c. Colony ensemble against E1", cell)
    md += table([(c, "iba_b") for c in ENS], "2d. Colony ensemble against the first study's ensemble (B)", cell)
    md += table([(c, "gpca|lin") for c in ENS], "2e. Colony ensemble against group PCA", cell)
    md += table([(c, "REF") for c in ["iba_e1|lin", "iba_b", "gpca|lin"] + GATED + ENS], "2f. Against the type's reference (historical mean / HAR / base rate)", cell)

    s1 = S.assign(sig=S.p_consistent < 0.05).groupby(["benchmark", "kind"]).agg(tasks=("task", "count"), significant=("sig", "sum"), median_p=("p_consistent", "median")).round(4).reset_index()
    s2 = S[S.benchmark == "REF"].groupby(["kind", "best_variant"]).size().unstack(fill_value=0).reset_index()
    md += ["## 3. SPA: does any of the 12 new configurations beat the benchmark? (consistent p-value; tasks with p < 0.05)", "", s1.to_markdown(index=False), "",
           "New configuration with the lowest pooled loss per task:", "", s2.to_markdown(index=False), ""]

    wins = []
    for a, b in [(c, "iba_e1|lin") for c in [A_CLEAN] + GATED] + [(c, "iba_b") for c in ENS] + [(c, "gpca|lin") for c in ENS]:
        row = {"a": a, "b": b}
        for k in KINDS:
            u = U[U.kind == k]
            row[k] = f"{int((u[a] < u[b]).sum())}-{int((u[a] > u[b]).sum())}"
        row["all"] = f"{int((U[a] < U[b]).sum())}-{int((U[a] > U[b]).sum())}"
        wins.append(row)
    md += ["## 4. Units (task x asset class) where a has the lower loss - where b has", "", pd.DataFrame(wins).to_markdown(index=False), "",
           "Seed spread (standard deviation over the three seeds of the pooled loss, relative to the loss):", "",
           SD.pivot_table(index="config", columns="kind", values="rel_seed_sd").round(4).reset_index().to_markdown(index=False), ""]

    # 5. decision rule
    dec = []
    for cand, inc in [(c, "iba_e1|lin") for c in [A_CLEAN] + GATED] + [(c, "iba_b") for c in ENS]:
        g = P[(P.a == cand) & (P.b == inc)]
        better, worse = int((g.verdict == "better").sum()), int((g.verdict == "worse").sum())
        neg = int((g.groupby("kind").rel_diff.mean() < 0).sum())
        dec.append({"candidate": cand, "incumbent": inc, "tasks better": better, "tasks worse": worse, "types with lower mean loss": f"{neg}/4",
                    "mean rel. diff (types equally weighted)": round(100 * g.groupby("kind").rel_diff.mean().mean(), 3),
                    "qualifies": bool(better > worse and neg >= 3)})
    D = pd.DataFrame(dec)
    md += ["## 5. Decision rule (spec section 6)", "",
           "A candidate qualifies if it is significantly better than its incumbent in more tasks than it is significantly worse AND its mean loss is lower in at least 3 of the 4 target types.", "",
           D.to_markdown(index=False), ""]
    q = D[D.qualifies]
    md += ["Qualifying: " + (", ".join(q.candidate) if len(q) else "none; the first study's implementation stays.")
           + (f" Lowest mean relative loss among them: {q.sort_values('mean rel. diff (types equally weighted)').candidate.iloc[0]}." if len(q) else ""), ""]
    open(os.path.join(out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
