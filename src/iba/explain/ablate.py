"""Fixed-formula linear forecasts of one cell under a changed component (SPEC-2026-11-15-ablations).

Built from the engine's own pieces, like ``trace.py``: block contexts, the IBA reducer, the tuning
on purged folds, the label states and the refit origins. ``variant_forecasts`` returns the
forecasts of the unchanged method (which must equal the stored ones) and of each variant:
  wo_<G>   the formula of group G removed (every group in turn, the own-behaviour group included)
  one      one literal per group: of a two-literal formula the literal whose factor comes first in the group
  ecdf     predicates scaled by the empirical distribution of the training rows instead of min-max
  nohar    volatility only: no HAR first stage; the linear model on the group values forecasts log variance directly"""
from __future__ import annotations

from typing import Dict

import numpy as np

from ..models.estimators import make_estimator
from ..models.reducers import IBAReducer
from ..protocol.dataset import LabelSpec, Task
from ..protocol.information_rule import n_admissible, walk_forward_blocks
from ..protocol.walkforward import _tune, block_contexts, protocol_for


class _Direct:
    """Label handling without a first stage: the estimator is trained on the raw label and its output is the forecast."""

    def __init__(self, ds):
        self.ds = ds

    def fit(self, rows):
        return None

    def train_y(self, state, rows):
        return self.ds.y[rows]

    def finalize(self, state, rows, raw):
        return raw


def one_literal(formula, group_cols):
    out = {}
    for g, (a, n) in formula.items():
        lits = [(c, True) for c in a] + [(c, False) for c in n]
        c, pol = min(lits, key=lambda x: group_cols[g].index(x[0]))
        out[g] = ([c], []) if pol else ([], [c])
    return out


def _roll(ctxs, ds, task, cfg, formula_of, scaler="minmax", direct=False) -> np.ndarray:
    h, T, et = task.h, len(ds), task.est_task
    L = _Direct(ds) if direct else LabelSpec(ds)
    ho0, blocks = walk_forward_blocks(T, cfg.holdout, cfg.reselect_every, cfg.min_train)
    out = np.full(T - ho0, np.nan)
    for b, (p0, p1) in enumerate(blocks):
        ctx = ctxs[b]
        cut, formula = len(ctx.rows), formula_of(ctx.prior)
        red = IBAReducer(ds.group_cols, formula, scaler=scaler).fit(ds.X.iloc[ctx.rows])
        folds = [IBAReducer(ds.group_cols, formula, scaler=scaler).fit(ds.X.iloc[tr]) for tr, _ in ctx.folds]
        Zb, Zf = red.transform(ds.X), [r.transform(ds.X.iloc[:cut]) for r in folds]
        est = make_estimator("lin", et)
        if cfg.linear_grid is not None:
            est.grid = cfg.linear_grid
        if direct:                                            # the folds' labels without the first stage
            states = [L.fit(tr) for tr, _ in ctx.folds]
            ctx = type(ctx)(**{**ctx.__dict__, "fold_y": [(L.train_y(s, tr), L.train_y(s, va)) for s, (tr, va) in zip(states, ctx.folds)]})
        params = _tune(est, Zf, ctx)[0]
        model = st = None
        for i in range(p0, p1):
            t = ho0 + i
            if (i - p0) % max(1, cfg.retrain_every) == 0:
                n = n_admissible(t, h)
                st = L.fit(np.arange(n))
                model = est.fit(Zb[:n], L.train_y(st, np.arange(n)), params)
            out[i] = L.finalize(st, np.array([t]), est.predict(model, Zb[t:t + 1]))[0]
    return out


def variant_forecasts(panel, task: Task, cfg=None) -> Dict[str, np.ndarray]:
    cfg = cfg or protocol_for(task.frequency)
    ctxs = dict(block_contexts(panel, task, cfg))
    ds = ctxs[0].ds
    out = {"base": _roll(ctxs, ds, task, cfg, lambda f: f)}
    for g in ctxs[0].prior:
        out[f"wo_{g}"] = _roll(ctxs, ds, task, cfg, lambda f, g=g: {k: v for k, v in f.items() if k != g})
    out["one"] = _roll(ctxs, ds, task, cfg, lambda f: one_literal(f, ds.group_cols))
    out["ecdf"] = _roll(ctxs, ds, task, cfg, lambda f: f, scaler="ecdf")
    if task.kind == "logrv":
        out["nohar"] = _roll(ctxs, ds, task, cfg, lambda f: f, direct=True)
    return out
