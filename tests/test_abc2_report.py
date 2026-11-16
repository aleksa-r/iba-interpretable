"""The pre-written analysis of SPEC-2026-11-14-abc-v2 runs end to end on synthetic cells laid out
like the real artifacts (first study's stage 1 and 2, this spec's stage 4)."""
import importlib.util
import json
import os

import pandas as pd

from iba.protocol.dataset import Task
from iba.protocol.walkforward import run_cell

from .test_engine import CFG, panel

HERE = os.path.dirname(os.path.abspath(__file__))


def test_report_runs_on_synthetic_cells(tmp_path, capsys):
    spec = importlib.util.spec_from_file_location("abc2_report", os.path.join(HERE, "..", "scripts", "make_abc2_report.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    tasks = [Task(t, k, h, q) for t in ("T1", "T2") for k, h, q in (("return", 4, None), ("logrv", 1, None), ("tail_loss", 4, 0.2))]
    stages = {(mod.FIRST_SPEC, 1): ["gpca", "iba_e1"], (mod.FIRST_SPEC, 2): ["iba_a", "iba_b"],
              (mod.SPEC, 4): ["iba_ar", "iba_ac", "iba_w", "iba_v", "iba_g", "iba_z"]}
    for t in tasks:
        p = panel(seed=1 if t.target == "T1" else 2)
        if t.target == "T2":                                     # the synthetic panel has one target: rename it
            p.returns.columns = ["T2"]; p.rv.columns = ["T2"]
        for (sid, st), methods in stages.items():
            pred, meta = run_cell(p, t, methods, estimators=("lin",), cfg=CFG, seeds=(0, 1), with_garch=False)
            d = tmp_path / "artifacts" / sid / f"stage{st}" / t.frequency / t.name / t.target
            d.mkdir(parents=True)
            pred.to_csv(d / "predictions.csv", index=False)
            (d / "meta.json").write_text(json.dumps(meta, default=str))
    mod.REPO = str(tmp_path)
    mod.abc2_tasks = lambda: tasks
    mod.stratum_of = lambda: {"T1": "x", "T2": "y"}
    mod.main()
    out = tmp_path / "docs" / "results" / mod.SPEC
    text = (out / "report.md").read_text()
    assert "## 5. Decision rule" in text and "Qualifying:" in text
    P = pd.read_csv(out / "paired_tests.csv")
    assert len(P) == 3 * len(mod.PAIRS) and P[["rel_diff", "ci_low", "ci_high"]].notna().all().all()
    D = pd.read_csv(out / "search_diagnostics.csv")
    assert set(D.search) == {"ac", "w", "v", "g", "z"} and D.clean_gain.notna().any() and len(pd.read_csv(out / "spa_tests.csv")) == 12
