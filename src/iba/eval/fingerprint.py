"""Fingerprint cell: a fixed synthetic cell whose forecast hash must be identical on every machine
and at every run (verification finding: results that depend on the machine are not results).
Uses only platform-independent pieces: numpy's Generator, ridge/logistic in numpy, the ABC with a
seeded Generator, and LightGBM in deterministic mode on raw and IBA features."""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd


def _panel(n: int = 420, seed: int = 20261113):
    from ..data.panel import Panel
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2012-01-06", periods=n, freq="W-FRI")
    f = pd.DataFrame(rng.normal(size=(n, 8)), index=idx, columns=["a1", "a2", "a3", "a4", "b1", "b2", "b3", "b4"])
    vol = np.exp(0.3 * np.cumsum(rng.normal(0, 0.05, n))) * 0.02
    r = pd.DataFrame({"T1": 0.001 + 0.004 * f["a1"].shift(1).fillna(0).values + rng.normal(0, 1, n) * vol}, index=idx)
    rv = pd.DataFrame({"T1": (vol * (1 + 0.2 * np.abs(rng.normal(size=n)))) ** 2}, index=idx)
    formulas = {"groups": {"A": [["a1", "high"], ["a2", "not_high"]], "B": [["b1", "not_high"]], "ENDG": [["__target__", "high"]]}}
    return Panel("weekly", f, {"A": ["a1", "a2", "a3", "a4"], "B": ["b1", "b2", "b3", "b4"]}, r, rv, None, formulas, 52)


def fingerprint() -> str:
    from ..protocol.dataset import Task
    from ..protocol.information_rule import FoldGeometry
    from ..protocol.walkforward import ProtocolConfig, run_cell
    cfg = ProtocolConfig(24, 12, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=150, colony=8)
    h = hashlib.sha256()
    for task in (Task("T1", "return", 4), Task("T1", "logrv", 1), Task("T1", "tail_loss", 4, 0.2)):
        pred, _ = run_cell(_panel(), task, ["raw", "iba_e1", "iba_a", "iba_b", "iba_c"], cfg=cfg, seeds=(0,), with_garch=False)
        cols = sorted(c for c in pred.columns if c not in ("date", "block"))
        h.update(np.round(pred[cols].values.astype(np.float64), 7).tobytes())
    return h.hexdigest()[:24]


def fingerprint_xgb() -> str:
    """Hash of the XGBoost forecasts (no sampling) of the fingerprint cell. Not part of ``fingerprint``:
    XGBoost is checked separately, on the machine a run is made on (SPEC-2026-11-14-wrapup, section 4)."""
    from ..protocol.dataset import Task
    from ..protocol.information_rule import FoldGeometry
    from ..protocol.walkforward import ProtocolConfig, run_cell
    cfg = ProtocolConfig(24, 12, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=150, colony=8)
    h = hashlib.sha256()
    for task in (Task("T1", "return", 4), Task("T1", "logrv", 1), Task("T1", "tail_loss", 4, 0.2)):
        pred, _ = run_cell(_panel(), task, ["raw", "iba_e1"], estimators=("xgb",), cfg=cfg, seeds=(0,), with_garch=False)
        cols = sorted(c for c in pred.columns if c.endswith("|xgb"))
        h.update(np.round(pred[cols].values.astype(np.float64), 6).tobytes())
    return h.hexdigest()[:24]


def fingerprint_benchmarks() -> str:
    """Hash of the kernel-PCA and autoencoder forecasts (linear model) of the fingerprint cell. Like
    XGBoost these are outside ``fingerprint`` and are checked on the machine a run is made on
    (SPEC-2026-11-14-benchmarks-kpca-ae)."""
    from ..protocol.dataset import Task
    from ..protocol.information_rule import FoldGeometry
    from ..protocol.walkforward import ProtocolConfig, run_cell
    cfg = ProtocolConfig(24, 12, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=150, colony=8)
    h = hashlib.sha256()
    for task in (Task("T1", "return", 4), Task("T1", "logrv", 1), Task("T1", "tail_loss", 4, 0.2)):
        pred, _ = run_cell(_panel(), task, ["kpca", "ae"], estimators=("lin",), cfg=cfg, seeds=(0,), with_garch=False)
        h.update(np.round(pred[["ae|lin", "kpca|lin"]].values.astype(np.float64), 6).tobytes())
    return h.hexdigest()[:24]
