"""Tasks and datasets: one (target, target type, horizon[, quantile]) -> aligned label and features.

Row t holds the features observed at the end of period t and the label realised over t+1..t+h:
  return      compounded return over the next h periods
  logrv       log of the realised variance summed over the next h weeks
  tail_loss / tail_gain   the raw label is the h-period return; the 0/1 event is derived at every
              fit from a threshold computed on that fit's admissible rows (LabelSpec)
Feature naming follows the earlier code base (`<code>_<w>m_zs`, `<target>_raw`) so that formula
files and old outputs line up.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

KINDS = ("return", "logrv", "tail_loss", "tail_gain")
MONTHLY_WINDOWS = {1: [6, 12], 3: [6, 12], 6: [12, 18], 12: [12, 24]}
WEEKLY_WINDOWS = [26, 52]
HAR_LAGS = (1, 4, 13)
MONTHLY_VOL_LAGS = (3, 6, 12)


@dataclass(frozen=True)
class Task:
    target: str
    kind: str
    h: int
    q: Optional[float] = None
    frequency: str = "weekly"

    def __post_init__(self):
        assert self.kind in KINDS and self.frequency in ("weekly", "monthly")
        assert (self.q is not None) == self.kind.startswith("tail")

    @property
    def est_task(self) -> str:
        return "clf" if self.kind.startswith("tail") else "reg"

    @property
    def name(self) -> str:
        q = "" if self.q is None else f"_q{int(round(self.q * 100)):02d}"
        return f"{self.kind}{q}_h{self.h}"


def zscore(s: pd.Series, w: int) -> pd.Series:
    """Trailing rolling z-score (min_periods=1, population std; zero std -> NaN), as in the earlier code base."""
    mu = s.rolling(window=w, min_periods=1).mean()
    sd = s.rolling(window=w, min_periods=1).std(ddof=0)
    return (s - mu) / sd.replace(0, np.nan)


@dataclass
class Dataset:
    task: Task
    dates: pd.DatetimeIndex
    y: np.ndarray                      # raw label (return or log RV), row t -> periods t+1..t+h
    X: pd.DataFrame                    # features, same rows
    group_cols: Dict[str, List[str]]   # group -> feature columns (ENDG first)
    windows: List[int]
    har: Optional[np.ndarray]          # log RV over the past 1/4/13 weeks (logrv only)
    volterms: Optional[np.ndarray]     # volatility terms for the tail benchmarks
    r: np.ndarray                      # the target's own period return at row t
    trail: np.ndarray                  # trailing momentum return (52 w / 12 m) at row t

    def __len__(self):
        return len(self.y)


def build_dataset(panel, task: Task, windows: Optional[List[int]] = None) -> Dataset:
    h, tgt = task.h, task.target
    windows = windows or (WEEKLY_WINDOWS if task.frequency == "weekly" else MONTHLY_WINDOWS[h])
    r = panel.returns[tgt].astype(float)
    har = vol = None
    if task.kind == "logrv":
        if panel.rv is None:
            raise ValueError("volatility targets need daily data")
        v = panel.rv[tgt].astype(float)
        y = np.log(v.rolling(h, min_periods=h).sum().shift(-h))
        lv = np.log(v)
        endg = pd.DataFrame({f"{tgt}_{w}m_zs": zscore(lv, w) for w in windows})
        har = pd.DataFrame({f"har_{k}": np.log(v.rolling(k, min_periods=k).sum()) for k in HAR_LAGS})
    else:
        y = (np.exp(np.log1p(r.clip(lower=-1 + 1e-9)).rolling(h, min_periods=h).sum()) - 1.0).shift(-h)
        endg = pd.DataFrame({f"{tgt}_raw": r, **{f"{tgt}_{w}m_zs": zscore(r, w) for w in windows}})
    if task.kind.startswith("tail"):
        if panel.rv is not None:
            v = panel.rv[tgt].astype(float)
            vol = pd.DataFrame({f"vol_{k}": np.log(v.rolling(k, min_periods=k).sum()) for k in HAR_LAGS})
        else:
            vol = pd.DataFrame({f"vol_{k}": np.log((r ** 2).rolling(k, min_periods=k).sum()) for k in MONTHLY_VOL_LAGS})
    frames = {"ENDG": endg}
    for g, codes in panel.groups_for(tgt).items():
        frames[g] = pd.DataFrame({f"{c}_{w}m_zs": zscore(panel.factors[c].astype(float), w) for c in codes for w in windows})
    X = pd.concat(frames.values(), axis=1)
    ok = np.isfinite(y.values) & np.isfinite(X.values).all(axis=1)
    for extra in (har, vol):
        if extra is not None:
            ok &= np.isfinite(extra.values).all(axis=1)
    pos = np.flatnonzero(ok)
    if len(pos) == 0 or not np.array_equal(pos, np.arange(pos[0], pos[-1] + 1)):
        raise ValueError(f"[{tgt} {task.name}] valid rows are not one contiguous block")
    L = 52 if task.frequency == "weekly" else 12
    trail = np.exp(np.log1p(r.clip(lower=-1 + 1e-9)).rolling(L, min_periods=L).sum()) - 1.0
    sl = slice(pos[0], pos[-1] + 1)
    return Dataset(task=task, dates=X.index[sl], y=y.values[sl].astype(np.float64), X=X.iloc[sl].astype(np.float64),
                   group_cols={g: list(f.columns) for g, f in frames.items()}, windows=list(windows),
                   har=None if har is None else har.values[sl], volterms=None if vol is None else vol.values[sl],
                   r=r.values[sl], trail=trail.values[sl])


class LabelSpec:
    """Turns the raw label into what an estimator is trained on, using only the rows it is given.

      return   identity
      logrv    two-stage: HAR fitted on the rows; the estimator gets the HAR residual; forecast = HAR + residual
      tail_*   threshold = quantile of the rows' returns; the estimator gets the 0/1 event
    ``fit(rows)`` returns the state; the other methods take that state, so a fold, a block and a refit
    each carry their own (the information rule lives in the choice of ``rows``)."""

    def __init__(self, ds: Dataset):
        self.ds, self.kind, self.q = ds, ds.task.kind, ds.task.q

    def fit(self, rows: np.ndarray):
        y = self.ds.y[rows]
        if self.kind == "logrv":
            A = np.column_stack([np.ones(len(rows)), self.ds.har[rows]])
            beta, *_ = np.linalg.lstsq(A, y, rcond=None)
            return beta
        if self.kind == "tail_loss":
            return float(np.quantile(y, self.q))
        if self.kind == "tail_gain":
            return float(np.quantile(y, 1.0 - self.q))
        return None

    def base(self, state, rows: np.ndarray) -> np.ndarray:
        if self.kind == "logrv":
            return state[0] + self.ds.har[rows] @ state[1:]
        return np.zeros(len(rows))

    def train_y(self, state, rows: np.ndarray) -> np.ndarray:
        y = self.ds.y[rows]
        if self.kind == "logrv":
            return y - self.base(state, rows)
        if self.kind == "tail_loss":
            return (y < state).astype(np.float64)
        if self.kind == "tail_gain":
            return (y > state).astype(np.float64)
        return y

    def eval_y(self, state, rows: np.ndarray) -> np.ndarray:
        """The quantity a forecast made with this state is scored against."""
        return self.train_y(state, rows) if self.kind.startswith("tail") else self.ds.y[rows]

    def finalize(self, state, rows: np.ndarray, raw_pred: np.ndarray) -> np.ndarray:
        if self.kind == "logrv":
            return self.base(state, rows) + raw_pred
        if self.kind.startswith("tail"):
            return np.clip(raw_pred, 0.0, 1.0)
        return raw_pred
