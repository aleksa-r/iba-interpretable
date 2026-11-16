import numpy as np
import pytest

from iba.models.estimators import (GBTEstimator, LinearEstimator, XGBEstimator, make_estimator, logistic_fit, logistic_predict, loss,
                                       ridge_fit, ridge_predict)


def _data(n=300, p=6, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    y = X[:, 0] * 0.5 - X[:, 1] * 0.3 + rng.normal(0, 0.5, n)
    return X, y


def test_ridge_equals_sklearn_pipeline():
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    X, y = _data()
    for alpha in (0.01, 1.0, 100.0):
        sc = StandardScaler().fit(X[:200])
        ref = Ridge(alpha=alpha).fit(sc.transform(X[:200]), y[:200]).predict(sc.transform(X[200:]))
        np.testing.assert_allclose(ridge_predict(ridge_fit(X[:200], y[:200], alpha), X[200:]), ref, atol=1e-10)


def test_logistic_equals_sklearn():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    X, y = _data()
    yb = (y > np.quantile(y, 0.8)).astype(float)
    for C in (0.01, 1.0, 100.0):
        sc = StandardScaler().fit(X[:200])
        ref = LogisticRegression(C=C, tol=1e-10, max_iter=2000).fit(sc.transform(X[:200]), yb[:200]).predict_proba(sc.transform(X[200:]))[:, 1]
        np.testing.assert_allclose(logistic_predict(logistic_fit(X[:200], yb[:200], C), X[200:]), ref, atol=2e-5)


def test_logistic_handles_one_class_and_rare_events():
    X, _ = _data(100)
    m = logistic_fit(X, np.zeros(100), 1.0)
    assert np.all(logistic_predict(m, X) < 0.01)
    y = np.zeros(100); y[:3] = 1
    p = logistic_predict(logistic_fit(X, y, 1.0), X)
    assert np.all((p > 0) & (p < 1)) and abs(p.mean() - 0.03) < 0.01


def test_gbt_is_deterministic_and_estimators_share_the_interface():
    X, y = _data()
    yb = (y > 0).astype(float)
    for task, yy in (("reg", y), ("clf", yb)):
        for est in (LinearEstimator(task), GBTEstimator(task), XGBEstimator(task)):
            a = est.predict(est.fit(X[:200], yy[:200], est.grid[0]), X[200:])
            b = est.predict(est.fit(X[:200], yy[:200], est.grid[0]), X[200:])
            np.testing.assert_array_equal(a, b)
            assert np.isfinite(loss(task, yy[200:], a))
            if task == "clf":
                assert a.min() >= 0 and a.max() <= 1
    assert len(LinearEstimator("reg").grid) == 8 and len(GBTEstimator("reg").grid) == 4


def test_xgb_uses_no_sampling_and_handles_one_class():
    est = make_estimator("xgb", "clf")
    assert isinstance(est, XGBEstimator) and len(est.grid) == 4
    assert all(est.base[k] == 1.0 for k in ("subsample", "colsample_bytree", "colsample_bylevel", "colsample_bynode")) and est.base["n_jobs"] == 1
    X, _ = _data()
    p = est.predict(est.fit(X[:50], np.zeros(50), est.grid[0]), X[50:60])
    np.testing.assert_array_equal(p, np.zeros(10))
