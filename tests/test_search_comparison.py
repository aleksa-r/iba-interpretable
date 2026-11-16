import importlib.util
import os

import pandas as pd

from iba.protocol.dataset import Task
from iba.protocol.information_rule import FoldGeometry
from iba.protocol.walkforward import ProtocolConfig, block_contexts
from iba.search.run import search
from .test_engine import panel


def test_block_contexts_and_the_comparison_analysis():
    cfg = ProtocolConfig(24, 12, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=80, colony=8)
    rows = []
    for seed_panel in (0, 1):
        ctxs = list(block_contexts(panel(seed=seed_panel), Task("T1", "return", 4), cfg))
        assert len(ctxs) == 2 and all(len(c.folds) == 5 for _, c in ctxs)
        for b, ctx in ctxs:
            assert ctx.rows[-1] + 4 <= len(ctx.ds) - 24 + b * 12             # admissible at the block origin
            for algo, select in (("abc", "inner"), ("ga", "inner"), ("pso", "inner"), ("sa", "inner"), ("abc", "outer")):
                for seed in (0, 1):
                    res, _ = search(ctx, algo, "A", seed, select)
                    d = res.diag
                    rows.append({"target": f"T{seed_panel}", "task": "return_h4", "block": b, "algorithm": algo + ("_gv" if select == "outer" else ""),
                                 "seed": seed, "n_evals": res.n_evals, "accepted": res.accepted, "inner_best": d["inner_best"],
                                 "outer_best": d["outer_best"], "inner_prior": d["inner_prior"], "outer_prior": d["outer_prior"],
                                 "optimism": d["optimism"]})
    df = pd.DataFrame(rows)
    assert (df.n_evals <= 80).all()
    own = df[df.algorithm != "abc_gv"]                    # selection by inner fitness never loses in sample
    assert (own.inner_best <= own.inner_prior + 1e-12).all()
    # global validation picks by the outer fold, so its outer score is never worse than ABC's own pick
    gv = df[df.algorithm == "abc_gv"].set_index(["target", "block", "seed"])["outer_best"]
    ab = df[df.algorithm == "abc"].set_index(["target", "block", "seed"])["outer_best"]
    assert (gv <= ab + 1e-12).all()
    spec = importlib.util.spec_from_file_location("rsc", os.path.join(os.path.dirname(__file__), "..", "scripts", "run_search_comparison.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    text = mod.analyse(df)
    assert "Friedman" in text and "ABC vs ga" in text and "abc_gv" in text
