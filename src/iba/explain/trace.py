"""What a fixed-formula IBA forecast is made of, origin by origin (the input of the explanation step).

``trace_cell`` repeats the engine's ``iba_e1`` forecasts of one cell with the linear model and with
XGBoost, using the engine's own pieces (block contexts, reducer, tuning, label states, refit
origins), and keeps what the engine throws away: the value of every group formula at every
forecast origin, the linear model's coefficient and contribution per group, the exact tree
attribution per group, and the reducers (for the factor states behind a formula value).
``check_against`` compares the repeated forecasts with the stored ones: an explanation is only
written for a forecast that is reproduced.

Units of a contribution: the forecast's own for returns; log variance, on top of the HAR part,
for volatility; log-odds for the two tail probabilities."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from ..models.estimators import make_estimator
from ..models.reducers import make_reducer
from ..protocol.dataset import LabelSpec, Task
from ..protocol.information_rule import n_admissible, walk_forward_blocks
from ..protocol.walkforward import _tune, block_contexts, protocol_for


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def trace_cell(panel, task: Task, cfg=None, with_xgb: bool = True) -> Dict[str, Any]:
    cfg = cfg or protocol_for(task.frequency)
    ctxs = dict(block_contexts(panel, task, cfg))
    ds = ctxs[0].ds
    L, h, T, et = LabelSpec(ds), task.h, len(ds), task.est_task
    ho0, blocks = walk_forward_blocks(T, cfg.holdout, cfg.reselect_every, cfg.min_train)
    H = T - ho0
    names = ["lin"] + (["xgb"] if with_xgb else [])
    groups: Optional[List[str]] = None
    out: Dict[str, Any] = {"task": task, "dates": ds.dates[ho0:], "block": np.zeros(H, dtype=int), "reducers": {}, "tuned": {}}
    for b, (p0, p1) in enumerate(blocks):
        ctx = ctxs[b]
        cut = len(ctx.rows)
        red = make_reducer("iba", ds.group_cols, h, ctx.prior).fit(ds.X.iloc[ctx.rows], ctx.y_block)
        folds = [make_reducer("iba", ds.group_cols, h, ctx.prior).fit(ds.X.iloc[tr], ytr) for (tr, _), (ytr, _) in zip(ctx.folds, ctx.fold_y)]
        Zb, Zf = red.transform(ds.X), [r.transform(ds.X.iloc[:cut]) for r in folds]
        if groups is None:
            groups = list(red.formula)
            G = len(groups)
            for k in ("value", "coef", "contrib", "shap"):
                out[k] = np.full((H, G), np.nan)
            for k in ("intercept", "base", "raw", "forecast", "shap_bias", "forecast_xgb", "train_mean", "train_sd"):
                out[k] = np.full((H, G) if k.startswith("train_") else H, np.nan)
        elif list(red.formula) != groups:
            raise ValueError("the formula's groups change between blocks")
        ests, params = {}, {}
        for e in names:
            ests[e] = make_estimator(e, et)
            if e == "lin" and cfg.linear_grid is not None:
                ests[e].grid = cfg.linear_grid
            params[e] = _tune(ests[e], Zf, ctx)[0]
        out["reducers"][b], out["tuned"][b] = red, params
        models, st = {}, None
        for i in range(p0, p1):
            t = ho0 + i
            if (i - p0) % max(1, cfg.retrain_every) == 0:              # the engine's refit origins
                n = n_admissible(t, h)
                st = L.fit(np.arange(n))
                ytr = L.train_y(st, np.arange(n))
                models = {e: ests[e].fit(Zb[:n], ytr, params[e]) for e in names}
            z, m = Zb[t], models["lin"]
            c = (z - m["mu"]) / m["sd"] * m["beta"]
            raw = float(m["b0"] + c.sum())
            pred = raw if et == "reg" else float(_sigmoid(raw))
            out["block"][i], out["value"][i], out["coef"][i], out["contrib"][i] = b, z, m["beta"], c
            out["train_mean"][i], out["train_sd"][i] = m["mu"], m["sd"]
            out["intercept"][i], out["raw"][i] = float(m["b0"]), raw
            out["base"][i] = L.base(st, np.array([t]))[0]
            out["forecast"][i] = L.finalize(st, np.array([t]), np.array([pred]))[0]
            if with_xgb:
                mx = models["xgb"]
                if isinstance(mx, dict):                                # one class in the training rows: a constant
                    sh, px = np.r_[np.zeros(G), mx["const"]], mx["const"]
                else:
                    import xgboost as xgb
                    sh = mx.get_booster().predict(xgb.DMatrix(z[None, :].astype(np.float64)), pred_contribs=True)[0].astype(np.float64)
                    px = float(sh.sum()) if et == "reg" else float(_sigmoid(sh.sum()))
                out["shap"][i], out["shap_bias"][i] = sh[:G], sh[G]
                out["forecast_xgb"][i] = L.finalize(st, np.array([t]), np.array([px]))[0]
    out["groups"] = groups
    out["y"] = ds.y[ho0:]
    out["ds"] = ds
    out["ho0"] = ho0
    return out


def check_against(trace: Dict[str, Any], pred: pd.DataFrame, lin: str = "iba_e1|lin", xgb: Optional[str] = "iba_e1|xgb") -> Dict[str, float]:
    """Largest absolute difference between the repeated forecasts and the stored ones (same dates required)."""
    if len(pred) != len(trace["dates"]) or (pd.to_datetime(pred["date"]).values != np.asarray(trace["dates"], dtype="datetime64[ns]")).any():
        raise ValueError("stored predictions and trace do not share their dates")
    out = {"lin": float(np.max(np.abs(pred[lin].values - trace["forecast"])))}
    if xgb is not None and xgb in pred and np.isfinite(trace["forecast_xgb"]).all():
        out["xgb"] = float(np.max(np.abs(pred[xgb].values - trace["forecast_xgb"])))
    return out


def factor_of(column: str, target: str):
    """(factor code, window) of a feature column; the target's own column reads as ``__target__``."""
    m = re.match(r"^(.*)_(\d+)m_zs$", column)
    code, w = (m.group(1), int(m.group(2))) if m else (column, None)
    return ("__target__" if code == target else code), w


def literals_at(trace: Dict[str, Any], i: int) -> List[Dict[str, Any]]:
    """The factor states behind every group value at holdout origin ``i``: z-score, degree of truth of
    "the factor is high", the literal's value, and the group's value (their product)."""
    ds, t = trace["ds"], trace["ho0"] + i
    red = trace["reducers"][int(trace["block"][i])]
    rows = []
    for gi, g in enumerate(trace["groups"]):
        a, n = red.formula[g]
        cols = ds.group_cols[g]
        Z = red.scalers_[g].transform(ds.X[cols].values[t:t + 1])[0]
        for col, state in [(c, "high") for c in a] + [(c, "not_high") for c in n]:
            x = float(Z[cols.index(col)])
            code, w = factor_of(col, trace["task"].target)
            rows.append({"group": g, "factor": code, "window": w, "state": state, "zscore": float(ds.X[col].values[t]), "truth_high": x,
                         "literal": x if state == "high" else 1.0 - x, "group_value": float(trace["value"][i, gi])})
    return rows
