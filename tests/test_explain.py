"""The explanation step without the network: the trace reproduces the engine's forecasts, the
prepared numbers and the payloads are built, and an answer with a number that is not in the
material is rejected and asked again."""
import json
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from iba.explain import narrate as N
from iba.explain.cases import cell_numbers, class_case, forecast_case, rationales
from iba.explain.trace import check_against, factor_of, literals_at, trace_cell
from iba.protocol.dataset import Task
from iba.protocol.walkforward import run_cell

from .test_pooled import CFG, multi_panel

LABELS = {"a1": "first factor", "a2": "second factor", "HYG_RET": "high-yield return", "__target__": "the index's own recent behaviour"}
DRAWS = {1: {"return": {"A": {"literals": [{"factor": "a1", "state": "high"}], "rationale": "partial."}}},
         2: {"return": {"A": {"literals": [{"factor": "a1", "state": "high"}, {"factor": "a2", "state": "not_high"}], "rationale": "A matters."},
                        "B": {"literals": [{"factor": "HYG_RET", "state": "not_high"}], "rationale": "B matters."}}}}


@pytest.fixture(scope="module")
def cells():
    p = multi_panel(strength=0.02)
    out = {}
    for t in (Task("T1", "return", 1), Task("T2", "return", 1), Task("T1", "return", 4), Task("T2", "logrv", 1), Task("T1", "tail_loss", 4, 0.2)):
        pred, _ = run_cell(p, t, ["iba_e1", "iba_rnda"], estimators=("lin", "xgb"), cfg=CFG, seeds=(0, 1), with_garch=False)
        tr = trace_cell(p, t, CFG)
        out[(t.target, t.name)] = (tr, pred, cell_numbers(tr, pred, ["iba_rnda.s0", "iba_rnda.s1"]))
    return out


def test_trace_reproduces_the_engine_and_decomposes_the_forecast(cells):
    for (tgt, name), (tr, pred, cell) in cells.items():
        d = check_against(tr, pred)
        assert d["lin"] < 1e-12 and d["xgb"] < 1e-5, (tgt, name, d)
        np.testing.assert_allclose(tr["raw"], tr["intercept"] + tr["contrib"].sum(axis=1), rtol=0, atol=1e-12)
        last = len(tr["dates"]) - 1
        prod = {}
        for r in literals_at(tr, last):
            prod[r["group"]] = prod.get(r["group"], 1.0) * r["literal"]
            assert 0 <= r["truth_high"] <= 1
        np.testing.assert_allclose([prod[g] for g in tr["groups"]], tr["value"][last], atol=1e-12)
        assert cell["diffs"] == d and np.isfinite(cell["loss"]["accuracy"])
    assert factor_of("T1_52m_zs", "T1") == ("__target__", 52) and factor_of("HYG_RET_13m_zs", "T1") == ("HYG_RET", 13)


def test_rationale_rule_prefers_the_draw_with_the_same_formula():
    lits = [{"group": "A", "factor": "a1", "state": "high"}, {"group": "A", "factor": "a2", "state": "not_high"}, {"group": "ENDG", "factor": "__target__", "state": "high"}]
    r = rationales(lits, DRAWS, "return")
    assert r["A"] == "(draw 2) A matters." and r["ENDG"].startswith("(no rationale")
    assert rationales(lits[:1], {1: DRAWS[2]}, "return")["A"].startswith("(draw 1, whose formula for the group differed in part)")


def test_payloads_and_number_check(cells):
    tests = pd.DataFrame([{"a": "P|lin", "b": "REF", "frequency": "weekly", "task": "return_h1", "series": 3, "rel_diff": -0.0123, "ci_low": -0.03, "ci_high": 0.004, "verdict": "n.s."}])
    c1 = cells[("T1", "return_h1")][2]
    fp = N.forecast_payload(forecast_case(c1, "test indices", LABELS, DRAWS, tests, "P|lin"))
    assert "first factor" in fp and "(draw 2) A matters." in fp and "-1.2 % (95 % interval -3.0 % to +0.4 %)" in fp and "XGBoost" in fp
    for key in (("T2", "logrv_h1"), ("T1", "tail_loss_q20_h4")):
        assert "Track record" in N.forecast_payload(forecast_case(cells[key][2], "test indices", LABELS, DRAWS))
    cc = class_case([cells[k][2] for k in (("T1", "return_h1"), ("T2", "return_h1"), ("T1", "return_h4"))], "test indices", LABELS, DRAWS, tests, "P|lin")
    assert cc["n_series"] == 2 and [r["horizon"] for r in cc["skill_rows"]] == ["1 week", "4 weeks"]
    assert abs(sum(g["share"] for g in cc["group_rows"]) - 100) < 1e-6
    cp = N.class_payload(cc)
    assert "| 1 week |" in cp and "n/a" in cp                      # the 4-week task has no test row here
    good = {"headline": "A small forecast.", "explanation": "Group A, 3 groups in all.", "limits": "No advantage."}
    assert N.check_numbers(good, fp) == []
    assert N.check_numbers({**good, "explanation": "A gain of 37.5 % is expected."}, fp) == ["37.5"]
    assert N.check_numbers({**good, "explanation": "A gain of 37.5x, or 81.25bp."}, fp) == ["37.5", "81.25"]      # a unit glued to the number does not hide it


def test_explain_asks_again_after_a_number_that_is_not_in_the_material():
    payload = "Forecast: +0.41 % over the next 4 weeks."
    answers = [{"headline": "h", "explanation": "about 0.4 %", "limits": "l"}, {"headline": "h", "explanation": "+0.41 % over 4 weeks", "limits": "l"}]
    calls = []

    class Stream:
        def __init__(self, a): self.a = a
        def __enter__(self): return self
        def __exit__(self, *x): return False
        def get_final_message(self):
            return SimpleNamespace(id="msg", stop_reason="end_turn", model=N.MODEL, usage=SimpleNamespace(input_tokens=1, output_tokens=1),
                                   content=[SimpleNamespace(type="text", text=json.dumps(self.a))])

    def stream(**kw):
        calls.append(kw)
        return Stream(answers[len(calls) - 1])

    rec = N.explain(SimpleNamespace(messages=SimpleNamespace(stream=stream)), payload)
    assert len(calls) == 2 and "0.4" in calls[1]["messages"][0]["content"].split("Note:")[1] and calls[0]["system"] == N.SYSTEM
    assert rec["answer"] == answers[1] and rec["attempts"][0]["problems"] and rec["attempts"][1]["problems"] == []
    answers[1] = answers[0]; answers.append(answers[0]); calls.clear()
    assert N.explain(SimpleNamespace(messages=SimpleNamespace(stream=stream)), payload)["answer"] is None and len(calls) == 3
