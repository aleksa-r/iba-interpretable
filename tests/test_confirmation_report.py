"""The pre-written report of SPEC-2026-11-14-confirmation: the claim rules on constructed tests, and the
whole report on synthetic cells laid out like the confirmation run (development colonies applied unchanged)."""
import importlib.util
import json
import os

import numpy as np
import pandas as pd
import pytest

from iba.protocol import study
from iba.protocol.dataset import Task
from iba.protocol.walkforward import run_cell
from iba.search import pooled

from .test_pooled import CFG, contexts, multi_panel
from .test_wrapup_report import MEMBERS, _with_formulas

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("confirmation_report", os.path.join(HERE, "..", "scripts", "make_confirmation_report.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _row(a, b, kind, task, rel, lo, hi, p=0.5):
    return {"frequency": "weekly", "task": task, "kind": kind, "a": a, "b": b, "series": 21, "rel_diff": rel, "ci_low": lo, "ci_high": hi, "p": p,
            "verdict": "better" if hi < 0 else "worse" if lo > 0 else "n.s."}


def test_claim_rules(mod):
    tasks = [("return", f"return_h{h}") for h in (1, 4, 13)] + [("logrv", f"logrv_h{h}") for h in (1, 4, 13)] + \
            [(k, f"{k}_q10_h{h}") for k in ("tail_loss", "tail_gain") for h in (4, 13)]
    rows = [_row(mod.FIXED, mod.GPCA, k, t, -0.005, -0.02, 0.012) for k, t in tasks]
    rows += [_row(mod.FIXED, "REF", "logrv", "logrv_h1", -0.07, -0.11, -0.03, 0.001), _row(mod.FIXED, "REF", "logrv", "logrv_h4", -0.06, -0.12, -0.01, 0.030),
             _row(mod.FIXED, "REF", "logrv", "logrv_h13", -0.01, -0.05, 0.02, 0.6)]
    rows += [_row(mod.ACC, mod.FIXED, k, t, -0.002, -0.004, -0.001 if i < 3 else 0.001) for i, (k, t) in enumerate(tasks)]
    C = mod.claims(pd.DataFrame(rows), None, None, None, 21).set_index("claim")
    assert C.loc["P1", "decision"] == "CONFIRMED" and C.loc["P2", "decision"] == "CONFIRMED" and "Holm-adjusted p = 0.030" in C.loc["P2", "result"]
    assert C.loc["P3", "decision"] == "CONFIRMED" and C.loc["S1", "decision"] == "reported" and C.loc["S2", "decision"] == "holds"
    assert C.loc["S5", "decision"] == "holds" and C.loc["S3", "decision"] == "does not hold"          # nothing available: not shown to hold
    weak = [r if not (r["a"] == mod.FIXED and r["b"] == "REF" and r["task"] == "logrv_h4") else {**r, "p": 0.04} for r in rows]
    C2 = mod.claims(pd.DataFrame(weak), None, None, None, 21).set_index("claim")
    assert C2.loc["P1", "decision"] == "CONFIRMED" and C2.loc["P2", "decision"] == "CONFIRMED"         # 0.04 against Holm's second threshold 0.05
    bad = [r if not (r["a"] == mod.FIXED and r["b"] == mod.GPCA and r["kind"] == "return") else {**r, "ci_high": 0.04} for r in rows]
    assert mod.claims(pd.DataFrame(bad), None, None, None, 21).set_index("claim").loc["P3", "decision"] == "NOT CONFIRMED"      # 3 of 10 tasks above the margin
    one_out = [r if not (r["a"] == mod.FIXED and r["b"] == mod.GPCA and r["task"] == "return_h1") else {**r, "ci_high": 0.04} for r in rows]
    assert mod.claims(pd.DataFrame(one_out), None, None, None, 21).set_index("claim").loc["P3", "decision"] == "CONFIRMED"      # 9 of 10 is enough
    worse = [r if not (r["a"] == mod.FIXED and r["b"] == mod.GPCA and r["task"] == "return_h1") else {**r, "ci_low": 0.001, "ci_high": 0.02, "verdict": "worse"} for r in rows]
    assert mod.claims(pd.DataFrame(worse), None, None, None, 21).set_index("claim").loc["P3", "decision"] == "NOT CONFIRMED"   # group PCA significantly better once
    from iba.protocol.dataset import Task
    full = [Task("X", k, int(t.rsplit("_h", 1)[1]), 0.10 if k.startswith("tail") else None) for k, t in tasks]
    short = pd.DataFrame([r for r in rows if not (r["a"] == mod.FIXED and r["b"] == mod.GPCA and r["task"] == "return_h13")])
    C4 = mod.claims(short, None, None, None, 21, full).set_index("claim")
    assert C4.loc["P3", "decision"] == "NOT RUN" and "MISSING TASKS: return_h13" in C4.loc["P3", "result"]      # 9 of 9 must not pass as 9 of 10
    assert mod.claims(pd.DataFrame(rows), None, None, None, 21, full).set_index("claim").loc["P3", "decision"] == "CONFIRMED"
    with pytest.raises(ValueError, match="incomplete comparisons"):
        mod.check_complete(short, full)
    lost = [r if not (r["a"] == mod.FIXED and r["b"] == "REF" and r["task"] == "logrv_h1") else {**r, "p": 0.2} for r in rows]
    C3 = mod.claims(pd.DataFrame(lost), None, None, None, 21).set_index("claim")
    assert C3.loc["P1", "decision"] == "NOT CONFIRMED" and C3.loc["P2", "decision"] == "NOT CONFIRMED"   # Holm: 0.03 * 2 = 0.06


def test_report_runs_on_synthetic_cells(mod, tmp_path, monkeypatch):
    base = multi_panel(strength=0.02)
    kinds = (("return", 1, None), ("return", 4, None), ("logrv", 1, None), ("logrv", 4, None), ("tail_loss", 4, 0.2), ("tail_gain", 4, 0.2))
    tasks = [Task(t, k, h, q) for t in MEMBERS for k, h, q in kinds]
    cfg = CFG.__class__(**{**CFG.__dict__, "search_budget": 100})
    st = study.STAGES[11]
    kc = _with_formulas(base, "Kc")
    store = tmp_path / "artifacts" / study.WRAPUP / "stage8" / "prior_Kc"
    for k, h, q in kinds:                                              # the "development" colonies, found on the same synthetic pool
        name = Task("T1", k, h, q).name
        for b in range(2):
            path = pooled.store_path("weekly", name, "x", b, str(store))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            ctxs = contexts(kc, k, h, q, block=b, targets=MEMBERS)
            res = pooled.pooled_search_block(ctxs, (0, 1), 100, 8, arms=("a",))
            res["_meta"] = {"frequency": "weekly", "task": name, "pool": "x", "block": b, "members": list(MEMBERS), "train_rows": int(len(ctxs[0].rows))}
            with open(path, "w") as fh:
                json.dump(res, fh)
    pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = str(store), {t: "x" for t in MEMBERS}, {}
    try:
        for name in st["priors"]:
            p = _with_formulas(base, name)
            for t in tasks:
                pred, _ = run_cell(p, t, st["methods"] + st["extra"].get(name, []), estimators=st["estimators"], cfg=cfg, seeds=(0, 1),
                                   with_garch=name in st["garch_sets"])
                d = tmp_path / "artifacts" / mod.SPEC / "stage11" / f"prior_{name}" / t.frequency / t.name / t.target
                d.mkdir(parents=True)
                pred.to_csv(d / "predictions.csv", index=False)
    finally:
        pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = None, {}, {}
    mod.wr.REPO = str(tmp_path)
    monkeypatch.setattr(study, "confirmation_tasks", lambda: tasks)
    monkeypatch.setattr(study, "stratum_of", lambda: {t: "x" for t in MEMBERS})
    monkeypatch.setattr(mod, "panel_returns", lambda: {"weekly": base.returns})
    C = mod.main().set_index("claim")
    out = tmp_path / "docs" / "results" / mod.SPEC
    assert list(C.index) == ["P1", "P2", "P3"] + [f"S{i}" for i in range(1, 12)]
    assert set(C.loc[["P1", "P2", "P3"], "decision"]) <= {"CONFIRMED", "NOT CONFIRMED"} and C.loc["S1", "decision"] == "reported"
    assert "task not run" in C.loc["S1", "result"] and "not available" not in " ".join(C.loc[["S2", "S3", "S4", "S6", "S7", "S8", "S9", "S10", "S11"], "result"])
    text = (out / "report.md").read_text()
    for head in ("### Primary", "### Secondary", "### 2a. Against the type's reference", "## 3. By asset class"):
        assert head in text, head
    P = pd.read_csv(out / "paired_tests.csv")
    assert P[["rel_diff", "ci_low", "ci_high"]].notna().all().all() and {"iba_ca_b", "Rm", "kpca|lin", "bench|garch", "bench|garch_prob", "Kc|xgb"} <= set(P.a)
    extra = (out / "extra" / "extra_metrics.md").read_text()
    assert "Sharpe after 10 bp per switch" in extra and "GARCH" in extra and (out / "extra" / "var_backtest.csv").exists()
    X = pd.read_csv(out / "extra" / "stress_periods.csv")
    assert {"other periods", "not in drawdown"} <= set(X.period) and X.rel_to_reference.notna().any() and "## 4. Crisis and drawdown periods" in extra


def test_a_colony_found_at_another_origin_is_refused(tmp_path):
    p = multi_panel(strength=0.02)
    ctxs = contexts(p, block=0)
    res = pooled.pooled_search_block(ctxs, (0,), 60, 8, arms=("a",))
    res["_meta"] = {"train_rows": int(len(ctxs[0].rows)) + 1}                       # as if the search had used other rows
    for b in range(2):
        path = pooled.store_path("weekly", "return_h1", "x", b, str(tmp_path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(res, fh)
    pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = str(tmp_path), {"T1": "x"}, {}
    try:
        with pytest.raises(ValueError, match="stored search"):
            run_cell(p, Task("T1", "return", 1), ["iba_ca"], estimators=("lin",), cfg=CFG, seeds=(0,), with_garch=False)
    finally:
        pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = None, {}, {}
