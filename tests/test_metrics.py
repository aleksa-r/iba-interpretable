import numpy as np
import pytest

from iba.eval.metrics import return_metrics, tail_metrics, vol_metrics


def test_return_metrics_gate_by_phase():
    y = np.array([0.02, -0.01, 0.03, -0.04, 0.01, 0.02, -0.02, 0.05])
    m = return_metrics(y, np.ones(8), np.full(8, y.mean()), h=2, ppy=12)       # always long
    assert m["sign_acc"] == m["always_long_acc"] == 5 / 8 and m["phases"] == 2
    assert m["gate_ann"] == pytest.approx(m["bh_ann"]) and m["gate_phases_won"] == 0
    perfect = return_metrics(y, y, np.full(8, y.mean()), h=2, ppy=12)
    assert perfect["sign_acc"] == 1.0 and perfect["gate_phases_won"] == 2 and perfect["r2_vs_mean"] == pytest.approx(1.0)


def test_vol_metrics_qlike_zero_for_perfect_variance_forecast():
    y = np.log(np.array([1e-4, 4e-4, 2e-4]))
    m = vol_metrics(y, y, np.exp(y), y + 0.1)
    assert m["mse_log"] == 0 and m["qlike"] == pytest.approx(0.0) and m["r2_vs_har"] == pytest.approx(1.0)


def test_tail_metrics_base_rate_has_zero_skill_and_calibration():
    rng = np.random.default_rng(0)
    e = (rng.uniform(size=2000) < 0.1).astype(float)
    base = np.full(2000, 0.1)
    m = tail_metrics(e, base, base)
    assert m["bss"] == pytest.approx(0.0) and m["ece"] < 0.05 and m["auc"] == pytest.approx(0.5)
    good = tail_metrics(e, np.where(e == 1, 0.8, 0.02), base)
    assert good["bss"] > 0.7 and good["auc"] == 1.0
