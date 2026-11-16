"""Model Confidence Set and Superior Predictive Ability tests (Hansen; Hansen-Lunde-Nason),
via the `arch` package, on a (T dates x K configurations) loss matrix with a block bootstrap.

Use: losses averaged across the series of a panel at each date (so cross-series dependence is
absorbed into the date series), block size >= the label horizon.
"""
from __future__ import annotations

from typing import Dict, Sequence

import numpy as np
import pandas as pd


def model_confidence_set(losses: pd.DataFrame, size: float = 0.10, block: int = 6, reps: int = 2000,
                         seed: int = 0, method: str = "R") -> pd.DataFrame:
    from arch.bootstrap import MCS
    L = losses.dropna()
    mcs = MCS(L, size=size, reps=reps, block_size=block, method=method, bootstrap="moving block", seed=seed)
    mcs.compute()
    out = mcs.pvalues.copy()
    out.columns = ["mcs_pvalue"]
    out["in_mcs"] = out["mcs_pvalue"] >= size
    out["mean_loss"] = L.mean().reindex(out.index)
    return out.sort_values("mean_loss")


def spa_test(benchmark: pd.Series, models: pd.DataFrame, block: int = 6, reps: int = 2000,
             seed: int = 0) -> Dict[str, float]:
    """H0: no model in ``models`` beats ``benchmark`` (loss). Returns the lower/consistent/upper
    p-values of the stepwise SPA test; the 'consistent' one is the headline."""
    from arch.bootstrap import SPA
    ok = benchmark.notna() & models.notna().all(axis=1)
    spa = SPA(benchmark[ok].values, models[ok].values, block_size=block, reps=reps,
              bootstrap="moving block", seed=seed)
    spa.compute()
    pv = spa.pvalues
    return {"lower": float(pv["lower"]), "consistent": float(pv["consistent"]), "upper": float(pv["upper"]),
            "n": int(ok.sum()), "k": int(models.shape[1])}
