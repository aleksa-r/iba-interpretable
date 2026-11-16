"""Pooled fitness and noise-aware replacement (SPEC-2026-11-14-abc-v3), on synthetic panels with
several targets, one of which lacks a factor (as HYG lacks HYG_RET in the real panel)."""
import json

import numpy as np
import pandas as pd
import pytest

from iba.data.panel import Panel
from iba.protocol.dataset import Task
from iba.protocol.information_rule import FoldGeometry
from iba.protocol.walkforward import ProtocolConfig, block_contexts, run_cell
from iba.search import pooled
from iba.search.fitness import FitnessEvaluator, one_se_test
from iba.search.pooled import (ARMS, Member, PooledEvaluator, abc_noise_aware, generic_groups, initial_colony, make_evaluator,
                                   own_formula, pooled_prior, pooled_search_block)
from iba.search.space import SearchSpace

CFG = ProtocolConfig(24, 12, 4, 250, FoldGeometry(0.6, 30, 15, 5), 52, search_budget=150, colony=8)
TARGETS = ("T1", "T2", "HYG")


def multi_panel(n=420, seed=0, strength=0.0, perturb_after=None):
    """Three targets on the same factors. With ``strength`` the next return of every target follows
    "a1 high AND a3 high" (the prior says a1 high AND a2 not high): a signal common to the pool."""
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2012-01-06", periods=n, freq="W-FRI")
    cols = ["a1", "a2", "a3", "a4", "b1", "b2", "HYG_RET", "b4"]
    f = pd.DataFrame(rng.normal(size=(n, 8)), index=idx, columns=cols)
    u = pd.DataFrame(norm.cdf(f.values), index=idx, columns=cols)
    sig = (u["a1"] * u["a3"]).shift(1).fillna(0.25).values
    r = pd.DataFrame({t: strength * (sig - sig.mean()) + rng.normal(0, 0.01, n) for t in TARGETS}, index=idx)
    rv = pd.DataFrame({t: np.full(n, 1e-4) * np.exp(rng.normal(0, 0.2, n)) for t in TARGETS}, index=idx)
    if perturb_after is not None:
        late = idx > perturb_after
        r2 = np.random.default_rng(seed + 1)
        f.loc[late] = r2.normal(size=(late.sum(), 8)) * 2
        r.loc[late] = r2.normal(0, 0.05, (late.sum(), len(TARGETS)))
    formulas = {"groups": {"A": [["a1", "high"], ["a2", "not_high"]], "B": [["HYG_RET", "not_high"]], "ENDG": [["__target__", "high"]]}}
    return Panel("weekly", f, {"A": ["a1", "a2", "a3", "a4"], "B": ["b1", "b2", "HYG_RET", "b4"]}, r, rv, None, formulas, 52)


def contexts(panel, kind="return", h=1, q=None, block=0, targets=TARGETS):
    out = []
    for t in targets:
        for b, ctx in block_contexts(panel, Task(t, kind, h, q), CFG):
            if b == block:
                out.append(ctx)
    return out


def test_generic_names_union_of_columns_and_translation_back():
    ctxs = contexts(multi_panel())
    g = generic_groups([c.ds for c in ctxs])
    assert g["ENDG"] == ["__target___raw", "__target___26m_zs", "__target___52m_zs"]
    assert "HYG_RET_52m_zs" in g["B"] and "HYG_RET_52m_zs" not in ctxs[2].ds.group_cols["B"]      # HYG lacks its own factor
    prior = pooled_prior(ctxs)
    assert prior["B"] == ([], ["HYG_RET_52m_zs"]) and prior["ENDG"] == (["__target___52m_zs"], [])
    for ctx in ctxs:                                              # the pooled prior IS every member's own prior
        assert own_formula(prior, ctx.ds) == {k: (list(a), list(n)) for k, (a, n) in ctx.prior.items()}
    assert "B" not in own_formula(prior, ctxs[2].ds) and "B" in own_formula(prior, ctxs[0].ds)


def test_one_member_pool_orders_formulas_as_the_single_series_fitness():
    ctx = contexts(multi_panel(strength=0.02), targets=("T1",))[0]
    ev = make_evaluator([ctx], "w")
    own = SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None)
    fe = FitnessEvaluator(ctx, own, mode="A", clean_outer=True)
    base = fe.evaluate(own.prior)["inner"]
    rng = np.random.default_rng(0)
    assert ev.evaluate(ev.space.prior)["fitness"] == pytest.approx(1.0)
    for _ in range(25):
        s = own.random_solution(rng)                              # same indices: one member, same column order
        a, b = ev.evaluate(s, with_outer=True), fe.evaluate(s, with_outer=True)
        assert a["fitness"] == pytest.approx(b["fitness"] / base, rel=1e-10)
        assert a["clean"] == pytest.approx(b["clean"] / base, rel=1e-10)
        x, y = ev.acceptance(s), fe.acceptance(s)
        assert x["accepted"] == y["accepted"] and x["gain"] == pytest.approx(y["gain"] / base, rel=1e-9)


def test_pooled_fitness_is_the_mean_of_normalised_member_losses_and_skips_missing_columns():
    ctxs = contexts(multi_panel(strength=0.02))
    ev = make_evaluator(ctxs, "w")
    singles = [make_evaluator([c], "w") for c in ctxs]
    rng = np.random.default_rng(1)
    gB = ev.space.groups.index("B"); jH = ev.space.cols[gB].index("HYG_RET_52m_zs")
    for _ in range(15):
        s = ev.space.random_solution(rng)
        r = ev.evaluate(s)
        parts = []
        for c, one in zip(ctxs, singles):                         # the same formula in each member's own space
            f = own_formula(ev.space.to_formula(s), c.ds)
            gf = pooled.generic_formula(f, c.ds.task.target)
            sol = tuple(None if g not in gf else frozenset([(one.space.cols[i].index(x), True) for x in gf[g][0]] + [(one.space.cols[i].index(x), False) for x in gf[g][1]])
                        for i, g in enumerate(one.space.groups))
            parts.append(one.evaluate(sol)["inner"] if any(x is not None for x in sol) else None)
        if all(p is not None for p in parts):
            assert r["inner"] == pytest.approx(np.mean(parts), rel=1e-9)
        assert r["profile"].shape == (len(ev.rows),) and np.isfinite(r["profile"]).all()
    only_h = tuple(frozenset([(jH, True)]) if i == gB else None for i in range(len(ev.space.groups)))
    assert ev.members[2].features(0, only_h).shape[1] == 0 and ev.members[0].features(0, only_h).shape[1] == 1
    a, b = ev.space.random_solution(rng), ev.space.random_solution(rng)
    t = one_se_test(ev.evaluate(b)["profile"] - ev.evaluate(a)["profile"], ev.h)
    assert ev.better(a, b) == bool(t["gain"] - (ev.evaluate(a)["penalty_term"] - ev.evaluate(b)["penalty_term"]) > t["se"])


@pytest.mark.parametrize("start", ["anchored", "spread"])
def test_noise_aware_abc_budget_determinism_and_a_winner_that_passed_the_test(start):
    def run(seed, strength):
        ev = make_evaluator(contexts(multi_panel(strength=strength)), "na" if start == "anchored" else "nw")
        return abc_noise_aware(ev, ev.space, budget=200, seed=seed, colony=8, start=start), ev
    (a, ev), (b, _) = run(0, 0.03), run(0, 0.03)
    assert a.best == b.best and a.population == b.population and a.n_evals <= 200 and all(ev.space.valid(s) for s in a.population)
    assert a.best == ev.space.prior or ev.better(a.best, ev.space.prior)
    assert a.chosen == (a.best if a.accepted else ev.space.prior)
    # without signal the rule slows the fit to noise (it cannot stop it: many states are held and each
    # comparison passes noise about one time in six): the winner fits the fitness folds less than the greedy one
    from iba.search.pooled import run_arm
    greedy_arm = "a" if start == "anchored" else "w"
    noise = [run(s, 0.0)[0].diag["inner_best"] for s in range(4)]
    greedy = [run_arm(make_evaluator(contexts(multi_panel()), greedy_arm), greedy_arm, 200, s, 8).diag["inner_best"] for s in range(4)]
    assert np.mean(noise) > np.mean(greedy)


def test_noise_aware_search_finds_a_signal_common_to_the_pool():
    ev = make_evaluator(contexts(multi_panel(n=520, strength=0.05)), "na")
    r = abc_noise_aware(ev, ev.space, budget=600, seed=0, colony=20, start="anchored")
    assert r.best != ev.space.prior and r.diag["inner_best"] < 0.97
    gA = ev.space.groups.index("A")
    assert (ev.space.cols[gA].index("a3_52m_zs"), True) in r.best[gA] or (ev.space.cols[gA].index("a3_26m_zs"), True) in r.best[gA]


def test_initial_colonies_match_the_two_abc_starts():
    ctx = contexts(multi_panel(), targets=("T1",))[0]
    ball = SearchSpace(ctx.ds.group_cols, ctx.prior); whole = SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None)
    a = initial_colony(ball, np.random.default_rng(0), 8, "anchored")
    w = initial_colony(whole, np.random.default_rng(0), 8, "spread")
    assert a[0] == ball.prior and w[0] == whole.prior and len({ball.key(s) for s in a}) == 8
    assert all(ball.distance(s) <= 2 for s in a) and max(whole.distance(s) for s in w) > 4


def test_pooled_search_uses_only_rows_before_the_block_origin_and_feeds_the_engine(tmp_path):
    p = multi_panel(strength=0.02)
    first = contexts(p, block=0)
    out0 = pooled_search_block(first, (0,), 150, 8)
    assert set(out0) == set(ARMS) and json.loads(json.dumps(out0)) is not None
    cut = first[0].ds.dates[len(first[0].ds.dates) - CFG.holdout + 2]             # inside block 0: after its origin
    again = pooled_search_block(contexts(multi_panel(strength=0.02, perturb_after=cut), block=0), (0,), 150, 8)
    assert json.dumps(out0, sort_keys=True) == json.dumps(again, sort_keys=True)
    for pool, members in (("x", ("T1", "T2", "HYG")), (pooled.ALL, TARGETS)):
        for b in range(2):
            path = pooled.store_path("weekly", "return_h1", pool, b, str(tmp_path))
            (tmp_path / "weekly" / "return_h1" / pool).mkdir(parents=True, exist_ok=True)
            with open(path, "w") as fh:
                json.dump(pooled_search_block(contexts(p, block=b, targets=members), (0,), 150, 8), fh)
    pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = str(tmp_path), {t: "x" for t in TARGETS}, {}
    try:
        methods = ["iba_e1", "iba_rnda", "iba_rndw", "iba_sna", "iba_snw", "iba_ca", "iba_cw", "iba_cna", "iba_cnw", "iba_fa", "iba_fw", "iba_fna", "iba_fnw"]
        for tgt in ("T1", "HYG"):
            pred, meta = run_cell(p, Task(tgt, "return", 1), methods, estimators=("lin",), cfg=CFG, seeds=(0,), with_garch=False)
            cols = [c for c in pred.columns if c.startswith("iba_")]
            arms = [(l, a) for l in "scf" for a in ARMS if not (l == "s" and a in ("a", "w"))]      # per-series greedy = the earlier specs
            want = {"iba_rnda.s0", "iba_rndw.s0"} | {f"iba_{l}{a}{t}" for l, a in arms for t in (".s0|lin", "_r.s0|lin", "_b.s0")}
            assert want <= set(cols) and np.isfinite(pred[cols].values).all()
            for b in meta["blocks"]:
                rows = (pred["block"] == b["block"]).values
                for l, a in arms:
                    info = b["methods"][f"iba_{l}{a}.s0"]
                    assert info["members"] == (1 if l == "s" else 3) and "clean_best" in info
                    if not info["accepted"]:
                        np.testing.assert_allclose(pred.loc[rows, f"iba_{l}{a}.s0|lin"].values, pred.loc[rows, "iba_e1|lin"].values, rtol=1e-9, atol=1e-12)
    finally:
        pooled.STORE_DIR, pooled.POOL_OF, pooled._LOADED = None, {}, {}


def test_per_series_noise_aware_arms_have_no_look_ahead():
    task = Task("T1", "return", 4)
    methods = ["iba_e1", "iba_rnda", "iba_rndw", "iba_sna", "iba_snw"]
    pa, _ = run_cell(multi_panel(strength=0.02), task, methods, estimators=("lin",), cfg=CFG, seeds=(0,), with_garch=False)
    cut = pa["date"].iloc[len(pa) // 2 - 1]
    pb, _ = run_cell(multi_panel(strength=0.02, perturb_after=cut), task, methods, estimators=("lin",), cfg=CFG, seeds=(0,), with_garch=False)
    cols = [c for c in pa.columns if c not in ("date", "y", "y_eval", "block")]
    early = (pa["date"] <= cut).values
    np.testing.assert_array_equal(pa.loc[early, cols].values, pb.loc[early, cols].values)
    assert not np.allclose(pa.loc[~early, cols].values, pb.loc[~early, cols].values)


def test_comparator_algorithms_run_on_the_pooled_fitness_in_the_anchored_space():
    ctxs = contexts(multi_panel(strength=0.02), block=0)
    arms = ("a", "ga", "pso", "sa", "de")
    out = pooled_search_block(ctxs, (0, 1), 150, 8, arms=arms)
    assert tuple(out) == arms and json.dumps(out, sort_keys=True) == json.dumps(pooled_search_block(ctxs, (0, 1), 150, 8, arms=arms), sort_keys=True)
    ev = make_evaluator(ctxs, "de")
    assert ev.space.max_distance == 4                                       # the comparators search the ball around the prior
    for arm in arms:
        for r in out[arm].values():
            assert r["members"] == len(ctxs) and 0.8 * 150 <= r["n_evals"] <= 150
            assert {"inner_best", "inner_prior", "clean_best", "clean_prior", "clean_rows"} <= set(r["diag"])
            assert r["diag"]["fitness_best"] <= r["diag"]["fitness_prior"] + 1e-12 and r["diag"]["distance"] <= 4
