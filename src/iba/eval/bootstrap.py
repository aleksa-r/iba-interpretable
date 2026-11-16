"""Date-block bootstrap for comparisons across a panel of correlated series.

Cells (target x horizon) are not independent: the same dates drive every target and h-period
labels overlap. Resampling DATES in blocks, and taking every series at the resampled dates,
keeps both the cross-series dependence and the serial dependence inside a block.

``paired_block_test`` takes a (T dates x K series) array of per-date differences
d = loss(A) - loss(B) (NaN allowed) and returns the mean difference, a percentile confidence
interval and a two-sided bootstrap p-value for H0: E[d] = 0 (centred bootstrap).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


def block_indices(n: int, block: int, rng: np.random.Generator) -> np.ndarray:
    """Circular moving-block bootstrap indices of length n."""
    k = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=k)
    idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % n
    return idx[:n]


@dataclass
class BlockTestResult:
    mean: float
    ci_low: float
    ci_high: float
    p_value: float
    n_dates: int
    n_series: int
    block: int
    reps: int


def paired_block_test(d: np.ndarray, block: int, reps: int = 2000, seed: int = 0,
                      alpha: float = 0.05) -> BlockTestResult:
    d = np.asarray(d, dtype=np.float64)
    if d.ndim == 1:
        d = d[:, None]
    T, K = d.shape
    rng = np.random.default_rng(seed)
    stat = float(np.nanmean(d))
    boots = np.empty(reps)
    for b in range(reps):
        boots[b] = np.nanmean(d[block_indices(T, block, rng)])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    p = float(np.mean(np.abs(boots - stat) >= abs(stat)))      # centred, two-sided
    return BlockTestResult(stat, float(lo), float(hi), p, T, K, block, reps)


def default_block(h: int, n_dates: int) -> int:
    """Block length: at least the label overlap h, and about n^(1/3) for long samples."""
    return int(max(h, round(n_dates ** (1 / 3))))
