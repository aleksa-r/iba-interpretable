"""Prior elicitation without the network: prompt, schema, validation, statistics, a fake client."""
import json
from types import SimpleNamespace

import pandas as pd
import pytest

from .conftest import needs_monthly_targets

from iba.priors import elicit as E

from .test_pooled import multi_panel

DICT = pd.DataFrame({"code": ["a1", "a2", "a3", "a4", "b1", "b2", "HYG_RET", "b4"], "label": list("abcdefgh"),
                     "description": ["x"] * 8, "group": ["A"] * 4 + ["B"] * 4})


def answer(freq="weekly", **override):
    one = {"A": {"literals": [{"factor": "a1", "state": "high"}, {"factor": "a3", "state": "not_high"}], "rationale": "r"},
           "B": {"literals": [], "rationale": "nothing"}, "ENDG": {"literals": [{"factor": "__target__", "state": "high"}], "rationale": "own"}}
    return {t: {**one, **override} for t in E.TARGETS[freq]}


def test_prompt_carries_the_manual_the_cutoff_and_no_data_unless_asked():
    system, user = E.build_prompt("weekly", "commodities", DICT)
    assert E.CUTOFF in system and "after" in system and "IBA formula manual" in user and "a3: c. x" in user
    assert "Statistics from the training sample" not in user and "commodity indices" in user
    stats = E.training_statistics(multi_panel(strength=0.02), "weekly", ["T1", "T2"], DICT)
    assert list(stats.columns) == ["factor", "group"] + E.TARGETS["weekly"] and len(stats) == 9
    assert stats.set_index("factor").loc["__target__", "group"] == "ENDG"
    _, with_stats = E.build_prompt("weekly", "commodities", DICT, stats)
    assert "Statistics from the training sample" in with_stats and "first forecast date" in with_stats


def test_schema_validation_and_formula_file_sections():
    g = E.groups_of(DICT)
    s = E.schema("weekly", g)
    assert s["required"] == E.TARGETS["weekly"] and s["properties"]["return"] == {"$ref": "#/$defs/target"} and s["$defs"]["target"]["required"] == list(g)
    assert E.validate(answer(), "weekly", g) == []
    three = {"literals": [{"factor": c, "state": "high"} for c in ("a1", "a2", "a3")], "rationale": "r"}
    assert any("return/A" in p for p in E.validate(answer(A=three), "weekly", g))
    wrong = {"literals": [{"factor": "b1", "state": "high"}], "rationale": "r"}
    assert E.validate(answer(A=wrong), "weekly", g)
    late = {"literals": [{"factor": "a1", "state": "high"}], "rationale": "as seen in 2020"}
    assert any("cut-off" in p for p in E.validate(answer(A=late), "weekly", g))
    f = E.to_formulas(answer("monthly"), "monthly")
    assert set(f) == {"return", "tail_loss", "tail_gain"} and f["return"]["groups"] == {"A": [["a1", "high"], ["a3", "not_high"]], "ENDG": [["__target__", "high"]]}


def test_elicit_retries_an_invalid_answer_and_records_everything():
    replies = [answer(A={"literals": [{"factor": "b1", "state": "high"}], "rationale": "r"}), answer()]

    class Stream:
        def __init__(self, payload): self.payload = payload
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def get_final_message(self):
            return SimpleNamespace(id="msg_x", stop_reason="end_turn", model=E.MODEL, usage=SimpleNamespace(input_tokens=1, output_tokens=2),
                                   content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=json.dumps(self.payload))])
    calls = []

    class Messages:
        def stream(self, **kw):
            calls.append(kw)
            return Stream(replies[len(calls) - 1])
    rec = E.elicit(SimpleNamespace(messages=Messages()), "weekly", "commodities", DICT)
    assert len(rec["attempts"]) == 2 and rec["attempts"][0]["problems"] and rec["answer"] == answer() and rec["procedure"] == "K"
    assert calls[0]["model"] == E.MODEL and calls[0]["thinking"] == {"type": "adaptive"} and calls[0]["output_config"]["format"]["type"] == "json_schema"
    assert "temperature" not in calls[0] and len(rec["prompt_sha256"]) == 64


def test_per_class_formula_file_picks_the_section_of_the_class_and_kind(monkeypatch):
    from iba.models import reducers as R
    monkeypatch.setattr(R, "_CLASS_OF", {"T1": ("weekly", "commodities"), "T2": ("weekly", "real_estate")})
    cols = {"A": ["a1_52m_zs", "a2_52m_zs", "a1_13m_zs"], "ENDG": ["T1_52m_zs"]}
    doc = {"source": "test", "classes": {"weekly": {"commodities": {
        "return": {"groups": {"A": [["a1", "high"], ["a2", "not_high"]], "ENDG": [["__target__", "high"]]}},
        "logrv": {"groups": {"A": [["a2", "high"]]}}}}}}
    assert R.prior_formula(doc, "T1", cols, (13, 52), "return") == {"A": (["a1_52m_zs"], ["a2_52m_zs"]), "ENDG": (["T1_52m_zs"], [])}
    assert R.prior_formula(doc, "T1", cols, (13, 52), "logrv") == {"A": (["a2_52m_zs"], [])}
    with pytest.raises(KeyError, match="tail_loss"):
        R.prior_formula(doc, "T1", cols, (13, 52), "tail_loss")           # a missing section is an error, not the generic prior
    with pytest.raises(KeyError, match="real_estate"):
        R.prior_formula(doc, "T2", cols, (13, 52), "return")


@needs_monthly_targets
def test_class_of_reads_the_universe_and_load_panel_takes_a_formula_file(tmp_path):
    import yaml
    from iba.data.panel import load_panel
    from iba.models.reducers import class_of
    from iba.protocol.study import development_tasks
    weekly = next(t for t in development_tasks() if t.frequency == "weekly")
    monthly = next(t for t in development_tasks() if t.frequency == "monthly")
    assert class_of(weekly.target)[0] == "weekly" and class_of(monthly.target) == ("monthly", "hedge_fund_monthly")
    f = tmp_path / "f.yaml"
    f.write_text(yaml.safe_dump({"source": "test", "classes": {"monthly": {}}}))
    assert load_panel("monthly", formulas=str(f)).formulas["source"] == "test"
    assert "groups" in load_panel("monthly").formulas
