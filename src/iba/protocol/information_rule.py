"""The information rule, enforced in one place.

Row j holds the features observed at the end of period j and the label realised over periods
j+1 .. j+h, i.e. known only at the end of period j+h. At forecast origin t (features of t known,
forecasting j = t) a row j may enter any fit, selection, tuning or threshold computation only if

    j + h <= t.

Every function here is a pure function of integer positions; callers pass positions, never dates.
Also: the earlier code base used the stricter cut j < t - h (one admissible row dropped). Not a leak;
noted so that exact replications of it can opt into it with ``strict_minus_one=True``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


def n_admissible(t: int, h: int, strict_minus_one: bool = False) -> int:
    """Number of rows [0, n) admissible at origin t: rows j <= t - h."""
    n = t - h + 1 - (1 if strict_minus_one else 0)
    return max(0, n)


def assert_admissible(train_rows: np.ndarray, t: int, h: int) -> None:
    if len(train_rows) and int(np.max(train_rows)) + h > t:
        raise AssertionError(f"information rule violated: row {int(np.max(train_rows))} + h={h} > origin {t}")


@dataclass(frozen=True)
class FoldGeometry:
    init_share: float = 0.7     # minimum initial training share of the last fold's training rows
    val: int = 18               # validation window (periods)
    step: int = 10              # requested step between folds
    k: int = 5                  # number of folds; the last validation window ends at the last row
    min_train: int = 50


def fold_starts(n_rows: int, geo: FoldGeometry) -> List[int]:
    """Validation-window starts in the fold geometry of the earlier code base:
    K folds whose last validation window ends exactly at n_rows; the step is the requested one,
    shortened if the initial training window would fall below ``init_share`` of the last one."""
    Q, K = geo.val, geo.k
    final_train = n_rows - Q
    if final_train < geo.min_train:
        raise ValueError(f"too few rows for selection folds: {n_rows} with validation window {Q}")
    while K > 1 and geo.min_train + (K - 1) > final_train:
        K -= 1
    if K == 1:
        return [final_train]
    m_target = max(geo.min_train, int(final_train * geo.init_share))
    max_n = (final_train - m_target) // (K - 1)
    N = 1 if max_n < 1 else min(geo.step, max_n)
    M = final_train - (K - 1) * N
    return [M + i * N for i in range(K)]


def purged_folds(n_rows: int, h: int, geo: FoldGeometry, strict_minus_one: bool = False
                 ) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Expanding-window folds over rows [0, n_rows), all of whose labels are realised at the block
    origin. Training rows of a fold obey the information rule at its first validation origin v0:
    j + h <= v0 (``strict_minus_one`` reproduces the earlier code base, which dropped one more row)."""
    folds = []
    for v0 in fold_starts(n_rows, geo):
        va = np.arange(v0, v0 + geo.val)
        tr = np.arange(0, max(v0 - h + (0 if strict_minus_one else 1), 0))
        if len(tr) >= 5:
            folds.append((tr, va))
    for tr, va in folds:
        assert_admissible(tr, int(va[0]), h)
    return folds


def walk_forward_blocks(n_rows: int, holdout: int, reselect_every: int, min_train: int
                        ) -> Tuple[int, List[Tuple[int, int]]]:
    """Out-of-sample origins are the last ``holdout`` rows (capped so that ``min_train`` rows
    remain); returned as (first_origin, [(start, end) offsets of the re-selection blocks])."""
    H = min(holdout, n_rows - min_train)
    ho0 = n_rows - H
    blocks = [(p, min(p + reselect_every, H)) for p in range(0, H, reselect_every)]
    return ho0, blocks
