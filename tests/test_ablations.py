import numpy as np

from iba.explain.ablate import one_literal, variant_forecasts
from iba.protocol.dataset import Task
from iba.protocol.walkforward import run_cell

from .test_pooled import CFG, multi_panel


def test_the_unchanged_variant_is_the_engine_and_each_variant_changes_one_thing():
    p = multi_panel(strength=0.02)
    assert one_literal({"A": (["a1"], ["a2"]), "B": ([], ["b1"])}, {"A": ["a2", "a1"], "B": ["b1"]}) == {"A": ([], ["a2"]), "B": ([], ["b1"])}
    for t in (Task("T1", "return", 1), Task("T2", "logrv", 1), Task("T1", "tail_loss", 4, 0.2)):
        pred, _ = run_cell(p, t, ["iba_e1"], estimators=("lin",), cfg=CFG, seeds=(0,), with_garch=False)
        v = variant_forecasts(p, t, CFG)
        np.testing.assert_allclose(v["base"], pred["iba_e1|lin"].values, rtol=0, atol=1e-12)
        assert {"wo_A", "wo_B", "wo_ENDG", "one", "ecdf"} <= set(v) and (("nohar" in v) == (t.kind == "logrv"))
        for k, f in v.items():
            assert np.isfinite(f).all()
            if k != "base":
                assert np.abs(f - v["base"]).max() > 1e-9, k
        if t.kind == "logrv":
            assert np.abs(v["nohar"] - v["base"]).mean() > np.abs(v["ecdf"] - v["base"]).mean()      # dropping HAR moves the forecast far more
