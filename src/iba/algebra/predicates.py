"""Turning engineered features into IBA predicates in [eps, 1 - eps].

Two scalers, both fitted on admissible training rows only:

  minmax  the published method: x -> eps + (1 - 2 eps) (x - min) / (max - min), then clipped to
          [eps, 1 - eps]. One outlier in the training window sets the range, so most values
          end up in a narrow band and "high" means "close to the training maximum".
  ecdf    empirical-CDF (rank) scaling: x -> eps + (1 - 2 eps) * F_train(x). Robust to outliers;
          "high" means "in the upper quantiles of the training window"; uniform on training rows.

The information rule applies to the fit: ``fit`` must only see rows j with j + h <= t.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

Array = np.ndarray


@dataclass
class PredicateScaler:
    method: str = "minmax"          # minmax | ecdf
    eps: float = 0.01
    lo_: Optional[Array] = field(default=None, repr=False)
    hi_: Optional[Array] = field(default=None, repr=False)
    sorted_: Optional[Array] = field(default=None, repr=False)

    def fit(self, X_train: Array) -> "PredicateScaler":
        X = np.asarray(X_train, dtype=np.float64)
        if self.method == "minmax":
            self.lo_, self.hi_ = X.min(axis=0), X.max(axis=0)
        elif self.method == "ecdf":
            self.sorted_ = np.sort(X, axis=0)
        else:
            raise ValueError(self.method)
        return self

    def transform(self, X: Array) -> Array:
        X = np.asarray(X, dtype=np.float64)
        e = self.eps
        if self.method == "minmax":
            rng = np.where(self.hi_ > self.lo_, self.hi_ - self.lo_, 1.0)
            z = e + (1.0 - 2.0 * e) * (X - self.lo_) / rng
        else:
            n = self.sorted_.shape[0]
            z = np.empty_like(X)
            for j in range(X.shape[1]):
                # mid-rank ECDF: F(x) = (#{x_train < x} + 0.5 #{x_train == x}) / n
                lo = np.searchsorted(self.sorted_[:, j], X[:, j], side="left")
                hi = np.searchsorted(self.sorted_[:, j], X[:, j], side="right")
                z[:, j] = e + (1.0 - 2.0 * e) * (lo + 0.5 * (hi - lo)) / n
        return np.clip(z, e, 1.0 - e)
