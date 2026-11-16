"""Descriptive forecast-comparison tests for single series (SPEC-2026-11-13, section 8).

Diebold–Mariano with the rectangular HAC variance up to lag h − 1 and the Harvey–Leybourne–Newbold
small-sample correction (Bartlett weights if the rectangular estimate is not positive), and
Clark–West for a model that nests the benchmark. Both are descriptives next to the date-block
bootstrap, which is the study's primary inference."""
from __future__ import annotations

from typing import Dict

import numpy as np
from scipy import stats


def _lrv(d: np.ndarray, lags: int, bartlett: bool) -> float:
    d = d - d.mean()
    T = len(d)
    v = float(d @ d) / T
    for k in range(1, min(lags, T - 1) + 1):
        w = 1.0 - k / (lags + 1.0) if bartlett else 1.0
        v += 2.0 * w * float(d[k:] @ d[:-k]) / T
    return v


def dm_test(loss_a: np.ndarray, loss_b: np.ndarray, h: int) -> Dict[str, float]:
    """Two-sided DM test of equal expected loss; stat < 0 means a has the lower loss."""
    d = np.asarray(loss_a, dtype=float) - np.asarray(loss_b, dtype=float)
    T = len(d)
    v = _lrv(d, h - 1, bartlett=False)
    if v <= 0:
        v = _lrv(d, h - 1, bartlett=True)
    if v <= 0 or T < 3:
        return {"stat": 0.0, "p": 1.0, "n": T}
    stat = d.mean() / np.sqrt(v / T) * np.sqrt(max(T + 1 - 2 * h + h * (h - 1) / T, 1e-12) / T)
    return {"stat": float(stat), "p": float(2 * stats.t.sf(abs(stat), T - 1)), "n": T}


def clark_west(y: np.ndarray, f_bench: np.ndarray, f_model: np.ndarray, h: int) -> Dict[str, float]:
    """One-sided Clark–West test: H0 the benchmark is at least as good in population MSPE."""
    y, fb, fm = (np.asarray(a, dtype=float) for a in (y, f_bench, f_model))
    adj = (y - fb) ** 2 - ((y - fm) ** 2 - (fb - fm) ** 2)
    T = len(adj)
    v = _lrv(adj, h - 1, bartlett=True)
    if v <= 0 or T < 3:
        return {"stat": 0.0, "p": 1.0, "n": T}
    stat = adj.mean() / np.sqrt(v / T)
    return {"stat": float(stat), "p": float(stats.norm.sf(stat)), "n": T}


def holm(p: np.ndarray) -> np.ndarray:
    """Holm step-down adjusted p-values."""
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for i, j in enumerate(order):
        running = max(running, (len(p) - i) * p[j])
        adj[j] = min(1.0, running)
    return adj
