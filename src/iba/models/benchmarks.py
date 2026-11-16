"""Type-specific benchmarks that need their own machinery: GARCH variance paths.

Information rule: GARCH uses no labels, only daily (or monthly) returns dated <= the forecast
origin. Parameters are re-estimated every ``refit_every`` origins on the expanding window and the
filter is updated at every origin. The number of trading days in the label window is taken from
the calendar (exchange holidays are known in advance)."""
from __future__ import annotations

import hashlib
import os
import warnings
from typing import List, Optional

import numpy as np
import pandas as pd

CACHE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "artifacts", "cache", "garch")


def _arch(x, kind: str, mean: str):
    from arch import arch_model
    return arch_model(x, mean=mean, vol="GARCH", p=1, o=1 if kind == "gjr" else 0, q=1, dist="normal", rescale=False)


def _days_ahead(days: pd.DatetimeIndex, origin: pd.Timestamp, weeks: int) -> int:
    lo = days.searchsorted(origin, side="right")
    hi = days.searchsorted(origin + pd.Timedelta(days=7 * weeks), side="right")
    n = int(hi - lo)
    return n if n > 0 else 5 * weeks


def garch_weekly_from_daily(daily_logret: pd.Series, origins: List[pd.Timestamp], h_weeks: int, refit_every: int,
                            kind: str = "garch", cache: bool = True) -> np.ndarray:
    """Variance of the next ``h_weeks`` weeks (sum of daily variance forecasts) at each origin."""
    r = daily_logret.dropna()
    key = hashlib.sha1(("|".join(map(str, [kind, h_weeks, refit_every, origins[0], origins[-1], len(origins), len(r)]))
                        + f"{float(r.abs().sum()):.12f}").encode()).hexdigest()[:20]
    path = os.path.join(CACHE, f"{key}.npy")
    if cache and os.path.exists(path):
        return np.load(path)
    x, days = r.values * 100.0, r.index
    out, params = np.full(len(origins), np.nan), None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i, o in enumerate(origins):
            n = int(days.searchsorted(o, side="right"))
            if n < 250:
                continue
            D = _days_ahead(days, o, h_weeks)
            am = _arch(x[:n], kind, "Zero")
            try:
                if params is None or i % refit_every == 0:
                    res = am.fit(disp="off", show_warning=False); params = res.params
                else:
                    res = am.fix(params)
            except Exception:                              # a failed fit keeps the previous parameters
                if params is None:
                    continue
                res = am.fix(params)
            out[i] = float(np.sum(res.forecast(horizon=D, reindex=False).variance.values[-1])) / 1e4
    if cache:                                              # atomic: several workers may compute the same path
        os.makedirs(CACHE, exist_ok=True)
        tmp = f"{path}.{os.getpid()}.tmp.npy"
        np.save(tmp, out); os.replace(tmp, path)
    return out


def garch_from_period_returns(r: np.ndarray, origin_rows: List[int], h: int, refit_every: int = 12) -> np.ndarray:
    """Variance of the next h periods from a GARCH(1,1) with constant mean on PERIOD returns
    (monthly series without daily data). ``r[:t+1]`` is used at origin row t."""
    out, params = np.full(len(origin_rows), np.nan), None
    x = np.asarray(r, dtype=np.float64) * 100.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i, t in enumerate(origin_rows):
            if t + 1 < 60:
                continue
            am = _arch(x[: t + 1], "garch", "Constant")
            try:
                if params is None or i % refit_every == 0:
                    res = am.fit(disp="off", show_warning=False); params = res.params
                else:
                    res = am.fix(params)
                out[i] = float(np.sum(res.forecast(horizon=h, reindex=False).variance.values[-1])) / 1e4
            except Exception:
                out[i] = float(np.var(r[: t + 1]) * h)
    return out
