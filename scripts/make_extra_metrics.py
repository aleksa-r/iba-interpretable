"""Financial and classification measures of the stored forecasts (docs/protocol/EXTRA_METRICS.md).

  .venv/bin/python scripts/make_extra_metrics.py     # writes docs/results/extra-metrics-development/

DESCRIPTIVE on the development series: reads the forecasts of SPEC-2026-11-14-wrapup (stage 7; stage 9
when present), of SPEC-2026-11-14-benchmarks-kpca-ae (when present) and the GARCH forecasts of the
first study; refits nothing; decides nothing."""
import importlib.util, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.eval import finmetrics as F
from iba.eval.bootstrap import default_block, paired_block_test
from iba.eval.map import base_name
from iba.protocol import study

_spec = importlib.util.spec_from_file_location("wrapup_report", os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_wrapup_report.py"))
wr = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(wr)
OUT = "extra-metrics-development"
GARCH = ("bench|garch", "bench|gjr", "bench|garch_prob")
PPY = {"weekly": 52, "monthly": 12}


def methods(P, accuracy=None):
    """``accuracy``: the accuracy reading of the final method (the no-search colony until the full report names it)."""
    name = "K formulas" if P == "Kc" else P
    return [(f"IBA, {name} (fixed)", f"{P}|lin"), (f"IBA, {name} (averaged)", accuracy or f"{P}_nb"),
            ("IBA, generic formulas", "G|lin"), ("group PCA", "gpca|lin"), ("PCA", "pca|lin"), ("kernel PCA", "kpca|lin"), ("autoencoder", "ae|lin"),
            ("LASSO", "lasso|lin"), ("raw factors", "raw|lin")]


REFS = {"return": [("historical mean", "bench|mean"), ("trailing momentum", "bench|tsmom")],
        "logrv": [("HAR", "bench|har"), ("GARCH", "bench|garch"), ("GJR-GARCH", "bench|gjr")],
        "tail_loss": [("base rate", "bench|base"), ("volatility-based logit", "bench|logit_vol"), ("GARCH-based probability", "bench|garch_prob")],
        "tail_gain": [("base rate", "bench|base"), ("volatility-based logit", "bench|logit_vol"), ("GARCH-based probability", "bench|garch_prob")]}


def add_columns(by, path_of, pick):
    """Columns of another run's cells (same dates and labels required); cells without a file are left as they are."""
    index = {(t.frequency, t.name, t.target): t for t in wr.tasks()}
    n = 0
    for (freq, name, kind, h), cells in by.items():
        for i, (target, pred) in enumerate(cells):
            p = path_of(index[(freq, name, target)])
            if not os.path.exists(p):
                continue
            q = pd.read_csv(p, parse_dates=["date"])
            if len(q) != len(pred) or (q["date"].values != pred["date"].values).any():
                raise ValueError(f"{name} {target}: {p} does not share the dates")
            cols = [c for c in q.columns if pick(c) and c not in pred.columns]
            cells[i] = (target, pd.concat([pred, q[cols]], axis=1)); n += 1
    return n


def seed_cols(pred, base):
    return [c for c in pred.columns if base_name(c) == base and "::" not in c]


def avg(dicts):
    return {k: float(np.mean([d[k] for d in dicts])) for k in dicts[0]}


def var_section(by, M):
    rows = []
    for (freq, name, kind, h), cells in sorted(by.items()):
        if kind != "logrv":
            continue
        ret = dict(by[(freq, f"return_h{h}", "return", h)])
        names = [(lab, b) for lab, b in M + REFS["logrv"] if all(seed_cols(p, b) for _, p in cells)]
        for alpha in (0.05, 0.01):
            L, FZ, stats = {}, {}, {}
            for lab, b in names:
                tl, fz, viol, kup, chr_, sr_num, sr_den = [], [], [], [], [], 0.0, 0.0
                for target, pred in cells:
                    rp = ret[target]
                    if (rp["date"].values != pred["date"].values).any():
                        raise ValueError(f"{target} h={h}: return and volatility cells do not share their dates")
                    r = np.log1p(rp["y"].values)
                    t1, f1, v1 = [], [], []
                    for c in seed_cols(pred, b):
                        q, e = F.var_es_normal(pred[c + "::var"].values, alpha)
                        t1.append(F.tick_loss(r, q, alpha)); f1.append(F.fz0_loss(r, q, e, alpha)); v1.append(r < q)
                        sr_num += r[r < q].sum(); sr_den += e[r < q].sum()
                        if h == 1:
                            kup.append(F.kupiec(r < q, alpha)["p"] < 0.05); chr_.append(F.christoffersen(r < q)["p"] < 0.05)
                    tl.append(np.mean(t1, axis=0)); fz.append(np.mean(f1, axis=0)); viol.append(np.mean(v1))
                L[lab], FZ[lab] = np.column_stack(tl), np.column_stack(fz)
                stats[lab] = {"violation_rate": float(np.mean(viol)), "shortfall_ratio": sr_num / sr_den if sr_den else np.nan,
                              "kupiec_reject": float(np.mean(kup)) if kup else np.nan, "christoffersen_reject": float(np.mean(chr_)) if chr_ else np.nan}
            T = L["HAR"].shape[0]; block = default_block(h, T)
            for lab, _ in names:
                a, b = paired_block_test(L[lab] - L["HAR"], block=block, reps=2000, seed=h), paired_block_test(FZ[lab] - FZ["HAR"], block=block, reps=2000, seed=h)
                verdict = lambda r_: "better" if r_.ci_high < 0 else "worse" if r_.ci_low > 0 else "n.s."
                rows.append({"h": h, "alpha": alpha, "method": lab, "series": L[lab].shape[1], **stats[lab], "tick_rel_to_har": a.mean / L["HAR"].mean(),
                             "tick_verdict": "" if lab == "HAR" else verdict(a), "fz0_diff_to_har": b.mean, "fz0_verdict": "" if lab == "HAR" else verdict(b)})
    return pd.DataFrame(rows)


COST = 0.001                               # 10 basis points per change of position, for the cost variant of the rule


def rule_stats(y, long, h, ppy):
    out = []
    for o in range(h):
        yy, ll = y[o::h], long[o::h].astype(float)
        if len(yy) < 2:
            continue
        g = ll * yy
        gc = g - COST * np.abs(np.diff(np.r_[0.0, ll]))             # the first entry counts as a change
        hv = F.hist_var_cvar(g, 0.05)
        out.append({"ann_return": float(np.prod(1 + g) ** (ppy / (h * len(g))) - 1), "sharpe": float(g.mean() / g.std() * np.sqrt(ppy / h)) if g.std() > 1e-12 else 0.0,
                    "sharpe_10bp": float(gc.mean() / gc.std() * np.sqrt(ppy / h)) if gc.std() > 1e-12 else 0.0,
                    "var5": hv["var"], "cvar5": hv["cvar"], "max_drawdown": F.max_drawdown(g), "invested": float(ll.mean()),
                    "switches_per_year": float(np.abs(np.diff(ll)).sum() / (len(ll) * h / ppy))})
    return avg(out)


def strategy_section(by, M):
    rows = []
    for (freq, name, kind, h), cells in sorted(by.items()):
        if kind != "return":
            continue
        names = [(lab, b) for lab, b in M + REFS["return"] if all(seed_cols(p, b) for _, p in cells)]
        per = {lab: [] for lab, _ in names + [("buy-and-hold", None)]}
        for target, pred in cells:
            y = pred["y"].values
            bh = rule_stats(y, np.ones(len(y), bool), h, PPY[freq])
            per["buy-and-hold"].append({**bh, "sharpe_above_bh": np.nan, "sharpe_10bp_above_bh": np.nan, "drawdown_below_bh": np.nan})
            for lab, b in names:
                s = avg([rule_stats(y, pred[c].values >= 0, h, PPY[freq]) for c in seed_cols(pred, b)])
                per[lab].append({**s, "sharpe_above_bh": float(s["sharpe"] > bh["sharpe"] + 1e-12), "sharpe_10bp_above_bh": float(s["sharpe_10bp"] > bh["sharpe_10bp"] + 1e-12),
                                 "drawdown_below_bh": float(s["max_drawdown"] < bh["max_drawdown"] - 1e-12)})
        for lab, v in per.items():
            a = pd.DataFrame(v)
            flags = ["sharpe_above_bh", "sharpe_10bp_above_bh", "drawdown_below_bh"]
            rows.append({"frequency": freq, "h": h, "method": lab, "series": len(v), **a.drop(columns=flags).mean().to_dict(),
                         **{f"series_{k}": (a[k].sum() if lab != "buy-and-hold" else np.nan) for k in flags}})
    return pd.DataFrame(rows)


def tail_section(by, M):
    rows, rel = [], []
    for (freq, name, kind, h), cells in sorted(by.items()):
        if not kind.startswith("tail"):
            continue
        names = [(lab, b) for lab, b in M + REFS[kind] if all(seed_cols(p, b) for _, p in cells)]
        e = np.concatenate([p["y_eval"].values for _, p in cells]).astype(bool)
        base = np.concatenate([p["bench|base"].values for _, p in cells])
        for lab, b in names:
            per_seed = []
            for k in range(len(seed_cols(cells[0][1], b))):
                p = np.clip(np.concatenate([pr[seed_cols(pr, b)[k]].values for _, pr in cells]), 0, 1)
                c1, c2, d = F.confusion(e, p > base), F.confusion(e, p > 2 * base), F.brier_decomposition(e, p)
                per_seed.append({**{k_: float(v) for k_, v in c1.items()}, **{f"strong_{k_}": float(v) for k_, v in c2.items()}, **d})
                if k == 0:
                    edges = np.unique(np.quantile(p, [0.2, 0.4, 0.6, 0.8])); which = np.searchsorted(edges, p, side="right")
                    for j in np.unique(which):
                        rel.append({"frequency": freq, "task": name, "kind": kind, "method": lab, "fifth": int(j) + 1, "n": int((which == j).sum()),
                                    "mean_forecast": float(p[which == j].mean()), "observed": float(e[which == j].mean())})
            rows.append({"frequency": freq, "task": name, "kind": kind, "h": h, "method": lab, "n": len(e), "event_rate": float(e.mean()), **avg(per_seed)})
    return pd.DataFrame(rows), pd.DataFrame(rel)


PERIODS = [("Q4 2018 sell-off", "2018-10-01", "2018-12-31"), ("COVID-19 crash", "2020-02-17", "2020-04-30"),
           ("2022: invasion of Ukraine and rate shock", "2022-02-21", "2022-10-31")]
DRAWDOWN, MIN_OBS = 0.10, 20


def drawdown_state(returns: pd.Series, dates) -> np.ndarray:
    """True on the dates at which the index stands DRAWDOWN or more below its running peak since the start of its
    sample. Uses returns up to each date only."""
    w = (1.0 + returns.fillna(0.0)).cumprod()
    dd = 1.0 - w / w.cummax()
    return (dd.reindex(pd.DatetimeIndex(dates)).values >= DRAWDOWN)


def stress_section(by, M, returns=None):
    """Primary loss relative to the reference on forecasts made in the named periods and in the drawdown state
    (docs/protocol/EXTRA_METRICS.md, section 5). ``returns``: {frequency: period returns of the series} for the drawdown state."""
    from iba.eval.map import REFERENCE, pointwise
    rows = []
    for (freq, name, kind, h), cells in sorted(by.items()):
        ref = REFERENCE[kind]
        extra = [x for x in REFS[kind] if x[1] != ref]
        names = [(lab, b) for lab, b in M + extra if all(seed_cols(p, b) for _, p in cells)]
        masks = {}
        d0 = pd.DatetimeIndex(cells[0][1]["date"])
        named = np.zeros(len(d0), bool)
        for lab, a, b in PERIODS:
            m = (d0 >= pd.Timestamp(a)) & (d0 <= pd.Timestamp(b))
            masks[lab] = [m] * len(cells); named |= m
        masks["other periods"] = [~named] * len(cells)
        if returns is not None and freq in returns:
            dd = [drawdown_state(returns[freq][t], p["date"]) for t, p in cells]
            masks[f"in drawdown (at least {int(100 * DRAWDOWN)} % below the peak)"] = dd
            masks["not in drawdown"] = [~x for x in dd]
        for period, ms in masks.items():
            n = int(sum(m.sum() for m in ms))
            lr = sum(pointwise(p, kind, ref)[m].sum() for (_, p), m in zip(cells, ms))
            for lab, b in names:
                lm = sum(np.mean([pointwise(p, kind, c)[m].sum() for c in seed_cols(p, b)]) for (_, p), m in zip(cells, ms))
                rows.append({"frequency": freq, "task": name, "kind": kind, "h": h, "period": period, "method": lab, "forecasts": n,
                             "rel_to_reference": lm / lr - 1 if n >= MIN_OBS and lr > 0 else np.nan})
    return pd.DataFrame(rows)


def pct(x, d=1):
    return "" if x != x else f"{100 * x:.{d}f} %"


def main():
    out = os.path.join(wr.REPO, "docs", "results", OUT); os.makedirs(out, exist_ok=True)
    res = os.path.join(wr.REPO, "docs", "results", wr.SPEC)
    P = json.load(open(os.path.join(res, "prior_choice.json")))["chosen"]
    by = wr.load()
    cell = lambda spec, stage, *mid: (lambda t: os.path.join(wr.REPO, "artifacts", spec, f"stage{stage}", *mid, t.frequency, t.name, t.target.replace("^", "_"), "predictions.csv"))
    n_g = add_columns(by, cell(study.FIRST_SPEC, 1), lambda c: c.split("::")[0] in GARCH)
    n_b = add_columns(by, cell(study.BENCH2, 10), lambda c: c.startswith(("kpca|", "ae|")))
    final = os.path.join(res, "final_method.json")
    accuracy = json.load(open(final))["accuracy"] if os.path.exists(final) else None
    if accuracy and not accuracy.endswith("_nb"):                 # the ABC colony: its forecasts are stage 9's
        add_columns(by, cell(wr.SPEC, 9, f"prior_{P}"), lambda c: c.split("::")[0].startswith("iba_ca"))
    head = ("DESCRIPTIVE. Definitions in `docs/protocol/EXTRA_METRICS.md`, written before these numbers were computed; the specs whose forecasts are read "
            "were frozen without these measures, so nothing here decides anything. All factor methods with the linear model. "
            f"Formula set of the final method: {P}; its averaged reading: `{accuracy or P + '_nb'}`. GARCH forecasts from the first study ({n_g} cells); "
            f"kernel PCA and autoencoder from their own run ({n_b} cells).")
    from iba.data.panel import load_panel
    returns = {f: load_panel(f).returns for f in ("weekly", "monthly")}
    tables(by, methods(P, accuracy), out, "Financial and classification measures of the stored forecasts (development series)", head, returns)


def tables(by, M, out, title, head, returns=None):
    """Compute the sections for the cells in ``by`` and write the CSV files and ``extra_metrics.md`` to ``out``.
    Returns the three tables (VaR backtest, long/flat rule, tail classification) for a caller that decides claims on them.
    ``returns``: {frequency: DataFrame of period returns} of the series, for the drawdown state of the stress table."""
    os.makedirs(out, exist_ok=True)
    V, S = var_section(by, M), strategy_section(by, M)
    X = stress_section(by, M, returns)
    X.to_csv(os.path.join(out, "stress_periods.csv"), index=False)
    T, R = tail_section(by, M)
    V.to_csv(os.path.join(out, "var_backtest.csv"), index=False); S.to_csv(os.path.join(out, "long_flat_rule.csv"), index=False)
    T.to_csv(os.path.join(out, "tail_classification.csv"), index=False); R.to_csv(os.path.join(out, "tail_reliability.csv"), index=False)
    order = [lab for lab, _ in M] + [lab for k in REFS.values() for lab, _ in k] + ["buy-and-hold"]
    rank = lambda d: d.assign(_o=d.method.map({m: i for i, m in enumerate(dict.fromkeys(order))})).sort_values("_o").drop(columns="_o")
    md = [f"# {title}", "", head, ""]
    md += ["## 1. Value at risk and expected shortfall from the volatility forecasts (weekly series, zero-mean normal returns)", ""]
    if not len(V):
        md += ["No volatility target in this run.", ""]
    for alpha in (0.05, 0.01) if len(V) else ():
        for h in sorted(V.h.unique()):
            g = rank(V[(V.alpha == alpha) & (V.h == h)])
            t = pd.DataFrame({"method": g.method, f"violations (target {pct(alpha, 0)})": g.violation_rate.map(lambda x: pct(x, 2)),
                              "quantile loss vs HAR": [f"{100 * a:+.2f} % {v}".strip() for a, v in zip(g.tick_rel_to_har, g.tick_verdict)],
                              "VaR-ES score (FZ0) vs HAR": [f"{a:+.4f} {v}".strip() for a, v in zip(g.fz0_diff_to_har, g.fz0_verdict)],
                              "shortfall ratio": g.shortfall_ratio.round(2)})
            if h == 1:
                t["series rejecting coverage (Kupiec)"] = g.kupiec_reject.map(lambda x: pct(x, 0)).values
                t["series rejecting independence (Christoffersen)"] = g.christoffersen_reject.map(lambda x: pct(x, 0)).values
            md += [f"### {pct(alpha, 0)} level, {h} week{'s' if h > 1 else ''} ({int(g.series.iloc[0])} series)", "", t.to_markdown(index=False), ""]
    md += ["## 2. The long/flat rule on the return forecasts (no transaction costs)", "",
           "Long for the next h periods when the forecast return is not negative, else flat. Means over series; VaR and CVaR are of the h-period returns.", ""]
    for freq in ("weekly", "monthly"):
        for h in sorted(S[S.frequency == freq].h.unique()):
            g = rank(S[(S.frequency == freq) & (S.h == h)])
            n = int(g.series.iloc[0])
            t = pd.DataFrame({"method": g.method, "annual return": g.ann_return.map(pct), "Sharpe": g.sharpe.round(2), "Sharpe after 10 bp per switch": g.sharpe_10bp.round(2),
                              "5 % VaR": g.var5.map(pct), "5 % CVaR": g.cvar5.map(pct),
                              "max drawdown": g.max_drawdown.map(pct), "time invested": g.invested.map(lambda x: pct(x, 0)), "switches / year": g.switches_per_year.round(1),
                              f"series with higher Sharpe than buy-and-hold (of {n})": g.series_sharpe_above_bh.map(lambda x: "" if x != x else int(x)),
                              f"series with smaller drawdown (of {n})": g.series_drawdown_below_bh.map(lambda x: "" if x != x else int(x))})
            md += [f"### {freq}, {h} {'week' if freq == 'weekly' else 'month'}{'s' if h > 1 else ''}", "", t.to_markdown(index=False), ""]
    md += ["## 3. The tail probabilities as a classifier (10 % events; all tasks of the type, counts summed)", "",
           "Signal: forecast probability above the base-rate forecast of the date; strong signal: above twice that.", ""]
    for kind, title in (("tail_loss", "Large loss"), ("tail_gain", "Large gain")):
        g = T[T.kind == kind]
        rows = []
        for lab in [m for m in dict.fromkeys(order) if m in set(g.method)]:
            x = g[g.method == lab]
            tp, fp, fn, tn = (x[k].sum() for k in ("tp", "fp", "fn", "tn"))
            stp, sfp, sfn = (x[k].sum() for k in ("strong_tp", "strong_fp", "strong_fn"))
            rows.append({"method": lab, "signal rate": pct((tp + fp) / (tp + fp + fn + tn)), "precision": pct(tp / (tp + fp)) if tp + fp else "never signals",
                         "recall": pct(tp / (tp + fn)), "specificity": pct(tn / (tn + fp)), "MCC": round(F.mcc(tp, fp, fn, tn), 3),
                         "strong: signal rate": pct((stp + sfp) / (tp + fp + fn + tn)), "strong: precision": pct(stp / (stp + sfp)) if stp + sfp else "never",
                         "strong: recall": pct(stp / (stp + sfn)), "reliability x1000": round(1000 * x.reliability.mean(), 2),
                         "resolution x1000": round(1000 * x.resolution.mean(), 2), "sharpness": round(x.sharpness.mean(), 3)})
        md += [f"### {title} (event rate {pct(g.event_rate.mean())})", "", pd.DataFrame(rows).to_markdown(index=False), ""]
        show = [M[0][0], "volatility-based logit"]
        r = R[(R.kind == kind) & R.method.isin(show)]
        tab = r.assign(w=r.n).groupby(["method", "fifth"]).apply(lambda d: pd.Series({"mean forecast": np.average(d.mean_forecast, weights=d.w), "observed": np.average(d.observed, weights=d.w)})).reset_index()
        tab["mean forecast"], tab["observed"] = tab["mean forecast"].map(pct), tab["observed"].map(pct)
        md += ["Reliability by fifth of the forecast (lowest to highest), tasks pooled:", "", tab.to_markdown(index=False), ""]
    md += ["## 4. Crisis and drawdown periods (descriptive: short subsamples, no test)", "",
           "Primary loss relative to the reference (negative = better) on forecasts made in the period, all series pooled; mean over the tasks of the type. "
           "In brackets: pooled forecasts per task, smallest to largest.", ""]
    kinds = [k for k in ("return", "logrv", "tail_loss", "tail_gain") if k in set(X.kind)]
    for freq in [f for f in ("weekly", "monthly") if f in set(X.frequency)]:
        x = X[X.frequency == freq]
        for period in dict.fromkeys(x.period):
            g = x[x.period == period]
            n = g.groupby("task").forecasts.first()
            t = g.pivot_table(index="method", columns="kind", values="rel_to_reference", aggfunc="mean").reindex(columns=kinds)
            t = t.reindex([m for m in dict.fromkeys(order) if m in t.index]).map(lambda v: "" if v != v else f"{100 * v:+.1f} %").reset_index()
            md += [f"### {freq}: {period} ({int(n.min())} to {int(n.max())} forecasts)", "", t.to_markdown(index=False), ""]
    open(os.path.join(out, "extra_metrics.md"), "w").write("\n".join(md))
    print("\n".join(md))
    return V, S, T


if __name__ == "__main__":
    main()
