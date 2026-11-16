import json
import numpy as np
import pandas as pd
import pytest

from iba.eval.bootstrap import block_indices, default_block, paired_block_test
from iba.eval.mcs import model_confidence_set, spa_test
from iba.eval.registry import TrialRegistry, config_hash


def test_block_indices_are_contiguous_blocks():
    rng = np.random.default_rng(0)
    idx = block_indices(100, 5, rng)
    assert len(idx) == 100 and set(idx) <= set(range(100))
    for s in range(0, 100, 5):
        blk = idx[s:s + 5]
        assert np.all(np.diff(blk) % 100 == 1)


def test_paired_block_test_detects_a_shift_and_not_noise():
    rng = np.random.default_rng(1)
    T, K = 96, 11
    # size: over 40 independent noise panels the 5 % test rejects in roughly 5 % of them
    rej = [paired_block_test(rng.normal(size=(T, K)), block=6, reps=300, seed=s).p_value < 0.05 for s in range(40)]
    assert 0 <= sum(rej) <= 8
    # power: a shift of one standard deviation is always found
    r1 = paired_block_test(rng.normal(size=(T, K)) + 1.0, block=6, reps=300, seed=2)
    assert r1.ci_low > 0 and r1.p_value < 0.01
    assert default_block(6, 96) == 6 and default_block(1, 416) == 7


def test_mcs_keeps_the_good_models_and_spa_rejects_a_clear_winner():
    rng = np.random.default_rng(3)
    T = 300
    base = rng.normal(size=T) ** 2
    L = pd.DataFrame({"good_a": base, "good_b": base + rng.normal(0, 0.05, T),
                      "bad": base + 0.8 + rng.normal(0, 0.05, T)})
    out = model_confidence_set(L, size=0.1, block=4, reps=300)
    assert out.loc["bad", "in_mcs"] == False and out.loc["good_a", "in_mcs"]  # noqa: E712
    spa = spa_test(L["bad"], L[["good_a", "good_b"]], block=4, reps=300)
    assert spa["consistent"] < 0.05
    spa2 = spa_test(L["good_a"], L[["bad"]], block=4, reps=300)
    assert spa2["consistent"] > 0.2


def test_registry_appends_and_hashes(tmp_path):
    reg = TrialRegistry(str(tmp_path / "registry" / "trials.jsonl"))
    cfg = {"reducer": "iba", "tnorm": "product", "h": 6}
    reg.record("SPEC-TEST", "development", cfg, {"mse": 0.1})
    reg.record("SPEC-TEST", "development", dict(reversed(list(cfg.items()))), {"mse": 0.2})
    reg.record("SPEC-TEST", "smoke", {"x": 1}, {})
    assert reg.count("SPEC-TEST") == 3 and reg.count("SPEC-TEST", "development") == 2
    assert reg.distinct_configs("SPEC-TEST") == 2 and config_hash(cfg) == reg.rows()[1]["config_hash"]
    with pytest.raises(ValueError):
        reg.record("SPEC-TEST", "test", {}, {})
    assert all(json.loads(l) for l in open(reg.path))
