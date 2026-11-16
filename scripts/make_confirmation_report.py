"""The report of SPEC-2026-11-14-confirmation (sections 4 and 5), written BEFORE the run.

  .venv/bin/python scripts/make_confirmation_report.py     # writes docs/results/SPEC-2026-11-14-confirmation/

Decides every claim of the spec by its written rule, then gives the tables behind the decisions:
every configuration against the reference, group PCA and the interpretable reading; the same by
asset class (descriptive); the financial and classification measures; and, next to each claim,
the same quantity on the weekly development series where a development report has it."""
import importlib.util, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from scipy.stats import binom
from iba.eval.map import REFERENCE
from iba.protocol import study

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


em = _load("make_extra_metrics")
wr = em.wr
SPEC = study.CONFIRM
FIXED, ACC, GPCA, MARGIN = "Kc|lin", "iba_ca_b", "gpca|lin", 0.03
FACTOR = ["raw|lin", "pca|lin", GPCA, "lasso|lin", "kpca|lin", "ae|lin"]
SHOW = [("IBA interpretable (fixed formulas)", FIXED), ("IBA accuracy (ABC colony)", ACC), ("IBA no-search colony", "Kc_nb"), ("IBA tested ABC winner", "iba_ca|lin"),
        ("IBA generic formulas", "G|lin"), ("random formulas (mean loss)", "Rm"), ("raw factors", "raw|lin"), ("PCA", "pca|lin"), ("group PCA", GPCA), ("LASSO", "lasso|lin"),
        ("kernel PCA", "kpca|lin"), ("autoencoder", "ae|lin"), ("IBA K + XGBoost", "Kc|xgb"), ("IBA K + LightGBM", "Kc|gbt"), ("raw + XGBoost", "raw|xgb"),
        ("group PCA + XGBoost", "gpca|xgb"), ("trailing momentum", "bench|tsmom"), ("GARCH", "bench|garch"), ("GJR-GARCH", "bench|gjr"),
        ("volatility-based logit", "bench|logit_vol"), ("GARCH-based probability", "bench|garch_prob")]


def horizon(task):
    return int(re.search(r"_h(\d+)$", task).group(1))


def pairs():
    out = [(c, b) for _, c in SHOW for b in ("REF", GPCA, FIXED) if c != b]
    out += [(FIXED, x) for x in ("Rm", "G|lin", "pca|lin", "kpca|lin", "ae|lin", "bench|logit_vol")] + [(ACC, "Kc_nb"), ("bench|logit_vol", FIXED)]
    out += [(f"{x}|{e}", f"{x}|lin") for x in ("Kc", "raw", "gpca") for e in ("xgb", "gbt")] + [(c, "REF") for c in FACTOR]
    return list(dict.fromkeys(out))


def sel(P, a, b, kind=None, h=None):
    g = P[(P.a == a) & (P.b == b)]
    if kind is not None:
        g = g[g.kind.isin([kind] if isinstance(kind, str) else list(kind))]
    if h is not None:
        g = g[g.task.map(horizon) == h]
    return g


def count(P, a, b, kind=None, h=None):
    g = sel(P, a, b, kind, h)
    return {"n": len(g), "better": int((g.verdict == "better").sum()), "worse": int((g.verdict == "worse").sum()),
            "rel": float(g.rel_diff.mean()) if len(g) else float("nan")}


def cell(c):
    return "not available" if c["n"] == 0 else f"{100 * c['rel']:+.2f} % ({c['better']} better, {c['worse']} worse of {c['n']})"


def one(P, a, b, kind, h):
    g = sel(P, a, b, kind, h)
    if len(g) != 1:
        return None
    r = g.iloc[0]
    return {"rel": r.rel_diff, "lo": r.ci_low, "hi": r.ci_high, "p": r.p, "text": f"{100 * r.rel_diff:+.1f} % ({100 * r.ci_low:+.1f} to {100 * r.ci_high:+.1f}), p = {r.p:.3f}"}


SPECIFIC = ("bench|tsmom", "bench|garch", "bench|gjr", "bench|logit_vol", "bench|garch_prob")      # exist for some target types only


def check_complete(P, tasks):
    """Every pair of configurations that exists for all target types must have a row for every task of the run:
    a configuration dropped from a task (a non-finite forecast for one series) must stop the report, not shrink a claim."""
    names = {t.name for t in tasks}
    bad = []
    for (a, b), g in P.groupby(["a", "b"]):
        if a not in SPECIFIC and b not in SPECIFIC and set(g.task) != names:
            bad.append(f"{a} against {b}: {len(set(g.task))} of {len(names)} tasks")
    missing = [f"{a} against {b}" for a, b in pairs() if a not in SPECIFIC and b not in SPECIFIC and not len(sel(P, a, b))]
    if bad or missing:
        raise ValueError("incomplete comparisons: " + "; ".join(bad + [m + ": no task" for m in missing]))


def claims(P, V, S, T, n_series, tasks=None):
    """Every claim of section 4 decided by its rule on the table of paired tests ``P`` and the extra-measure tables.
    Returns rows (claim, statement, result, decision). With V, S, T = None the three financial claims are left out.
    ``tasks``: the tasks of the run; a claim whose comparison lacks one of its tasks is then NOT decided."""
    rows = []
    want = None if tasks is None else {k: {t.name for t in tasks if t.kind == k} for k in {t.kind for t in tasks}}

    def lacking(g, kinds=None):
        """Tasks of the claim that the comparison ``g`` does not have (empty when ``tasks`` is not given)."""
        if want is None:
            return set()
        need = set().union(*[want.get(k, set()) for k in (kinds or want)])
        return need - set(g.task)

    def add(cid, text, result, ok, gaps=()):
        if gaps:
            result, ok = f"{result}; MISSING TASKS: {', '.join(sorted(gaps))}", "NOT RUN" if cid.startswith("P") else "not decided"
        rows.append({"claim": cid, "statement": text, "result": result, "decision": ok})
    # ---- primary
    p1, p2 = one(P, FIXED, "REF", "logrv", 1), one(P, FIXED, "REF", "logrv", 4)
    have = [x for x in (p1, p2) if x is not None]
    adj = dict(zip([id(x) for x in have], wr.holm([x["p"] for x in have])))
    for cid, x, w in (("P1", p1, "1 week"), ("P2", p2, "4 weeks")):
        if x is None:
            add(cid, f"Volatility at {w}: interpretable reading better than HAR", "task not run", "NOT RUN"); continue
        ok = adj[id(x)] < 0.05 and x["rel"] < 0
        add(cid, f"Volatility at {w}: interpretable reading better than HAR", f"{x['text']}; Holm-adjusted p = {adj[id(x)]:.3f}", "CONFIRMED" if ok else "NOT CONFIRMED")
    g = sel(P, FIXED, GPCA)
    inside, sig_worse = int((g.ci_high < MARGIN).sum()), int((g.verdict == "worse").sum())
    need = int(np.ceil(0.9 * len(g)))
    add("P3", f"Parity with group PCA: upper end of the interval below +{100 * MARGIN:.0f} % in at least {need} of {len(g)} tasks, group PCA significantly better in none",
        f"below the margin in {inside} of {len(g)}; group PCA significantly better in {sig_worse}; mean difference {100 * g.rel_diff.mean():+.2f} %; largest upper end {100 * g.ci_high.max():+.2f} %",
        "CONFIRMED" if len(g) and inside >= need and sig_worse == 0 else "NOT CONFIRMED", lacking(g))
    # ---- secondary
    hd = lambda ok: "holds" if ok else "does not hold"
    s1 = one(P, FIXED, "REF", "logrv", 13)
    add("S1", "Volatility at 13 weeks against HAR (no direction claimed)", s1["text"] if s1 else "task not run", "reported")
    c = count(P, ACC, FIXED)
    add("S2", "Accuracy reading better than the interpretable one in more tasks than worse", cell(c), hd(c["better"] > c["worse"]), lacking(sel(P, ACC, FIXED)))
    res, ok, gaps = [], True, set()
    for b, lab in (("pca|lin", "PCA"), ("kpca|lin", "kernel PCA"), ("ae|lin", "autoencoder")):
        c = count(P, FIXED, b, "logrv"); res.append(f"{lab}: {cell(c)}"); ok &= c["better"] >= 2; gaps |= lacking(sel(P, FIXED, b, "logrv"), ["logrv"])
    add("S3", "On volatility the interpretable reading is better than PCA, kernel PCA and the autoencoder in at least 2 of 3 horizons each", "; ".join(res), hd(ok), gaps)
    cv, co = count(P, FIXED, "Rm", "logrv"), count(P, FIXED, "Rm", ("return", "tail_loss", "tail_gain"))
    add("S4", "Against random formulas: better on volatility in at least 2 of 3 horizons; at most 1 significant difference in the return and tail tasks",
        f"volatility: {cell(cv)}; returns and tails: {cell(co)}", hd(cv["better"] >= 2 and co["better"] + co["worse"] <= 1), lacking(sel(P, FIXED, "Rm")))
    wins = [(lab, t) for lab, c_ in [(FIXED, FIXED), (ACC, ACC)] + [(x, x) for x in FACTOR] for t in sel(P, c_, "REF", ("return", "tail_loss")).query("verdict == 'better'").task]
    add("S5", "No factor method is significantly better than the reference in any return or large-loss task",
        "none" if not wins else "; ".join(f"{a} in {t}" for a, t in wins), hd(not wins),
        set().union(*[lacking(sel(P, c_, "REF", ("return", "tail_loss")), ["return", "tail_loss"]) for c_ in [FIXED, ACC] + FACTOR]))
    c = count(P, FIXED, "G|lin")
    add("S6", "Elicited and generic formulas at parity: at most 1 task with a significant difference", cell(c), hd(c["better"] + c["worse"] <= 1), lacking(sel(P, FIXED, "G|lin")))
    res, ok, gaps = [], True, set()
    for x in ("Kc", "raw", "gpca"):
        for e in ("xgb", "gbt"):
            c = count(P, f"{x}|{e}", f"{x}|lin"); res.append(f"{x}+{e}: {c['better']} better, {c['worse']} worse of {c['n']}"); ok &= c["worse"] > c["better"]
            gaps |= lacking(sel(P, f"{x}|{e}", f"{x}|lin"))
    add("S7", "Trees do not help: XGBoost and LightGBM significantly worse than the linear model in more tasks than better (IBA, raw factors, group PCA)", "; ".join(res), hd(ok), gaps)
    g = sel(P, "bench|logit_vol", FIXED, "tail_gain")
    add("S8", "Large gains: the volatility-based logit has the lower loss than the interpretable reading in every large-gain task",
        "; ".join(f"{t}: {100 * r:+.1f} %" for t, r in zip(g.task, g.rel_diff)) or "not available", hd(len(g) > 0 and (g.rel_diff < 0).all()), lacking(g, ["tail_gain"]))
    if V is not None:
        m = "IBA, K formulas (fixed)"
        v = V[(V.method == m) & (V.h == 1) & (V.alpha == 0.01)]
        add("S9", "One-week 1 % value at risk: lower quantile loss than HAR", "not available" if v.empty else f"{100 * v.tick_rel_to_har.iloc[0]:+.1f} % ({v.tick_verdict.iloc[0]})",
            hd(len(v) and v.tick_verdict.iloc[0] == "better"))
        s = S[(S.method == m) & (S.frequency == "weekly") & (S.h == 1)]
        need = int(binom.isf(0.05, n_series, 0.5)) + 1                  # smallest count with a one-sided sign-test p below 5 %
        if s.empty:
            add("S10", "Long/flat rule at one week", "not available", hd(False))
        else:
            r = s.iloc[0]; bh = S[(S.method == "buy-and-hold") & (S.frequency == "weekly") & (S.h == 1)].iloc[0]
            add("S10", f"Long/flat rule at one week: higher Sharpe ratio than buy-and-hold in at least {need} of {n_series} series, and a smaller maximum drawdown in at least {need}",
                f"Sharpe {r.sharpe:.2f} against {bh.sharpe:.2f}, higher in {int(r.series_sharpe_above_bh)}; drawdown {100 * r.max_drawdown:.1f} % against {100 * bh.max_drawdown:.1f} %, "
                f"smaller in {int(r.series_drawdown_below_bh)}; after 10 bp per switch Sharpe {r.sharpe_10bp:.2f} against {bh.sharpe_10bp:.2f}, higher in {int(r.series_sharpe_10bp_above_bh)}",
                hd(r.series_sharpe_above_bh >= need and r.series_drawdown_below_bh >= need))
        mcc = {}
        for lab in (m, "volatility-based logit"):
            x = T[(T.kind == "tail_gain") & (T.method == lab)]
            mcc[lab] = em.F.mcc(*(x[k].sum() for k in ("tp", "fp", "fn", "tn"))) if len(x) else None      # the helper of the tables
        if None in mcc.values():
            add("S11", "Large gains as a classifier: Matthews correlation below that of the volatility-based logit", "not available", "not decided")
        else:
            add("S11", "Large gains as a classifier: Matthews correlation below that of the volatility-based logit",
                f"{mcc[m]:.3f} against {mcc['volatility-based logit']:.3f}", hd(mcc[m] < mcc["volatility-based logit"]))
    return pd.DataFrame(rows)


def development_tests():
    """Paired tests of the development reports, weekly tasks only, for the side-by-side column."""
    files = [("docs", "results", study.WRAPUP, "paired_tests_priors.csv"), ("docs", "results", study.WRAPUP, "paired_tests_search.csv"),
             ("docs", "results", study.BENCH2, "paired_tests.csv")]
    parts = [pd.read_csv(os.path.join(wr.REPO, *f)) for f in files if os.path.exists(os.path.join(wr.REPO, *f))]
    if not parts:
        return None
    D = pd.concat(parts, ignore_index=True)
    D = D[D.frequency == "weekly"].drop_duplicates(["task", "a", "b"])
    D["verdict"] = np.where(D.ci_high < 0, "better", np.where(D.ci_low > 0, "worse", "n.s."))
    return D


def by_class(by):
    """Loss relative to the reference per asset class and target type (descriptive: few series per class)."""
    strata, rows = study.stratum_of(), []
    for (freq, task, kind, h), cells in sorted(by.items()):
        L = wr.losses(cells, kind)
        ref = L[REFERENCE[kind]].mean(axis=0)
        for lab, c in SHOW[:2] + [("group PCA", GPCA)]:
            if c in L:
                for (target, _), a, r in zip(cells, L[c].mean(axis=0), ref):
                    rows.append({"class": strata.get(target, "?"), "kind": kind, "task": task, "method": lab, "target": target, "loss": a, "ref": r})
    D = pd.DataFrame(rows)
    # per task the class's pooled loss against the reference's, then the mean over the tasks of the type: every horizon
    # counts the same, as in the other tables (summing losses over horizons would let the longest one dominate)
    per_task = D.groupby(["class", "kind", "method", "task"]).apply(lambda d: d.loss.sum() / d.ref.sum() - 1).rename("rel").reset_index()
    g = per_task.groupby(["class", "kind", "method"]).rel.mean().reset_index()
    t = g.pivot_table(index=["class", "method"], columns="kind", values="rel").mul(100).round(1).reset_index()
    n = D.groupby("class").target.nunique().to_dict()
    t.insert(1, "series", t["class"].map(n))
    return t


def panel_returns():
    """Weekly returns of the confirmation series, for the drawdown state of the stress table (read under the frozen spec)."""
    from iba.data.panel import load_panel
    return {"weekly": load_panel("weekly", confirmation_run=SPEC).returns}


def main():
    out = os.path.join(wr.REPO, "docs", "results", SPEC); os.makedirs(out, exist_ok=True)
    tasks = study.confirmation_tasks()
    n_series = len({t.target for t in tasks})
    by = wr.load(stage=11, sets=study.STAGES[11]["priors"], spec=SPEC, task_list=tasks)
    P, _ = wr.paired(by, pairs(), spread_table=False, skip_missing=True)
    P.to_csv(os.path.join(out, "paired_tests.csv"), index=False)
    check_complete(P, tasks)
    head = (f"CONFIRMATION series ({n_series}), measures declared in the spec before the run (`docs/protocol/EXTRA_METRICS.md`). All factor methods with the linear model. "
            "The averaged reading is the ABC colony of the development run, applied unchanged.")
    V, S, T = em.tables(by, em.methods("Kc", ACC), os.path.join(out, "extra"), "Financial and classification measures (confirmation series)", head, panel_returns())
    C = claims(P, V, S, T, n_series, tasks)
    D = development_tests()
    if D is not None:
        dev = claims(D, None, None, None, n_series).set_index("claim").result.to_dict()
        C["development (weekly series; decisions were not made there)"] = C.claim.map(lambda c: dev.get(c, ""))
    C.to_csv(os.path.join(out, "claims.csv"), index=False)
    table = wr.table_maker(P)
    dates = next(iter(by.values()))[0][1]["date"]
    md = [f"# {SPEC}: the frozen final method on the confirmation series", "",
          f"{n_series} series, {len(tasks)} cells, test period {dates.min().date()} to {dates.max().date()}. One run. Decisions below are made by the rules written in the spec before any "
          "of these numbers existed. Relative differences in the primary loss, a minus b (negative = a better), all series pooled on the same dates, 95 % date-block bootstrap.", "",
          "## 1. The claims", "", "### Primary", "", C[C.claim.str.startswith("P")].to_markdown(index=False), "",
          "### Secondary", "", C[C.claim.str.startswith("S")].to_markdown(index=False), "",
          "## 2. Every configuration", "", "Cell: mean relative difference; tasks where the interval excludes zero (b = a better, w = a worse).", ""]
    present = [(lab, c) for lab, c in SHOW if len(P[P.a == c])]
    md += table("2a. Against the type's reference (historical mean / HAR / base rate)", [(lab, c, "REF") for lab, c in present])
    md += table("2b. Against group PCA", [(lab, c, GPCA) for lab, c in present if c != GPCA and len(sel(P, c, GPCA))])
    md += table("2c. Against the interpretable reading", [(lab, c, FIXED) for lab, c in present if c != FIXED and len(sel(P, c, FIXED))])
    md += ["## 3. By asset class (descriptive; loss relative to the reference, %, per target type)", "", by_class(by).to_markdown(index=False), "",
           "## 4. Financial and classification measures", "", "In `extra/extra_metrics.md`, with the tables behind claims S9 to S11.", ""]
    open(os.path.join(out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))
    return C


if __name__ == "__main__":
    main()
