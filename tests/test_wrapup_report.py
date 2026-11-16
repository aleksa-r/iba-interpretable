"""The pre-written analysis of SPEC-2026-11-14-wrapup runs end to end on synthetic cells laid out
like the real artifacts: stage 7 per formula set, the stage-8 store and stage 9 for the chosen set."""
import copy
import importlib.util
import json
import os

import numpy as np
import pandas as pd

from iba.protocol.dataset import Task
from iba.protocol.study import POOLED_STAGES, PRIOR_SETS, STAGES
from iba.protocol.walkforward import run_cell
from iba.search import pooled

from .test_pooled import CFG, contexts, multi_panel

HERE = os.path.dirname(os.path.abspath(__file__))
MEMBERS = ("T1", "T2")


def _with_formulas(panel, name):
    """A synthetic stand-in for formula set ``name``: the panel's formulas with one literal changed per set."""
    p = copy.copy(panel)
    f = copy.deepcopy(panel.formulas)
    k = sum(ord(c) for c in name)
    if name != "G":
        f["groups"]["A"] = [[["a1", "a2", "a3", "a4"][k % 4], "high" if k % 2 else "not_high"], [["a1", "a2", "a3", "a4"][(k + 1) % 4], "not_high"]]
        f["groups"]["B"] = [[["b1", "b2", "b4"][k % 3], "high"]]
    p.formulas = f
    return p


def test_helpers():
    spec = importlib.util.spec_from_file_location("wrapup_report", os.path.join(HERE, "..", "scripts", "make_wrapup_report.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    np.testing.assert_allclose(mod.holm([0.01, 0.04, 0.03, 0.5]), [0.04, 0.09, 0.09, 0.5])
    assert mod.rename("iba_e1|xgb", "K3") == "K3|xgb" and mod.rename("iba_rnda.s1::var", "Kc") == "Kc_nb.s1::var" and mod.rename("raw|lin", "G") == "raw|lin"
    P = pd.DataFrame({"a": "x", "b": "y", "kind": ["return", "logrv", "tail_loss", "tail_gain"], "rel_diff": [-0.01, -0.02, -0.01, 0.03],
                      "verdict": ["better", "n.s.", "n.s.", "n.s."]})
    assert mod.qualifies(P, "x", "y")["qualifies"] and not mod.qualifies(P.assign(verdict="n.s."), "x", "y")["qualifies"]
    assert not mod.qualifies(P.assign(rel_diff=[-0.01, 0.02, -0.01, 0.03]), "x", "y")["qualifies"]


def test_report_runs_on_synthetic_cells(tmp_path):
    spec = importlib.util.spec_from_file_location("wrapup_report", os.path.join(HERE, "..", "scripts", "make_wrapup_report.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    base = multi_panel(strength=0.02)
    kinds = (("return", 1, None), ("logrv", 1, None), ("tail_loss", 4, 0.2), ("tail_gain", 4, 0.2))
    tasks = [Task(t, k, h, q) for t in MEMBERS for k, h, q in kinds]
    cfg = CFG.__class__(**{**CFG.__dict__, "search_budget": 100})
    st = STAGES[7]
    for name in PRIOR_SETS:
        p = _with_formulas(base, name)
        for t in tasks:
            pred, meta = run_cell(p, t, st["methods"] + st["extra"].get(name, []), estimators=st["estimators"], cfg=cfg, seeds=(0, 1), with_garch=False)
            d = tmp_path / "artifacts" / mod.SPEC / "stage7" / f"prior_{name}" / t.frequency / t.name / t.target
            d.mkdir(parents=True)
            pred.to_csv(d / "predictions.csv", index=False)
    mod.REPO = str(tmp_path)
    mod.tasks = lambda: tasks
    chosen = mod.main("A")
    out = tmp_path / "docs" / "results" / mod.SPEC
    assert chosen in ("Kc", "Sc") and json.loads((out / "prior_choice.json").read_text())["chosen"] == chosen
    assert "## 2. The formula set of the method" in (out / "report_part_A.md").read_text()

    p = _with_formulas(base, chosen)
    store = tmp_path / "artifacts" / mod.SPEC / "stage8" / f"prior_{chosen}"
    for k, h, q in kinds:
        name = Task("T1", k, h, q).name
        for b in range(2):
            path = pooled.store_path("weekly", name, "x", b, str(store))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            res = pooled.pooled_search_block(contexts(p, k, h, q, block=b, targets=MEMBERS), (0, 1), 100, 8, arms=POOLED_STAGES[8]["arms"])
            res["_meta"] = {"frequency": "weekly", "task": name, "pool": "x", "block": b, "members": list(MEMBERS)}
            with open(path, "w") as fh:
                json.dump(res, fh)
    pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = str(store), {t: "x" for t in MEMBERS}, {}
    try:
        for t in tasks:
            pred, meta = run_cell(p, t, STAGES[9]["methods"], estimators=STAGES[9]["estimators"], cfg=cfg, seeds=(0, 1), with_garch=False)
            d = tmp_path / "artifacts" / mod.SPEC / "stage9" / f"prior_{chosen}" / t.frequency / t.name / t.target
            d.mkdir(parents=True)
            pred.to_csv(d / "predictions.csv", index=False)
    finally:
        pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = None, {}, {}
    assert mod.main() == chosen
    text = (out / "report.md").read_text()
    for head in ("## 1. Prior formulas", "## 3. Estimators", "### 4a. Five algorithms", "## 5. The final method", "## 6. Best-of-many test"):
        assert head in text, head
    P = pd.read_csv(out / "paired_tests_priors.csv")
    assert P[["rel_diff", "ci_low", "ci_high"]].notna().all().all() and {"K@5", "Rm", "Sc_nb", "R3|lin", "raw|xgb"} <= set(P.a) | set(P.b)
    U = pd.read_csv(out / "search_units.csv")
    assert set(U.algorithm) == {"ABC", "GA", "PSO", "SA", "DE"} and len(U) == 5 * 4 * 2 and set(U.kind) == {"return", "logrv", "tail_loss", "tail_gain"}
    final = json.loads((out / "final_method.json").read_text())
    assert final["formula_set"] == chosen and final["algorithm"] in ("ABC", "GA", "PSO", "SA", "DE")

    # the two later benchmarks (SPEC-2026-11-14-benchmarks-kpca-ae) on top of the finished wrap-up
    spec2 = importlib.util.spec_from_file_location("kpca_ae_report", os.path.join(HERE, "..", "scripts", "make_kpca_ae_report.py"))
    rep = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(rep)
    for t in tasks:
        pred, _ = run_cell(base, t, STAGES[10]["methods"], estimators=STAGES[10]["estimators"], cfg=cfg, seeds=(0,), with_garch=False)
        d = tmp_path / "artifacts" / rep.SPEC / "stage10" / t.frequency / t.name / t.target
        d.mkdir(parents=True)
        pred.to_csv(d / "predictions.csv", index=False)
    rep.wr.REPO = str(tmp_path); rep.wr.tasks = lambda: tasks
    rep.main()
    text2 = (tmp_path / "docs" / "results" / rep.SPEC / "report.md").read_text()
    assert "### 3. IBA against the two benchmarks" in text2
    P3 = pd.read_csv(tmp_path / "docs" / "results" / rep.SPEC / "paired_tests.csv")
    assert P3[["rel_diff", "ci_low", "ci_high"]].notna().all().all() and {"kpca|lin", "ae|xgb", "ae|gbt"} <= set(P3.a) | set(P3.b)
