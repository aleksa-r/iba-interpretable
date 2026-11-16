"""Estimators with one interface: ``fit(X, y, params) -> model``, ``predict(model, X)``.

Deterministic by construction (verification finding: XGBoost column sampling is machine-dependent):
ridge and L2-logistic are closed-form / Newton in numpy; LightGBM runs without bagging or feature
sub-sampling, one thread, deterministic mode; XGBoost likewise without any sampling. ``task`` is 'reg' (squared error) or 'clf'
(probability of the event, logistic loss).
"""
from __future__ import annotations

import itertools
import warnings
from typing import Any, Dict, List

import numpy as np

EPS_P = 1e-3   # probabilities are clipped to [EPS_P, 1 - EPS_P] before the log score


def _grid(**axes) -> List[Dict[str, Any]]:
    keys = list(axes)
    return [dict(zip(keys, v)) for v in itertools.product(*axes.values())]


def _standardise(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd > 1e-12, sd, 1.0)
    return mu, sd


def ridge_fit(X, y, alpha: float):
    """Ridge on standardised features with an unpenalised intercept (= sklearn Ridge after StandardScaler)."""
    X = np.asarray(X, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    mu, sd = _standardise(X)
    Z = (X - mu) / sd
    ybar = y.mean()
    A = Z.T @ Z + alpha * np.eye(Z.shape[1])
    beta = np.linalg.solve(A, Z.T @ (y - ybar)) if Z.shape[1] else np.zeros(0)
    return {"mu": mu, "sd": sd, "beta": beta, "b0": ybar}


def ridge_predict(m, X):
    X = np.asarray(X, dtype=np.float64)
    return m["b0"] + ((X - m["mu"]) / m["sd"]) @ m["beta"]


def logistic_fit(X, y, C: float, iters: int = 50, tol: float = 1e-10):
    """L2-penalised logistic regression (penalty 1/(2C) * |beta|^2, intercept free) by damped Newton
    on standardised features. With one class in ``y`` the model is the constant base rate."""
    X = np.asarray(X, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    mu, sd = _standardise(X)
    Z = (X - mu) / sd
    n, p = Z.shape
    pbar = float(np.clip(y.mean(), 1.0 / (2 * n), 1 - 1.0 / (2 * n)))
    b0, beta = float(np.log(pbar / (1 - pbar))), np.zeros(p)
    if y.min() == y.max() or p == 0:
        return {"mu": mu, "sd": sd, "beta": beta, "b0": b0}
    lam = 1.0 / C
    A = np.column_stack([np.ones(n), Z])
    P = np.diag(np.r_[0.0, np.full(p, lam)])
    w = np.r_[b0, beta]

    def nll(w_):
        eta = A @ w_
        return float(np.sum(np.logaddexp(0.0, eta) - y * eta) + 0.5 * lam * np.sum(w_[1:] ** 2))

    cur = nll(w)
    for _ in range(iters):
        eta = A @ w
        pr = 1.0 / (1.0 + np.exp(-eta))
        g = A.T @ (pr - y) + P @ w
        H = (A * (pr * (1 - pr))[:, None]).T @ A + P + 1e-10 * np.eye(p + 1)
        step = np.linalg.solve(H, g)
        t = 1.0
        while t > 1e-6:                                   # backtracking keeps the Newton step monotone
            new = nll(w - t * step)
            if new <= cur + 1e-12:
                break
            t *= 0.5
        w = w - t * step
        if cur - new < tol * max(1.0, abs(cur)):
            cur = new
            break
        cur = new
    return {"mu": mu, "sd": sd, "beta": w[1:], "b0": float(w[0])}


def logistic_predict(m, X):
    X = np.asarray(X, dtype=np.float64)
    eta = m["b0"] + ((X - m["mu"]) / m["sd"]) @ m["beta"]
    return 1.0 / (1.0 + np.exp(-eta))


class Estimator:
    name = "base"
    grid: List[Dict[str, Any]] = [{}]

    def __init__(self, task: str):
        assert task in ("reg", "clf")
        self.task = task

    def fit(self, X, y, params):
        raise NotImplementedError

    def predict(self, model, X):
        raise NotImplementedError


class LinearEstimator(Estimator):
    """ridge for 'reg', L2-logistic for 'clf'."""
    name = "lin"
    RIDGE_GRID = _grid(alpha=[float(a) for a in np.logspace(-2, 3, 8)])
    LOGIT_GRID = _grid(C=[float(c) for c in np.logspace(-3, 2, 8)])

    def __init__(self, task: str, grid=None):
        super().__init__(task)
        self.grid = grid or (self.RIDGE_GRID if task == "reg" else self.LOGIT_GRID)

    def fit(self, X, y, params):
        return ridge_fit(X, y, params["alpha"]) if self.task == "reg" else logistic_fit(X, y, params["C"])

    def predict(self, model, X):
        return ridge_predict(model, X) if self.task == "reg" else logistic_predict(model, X)


class GBTEstimator(Estimator):
    """LightGBM without any random element."""
    name = "gbt"
    grid = _grid(max_depth=[2, 4], n_estimators=[100, 300])
    base = dict(learning_rate=0.05, min_child_samples=10, subsample=1.0, colsample_bytree=1.0, reg_lambda=1.0,
                n_jobs=1, deterministic=True, force_row_wise=True, verbose=-1, random_state=0)

    def fit(self, X, y, params):
        import lightgbm as lgb
        p = {**self.base, **params, "num_leaves": 2 ** int(params["max_depth"])}
        y = np.asarray(y, dtype=np.float64)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if self.task == "reg":
                return lgb.LGBMRegressor(**p).fit(np.asarray(X, dtype=np.float64), y)
            if y.min() == y.max():
                return {"const": float(y.mean())}
            return lgb.LGBMClassifier(**p).fit(np.asarray(X, dtype=np.float64), y.astype(int))

    def predict(self, model, X):
        X = np.asarray(X, dtype=np.float64)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if isinstance(model, dict):
                return np.full(X.shape[0], model["const"])
            return model.predict(X) if self.task == "reg" else model.predict_proba(X)[:, 1]


class XGBEstimator(Estimator):
    """XGBoost without any random element: no row and no column sampling (column sampling is the
    setting whose draws differ between machines, docs/VERIFICATION.md), histogram method,
    one thread. Same grid and shrinkage as the LightGBM estimator."""
    name = "xgb"
    grid = _grid(max_depth=[2, 4], n_estimators=[100, 300])
    base = dict(learning_rate=0.05, subsample=1.0, colsample_bytree=1.0, colsample_bylevel=1.0, colsample_bynode=1.0,
                reg_lambda=1.0, tree_method="hist", n_jobs=1, random_state=0, verbosity=0)

    def fit(self, X, y, params):
        import xgboost as xgb
        p = {**self.base, **params}
        y = np.asarray(y, dtype=np.float64)
        if self.task == "reg":
            return xgb.XGBRegressor(**p).fit(np.asarray(X, dtype=np.float64), y)
        if y.min() == y.max():
            return {"const": float(y.mean())}
        return xgb.XGBClassifier(**p).fit(np.asarray(X, dtype=np.float64), y.astype(int))

    def predict(self, model, X):
        X = np.asarray(X, dtype=np.float64)
        if isinstance(model, dict):
            return np.full(X.shape[0], model["const"])
        return model.predict(X).astype(np.float64) if self.task == "reg" else model.predict_proba(X)[:, 1].astype(np.float64)


def make_estimator(name: str, task: str) -> Estimator:
    if name == "lin":
        return LinearEstimator(task)
    if name == "gbt":
        return GBTEstimator(task)
    if name == "xgb":
        return XGBEstimator(task)
    raise KeyError(name)


def loss(task: str, y, f) -> float:
    """Mean squared error ('reg') or mean logistic loss with clipped probabilities ('clf')."""
    return float(np.mean(pointwise_loss(task, y, f)))


def pointwise_loss(task: str, y, f) -> np.ndarray:
    y = np.asarray(y, dtype=np.float64); f = np.asarray(f, dtype=np.float64)
    if task == "reg":
        return (f - y) ** 2
    p = np.clip(f, EPS_P, 1 - EPS_P)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))
