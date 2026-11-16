import numpy as np
import pandas as pd

from iba.eval.map import base_name, build_map, headline_table
from iba.protocol.dataset import Task
from iba.protocol.information_rule import FoldGeometry
from iba.protocol.walkforward import ProtocolConfig, run_cell
from .test_engine import panel

CFG = ProtocolConfig(24, 12, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=100, colony=8)


def test_map_on_synthetic_cells():
    cells = []
    for kind, h, q in (("return", 4, None), ("logrv", 1, None), ("tail_loss", 4, 0.2)):
        task = Task("T1", kind, h, q)
        for stratum, seed in (("s1", 0), ("s1", 1), ("s2", 2)):
            pred, meta = run_cell(panel(seed=seed), task, ["raw", "gpca", "iba_e1", "iba_a", "iba_b", "iba_c"], cfg=CFG, seeds=(0, 1), with_garch=False)
            cells.append({"stratum": stratum, "frequency": "weekly", "task": task.name, "kind": kind, "h": h, "target": f"T{seed}", "pred": pred, "meta": meta})
    m = build_map(cells, reps=200)
    assert base_name("iba_a.s1|lin") == "iba_a|lin" and base_name("iba_b.s0") == "iba_b"
    assert set(m["task"]) == {"return_h4", "logrv_h1", "tail_loss_q20_h4"} and set(m["stratum"]) == {"s1", "s2"}
    g = m[(m.task == "return_h4") & (m.stratum == "s1")]
    assert g["cells"].iloc[0] == 2
    assert abs(g.loc[g.config == "bench|mean", "skill_vs_reference"].iloc[0]) < 1e-12        # the reference has zero skill
    iba = g[~g.benchmark]
    assert {"iba_e1|lin", "iba_a|lin", "iba_b", "iba_c"} <= set(iba["config"])
    assert iba["rank_among_benchmarks"].between(1, iba["n_benchmarks"].iloc[0] + 1).all()
    assert (iba["ci_low"] <= iba["diff_to_best_benchmark"]).all() and (iba["diff_to_best_benchmark"] <= iba["ci_high"]).all()
    a = g[g.config == "iba_a|lin"].iloc[0]
    assert np.isfinite(a["search_optimism"]) and 0 <= a["search_accept_rate"] <= 1 and a["search_evals"] <= 100
    assert np.isfinite(g.loc[g.config == "gpca|lin", "optimism_gap"].iloc[0])
    h = headline_table(m)
    assert len(h) == 6 and "iba_b" in h.columns
