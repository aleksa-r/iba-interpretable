"""Search layer: space moves, budget accounting, determinism, the acceptance rule, and that a
planted formula is found. All on synthetic data."""
import numpy as np
import pandas as pd
import pytest

from iba.data.panel import Panel
from iba.protocol.dataset import LabelSpec, Task, build_dataset
from iba.protocol.information_rule import FoldGeometry, n_admissible, purged_folds
from iba.protocol.walkforward import BlockContext, ProtocolConfig
from iba.models.reducers import prior_formula
from iba.search.algorithms import ALGORITHMS, abc, exhaustive_atoms, exhaustive_low_order
from iba.search.fitness import FitnessEvaluator
from iba.search.space import SearchSpace

CFG = ProtocolConfig(48, 24, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=250)


def planted_panel(n=520, seed=0, strength=0.03):
    """T1's next-period return is a soft version of "a1 high AND a2 not high AND a3 high" plus
    "b2 not high" (u = normal CDF of the factor). The prior says "a1 high and a2 not high; b1 not
    high", so the truth is three status changes away (add a3; replace b1 by b2): inside the search
    neighbourhood, and expressible by one GBP per group with a linear model on top."""
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-08", periods=n, freq="W-FRI")
    f = pd.DataFrame(rng.normal(size=(n, 8)), index=idx, columns=["a1", "a2", "a3", "a4", "b1", "b2", "b3", "b4"])
    u = pd.DataFrame(norm.cdf(f.values), index=idx, columns=f.columns)
    sig = (4.0 * u["a1"] * (1 - u["a2"]) * u["a3"] + (1 - u["b2"])).shift(1).fillna(0.5).values
    r = pd.DataFrame({"T1": strength * (sig - sig.mean()) + rng.normal(0, 0.01, n)}, index=idx)
    rv = pd.DataFrame({"T1": np.full(n, 1e-4) * np.exp(rng.normal(0, 0.2, n))}, index=idx)
    formulas = {"groups": {"A": [["a1", "high"], ["a2", "not_high"]], "B": [["b1", "not_high"]], "ENDG": [["__target__", "high"]]}}
    return Panel("weekly", f, {"A": ["a1", "a2", "a3", "a4"], "B": ["b1", "b2", "b3", "b4"]}, r, rv, None, formulas, 52)


def context(panel, task, cfg=CFG, zs=None):
    ds = build_dataset(panel, task, zs)
    L = LabelSpec(ds)
    cut = n_admissible(len(ds) - cfg.holdout, task.h)
    rows = np.arange(cut)
    folds = purged_folds(cut, task.h, cfg.geo)
    st = L.fit(rows)
    fs = [L.fit(tr) for tr, _ in folds]
    prior = prior_formula(panel.formulas, task.target, ds.group_cols, ds.windows, task.kind)
    return BlockContext(ds, L, rows, L.train_y(st, rows), folds,
                        [(L.train_y(s, tr), L.train_y(s, va)) for s, (tr, va) in zip(fs, folds)], prior, task.est_task, task.h, cfg)


def test_space_moves_stay_valid_and_within_distance():
    ctx = context(planted_panel(), Task("T1", "return", 1))
    sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
    rng = np.random.default_rng(0)
    assert sp.valid(sp.prior) and sp.distance(sp.prior) == 0
    s = sp.prior
    seen = set()
    for _ in range(400):
        s = sp.neighbour(s, rng)
        assert sp.valid(s) and sp.distance(s) <= sp.max_distance
        seen.add(sp.key(s))
    assert len(seen) > 50
    flipped = list(sp.prior); g = sp.groups.index("B"); (j, pol), = sp.prior[g]
    flipped[g] = frozenset([(j, not pol)])
    assert sp.distance(tuple(flipped)) == 1                      # a polarity flip is one status change
    wild = tuple(frozenset((j, True) for j in range(len(c))) for c in sp.cols)
    assert sp.valid(sp.repair(wild, rng))
    assert sp.to_formula(sp.prior) == ctx.prior


def test_fitness_budget_counts_distinct_solutions_and_fold_roles():
    ctx = context(planted_panel(), Task("T1", "return", 1))
    sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
    ev = FitnessEvaluator(ctx, sp, mode="A")
    assert ev.fit_folds == [0, 1, 2, 3] and ev.outer == 4 and ev.penalty is None
    a = ev.evaluate(sp.prior); b = ev.evaluate(sp.prior)
    assert ev.n_evals == 1 and a is b and "outer" not in a          # the outer fold is not touched by fitness
    evd = FitnessEvaluator(ctx, sp, mode="D")
    assert evd.fit_folds == [0, 1, 2] and evd.penalty == 3 and evd.outer == 4
    r = evd.evaluate(sp.prior)
    assert r["fitness"] == pytest.approx(r["inner"] + max(0.0, r["penalty"] - r["inner"]))
    more = list(sp.prior); g = sp.groups.index("B"); more[g] = frozenset(set(sp.prior[g]) | {(3, True)})
    assert ev.evaluate(tuple(more))["fitness"] == pytest.approx(ev.evaluate(tuple(more))["inner"] + 0.005 * a["inner"])


@pytest.mark.parametrize("algo", ["abc", "ga", "pso", "sa", "de"])
def test_algorithms_spend_the_budget_and_are_deterministic_per_seed(algo):
    ctx = context(planted_panel(), Task("T1", "return", 1))
    out = []
    for seed in (3, 3, 4):
        sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
        ev = FitnessEvaluator(ctx, sp, mode="A")
        res = ALGORITHMS[algo](ev, sp, budget=250, seed=seed)
        assert 0.9 * 250 <= res.n_evals <= 250
        assert sp.valid(res.best) and res.diag["fitness_best"] <= res.diag["fitness_prior"] + 1e-12
        out.append((sp.key(res.best), res.n_evals, res.diag["inner_best"]))
    assert out[0] == out[1]


def test_abc_finds_a_planted_formula_and_the_acceptance_test_passes_it():
    ctx = context(planted_panel(strength=0.05), Task("T1", "return", 1))
    sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
    ev = FitnessEvaluator(ctx, sp, mode="A")
    res = abc(ev, sp, budget=600, seed=0)
    f = sp.to_formula(res.best)
    assert any(c.startswith("a3_") for c in f["A"][0])            # a3 asserted was added to group A
    assert any(c.startswith("b2_") for c in f["B"][1])            # b2 negated replaced b1 in group B
    assert sp.distance(res.best) <= 4
    assert res.accepted and res.chosen == res.best and res.diag["gain_outer"] > res.diag["se_outer"] > 0


def test_on_pure_noise_the_prior_is_kept_most_of_the_time():
    kept = 0
    for seed in range(6):
        ctx = context(planted_panel(seed=seed, strength=0.0), Task("T1", "return", 1))
        sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
        res = abc(FitnessEvaluator(ctx, sp, mode="A"), sp, budget=250, seed=seed)
        assert res.diag["inner_best"] <= res.diag["inner_prior"]     # the search always "improves" in sample
        kept += int(not res.accepted)
    assert kept >= 4


def test_exhaustive_references_cover_their_spaces():
    ctx = context(planted_panel(), Task("T1", "return", 1))
    sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
    ev = FitnessEvaluator(ctx, sp, mode="A")
    res = exhaustive_atoms(ev, sp)
    assert res.n_evals <= 2 ** 3 + 2 ** 8 + 2 ** 8 + 7 and res.n_evals >= 2 ** 8      # ENDG 3 cols, A and B 8 cols, 7 subsets
    for g in res.best:
        assert g is None or len(g) in (3, 8)
    ev2 = FitnessEvaluator(ctx, sp, mode="A")
    lo = exhaustive_low_order(ev2, sp)
    assert all(g is None or len(g) <= 2 for g in lo.best)


def test_de_moves_away_from_the_prior_and_repair_works_without_a_distance_bound():
    ctx = context(planted_panel(), Task("T1", "return", 1))
    sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
    res = ALGORITHMS["de"](FitnessEvaluator(ctx, sp, mode="A"), sp, budget=250, seed=0)
    assert res.algorithm == "de" and len(res.population) == 20 and len({sp.key(s) for s in res.population}) > 1
    assert res.diag["fitness_best"] < res.diag["fitness_prior"]          # the planted formula is three moves away
    free = SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None)
    rng = np.random.default_rng(0)
    far = tuple(frozenset([(j, False) for j in range(len(c))]) for c in free.cols)   # too many literals in every group
    fixed = free.repair(far, rng)
    assert free.valid(fixed) and all(len(s) <= free.max_literals for s in fixed if s is not None)
