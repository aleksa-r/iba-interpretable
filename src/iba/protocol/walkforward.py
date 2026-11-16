"""The walk-forward engine: one cell = one Task on one panel, every configuration under the same
protocol.

  blocks      the last ``holdout`` rows are forecast origins, in blocks of ``reselect_every``;
  block start representation (reducer fit, IBA search) and tuning on rows j + h <= t0 only, with
              purged expanding folds; the LabelSpec is re-fitted inside every fold;
  in a block  the representation is frozen; LabelSpec and estimator are re-fitted every
              ``retrain_every`` origins on rows j + h <= t.

A configuration is "<method>|<estimator>" (reducer-based), "<method>" for direct forecasters
(colony ensemble, logical aggregation) or "bench|<name>". Nothing here computes a metric on
out-of-sample forecasts except ``evaluate``, which also writes the trial registry.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from ..eval import metrics as M
from ..models.estimators import LinearEstimator, logistic_fit, logistic_predict, loss, make_estimator
from ..models.reducers import IBAReducer, make_reducer, prior_formula
from .dataset import Dataset, LabelSpec, Task, build_dataset
from .information_rule import FoldGeometry, n_admissible, purged_folds, walk_forward_blocks


@dataclass
class ProtocolConfig:
    holdout: int
    reselect_every: int
    retrain_every: int
    min_train: int
    geo: FoldGeometry
    periods_per_year: int
    strict_minus_one: bool = False            # fold purge of the earlier code base (verification only)
    linear_grid: Optional[List[Dict[str, float]]] = None   # override (verification only)
    search_budget: int = 2000
    colony: int = 20


WEEKLY = ProtocolConfig(416, 104, 4, 300, FoldGeometry(0.7, 78, 43, 5), 52)
MONTHLY = ProtocolConfig(96, 24, 1, 110, FoldGeometry(0.7, 18, 10, 5), 12)
BENCH_REDUCERS = ("raw", "pca", "gpca", "lasso", "kpca", "ae")


def protocol_for(frequency: str) -> ProtocolConfig:
    return WEEKLY if frequency == "weekly" else MONTHLY


@dataclass
class BlockContext:
    """Everything a representation may use at a block start (all rows admissible at the origin)."""
    ds: Dataset
    label: LabelSpec
    rows: np.ndarray                                   # admissible rows [0, cut)
    y_block: np.ndarray                                # training labels on ``rows``
    folds: List[Tuple[np.ndarray, np.ndarray]]
    fold_y: List[Tuple[np.ndarray, np.ndarray]]        # (train labels, validation labels) per fold
    prior: Dict[str, Tuple[List[str], List[str]]]
    est_task: str
    h: int
    cfg: ProtocolConfig


def _tune(est, Zf, ctx: BlockContext):
    scores = []
    for params in est.grid:
        ls = []
        for (tr, va), Z, (ytr, yva) in zip(ctx.folds, Zf, ctx.fold_y):
            ls.append(loss(ctx.est_task, yva, est.predict(est.fit(Z[tr], ytr, params), Z[va])))
        scores.append(float(np.mean(ls)))
    i = int(np.argmin(scores))
    return est.grid[i], scores[i]


def run_cell(panel, task: Task, methods: Sequence[str], estimators: Sequence[str] = ("lin", "gbt"),
             cfg: Optional[ProtocolConfig] = None, seeds: Sequence[int] = (0,), with_garch: bool = True
             ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    cfg = cfg or protocol_for(task.frequency)
    ds = build_dataset(panel, task)
    L, h, T, et = LabelSpec(ds), task.h, len(ds), task.est_task
    ho0, blocks = walk_forward_blocks(T, cfg.holdout, cfg.reselect_every, cfg.min_train)
    H = T - ho0
    prior = prior_formula(panel.formulas, task.target, ds.group_cols, ds.windows, task.kind)
    preds: Dict[str, np.ndarray] = {}
    var_f: Dict[str, np.ndarray] = {}                    # variance-level forecasts (logrv)
    y_eval, thr, block_of = np.full(H, np.nan), np.full(H, np.nan), np.zeros(H, dtype=int)
    meta: Dict[str, Any] = {"task": asdict(task), "protocol": {**asdict(cfg), "geo": asdict(cfg.geo)}, "T": T, "holdout": H,
                            "first": str(ds.dates[0].date()), "holdout_start": str(ds.dates[ho0].date()),
                            "n_features": int(ds.X.shape[1]), "prior": prior, "blocks": []}

    def slot(name):
        if name not in preds:
            preds[name] = np.full(H, np.nan)
            if task.kind == "logrv":
                var_f[name] = np.full(H, np.nan)
        return preds[name]

    for b, (p0, p1) in enumerate(blocks):
        t0 = ho0 + p0
        cut = n_admissible(t0, h)
        rows = np.arange(cut)
        folds = purged_folds(cut, h, cfg.geo, cfg.strict_minus_one)
        st_blk = L.fit(rows)
        fold_states = [L.fit(tr) for tr, _ in folds]
        ctx = BlockContext(ds, L, rows, L.train_y(st_blk, rows), folds,
                           [(L.train_y(s, tr), L.train_y(s, va)) for s, (tr, va) in zip(fold_states, folds)],
                           prior, et, h, cfg)
        bmeta: Dict[str, Any] = {"block": b, "origin": str(ds.dates[t0].date()), "train_rows": int(cut),
                                 "folds": [[int(tr[-1]) + 1, int(va[0]), int(va[-1]) + 1] for tr, va in folds],
                                 "methods": {}, "tuning": {}, "seconds": {}}
        refits = [i for i in range(p0, p1) if (i - p0) % max(1, cfg.retrain_every) == 0]
        states = {i: L.fit(np.arange(n_admissible(ho0 + i, h))) for i in refits}

        # ---- representations -------------------------------------------------------------
        reps: Dict[str, Dict[str, Any]] = {}
        for m in methods:
            tic = time.perf_counter()
            reps.update(_build(m, ctx, seeds, bmeta))
            bmeta["seconds"][f"build:{m}"] = time.perf_counter() - tic

        # ---- tune and roll ----------------------------------------------------------------
        for name, rep in reps.items():
            tic = time.perf_counter()
            if rep["type"] == "reducer":
                Zb = rep["block"].transform(ds.X)
                Zf = [r.transform(ds.X.iloc[: cut]) for r in rep["folds"]]
                for e in (estimators if rep.get("all_estimators", True) else ("lin",)):
                    est = make_estimator(e, et)
                    if e == "lin" and cfg.linear_grid is not None:
                        est.grid = cfg.linear_grid
                    best, cv = _tune(est, Zf, ctx)
                    key = f"{name}|{e}"
                    bmeta["tuning"][key] = {"params": best, "cv_loss": cv}
                    _roll(key, est, best, Zb, ds, L, states, refits, p0, p1, ho0, h, slot, var_f)
            elif rep["type"] == "ensemble":                       # colony: average of members' linear forecasts
                acc = np.zeros(p1 - p0); accv = np.zeros(p1 - p0)
                for mem_block, mem_folds in rep["members"]:
                    est = LinearEstimator(et)
                    Zb = mem_block.transform(ds.X)
                    best, _ = _tune(est, [r.transform(ds.X.iloc[: cut]) for r in mem_folds], ctx)
                    tmp: Dict[str, np.ndarray] = {}
                    tmpv: Dict[str, np.ndarray] = {"m": np.full(H, np.nan)} if task.kind == "logrv" else {}
                    _roll("m", est, best, Zb, ds, L, states, refits, p0, p1, ho0, h,
                          lambda k: tmp.setdefault(k, np.full(H, np.nan)), tmpv)
                    acc += tmp["m"][p0:p1]
                    if task.kind == "logrv":
                        accv += tmpv["m"][p0:p1]
                slot(name)[p0:p1] = acc / len(rep["members"])
                if task.kind == "logrv":
                    var_f[name][p0:p1] = accv / len(rep["members"])
            elif rep["type"] == "direct":                         # logical aggregation with a two-parameter link
                _roll(name, rep["model"], {}, rep["block_feature"](ds.X), ds, L, states, refits, p0, p1, ho0, h, slot, var_f)
            bmeta["seconds"][f"fit:{name}"] = time.perf_counter() - tic

        # ---- labels for evaluation and label-based benchmarks -----------------------------
        st = None
        for i in range(p0, p1):
            t = ho0 + i
            if i in states:
                st = states[i]
                n = n_admissible(t, h)
                tr_rows = np.arange(n)
                if task.kind == "return":
                    cur = {"mean": float(np.mean(ds.y[:n]))}
                elif task.kind == "logrv":
                    resid = ds.y[:n] - L.base(st, tr_rows)
                    lastcol = {1: 0, 4: 1, 13: 2}[h]
                    cur = {"s2_har": float(np.mean(resid ** 2)), "s2_last": float(np.mean((ds.y[:n] - ds.har[:n, lastcol]) ** 2)), "lastcol": lastcol}
                else:
                    ytr = L.train_y(st, tr_rows)
                    cur = {"base": float(ytr.mean()), "logit": logistic_fit(ds.volterms[:n], ytr, C=100.0), "mu": float(np.mean(ds.y[:n]))}
            block_of[i] = b
            y_eval[i] = L.eval_y(st, np.array([t]))[0]
            if task.kind == "return":
                slot("bench|mean")[i] = cur["mean"]
                L_ = 52 if task.frequency == "weekly" else 12
                slot("bench|tsmom")[i] = ds.trail[t] * h / L_
            elif task.kind == "logrv":
                slot("bench|har")[i] = L.base(st, np.array([t]))[0]
                var_f["bench|har"][i] = np.exp(preds["bench|har"][i] + cur["s2_har"] / 2)
                slot("bench|last")[i] = ds.har[t, cur["lastcol"]]
                var_f["bench|last"][i] = np.exp(preds["bench|last"][i] + cur["s2_last"] / 2)
            else:
                thr[i] = st
                slot("bench|base")[i] = cur["base"]
                slot("bench|logit_vol")[i] = logistic_predict(cur["logit"], ds.volterms[t:t + 1])[0]
                slot("_mu")[i] = cur["mu"]
        meta["blocks"].append(bmeta)

    # ---- GARCH benchmarks (no labels; data dated <= origin) -------------------------------
    origins = list(ds.dates[ho0:])
    if with_garch and task.kind != "return":
        from ..models.benchmarks import garch_from_period_returns, garch_weekly_from_daily
        if panel.daily is not None and task.target in panel.daily:
            d = panel.daily[task.target]
            v = garch_weekly_from_daily(d, origins, h, max(1, cfg.retrain_every), "garch")
            vg = garch_weekly_from_daily(d, origins, h, max(1, cfg.retrain_every), "gjr") if task.kind == "logrv" else None
        else:
            v = garch_from_period_returns(ds.r, list(range(ho0, T)), h); vg = None
        if task.kind == "logrv":
            for nm, vv in (("bench|garch", v), ("bench|gjr", vg)):
                if vv is not None:
                    slot(nm)[:] = np.log(vv); var_f[nm][:] = vv
        else:
            from scipy.stats import norm
            z = (thr - preds["_mu"]) / np.sqrt(np.maximum(v, 1e-18))
            slot("bench|garch_prob")[:] = norm.cdf(z) if task.kind == "tail_loss" else 1.0 - norm.cdf(z)
    preds.pop("_mu", None)

    out = pd.DataFrame({"date": ds.dates[ho0:], "y": ds.y[ho0:], "y_eval": y_eval, "block": block_of})
    if task.kind.startswith("tail"):
        out["threshold"] = thr
    for k, a in preds.items():
        out[k] = a
    for k, a in var_f.items():
        out[k + "::var"] = a
    return out, meta


def block_contexts(panel, task: Task, cfg: Optional[ProtocolConfig] = None):
    """The BlockContext of every re-selection block of a cell (what a search is allowed to see),
    without running any estimator: used by the search-comparison study."""
    cfg = cfg or protocol_for(task.frequency)
    ds = build_dataset(panel, task)
    L, h = LabelSpec(ds), task.h
    ho0, blocks = walk_forward_blocks(len(ds), cfg.holdout, cfg.reselect_every, cfg.min_train)
    prior = prior_formula(panel.formulas, task.target, ds.group_cols, ds.windows, task.kind)
    for b, (p0, _) in enumerate(blocks):
        cut = n_admissible(ho0 + p0, h)
        rows = np.arange(cut)
        folds = purged_folds(cut, h, cfg.geo, cfg.strict_minus_one)
        st = L.fit(rows)
        fs = [L.fit(tr) for tr, _ in folds]
        yield b, BlockContext(ds, L, rows, L.train_y(st, rows), folds,
                              [(L.train_y(s, tr), L.train_y(s, va)) for s, (tr, va) in zip(fs, folds)], prior, task.est_task, h, cfg)


def _roll(key, est, params, Zb, ds, L, states, refits, p0, p1, ho0, h, slot, var_f):
    """Refit at the refit origins on admissible rows; forecast every origin of the block."""
    model = st = None
    s2 = 0.0
    arr = slot(key)
    for i in range(p0, p1):
        t = ho0 + i
        if i in states:
            st = states[i]
            n = n_admissible(t, h)
            tr = np.arange(n)
            ytr = L.train_y(st, tr)
            model = est.fit(Zb[:n], ytr, params)
            if ds.task.kind == "logrv":
                s2 = float(np.mean((ytr - est.predict(model, Zb[:n])) ** 2))
        f = L.finalize(st, np.array([t]), est.predict(model, Zb[t:t + 1]))[0]
        arr[i] = f
        if ds.task.kind == "logrv" and key in var_f:
            var_f[key][i] = np.exp(f + s2 / 2.0)


def _build(method: str, ctx: BlockContext, seeds: Sequence[int], bmeta) -> Dict[str, Dict[str, Any]]:
    """Representation(s) of one method for one block. Reducer-based entries carry the block
    reducer (fitted on all admissible rows) and one reducer per fold (fitted on that fold's
    training rows) for tuning."""
    ds, h = ctx.ds, ctx.h
    Xb = ds.X.iloc[ctx.rows]

    def red(name, formula=None, y=None):
        blk = make_reducer(name, ds.group_cols, h, formula).fit(Xb, ctx.y_block if y is None else y)
        fl = [make_reducer(name, ds.group_cols, h, formula).fit(ds.X.iloc[tr], ytr) for (tr, _), (ytr, _) in zip(ctx.folds, ctx.fold_y)]
        return blk, fl

    if method in BENCH_REDUCERS:
        blk, fl = red(method)
        bmeta["methods"][method] = blk.info()
        return {method: {"type": "reducer", "block": blk, "folds": fl}}
    if method == "iba_e1":
        blk, fl = red("iba", ctx.prior)
        bmeta["methods"][method] = blk.info()
        return {method: {"type": "reducer", "block": blk, "folds": fl}}
    from ..search.run import build_search_method          # search-based methods
    return build_search_method(method, ctx, seeds, bmeta, red)


# --------------------------------------------------------------------------- evaluation
def evaluate(pred: pd.DataFrame, task: Task, ppy: int, registry=None, spec_id: str = "", split: str = "development",
             extra_config: Optional[dict] = None, register=None) -> pd.DataFrame:
    """Metrics per configuration; every row is also written to the trial registry (with ``register``, a predicate
    on the configuration name, only the rows it accepts: a configuration that is identical in several cells of a
    stage, such as a reference, is then one trial and not several)."""
    cfgs = [c for c in pred.columns if c not in ("date", "y", "y_eval", "block", "threshold") and not c.endswith("::var")]
    rows = []
    for c in cfgs:
        f = pred[c].values
        if not np.isfinite(f).all():
            continue
        if task.kind == "return":
            m = M.return_metrics(pred["y"].values, f, pred["bench|mean"].values, task.h, ppy)
        elif task.kind == "logrv":
            m = M.vol_metrics(pred["y"].values, f, pred[c + "::var"].values, pred["bench|har"].values)
        else:
            m = M.tail_metrics(pred["y_eval"].values, f, pred["bench|base"].values)
        rows.append({"target": task.target, "task": task.name, "config": c, **m})
        if registry is not None and (register is None or register(c)):
            registry.record(spec_id, split, {"target": task.target, "task": task.name, "frequency": task.frequency,
                                             "config": c, **(extra_config or {})}, m)
    return pd.DataFrame(rows)
