import numpy as np

from iba.eval.dm import clark_west, dm_test, holm


def test_dm_detects_a_real_difference_and_not_a_null():
    rng = np.random.default_rng(0)
    e = rng.normal(size=400)
    assert dm_test(e ** 2, e ** 2, h=4)["p"] == 1.0
    better, worse = (0.5 * e) ** 2, (1.5 * e) ** 2
    r = dm_test(better, worse, h=4)
    assert r["stat"] < 0 and r["p"] < 0.01
    null = [dm_test(rng.normal(size=300) ** 2, rng.normal(size=300) ** 2, h=1)["p"] < 0.05 for _ in range(400)]
    assert 0.01 < np.mean(null) < 0.10


def test_clark_west_rewards_signal_and_ignores_noise():
    rng = np.random.default_rng(1)
    x = rng.normal(size=600)
    y = 0.3 * x + rng.normal(size=600)
    zero = np.zeros(600)
    assert clark_west(y, zero, 0.3 * x, h=1)["p"] < 0.001
    rej = []
    for _ in range(400):
        yy, noise = rng.normal(size=300), 0.1 * rng.normal(size=300)
        rej.append(clark_west(yy, np.zeros(300), noise, h=1)["p"] < 0.05)
    assert np.mean(rej) < 0.12


def test_holm_is_monotone_and_bounded():
    p = np.array([0.001, 0.04, 0.03, 0.5])
    a = holm(p)
    assert np.allclose(a, [0.004, 0.09, 0.09, 0.5]) and (a >= p).all() and (a <= 1).all()
