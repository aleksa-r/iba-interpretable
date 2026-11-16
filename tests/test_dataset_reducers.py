import numpy as np
import pandas as pd
import pytest

from iba.data.panel import Panel
from iba.models.reducers import IBAReducer, make_reducer, prior_formula
from iba.protocol.dataset import LabelSpec, Task, build_dataset


def synthetic_panel(n=400, seed=0, frequency="weekly"):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-08", periods=n, freq="W-FRI") if frequency == "weekly" else pd.date_range("2000-01-31", periods=n, freq="ME")
    f = pd.DataFrame(rng.normal(size=(n, 8)), index=idx, columns=["a1", "a2", "a3", "a4", "b1", "b2", "b3", "b4"])
    vol = np.exp(0.3 * np.cumsum(rng.normal(0, 0.05, n))) * 0.02
    r = pd.DataFrame({"T1": 0.002 + 0.01 * f["a1"].shift(1).fillna(0).values * 0.2 + rng.normal(0, 1, n) * vol,
                      "T2": rng.normal(0.001, 0.02, n)}, index=idx)
    rv = pd.DataFrame({c: (vol * (1 + 0.2 * np.abs(rng.normal(size=n)))) ** 2 for c in r}, index=idx) if frequency == "weekly" else None
    formulas = {"groups": {"A": [["a1", "high"], ["a2", "not_high"]], "B": [["b1", "not_high"]], "ENDG": [["__target__", "high"]]}}
    return Panel(frequency, f, {"A": ["a1", "a2", "a3", "a4"], "B": ["b1", "b2", "b3", "b4"]}, r, rv, None, formulas, 52 if frequency == "weekly" else 12)


def test_labels_look_forward_exactly_h_periods():
    p = synthetic_panel()
    ds = build_dataset(p, Task("T1", "return", 4))
    t = 100; k = p.returns.index.get_loc(ds.dates[t])
    assert ds.y[t] == pytest.approx(np.prod(1 + p.returns["T1"].values[k + 1:k + 5]) - 1)
    dv = build_dataset(p, Task("T1", "logrv", 4))
    k = p.rv.index.get_loc(dv.dates[t])
    assert dv.y[t] == pytest.approx(np.log(p.rv["T1"].values[k + 1:k + 5].sum()))
    assert dv.har[t, 1] == pytest.approx(np.log(p.rv["T1"].values[k - 3:k + 1].sum()))
    assert dv.group_cols["ENDG"] == ["T1_26m_zs", "T1_52m_zs"] and ds.group_cols["ENDG"][0] == "T1_raw"


def test_label_spec_uses_only_the_rows_it_is_given():
    p = synthetic_panel()
    for task in (Task("T1", "logrv", 1), Task("T1", "tail_loss", 4, 0.10), Task("T1", "tail_gain", 4, 0.20)):
        ds = build_dataset(p, task); L = LabelSpec(ds)
        rows = np.arange(150)
        s1 = L.fit(rows)
        y_before = L.train_y(s1, rows).copy()
        ds.y[150:] += 5.0                                   # change everything after the training rows
        s2 = L.fit(rows)
        np.testing.assert_allclose(np.atleast_1d(s1), np.atleast_1d(s2))
        np.testing.assert_allclose(L.train_y(s2, rows), y_before)
    ds = build_dataset(p, Task("T1", "tail_loss", 4, 0.10)); L = LabelSpec(ds); s = L.fit(np.arange(200))
    assert L.train_y(s, np.arange(200)).mean() == pytest.approx(0.10, abs=0.01)


def test_prior_formula_and_iba_reducer_product():
    p = synthetic_panel()
    ds = build_dataset(p, Task("T1", "return", 4))
    f = prior_formula(p.formulas, "T1", ds.group_cols, ds.windows)
    assert f == {"A": (["a1_52m_zs"], ["a2_52m_zs"]), "B": ([], ["b1_52m_zs"]), "ENDG": (["T1_52m_zs"], [])}
    red = IBAReducer(ds.group_cols, f).fit(ds.X.iloc[:200])
    Z = red.transform(ds.X)
    assert Z.shape == (len(ds), 3) and Z.min() > 0 and Z.max() < 1
    cols = ds.group_cols["A"]; V = ds.X[cols].values
    lo, hi = V[:200].min(axis=0), V[:200].max(axis=0)
    S = np.clip(0.01 + 0.98 * (V - lo) / (hi - lo), 0.01, 0.99)
    np.testing.assert_allclose(Z[:, 0], S[:, cols.index("a1_52m_zs")] * (1 - S[:, cols.index("a2_52m_zs")]), atol=1e-12)


@pytest.mark.parametrize("name", ["raw", "pca", "gpca", "lasso", "iba"])
def test_reducers_are_point_in_time(name):
    p = synthetic_panel()
    ds = build_dataset(p, Task("T1", "return", 4))
    f = prior_formula(p.formulas, "T1", ds.group_cols, ds.windows)
    r1 = make_reducer(name, ds.group_cols, 4, f).fit(ds.X.iloc[:200], ds.y[:200])
    X2 = ds.X.copy(); X2.iloc[200:] = X2.iloc[200:] * 3 + 1
    r2 = make_reducer(name, ds.group_cols, 4, f).fit(X2.iloc[:200], ds.y[:200])
    np.testing.assert_allclose(r1.transform(ds.X.iloc[:200]), r2.transform(X2.iloc[:200]), atol=1e-9)


def test_kernel_pca_and_autoencoder_reducers_fit_on_the_rows_given_only():
    import numpy as np, pandas as pd
    from iba.models.reducers import AutoencoderReducer, KernelPCAReducer, make_reducer
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.normal(size=(300, 12)))
    X2 = X.copy(); X2.iloc[200:] = rng.normal(size=(100, 12)) * 5            # later rows changed
    for name, cls in (("kpca", KernelPCAReducer), ("ae", AutoencoderReducer)):
        r = make_reducer(name, {}, 1).fit(X.iloc[:200]); r2 = make_reducer(name, {}, 1).fit(X2.iloc[:200])
        assert isinstance(r, cls) and r.transform(X).shape == (300, 6) and np.isfinite(r.transform(X)).all()
        np.testing.assert_array_equal(r.transform(X.iloc[:200]), r2.transform(X2.iloc[:200]))       # no look-ahead, deterministic
        assert r.info()
