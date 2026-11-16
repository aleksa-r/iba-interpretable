import numpy as np
from scipy.stats import norm

from iba.eval import finmetrics as F


def test_var_es_normal_and_scores_prefer_the_true_variance():
    rng = np.random.default_rng(0)
    s = 0.02 * np.exp(0.5 * rng.normal(size=20000))
    r = rng.normal(0, s)
    q, e = F.var_es_normal(s ** 2, 0.05)
    assert abs((r < q).mean() - 0.05) < 0.005 and abs(r[r < q].mean() / e[r < q].mean() - 1) < 0.05
    np.testing.assert_allclose(q[:3] / s[:3], norm.ppf(0.05))
    for wrong in (0.5, 2.0):
        q2, e2 = F.var_es_normal((wrong * s) ** 2, 0.05)
        assert F.tick_loss(r, q, 0.05).mean() < F.tick_loss(r, q2, 0.05).mean()
        assert F.fz0_loss(r, q, e, 0.05).mean() < F.fz0_loss(r, q2, e2, 0.05).mean()
    flat = np.full(len(r), (s ** 2).mean())                               # ignoring the changes in variance scores worse
    assert F.tick_loss(r, q, 0.05).mean() < F.tick_loss(r, F.var_es_normal(flat, 0.05)[0], 0.05).mean()


def test_coverage_tests():
    rng = np.random.default_rng(1)
    ok = rng.uniform(size=5000) < 0.05
    assert F.kupiec(ok, 0.05)["p"] > 0.05 and F.christoffersen(ok)["p"] > 0.01
    assert F.kupiec(rng.uniform(size=5000) < 0.10, 0.05)["p"] < 1e-6
    k = F.kupiec(np.zeros(200, bool), 0.05)
    assert k["violations"] == 0 and k["p"] < 0.001
    clustered = np.zeros(5000, bool); clustered[np.arange(0, 5000, 100)[:, None] + np.arange(5)] = True      # 5 % in runs of five
    assert F.kupiec(clustered, 0.05)["p"] > 0.5 and F.christoffersen(clustered)["p"] < 1e-6


def test_risk_measures_of_a_return_series():
    assert abs(F.max_drawdown([0.1, -0.5, 0.2, -0.1]) - 0.5) < 1e-12 and abs(F.max_drawdown([0.1, -0.5, 0.2, -0.5]) - 0.7) < 1e-12 and F.max_drawdown([0.01, 0.02]) == 0.0
    r = np.r_[np.full(95, 0.01), np.full(5, -0.10)]
    h = F.hist_var_cvar(r, 0.05)
    assert h["cvar"] == 0.10 and -0.01 <= h["var"] <= 0.10


def test_confusion_and_brier_decomposition():
    e = np.array([1, 1, 0, 0, 0, 0, 1, 0], bool); s = np.array([1, 0, 1, 0, 0, 0, 1, 0], bool)
    c = F.confusion(e, s)
    assert (c["tp"], c["fp"], c["fn"], c["tn"]) == (2, 1, 1, 4) and abs(c["precision"] - 2 / 3) < 1e-12 and abs(c["recall"] - 2 / 3) < 1e-12
    assert abs(c["specificity"] - 0.8) < 1e-12 and c["signal_rate"] == 3 / 8 and 0 < c["mcc"] < 1
    never = F.confusion(e, np.zeros(8, bool))
    assert never["signal_rate"] == 0 and np.isnan(never["precision"]) and never["recall"] == 0 and never["mcc"] == 0
    rng = np.random.default_rng(2)
    p = rng.uniform(0.02, 0.4, 20000); ev = rng.uniform(size=20000) < p
    d = F.brier_decomposition(ev, p, bins=20)
    assert d["reliability"] < 2e-4 and d["resolution"] > 0.005 and abs(d["brier"] - (d["reliability"] - d["resolution"] + d["uncertainty"])) < 2e-3
    const = F.brier_decomposition(ev, np.full(20000, ev.mean()))
    assert const["resolution"] < 1e-12 and const["sharpness"] == 0 and const["brier"] > d["brier"]


def test_drawdown_state_uses_the_past_only():
    import importlib.util, os
    import pandas as pd
    spec = importlib.util.spec_from_file_location("em", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "make_extra_metrics.py"))
    em = importlib.util.module_from_spec(spec); spec.loader.exec_module(em)
    idx = pd.date_range("2020-01-03", periods=8, freq="W-FRI")
    r = pd.Series([0.05, -0.08, -0.05, 0.02, 0.20, -0.02, -0.12, 0.01], index=idx)      # wealth: 1.05, .966, .918, .936, 1.123, 1.101, .969, .978
    flags = em.drawdown_state(r, idx)
    assert flags.tolist() == [False, False, True, True, False, False, True, True]
    later = r.copy(); later.iloc[5:] = 0.5                                              # what happens later does not change earlier flags
    assert em.drawdown_state(later, idx)[:5].tolist() == flags[:5].tolist()
