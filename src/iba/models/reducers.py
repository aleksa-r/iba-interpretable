"""Representations with one interface: ``fit(X_train_df, y_train) -> self``, ``transform(X_df) -> array``.
All are fitted on the rows they are given only (the engine passes admissible rows)."""
from __future__ import annotations

import warnings
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from ..algebra.gbp import conjunction, describe
from ..algebra.predicates import PredicateScaler

Formula = Dict[str, Tuple[List[str], List[str]]]     # group -> (asserted columns, negated columns)


class Reducer:
    name = "base"

    def fit(self, X: pd.DataFrame, y=None) -> "Reducer":
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError

    def info(self) -> dict:
        return {}


class RawReducer(Reducer):
    name = "raw"

    def transform(self, X):
        return X.values.astype(np.float64)


class PCAReducer(Reducer):
    name = "pca"

    def __init__(self, k: int = 6):
        self.k = k

    def fit(self, X, y=None):
        from sklearn.decomposition import PCA
        self.mu_, self.sd_ = X.values.mean(axis=0), np.where(X.values.std(axis=0) > 1e-12, X.values.std(axis=0), 1.0)
        k = min(self.k, X.shape[1], X.shape[0] - 1)
        self.pca_ = PCA(n_components=k, svd_solver="full").fit((X.values - self.mu_) / self.sd_)
        return self

    def transform(self, X):
        return self.pca_.transform((X.values - self.mu_) / self.sd_)

    def info(self):
        return {"explained_variance": float(self.pca_.explained_variance_ratio_.sum())}


class GroupPCAReducer(Reducer):
    """First principal component of each group: the closest non-symbolic analogue of one formula per group."""
    name = "gpca"

    def __init__(self, group_cols: Dict[str, List[str]]):
        self.group_cols = group_cols

    def fit(self, X, y=None):
        from sklearn.decomposition import PCA
        self.models_ = {}
        for g, cols in self.group_cols.items():
            V = X[cols].values
            mu, sd = V.mean(axis=0), np.where(V.std(axis=0) > 1e-12, V.std(axis=0), 1.0)
            self.models_[g] = (mu, sd, PCA(n_components=1, svd_solver="full").fit((V - mu) / sd))
        return self

    def transform(self, X):
        return np.hstack([p.transform((X[self.group_cols[g]].values - mu) / sd) for g, (mu, sd, p) in self.models_.items()])


class KernelPCAReducer(Reducer):
    """Standardise, RBF kernel PCA with gamma = 1 / number of features, k components: the kernel
    PCA benchmark of the earlier code base, unchanged, with the dense eigen-solver (no random start)."""
    name = "kpca"

    def __init__(self, k: int = 6):
        self.k = k

    def fit(self, X, y=None):
        from sklearn.decomposition import KernelPCA
        self.mu_, self.sd_ = X.values.mean(axis=0), np.where(X.values.std(axis=0) > 1e-12, X.values.std(axis=0), 1.0)
        Z = (X.values - self.mu_) / self.sd_
        k = min(self.k, X.shape[0] - 1)
        self.kpca_ = KernelPCA(n_components=k, kernel="rbf", gamma=1.0 / Z.shape[1], eigen_solver="dense").fit(Z)
        return self

    def transform(self, X):
        return self.kpca_.transform((X.values - self.mu_) / self.sd_).astype(np.float64)

    def info(self):
        ev = np.asarray(self.kpca_.eigenvalues_, dtype=float)
        return {"components": int(len(ev)), "smallest_to_largest_eigenvalue": float(ev.min() / ev.max())}


class AutoencoderReducer(Reducer):
    """Autoencoder on standardised features: p -> 16 -> k -> 16 -> p with tanh, squared reconstruction
    error, Adam, L2 penalty 1e-3, at most 400 epochs, one fixed seed; the features are the k
    bottleneck activations. The autoencoder benchmark of the earlier code base, unchanged. Unsupervised: the
    labels are not used."""
    name = "ae"

    def __init__(self, k: int = 6, hidden: int = 16, seed: int = 0):
        self.k, self.hidden, self.seed = k, hidden, seed

    def fit(self, X, y=None):
        from sklearn.neural_network import MLPRegressor
        self.mu_, self.sd_ = X.values.mean(axis=0), np.where(X.values.std(axis=0) > 1e-12, X.values.std(axis=0), 1.0)
        Z = (X.values - self.mu_) / self.sd_
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.mlp_ = MLPRegressor(hidden_layer_sizes=(self.hidden, self.k, self.hidden), activation="tanh", solver="adam",
                                     alpha=1e-3, max_iter=400, random_state=self.seed).fit(Z, Z)
        return self

    def transform(self, X):
        a = (X.values - self.mu_) / self.sd_
        for W, b in list(zip(self.mlp_.coefs_, self.mlp_.intercepts_))[:2]:      # encoder half: input -> 16 -> k
            a = np.tanh(a @ W + b)
        return a.astype(np.float64)

    def info(self):
        return {"epochs": int(self.mlp_.n_iter_), "reconstruction_loss": float(self.mlp_.loss_)}


class LassoReducer(Reducer):
    """Features with a non-zero LassoCV coefficient; inner time-series splits separated by the horizon."""
    name = "lasso"

    def __init__(self, gap: int, fallback_top: int = 5):
        self.gap, self.fallback_top = gap, fallback_top

    def fit(self, X, y=None):
        from sklearn.linear_model import LassoCV
        from sklearn.model_selection import TimeSeriesSplit
        V = X.values
        mu, sd = V.mean(axis=0), np.where(V.std(axis=0) > 1e-12, V.std(axis=0), 1.0)
        Z = (V - mu) / sd
        y = np.asarray(y, dtype=np.float64)
        n_splits = 5
        while n_splits > 2 and len(y) // (n_splits + 1) <= self.gap:
            n_splits -= 1
        sel = np.zeros(V.shape[1], dtype=bool)
        if y.std() > 0:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = LassoCV(cv=TimeSeriesSplit(n_splits=n_splits, gap=self.gap), alphas=50, max_iter=20000).fit(Z, y)
            sel = np.abs(m.coef_) > 1e-10
        self.fallback_ = not sel.any()
        if self.fallback_:
            c = np.nan_to_num(np.abs(np.corrcoef(Z.T, y)[-1, :-1])) if y.std() > 0 else np.zeros(V.shape[1])
            sel[np.argsort(-c, kind="stable")[: self.fallback_top]] = True
        self.sel_ = sel
        return self

    def transform(self, X):
        return X.values[:, self.sel_].astype(np.float64)

    def info(self):
        return {"n_selected": int(self.sel_.sum()), "fallback": bool(self.fallback_)}


class IBAReducer(Reducer):
    """One GBP per active group: the conjunction of the formula's literals under the chosen
    generalized product. Predicates are scaled per group on the training rows."""
    name = "iba"

    def __init__(self, group_cols: Dict[str, List[str]], formula: Formula, tnorm: str = "product",
                 scaler: str = "minmax"):
        self.group_cols, self.tnorm, self.scaler = group_cols, tnorm, scaler
        self.formula = {g: (list(a), list(n)) for g, (a, n) in formula.items() if (a or n)}
        for g, (a, n) in self.formula.items():
            missing = [c for c in a + n if c not in group_cols[g]]
            if missing:
                raise KeyError(f"formula of group {g} uses unknown columns {missing}")

    def fit(self, X, y=None):
        self.scalers_ = {g: PredicateScaler(self.scaler).fit(X[self.group_cols[g]].values) for g in self.formula}
        return self

    def transform(self, X):
        if not self.formula:
            return np.zeros((len(X), 0))
        out = []
        for g, (a, n) in self.formula.items():
            cols = self.group_cols[g]
            Z = self.scalers_[g].transform(X[cols].values)
            out.append(conjunction(Z, [cols.index(c) for c in a], [cols.index(c) for c in n], self.tnorm))
        return np.column_stack(out)

    def info(self):
        return {"formula": {g: {"asserted": a, "negated": n, "text": describe(a + n, range(len(a)), range(len(a), len(a) + len(n)))}
                            for g, (a, n) in self.formula.items()}}


class GradedIBAReducer(Reducer):
    """One graded conjunction per active group (SPEC-2026-11-14-abc-v2). Every predicate j of a
    group has a weight w_j in [-1, 1]: its sign is the polarity of the literal, |w_j| the degree
    u_j to which the literal is in the conjunction (weights below ``delta`` in absolute value
    count as exactly 0, "not used"):
        f(x) = prod_j [ (1 - u_j) + u_j * lit_j(x) ],   lit_j = x_j if w_j > 0 else 1 - x_j.
    Expanding the product gives a convex combination of conjunctions of the literals, i.e. a
    logical aggregation of generalized Boolean polynomials under the product; with every u_j in
    {0, 1} it is exactly the conjunction of ``IBAReducer``. A group with no used predicate is off."""
    name = "iba_graded"

    def __init__(self, group_cols: Dict[str, List[str]], weights: Dict[str, Sequence[float]], delta: float = 0.1,
                 scaler: str = "minmax"):
        self.group_cols, self.delta, self.scaler = group_cols, delta, scaler
        self.weights = {}
        for g, w in weights.items():
            w = np.asarray(w, dtype=np.float64)
            if len(w) != len(group_cols[g]):
                raise ValueError(f"group {g}: {len(w)} weights for {len(group_cols[g])} predicates")
            if (np.abs(w) >= delta).any():
                self.weights[g] = w

    def fit(self, X, y=None):
        self.scalers_ = {g: PredicateScaler(self.scaler).fit(X[self.group_cols[g]].values) for g in self.weights}
        return self

    def transform(self, X):
        if not self.weights:
            return np.zeros((len(X), 0))
        return np.column_stack([graded_conjunction(self.scalers_[g].transform(X[self.group_cols[g]].values), w, self.delta)
                                for g, w in self.weights.items()])

    def info(self):
        return {"weights": {g: [round(float(x), 4) for x in w] for g, w in self.weights.items()}}


def graded_conjunction(Z: np.ndarray, w: np.ndarray, delta: float = 0.1) -> np.ndarray:
    """prod_j [(1 - u_j) + u_j * lit_j] on scaled predicates Z (rows x predicates of one group)."""
    out = np.ones(Z.shape[0])
    for j in np.flatnonzero(np.abs(w) >= delta):
        u = abs(float(w[j]))
        out = out * (1.0 - u * (1.0 - (Z[:, j] if w[j] > 0 else 1.0 - Z[:, j])))
    return out


_CLASS_OF: Dict[str, Tuple[str, str]] = {}


def class_of(target: str) -> Tuple[str, str]:
    """(panel frequency, asset class) of a series of the universe."""
    if not _CLASS_OF:
        from ..data.universe import load_hf_catalogue, load_universe
        for s in load_universe()[0]:
            _CLASS_OF[s.ticker] = ("weekly" if s.frequency == "daily" else "monthly", s.asset_class)
        cat = load_hf_catalogue()                                 # the hedge-fund extension: one asset class, monthly
        for s in cat["series"]:
            _CLASS_OF[s["code"]] = ("monthly", cat["asset_class"])
    return _CLASS_OF[target]


def prior_formula(formulas: dict, target: str, group_cols: Dict[str, List[str]], windows: Sequence[int],
                  kind: str = "return") -> Formula:
    """Map a formula file onto one target's feature columns. Two layouts:
    generic (`groups: {G: [[code, high|not_high], ...]}`, optional per-type variants under
    `return:` / `volatility:` / `tail:`), the same for every target; and per asset class
    (`classes: {frequency: {asset class: {kind: {groups: ...}}}}`, written by
    ``scripts/elicit_priors.py``), where the target's class and the task's kind pick the section
    and a missing one is an error, never a silent fall-back. Every predicate uses the LONGER
    z-score window; a literal whose factor is excluded for the target is dropped; a group left
    without literals is dropped."""
    if "classes" in formulas:
        freq, cls = class_of(target)
        try:
            groups = formulas["classes"][freq][cls][kind]["groups"]
        except KeyError:
            raise KeyError(f"no prior formula for {freq} / {cls} / {kind} (target {target}) in: {formulas.get('source', 'formula file')}") from None
    else:
        section = {"return": "return", "logrv": "volatility", "tail_loss": "tail", "tail_gain": "tail"}[kind]
        groups = (formulas.get(section) or {}).get("groups") or formulas["groups"]
    w = max(int(x) for x in windows)
    out: Formula = {}
    for g, lits in groups.items():
        if g not in group_cols:
            continue
        a, n = [], []
        for code, state in lits:
            col = f"{target if code == '__target__' else code}_{w}m_zs"
            if col in group_cols[g]:
                (a if state == "high" else n).append(col)
        if a or n:
            out[g] = (a, n)
    return out


def make_reducer(name: str, group_cols: Dict[str, List[str]], horizon: int, formula: Optional[Formula] = None) -> Reducer:
    if name == "raw":
        return RawReducer()
    if name == "pca":
        return PCAReducer(6)
    if name == "gpca":
        return GroupPCAReducer(group_cols)
    if name == "lasso":
        return LassoReducer(gap=horizon)
    if name == "kpca":
        return KernelPCAReducer(6)
    if name == "ae":
        return AutoencoderReducer(6)
    if name == "iba":
        return IBAReducer(group_cols, formula or {})
    raise KeyError(name)
