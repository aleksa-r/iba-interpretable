"""Fitness of an IBA structure on the selection folds.

Fold roles (folds are in time order; the last one ends at the block origin's last admissible row):
  mode "A"  folds 1..K-1 = fitness, fold K = outer;
  mode "D"  folds 1..K-2 = fitness, fold K-1 = penalty, fold K = outer.
Fitness (minimised) = mean fitness-fold loss of a linear model at FIXED regularisation
(ridge alpha = 1 or logistic C = 1, standardised features) + lam * max(0, L_penalty - L_fit) [mode D]
+ kappa * (literals in excess of the prior) * L_fit(prior).
The outer fold never enters the fitness. Predicates are scaled inside every fold on that fold's
training rows. ``n_evals`` counts distinct solutions evaluated: that is the budget unit."""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from ..algebra.predicates import PredicateScaler
from ..models.estimators import logistic_fit, logistic_predict, pointwise_loss, ridge_fit, ridge_predict
from .space import SearchSpace, Solution


class FitnessEvaluator:
    def __init__(self, ctx, space: SearchSpace, mode: str = "A", kappa: float = 0.005, lam: float = 1.0,
                 alpha: float = 1.0, C: float = 1.0, scaler: str = "minmax", clean_outer: bool = False):
        self.space, self.task, self.mode, self.kappa, self.lam, self.alpha, self.C = space, ctx.est_task, mode, kappa, lam, alpha, C
        K = len(ctx.folds)
        self.outer = K - 1 if K >= 2 else None
        if mode == "D" and K >= 3:
            self.penalty, self.fit_folds = K - 2, list(range(K - 2))
        else:
            self.penalty, self.fit_folds = None, list(range(K - 1)) if K >= 2 else [0]
        self.folds, self.fold_y = ctx.folds, ctx.fold_y
        # The validation windows of consecutive folds overlap (window 78, step 34 weekly), so part of
        # the outer fold's rows are also validation rows of the last fitness fold. ``clean`` are the
        # positions of the outer rows whose labels start after every label used by the search
        # (row >= last fitness/penalty validation row + h). ``clean_outer`` makes the acceptance test
        # use only those rows (SPEC-2026-11-14-abc-v2); the first spec ran with the whole fold.
        self.clean_outer = clean_outer
        self.clean = np.zeros(0, dtype=int)
        if self.outer is not None:
            used = self.fit_folds + ([self.penalty] if self.penalty is not None else [])
            last = max(int(ctx.folds[f][1][-1]) for f in used)
            self.clean = np.flatnonzero(ctx.folds[self.outer][1] >= last + ctx.h)
        X = ctx.ds.X.iloc[ctx.rows]
        self.S: List[List[np.ndarray]] = []           # [fold][group] scaled predicates on all admissible rows
        for tr, _ in ctx.folds:
            self.S.append([PredicateScaler(scaler).fit(X[cols].values[tr]).transform(X[cols].values) for cols in space.cols])
        self.cache: Dict = {}
        self.n_evals = 0
        self.h = ctx.h
        self._prior_fit: Optional[float] = None

    # -------------------------------------------------------------------- features / losses
    def features(self, f: int, sol: Solution) -> np.ndarray:
        cols = []
        for gi, s in enumerate(sol):
            if s is None:
                continue
            Z = self.S[f][gi]
            v = np.ones(Z.shape[0])
            for j, pol in s:
                v = v * (Z[:, j] if pol else 1.0 - Z[:, j])
            cols.append(v)
        if not cols:                                   # empty formula: the model is its intercept
            return np.zeros((self.S[f][0].shape[0], 0))
        return np.column_stack(cols)

    def _fold_pointwise(self, f: int, Z: np.ndarray) -> np.ndarray:
        (tr, va), (ytr, yva) = self.folds[f], self.fold_y[f]
        if self.task == "reg":
            p = ridge_predict(ridge_fit(Z[tr], ytr, self.alpha), Z[va])
        else:
            p = logistic_predict(logistic_fit(Z[tr], ytr, self.C), Z[va])
        return pointwise_loss(self.task, yva, p)

    def fold_loss(self, f: int, sol: Solution) -> float:
        return float(np.mean(self._fold_pointwise(f, self.features(f, sol))))

    def outer_pointwise(self, sol: Solution) -> np.ndarray:
        return self._fold_pointwise(self.outer, self.features(self.outer, sol))

    # -------------------------------------------------------------------- fitness
    def evaluate(self, sol: Solution, with_outer: bool = False) -> Dict[str, float]:
        k = self.space.key(sol)
        r = self.cache.get(k)
        if r is None:
            fl = [self.fold_loss(f, sol) for f in self.fit_folds]
            inner = float(np.mean(fl))
            pen = self.fold_loss(self.penalty, sol) if self.penalty is not None else None
            r = {"inner": inner, "fold_losses": fl, "penalty": pen}
            self.cache[k] = r
            self.n_evals += 1
            if self._prior_fit is None and sol == self.space.prior:
                self._prior_fit = inner
            base = self._prior_fit if self._prior_fit is not None else inner
            r["fitness"] = inner + (self.lam * max(0.0, pen - inner) if pen is not None else 0.0) \
                + self.kappa * self.space.excess_literals(sol) * base
        if with_outer and "outer" not in r and self.outer is not None:
            pw = self.outer_pointwise(sol)
            r["outer"] = float(np.mean(pw))
            r["clean"] = float(np.mean(pw[self.clean])) if len(self.clean) else float("nan")
        return r

    def acceptance(self, cand: Solution) -> Dict[str, float]:
        """ONE test of a selected candidate against the prior on the outer fold: accepted iff its
        mean pointwise loss is lower by more than one block standard error."""
        if cand == self.space.prior or self.outer is None:
            return {"accepted": False, "gain": 0.0, "se": 0.0}
        d = self.outer_pointwise(self.space.prior) - self.outer_pointwise(cand)
        if getattr(self, "clean_outer", False):         # (the aggregation evaluator borrows this method)
            if len(self.clean) < 2:                       # no row the search has not used: the prior is kept
                return {"accepted": False, "gain": float("nan"), "se": float("nan")}
            d = d[self.clean]
        return one_se_test(d, self.h)


def one_se_test(d: np.ndarray, h: int) -> Dict[str, float]:
    """The acceptance rule on pointwise loss differences (reference minus candidate) of the outer
    fold: accepted iff the mean gain exceeds one standard error of non-overlapping block means."""
    b = max(h, 4)
    nb = len(d) // b
    if nb >= 3:
        bm = d[: nb * b].reshape(nb, b).mean(axis=1)
        se = float(bm.std(ddof=1) / np.sqrt(nb))
    else:
        se = float(d.std(ddof=1) / np.sqrt(max(len(d) / b, 1.0)))
    gain = float(d.mean())
    return {"accepted": bool(gain > se), "gain": gain, "se": se}
