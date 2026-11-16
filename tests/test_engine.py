"""End-to-end properties of the walk-forward engine on synthetic panels.

No look-ahead: two panels identical up to a cut-off date and different afterwards must give
bit-identical forecasts at every origin up to the cut-off, for every method (searches included)
and every target type; and later forecasts must differ (the test has power)."""
import numpy as np
import pandas as pd
import pytest

from iba.data.panel import Panel
from iba.models.benchmarks import garch_weekly_from_daily
from iba.protocol.dataset import Task
from iba.protocol.information_rule import FoldGeometry
from iba.protocol.walkforward import ProtocolConfig, evaluate, run_cell

CFG = ProtocolConfig(24, 12, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=120, colony=8)
METHODS = ["raw", "lasso", "gpca", "iba_e1", "iba_x", "iba_xlo", "iba_a", "iba_b", "iba_c", "iba_d"]


def panel(n=420, seed=0, perturb_after=None):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2012-01-06", periods=n, freq="W-FRI")
    f = pd.DataFrame(rng.normal(size=(n, 8)), index=idx, columns=["a1", "a2", "a3", "a4", "b1", "b2", "b3", "b4"])
    vol = np.exp(0.3 * np.cumsum(rng.normal(0, 0.05, n))) * 0.02
    r = pd.DataFrame({"T1": 0.001 + 0.004 * f["a1"].shift(1).fillna(0).values + rng.normal(0, 1, n) * vol}, index=idx)
    rv = pd.DataFrame({"T1": (vol * (1 + 0.2 * np.abs(rng.normal(size=n)))) ** 2}, index=idx)
    if perturb_after is not None:                       # every draw above is shared by both panels
        late = idx > perturb_after
        r2 = np.random.default_rng(seed + 1)
        f.loc[late] = r2.normal(size=(late.sum(), 8)) * 2
        r.loc[late, "T1"] = r2.normal(0, 0.05, late.sum())
        rv.loc[late, "T1"] = rv.loc[late, "T1"].values * np.exp(r2.normal(0, 1, late.sum()))
    formulas = {"groups": {"A": [["a1", "high"], ["a2", "not_high"]], "B": [["b1", "not_high"]], "ENDG": [["__target__", "high"]]}}
    return Panel("weekly", f, {"A": ["a1", "a2", "a3", "a4"], "B": ["b1", "b2", "b3", "b4"]}, r, rv, None, formulas, 52)


@pytest.mark.parametrize("task", [Task("T1", "return", 4), Task("T1", "logrv", 1), Task("T1", "tail_loss", 4, 0.2),
                                  Task("T1", "tail_gain", 13, 0.2)])
def test_no_forecast_depends_on_data_after_its_origin(task):
    pa, _ = run_cell(panel(), task, METHODS, cfg=CFG, seeds=(0,), with_garch=False)
    cut = pa["date"].iloc[len(pa) // 2 - 1]              # the middle of the out-of-sample span
    pb, _ = run_cell(panel(perturb_after=cut), task, METHODS, cfg=CFG, seeds=(0,), with_garch=False)
    cols = [c for c in pa.columns if c not in ("date", "y", "y_eval", "block")]       # forecasts and thresholds
    early = (pa["date"] <= cut).values
    assert early.sum() >= 5 and (~early).sum() >= 5 and len(cols) >= 20
    assert np.isfinite(pa[cols].values).all()
    np.testing.assert_array_equal(pa.loc[early, cols].values, pb.loc[early, cols].values)
    assert not np.allclose(pa.loc[~early, cols].values, pb.loc[~early, cols].values)


def test_runs_are_reproducible_and_evaluation_covers_every_configuration():
    p = panel()
    task = Task("T1", "return", 4)
    a, meta = run_cell(p, task, ["gpca", "iba_e1", "iba_a", "iba_b", "iba_c"], cfg=CFG, seeds=(0, 1), with_garch=False)
    b, _ = run_cell(p, task, ["gpca", "iba_e1", "iba_a", "iba_b", "iba_c"], cfg=CFG, seeds=(0, 1), with_garch=False)
    pd.testing.assert_frame_equal(a, b)
    ev = evaluate(a, task, 52)
    assert {"gpca|lin", "gpca|gbt", "iba_e1|lin", "iba_a.s0|lin", "iba_a.s0|gbt", "iba_a.s1|lin", "iba_b.s0", "iba_c.s1",
            "bench|mean", "bench|tsmom"} <= set(ev["config"])
    assert "iba_a.s1|gbt" not in set(ev["config"])       # trees only for the first seed
    m = meta["blocks"][0]["methods"]["iba_a.s0"]
    assert m["n_evals"] <= CFG.search_budget and {"inner_best", "outer_best", "optimism", "accepted"} <= set(m)


def test_garch_path_uses_only_days_up_to_the_origin():
    rng = np.random.default_rng(0)
    days = pd.bdate_range("2012-01-02", periods=900)
    d = pd.Series(rng.normal(0, 0.01, len(days)), index=days)
    origins = list(pd.date_range("2014-06-06", periods=12, freq="W-FRI"))
    a = garch_weekly_from_daily(d, origins, 4, 4, cache=False)
    d2 = d.copy(); d2[d2.index > origins[5]] = rng.normal(0, 0.05, (d2.index > origins[5]).sum())
    b = garch_weekly_from_daily(d2, origins, 4, 4, cache=False)
    np.testing.assert_array_equal(a[:6], b[:6])
    assert not np.allclose(a[6:], b[6:])
