"""The analysis of SPEC-2026-11-14-wrapup (section 7), written BEFORE the run.

  .venv/bin/python scripts/make_wrapup_report.py --part A    # after stage 7: priors, estimators, the choice of P* (prior_choice.json)
  .venv/bin/python scripts/make_wrapup_report.py             # after stages 8 and 9: everything; writes docs/results/<spec>/report.md

Formula sets: G generic; K1-K5 / S1-S5 the draws of the knowledge-only / statistics-informed
elicitation; Kc / Sc their consensus; R1-R5 random formulas. Readings of a set P: `P|lin`, `P|gbt`,
`P|xgb` (fixed formula, three estimators), `P_nb` (the formula and 19 one- or two-move neighbours,
linear forecasts averaged; G, Kc, Sc only). Derived here: `K@5`, `S@5` (average of the five draws'
linear forecasts) and `Rm` (the mean LOSS of R1-R5).

 1. priors: paired date-block-bootstrap differences per (frequency, task), all development series
    of the frequency pooled on the same dates; spread between draws next to the difference between
    procedures;
 2. the choice of P* (K unless S qualifies), applied mechanically and written to prior_choice.json;
 3. estimators: XGBoost against LightGBM and the linear model;
 4. search: five algorithms on the pooled fitness (Friedman, sign tests against ABC, Holm), and the
    ABC readings of stage 9 against the fixed formula and the no-search colony;
 5. the final method by the rules of the spec; 6. best-of-many test over all new configurations."""
import argparse, glob, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.eval.bootstrap import default_block, paired_block_test
from iba.eval.map import REFERENCE, base_name, configs_of, pointwise
from iba.eval.mcs import spa_test
from iba.protocol import study
from iba.protocol.study import PRIOR_SETS, WRAPUP as SPEC

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
KINDS = ("return", "logrv", "tail_loss", "tail_gain")
GPCA = "gpca|lin"
DRAWS = {"K": [f"K{k}" for k in range(1, 6)], "S": [f"S{k}" for k in range(1, 6)], "R": [f"R{k}" for k in range(1, 6)]}
ALGOS = {"a": "ABC", "ga": "GA", "pso": "PSO", "sa": "SA", "de": "DE"}
ABC = {"tested": "iba_ca|lin", "untested": "iba_ca_r|lin", "ensemble": "iba_ca_b"}


def tasks():
    return study.stage_tasks(7)


def stage_dir(stage, prior, t, spec=None):
    return os.path.join(REPO, "artifacts", spec or SPEC, f"stage{stage}", f"prior_{prior}", t.frequency, t.name, t.target.replace("^", "_"))


def rename(col, prior):
    """Column of a stage-7 cell of formula set ``prior`` -> its name in the report."""
    if col.startswith("iba_e1|"):
        return f"{prior}|{col.split('|', 1)[1]}"
    if col.startswith("iba_rnda"):
        return f"{prior}_nb" + col[len("iba_rnda"):]
    return col


def load(chosen=None, stage=7, sets=None, spec=None, task_list=None):
    """{(frequency, task, kind, h): [(target, predictions of every set side by side)]}. With ``chosen``,
    the stage-9 forecasts made with that formula set are added. ``stage``, ``sets``, ``spec`` and
    ``task_list`` read another run laid out the same way (the confirmation run)."""
    by = {}
    sets = list(sets or PRIOR_SETS)
    for t in (task_list if task_list is not None else tasks()):
        pred = None
        for prior in sets:
            p = pd.read_csv(os.path.join(stage_dir(stage, prior, t, spec), "predictions.csv"), parse_dates=["date"])
            p = p.rename(columns={c: rename(c, prior) for c in p.columns})
            keep = [c for c in p.columns if c.startswith((prior + "|", prior + "_nb", "iba_ca"))]
            if pred is None:                                      # G comes first and brings the benchmarks and references
                pred = p
            else:
                if len(p) != len(pred) or (p["date"].values != pred["date"].values).any() or not np.allclose(p["y_eval"].values, pred["y_eval"].values, equal_nan=True):
                    raise ValueError(f"{t.name} {t.target}: set {prior} does not share dates and labels with G")
                pred = pd.concat([pred, p[keep]], axis=1)
        if chosen:
            p = pd.read_csv(os.path.join(stage_dir(9, chosen, t), "predictions.csv"), parse_dates=["date"])
            if len(p) != len(pred) or (p["date"].values != pred["date"].values).any() or not np.allclose(p["y_eval"].values, pred["y_eval"].values, equal_nan=True):
                raise ValueError(f"{t.name} {t.target}: stage 9 does not share dates and labels with stage 7")
            pred = pd.concat([pred, p[[c for c in p.columns if c.startswith("iba_ca")]]], axis=1)
        for proc in [x for x in ("K", "S") if all(d in sets for d in DRAWS[x])]:      # the five draws' linear forecasts averaged
            pred[f"{proc}@5"] = pred[[f"{d}|lin" for d in DRAWS[proc]]].mean(axis=1)
            if t.kind == "logrv":
                pred[f"{proc}@5::var"] = pred[[f"{d}|lin::var" for d in DRAWS[proc]]].mean(axis=1)
        by.setdefault((t.frequency, t.name, t.kind, t.h), []).append((t.target, pred.copy()))
    for (freq, name, _, _), cells in by.items():                  # "all series pooled on the same dates" must be true
        d0 = cells[0][1]["date"].values
        for target, p in cells[1:]:
            if len(p) != len(d0) or (p["date"].values != d0).any():
                raise ValueError(f"{freq} {name}: {target} does not share the forecast dates of {cells[0][0]}")
    return by


def reproduces_first_study():
    """Largest absolute difference between G's linear fixed-formula forecasts here and the first study's
    (same engine, same formulas: expected 0), over the cells where both exist; None if there is no overlap."""
    worst, n = 0.0, 0
    for t in tasks():
        old = os.path.join(REPO, "artifacts", study.FIRST_SPEC, "stage1", t.frequency, t.name, t.target.replace("^", "_"), "predictions.csv")
        new = os.path.join(stage_dir(7, "G", t), "predictions.csv")
        if os.path.exists(old) and os.path.exists(new):
            a, b = pd.read_csv(old)["iba_e1|lin"].values, pd.read_csv(new)["iba_e1|lin"].values
            worst, n = max(worst, float(np.max(np.abs(a - b)))), n + 1
    return (worst, n) if n else None


def losses(cells, kind):
    """Config (seeds averaged) -> (dates x series) primary loss; plus the per-seed list for the seed spread."""
    preds = [p for _, p in cells]
    common = sorted(set.intersection(*[set(configs_of(p)) for p in preds]))
    per_seed = {}
    for m in common:
        per_seed.setdefault(base_name(m), []).append(np.column_stack([pointwise(p, kind, m) for p in preds]))
    L = {b: np.mean(v, axis=0) for b, v in per_seed.items()}
    if all(f"{d}|lin" in L for d in DRAWS["R"]):
        L["Rm"] = np.mean([L[f"{d}|lin"] for d in DRAWS["R"]], axis=0)
    return L


def holm(p):
    """Holm-adjusted p-values, in the order given."""
    p = np.asarray(p, dtype=float); order = np.argsort(p); out = np.empty(len(p)); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(p) - rank) * p[i])); out[i] = run
    return out


def qualifies(P, cand, inc):
    """The rule of the earlier specs: significantly better in more tasks than worse AND lower mean loss in >= 3 of the 4 types."""
    g = P[(P.a == cand) & (P.b == inc)]
    better, worse = int((g.verdict == "better").sum()), int((g.verdict == "worse").sum())
    by_kind = g.groupby("kind").rel_diff.mean()
    return {"candidate": cand, "incumbent": inc, "tasks": len(g), "tasks better": better, "tasks worse": worse,
            "types with lower mean loss": f"{int((by_kind < 0).sum())}/{len(by_kind)}",
            "mean rel. diff % (types equally weighted)": round(100 * by_kind.mean(), 3),
            "qualifies": bool(better > worse and (by_kind < 0).sum() >= 3)}


def paired(by, pairs, chosen_pairs=(), spread_table=True, skip_missing=False):
    """``skip_missing``: a pair whose configuration does not exist for the task's type is left out (type-specific references)."""
    rows, spread = [], []
    for (freq, task, kind, h), cells in sorted(by.items()):
        L = losses(cells, kind)
        T = next(iter(L.values())).shape[0]; block = default_block(h, T)
        ref = REFERENCE[kind]
        for a, b in list(pairs) + list(chosen_pairs):
            bb = ref if b == "REF" else b
            if a not in L or bb not in L:
                if skip_missing:
                    continue
                raise KeyError(f"{task}: {a} or {bb} missing")
            r = paired_block_test(L[a] - L[bb], block=block, reps=2000, seed=h)
            rows.append({"frequency": freq, "task": task, "kind": kind, "a": a, "b": b, "series": len(cells), "rel_diff": r.mean / L[bb].mean(),
                         "ci_low": r.ci_low / L[bb].mean(), "ci_high": r.ci_high / L[bb].mean(), "p": r.p_value})
        if not spread_table:
            continue
        m = {proc: np.array([L[f"{d}|lin"].mean() for d in DRAWS[proc]]) for proc in DRAWS}
        g = L["G|lin"].mean()
        spread.append({"frequency": freq, "task": task, "kind": kind, **{f"sd {proc} draws": m[proc].std(ddof=1) / g for proc in DRAWS},
                       "mean S - mean K": (m["S"].mean() - m["K"].mean()) / g, "mean K - G": (m["K"].mean() - g) / g,
                       "mean S - G": (m["S"].mean() - g) / g, "mean R - G": (m["R"].mean() - g) / g})
    P = pd.DataFrame(rows)
    P["verdict"] = np.where(P.ci_high < 0, "better", np.where(P.ci_low > 0, "worse", "n.s."))
    return P, pd.DataFrame(spread)


def table_maker(P):
    key = {k: g for k, g in P.groupby(["a", "b", "kind"])}

    def cells(a, b):
        row, tb, tw, tn = {}, 0, 0, 0
        for k in KINDS:
            if (a, b, k) not in key:
                row[k] = ""; continue
            g = key[(a, b, k)]
            nb, nw = int((g.verdict == "better").sum()), int((g.verdict == "worse").sum())
            row[k] = f"{100 * g.rel_diff.mean():+.2f} % ({nb}b {nw}w / {len(g)})"
            tb, tw, tn = tb + nb, tw + nw, tn + len(g)
        row["all tasks"] = f"{tb} better, {tw} worse of {tn}"
        return row

    def table(title, items):
        return [f"### {title}", "", pd.DataFrame([{"a": lab, "against": b, **cells(a, b)} for lab, a, b in items]).to_markdown(index=False), ""]
    return table


def search_table(chosen):
    """Stage 8: one row per (unit, algorithm), seeds averaged. Unit = (frequency, task, pool, block)."""
    rows = []
    base = os.path.join(REPO, "artifacts", SPEC, "stage8", f"prior_{chosen}")
    for path in sorted(glob.glob(os.path.join(base, "*", "*", "*", "block*.json"))):
        res = json.load(open(path))
        meta = res["_meta"]
        kind = re.sub(r"(_q\d+)?_h\d+$", "", meta["task"])
        for arm, by_seed in res.items():
            if arm.startswith("_"):
                continue
            d = [r["diag"] for r in by_seed.values()]
            clean = [1 - x["clean_best"] / x["clean_prior"] for x in d if x.get("clean_rows", 0) > 0 and x["clean_prior"] > 0]
            rows.append({"frequency": meta["frequency"], "task": meta["task"], "kind": kind, "pool": meta["pool"], "block": meta["block"],
                         "members": len(meta["members"]), "algorithm": ALGOS[arm],
                         "inner_gain": float(np.mean([1 - x["inner_best"] / x["inner_prior"] for x in d])),
                         "clean_gain": float(np.mean(clean)) if clean else np.nan,
                         "passes": float(np.mean([r["accepted"] for r in by_seed.values()])),
                         "moved": float(np.mean([x["distance"] > 0 for x in d])), "literals": float(np.mean([x["literals"] for x in d])),
                         "n_evals": float(np.mean([r["n_evals"] for r in by_seed.values()]))})
    return pd.DataFrame(rows)


def search_tests(U):
    """Friedman across the algorithms and sign tests of each against ABC (Holm over the four), on complete units."""
    from scipy.stats import binomtest, friedmanchisquare
    out, pair = [], []
    for metric in ("clean_gain", "passes", "inner_gain"):
        W = U.pivot_table(index=["frequency", "task", "pool", "block"], columns="algorithm", values=metric).dropna()
        stat, p = friedmanchisquare(*[W[a].values for a in ALGOS.values()]) if len(W) > 2 else (np.nan, np.nan)
        out.append({"metric": metric, "units": len(W), **{a: round(float(W[a].mean()), 5) for a in ALGOS.values()}, "friedman_p": p})
        if metric == "clean_gain":
            for a in [x for x in ALGOS.values() if x != "ABC"]:
                d = (W[a] - W["ABC"]).values
                up, down = int((d > 0).sum()), int((d < 0).sum())
                pair.append({"algorithm": a, "units": len(d), "better than ABC": up, "worse than ABC": down, "mean difference": float(d.mean()),
                             "sign_p": binomtest(up, up + down, 0.5).pvalue if up + down else 1.0})
    T = pd.DataFrame(pair)
    if len(T):
        T["holm_p"] = holm(T.sign_p.values)
        T["replaces ABC"] = (T.holm_p < 0.05) & (T["mean difference"] > 0) & (T["better than ABC"] > T["worse than ABC"])
    return pd.DataFrame(out), T


def main(part="all"):
    out = os.path.join(REPO, "docs", "results", SPEC); os.makedirs(out, exist_ok=True)
    sets = [p for p in PRIOR_SETS if p != "G"]
    note = ("Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap "
            "interval excludes zero (b = a better, w = a worse).")
    md = [f"# {SPEC}: elicited priors, XGBoost, five search algorithms, the final method (development series)", "",
          "Formula sets: G generic; K1-K5 knowledge-only draws; S1-S5 statistics-informed draws; Kc, Sc consensus; R1-R5 random. "
          "`|lin`, `|gbt`, `|xgb` = fixed formula with the linear model, LightGBM, XGBoost; `_nb` = the formula and 19 near neighbours averaged "
          "(no search); `K@5`, `S@5` = the five draws' linear forecasts averaged; `Rm` = mean loss of the five random sets.", "", note, ""]

    rep = reproduces_first_study()
    if rep:
        md += [f"Check: the linear fixed-formula forecasts of G made here differ from the first study's by at most {rep[0]:.2e} over {rep[1]} cells.", ""]

    # ---- 1. priors -------------------------------------------------------------------------
    extra = ["K@5", "S@5"]
    pairs = [(f"{p}|lin", "G|lin") for p in sets] + [(x, "G|lin") for x in extra + ["Rm"]]
    pairs += [(f"{p}|lin", b) for p in PRIOR_SETS for b in ("REF", GPCA)] + [(x, b) for x in extra for b in ("REF", GPCA)]
    pairs += [("Sc|lin", "Kc|lin"), ("K@5", "Kc|lin"), ("S@5", "Sc|lin"), ("S@5", "K@5"), ("Kc|lin", "Rm"), ("Sc|lin", "Rm"), ("G|lin", "Rm")]
    pairs += [(f"{p}_nb", f"{p}|lin") for p in ("G", "Kc", "Sc")] + [(f"{p}_nb", b) for p in ("G", "Kc", "Sc") for b in ("G|lin", "REF", GPCA)]
    pairs += [("Kc_nb", "G_nb"), ("Sc_nb", "G_nb"), (GPCA, "REF")]
    est_pairs = lambda P_: [(f"{x}|xgb", f"{x}|gbt") for x in (P_, "G", "raw", "gpca")] + [(f"{x}|{e}", f"{x}|lin") for x in (P_, "G", "raw", "gpca") for e in ("xgb", "gbt")]
    pairs += est_pairs("Kc") + est_pairs("Sc")
    pairs = list(dict.fromkeys(pairs))
    by = load()
    P, SP = paired(by, pairs)
    table = table_maker(P)
    lab = lambda p: {"Kc": "K consensus", "Sc": "S consensus", "K@5": "K, five draws averaged", "S@5": "S, five draws averaged", "Rm": "random (mean loss)"}.get(p, p)
    md += ["## 1. Prior formulas", ""]
    md += table("1a. Every formula set, linear model, against the generic formulas (G)", [(lab(p), f"{p}|lin", "G|lin") for p in sets] + [(lab(x), x, "G|lin") for x in extra + ["Rm"]])
    md += table("1b. Against the type's reference (historical mean / HAR / base rate)", [(lab(p), f"{p}|lin", "REF") for p in PRIOR_SETS] + [(lab(x), x, "REF") for x in extra] + [("group PCA", GPCA, "REF")])
    md += table("1c. Against group PCA", [(lab(p), f"{p}|lin", GPCA) for p in PRIOR_SETS] + [(lab(x), x, GPCA) for x in extra])
    md += table("1d. Procedures against each other, consensus against the draws' average, elicited against random",
                [("S consensus", "Sc|lin", "Kc|lin"), ("K, five draws averaged", "K@5", "Kc|lin"), ("S, five draws averaged", "S@5", "Sc|lin"), ("S, five draws averaged", "S@5", "K@5"),
                 ("K consensus", "Kc|lin", "Rm"), ("S consensus", "Sc|lin", "Rm"), ("generic", "G|lin", "Rm")])
    md += table("1e. The no-search colony of a set", [(f"{p} colony", f"{p}_nb", b) for p in ("G", "Kc", "Sc") for b in (f"{p}|lin", "G|lin", "REF", GPCA)]
                + [("Kc colony", "Kc_nb", "G_nb"), ("Sc colony", "Sc_nb", "G_nb")])
    sp = SP.groupby("kind")[[c for c in SP.columns if c not in ("frequency", "task", "kind")]].mean().reindex([k for k in KINDS if k in set(SP.kind)])
    md += ["### 1f. Spread between draws and difference between procedures", "",
           "Per task, relative to the loss of G: standard deviation across the five draws of a procedure; differences of the procedures' mean losses. Averaged over the tasks of a type, in %.", "",
           (100 * sp).round(3).reset_index().to_markdown(index=False), ""]

    # ---- 2. the choice of P* ---------------------------------------------------------------
    rule = qualifies(P, "Sc|lin", "Kc|lin")
    chosen = "Sc" if rule["qualifies"] else "Kc"
    vsG = qualifies(P, f"{chosen}|lin", "G|lin")
    negative = vsG["tasks worse"] > vsG["tasks better"]
    md += ["## 2. The formula set of the method (spec 7.2)", "",
           "K is the default. Sc replaces Kc only if it is significantly better than Kc in more tasks than worse AND its mean loss is lower in at least 3 of the 4 target types.", "",
           pd.DataFrame([rule, vsG]).to_markdown(index=False), "",
           f"**Chosen: {chosen}** ({'S qualifies against K' if rule['qualifies'] else 'S does not qualify; the default stays'}). "
           + ("NEGATIVE FINDING: the chosen set is significantly worse than the generic formulas in more tasks than better; it stays, as the spec says."
              if negative else "Against the generic formulas the chosen set is not worse in more tasks than better."), ""]
    choice = {"chosen": chosen, "rule_S_against_K": rule, "chosen_against_G": vsG, "negative_finding_against_G": bool(negative)}
    path = os.path.join(out, "prior_choice.json")                 # = iba.protocol.study.prior_choice_path()
    if part == "A":
        with open(path, "w") as fh:
            json.dump(choice, fh, indent=1)
    else:
        with open(path) as fh:
            if json.load(fh)["chosen"] != chosen:
                raise ValueError("prior_choice.json does not agree with the rule re-evaluated here")

    # ---- 3. estimators ---------------------------------------------------------------------
    md += ["## 3. Estimators", ""]
    md += table("3a. XGBoost against LightGBM", [(f"{lab(x)} + XGBoost", f"{x}|xgb", f"{x}|gbt") for x in (chosen, "G", "raw", "gpca")])
    md += table("3b. Trees against the linear model", [(f"{lab(x)} + {e}", f"{x}|{e}", f"{x}|lin") for x in (chosen, "G", "raw", "gpca") for e in ("xgb", "gbt")])

    P.to_csv(os.path.join(out, "paired_tests_priors.csv"), index=False); SP.to_csv(os.path.join(out, "draw_spread.csv"), index=False)
    if part == "A":
        open(os.path.join(out, "report_part_A.md"), "w").write("\n".join(md))
        print("\n".join(md)); print(f"\nCHOSEN {chosen}")
        return chosen

    # ---- 4. search -------------------------------------------------------------------------
    U = search_table(chosen)
    U.to_csv(os.path.join(out, "search_units.csv"), index=False)
    F, S = search_tests(U)
    summ = U.groupby(["algorithm", "kind"])[["inner_gain", "clean_gain", "passes", "moved", "literals"]].mean()
    rows = []
    for a in ALGOS.values():
        row = {"algorithm": a}
        for k in KINDS:
            if (a, k) in summ.index:
                x = summ.loc[(a, k)]
                row[k] = f"{100 * x.inner_gain:+.1f} / {100 * x.clean_gain:+.1f} / {100 * x.passes:.0f} % / {x.literals:.1f}"
        rows.append(row)
    replace = list(S[S["replaces ABC"]].sort_values("mean difference", ascending=False).algorithm) if len(S) else []
    algorithm = replace[0] if replace else "ABC"
    md += [f"## 4. Search with the chosen formula set ({chosen}) as the prior", "",
           "### 4a. Five algorithms on the pooled fitness of the asset-class pools, equal budget", "",
           "Cell: gain of the winner over the prior on the fitness folds / on the clean outer rows / share of winners that pass the test / literals. "
           "Units = (task, pool, block), seeds averaged.", "", pd.DataFrame(rows).to_markdown(index=False), "",
           "Friedman test across the five algorithms (means in the columns):", "", F.round(5).to_markdown(index=False), "",
           "Each algorithm against ABC on the clean-row gain (sign test over units, Holm over the four comparisons). Units share dates and are not independent; the test is the one fixed in the spec.", "",
           S.round(5).to_markdown(index=False) if len(S) else "(no complete units)", "",
           f"**Algorithm of the method: {algorithm}**" + (" (the default; no algorithm is better than ABC at Holm p < 0.05)." if algorithm == "ABC" else " (better than ABC at Holm p < 0.05)."), ""]
    by = load(chosen)
    fixed, colony = f"{chosen}|lin", f"{chosen}_nb"
    abc_pairs = [(ABC["tested"], fixed), (ABC["untested"], fixed), (ABC["ensemble"], fixed), (ABC["ensemble"], colony), (ABC["tested"], "REF"),
                 (ABC["ensemble"], "REF"), (ABC["ensemble"], GPCA), (ABC["tested"], "G|lin"), (ABC["ensemble"], "G|lin")]
    P2, _ = paired(by, abc_pairs)
    table2 = table_maker(P2)
    md += table2("4b. Forecasts from the pooled ABC (class pools, anchored, greedy)",
                 [("tested winner", ABC["tested"], fixed), ("winner without the test", ABC["untested"], fixed), ("colony ensemble", ABC["ensemble"], fixed),
                  ("colony ensemble", ABC["ensemble"], colony), ("tested winner", ABC["tested"], "REF"), ("colony ensemble", ABC["ensemble"], "REF"),
                  ("colony ensemble", ABC["ensemble"], GPCA), ("tested winner", ABC["tested"], "G|lin"), ("colony ensemble", ABC["ensemble"], "G|lin")])
    P2.to_csv(os.path.join(out, "paired_tests_search.csv"), index=False)

    # ---- 5. final method -------------------------------------------------------------------
    r_int, r_acc = qualifies(P2, ABC["tested"], fixed), qualifies(P2, ABC["ensemble"], colony)
    interp = ABC["tested"] if r_int["qualifies"] else fixed
    accur = ABC["ensemble"] if r_acc["qualifies"] else colony
    md += ["## 5. The final method (spec 7.5)", "", pd.DataFrame([r_int, r_acc]).to_markdown(index=False), "",
           f"- **Interpretable reading: `{interp}`** " + ("(the tested ABC winner qualifies against the fixed formula)." if r_int["qualifies"] else "(the fixed formula; the tested ABC winner does not qualify)."),
           f"- **Accuracy reading: `{accur}`** " + ("(the ABC colony qualifies against the no-search colony)." if r_acc["qualifies"] else "(the no-search colony; the ABC colony does not qualify)."),
           f"- Formula set: {chosen}. Search algorithm of the method: {algorithm}.", ""]
    json.dump({"formula_set": chosen, "algorithm": algorithm, "interpretable": interp, "accuracy": accur, "rules": [r_int, r_acc]},
              open(os.path.join(out, "final_method.json"), "w"), indent=1)

    # ---- 6. best-of-many -------------------------------------------------------------------
    new = [f"{p}|{e}" for p in sets for e in ("lin", "gbt", "xgb")] + ["G|xgb", "Kc_nb", "Sc_nb", "K@5", "S@5", "raw|xgb", "pca|xgb", "gpca|xgb", "lasso|xgb"] + list(ABC.values())
    spa = []
    for (freq, task, kind, h), cells in sorted(by.items()):
        L = losses(cells, kind)
        T = L["G|lin"].shape[0]; block = default_block(h, T)
        models = pd.DataFrame({c: L[c].mean(axis=1) for c in new})
        for bench in ("G|lin", GPCA, REFERENCE[kind]):
            s = spa_test(pd.Series(L[bench].mean(axis=1)), models, block=block, reps=2000, seed=h)
            spa.append({"frequency": freq, "task": task, "kind": kind, "benchmark": "REF" if bench == REFERENCE[kind] else bench, "variants": s["k"],
                        "best_variant": models.mean().idxmin(), "p_consistent": s["consistent"]})
    S6 = pd.DataFrame(spa); S6.to_csv(os.path.join(out, "spa_tests.csv"), index=False)
    s1 = S6.assign(sig=S6.p_consistent < 0.05).groupby(["benchmark", "kind"]).agg(tasks=("task", "count"), significant=("sig", "sum"), median_p=("p_consistent", "median")).round(4).reset_index()
    md += [f"## 6. Best-of-many test: does any of the {len(new)} new configurations beat the benchmark? (consistent p-value; tasks with p < 0.05)", "",
           s1.to_markdown(index=False), "", "New configuration with the lowest pooled loss per task:", "",
           S6[S6.benchmark == "REF"].groupby(["kind", "best_variant"]).size().rename("tasks").reset_index().to_markdown(index=False), ""]
    open(os.path.join(out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))
    return chosen


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["A", "all"], default="all")
    main(ap.parse_args().part)
