"""The pre-written analysis of SPEC-2026-11-14-abc-v3 runs end to end on synthetic cells laid out
like the real artifacts (first study, the abc-v2 stage, the pooled store and this spec's stage 6)."""
import importlib.util
import json
import os

import pandas as pd

from iba.protocol.dataset import Task
from iba.protocol.study import STAGES
from iba.protocol.walkforward import run_cell
from iba.search import pooled

from .test_pooled import CFG, TARGETS, contexts, multi_panel

HERE = os.path.dirname(os.path.abspath(__file__))


def test_report_runs_on_synthetic_cells(tmp_path):
    spec = importlib.util.spec_from_file_location("abc3_report", os.path.join(HERE, "..", "scripts", "make_abc3_report.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    p = multi_panel(strength=0.02)
    kinds = (("return", 1, None), ("logrv", 1, None), ("tail_loss", 4, 0.2), ("tail_gain", 4, 0.2))
    tasks = [Task(t, k, h, q) for t in TARGETS for k, h, q in kinds]
    store = tmp_path / "artifacts" / mod.SPEC / "stage5"
    for k, h, q in kinds:
        name = Task("T1", k, h, q).name
        for pool in ("x", pooled.ALL):
            for b in range(2):
                path = pooled.store_path("weekly", name, pool, b, str(store))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as fh:
                    json.dump(pooled.pooled_search_block(contexts(p, k, h, q, block=b), (0, 1), 100, 8), fh)
    stages = {(mod.FIRST_SPEC, 1): ["gpca", "iba_e1"], (mod.FIRST_SPEC, 2): ["iba_a", "iba_b"], (mod.SPEC2, 4): ["iba_ar", "iba_ac", "iba_w"],
              (mod.SPEC, 6): STAGES[6]["methods"]}
    pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = str(store), {t: "x" for t in TARGETS}, {}
    try:
        cfg = CFG.__class__(**{**CFG.__dict__, "search_budget": 100})
        for t in tasks:
            for (sid, st), methods in stages.items():
                pred, meta = run_cell(p, t, methods, estimators=("lin",), cfg=cfg, seeds=(0, 1), with_garch=False)
                d = tmp_path / "artifacts" / sid / f"stage{st}" / t.frequency / t.name / t.target
                d.mkdir(parents=True)
                pred.to_csv(d / "predictions.csv", index=False)
                (d / "meta.json").write_text(json.dumps(meta, default=str))
    finally:
        pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = None, {}, {}
    mod.REPO = str(tmp_path)
    mod.abc2_tasks = lambda: tasks
    mod.main()
    out = tmp_path / "docs" / "results" / mod.SPEC
    text = (out / "report.md").read_text()
    assert "## 5. Decision rule" in text and "Qualifying:" in text and "## 3. The three factors" in text
    P = pd.read_csv(out / "paired_tests.csv")
    assert P[["rel_diff", "ci_low", "ci_high"]].notna().all().all() and {"iba_fnw_b@3", "iba_rnda", "iba_cna_r|lin"} <= set(P.a)
    D = pd.read_csv(out / "decision.csv")
    assert len(D) == 22 and len(mod.ARMS) == 12 and len(mod.NEW_CONFIGS) == 32
