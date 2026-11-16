"""ABC over the whole space (SPEC-2026-11-14-abc-v2): the vector codec, graded conjunctions and
their agreement with crisp formulas at the corners of the box, budgets, determinism, the start
positions, and that no forecast of the new methods depends on later data. All on synthetic data."""
import numpy as np
import pytest

from iba.models.reducers import GradedIBAReducer, IBAReducer, graded_conjunction
from iba.protocol.dataset import Task
from iba.protocol.walkforward import run_cell
from iba.search.fitness import FitnessEvaluator
from iba.search.space import SearchSpace
from iba.search.vector import GradedEvaluator, VectorCodec, abc_full, abc_graded, abc_vector

from .test_engine import CFG as ENGINE_CFG, panel
from .test_search import context, planted_panel


def setup(allow_empty=True, kind="return", h=1, seed=0, strength=0.03):
    ctx = context(planted_panel(seed=seed, strength=strength), Task("T1", kind, h))
    sp = SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None, allow_empty=allow_empty)
    return ctx, sp, FitnessEvaluator(ctx, sp, mode="A")


def test_codec_round_trip_cap_and_empty_formula():
    ctx, sp, _ = setup()
    rng = np.random.default_rng(0)
    codec = VectorCodec(sp, tau=0.5)
    assert codec.D == sum(len(c) for c in sp.cols)
    for _ in range(200):
        s = sp.random_solution(rng)
        assert sp.valid(s) and codec.decode(codec.encode(s, rng)) == s
    assert codec.decode(codec.exact(sp.prior)) == sp.prior
    x = np.zeros(codec.D); x[:4] = [0.9, -0.8, 0.7, 0.6]              # four predicates of one group: keep the three largest
    assert codec.decode(x)[0] == frozenset({(0, True), (1, False), (2, True)})
    assert all(g is None for g in codec.decode(np.zeros(codec.D)))      # zero = nothing used
    strict = VectorCodec(SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None), tau=0.5)
    y = np.zeros(codec.D); y[5] = -0.2
    only = strict.decode(y)                                             # without the empty formula: the strongest coordinate
    assert sum(g is not None for g in only) == 1 and sp.n_literals(only) == 1


def test_whole_space_has_no_leash_but_keeps_the_literal_cap():
    ctx, sp, _ = setup(allow_empty=False)
    rng = np.random.default_rng(1)
    s, far = sp.prior, 0
    for _ in range(600):
        s = sp.neighbour(s, rng)
        assert sp.valid(s) and all(g is None or 1 <= len(g) <= sp.max_literals for g in s)
        far = max(far, sp.distance(s))
    assert far > 4                                                      # the first spec's bound was 4
    assert not sp.valid(tuple(None for _ in sp.groups)) and SearchSpace(ctx.ds.group_cols, ctx.prior, allow_empty=True).valid(tuple(None for _ in sp.groups))


def test_graded_conjunction_is_a_convex_combination_and_crisp_at_the_corners():
    rng = np.random.default_rng(2)
    Z = rng.uniform(0.01, 0.99, size=(50, 3))
    w = np.array([0.6, -0.3, 0.05])                                     # the third weight is below delta: not used
    u1, u2 = 0.6, 0.3
    l1, l2 = Z[:, 0], 1 - Z[:, 1]
    expanded = (1 - u1) * (1 - u2) + u1 * (1 - u2) * l1 + (1 - u1) * u2 * l2 + u1 * u2 * l1 * l2
    np.testing.assert_allclose(graded_conjunction(Z, w, 0.1), expanded, rtol=0, atol=1e-14)
    np.testing.assert_allclose(graded_conjunction(Z, np.array([1.0, -1.0, 0.0])), Z[:, 0] * (1 - Z[:, 1]), atol=1e-15)
    f = graded_conjunction(Z, rng.uniform(-1, 1, 3))
    assert (f >= 0).all() and (f <= 1).all()


def test_graded_evaluator_and_reducer_agree_with_the_crisp_ones_at_the_corners():
    ctx, sp, ev = setup()
    gev = GradedEvaluator(ev, delta=0.1)
    rng = np.random.default_rng(3)
    for sol in [sp.prior] + [sp.random_solution(rng) for _ in range(10)]:
        w = gev.codec.exact(sol)
        for f in range(len(ctx.folds)):
            np.testing.assert_allclose(gev.features(f, w), ev.features(f, sol), atol=1e-14)
    a, b = gev.evaluate(gev.prior_w), ev.evaluate(sp.prior)
    assert a["inner"] == pytest.approx(b["inner"], abs=1e-14) and a["fitness"] == pytest.approx(b["fitness"], abs=1e-14)
    assert gev.features(0, np.zeros(gev.D)).shape[1] == 0 and np.isfinite(gev.evaluate(np.zeros(gev.D))["fitness"])
    X = ctx.ds.X.iloc[ctx.rows]
    off = gev.off
    weights = {g: gev.prior_w[off[i]: off[i + 1]] for i, g in enumerate(sp.groups)}
    np.testing.assert_allclose(GradedIBAReducer(ctx.ds.group_cols, weights).fit(X).transform(X),
                               IBAReducer(ctx.ds.group_cols, sp.to_formula(sp.prior)).fit(X).transform(X), atol=1e-14)
    assert GradedIBAReducer(ctx.ds.group_cols, {g: np.zeros(len(c)) for g, c in ctx.ds.group_cols.items()}).fit(X).transform(X).shape == (len(X), 0)


@pytest.mark.parametrize("algo", ["w", "v", "g", "z"])
def test_whole_space_searches_spend_the_budget_and_are_deterministic(algo):
    def run(seed):
        ctx, sp, ev = setup(allow_empty=algo != "w")
        if algo == "w":
            return abc_full(ev, sp, budget=250, seed=seed, colony=8), sp
        if algo == "v":
            return abc_vector(ev, sp, budget=250, seed=seed, colony=8, mr=0.1), sp
        return abc_graded(GradedEvaluator(ev), budget=250, seed=seed, colony=8, start="spread" if algo == "g" else "zero"), sp
    (a, sp), (b, _), (c, _) = run(0), run(0), run(1)
    assert 200 <= a.n_evals <= 250 and a.diag["inner_best"] <= a.diag["inner_prior"] + (1e-12 if algo != "z" else np.inf)
    if algo in ("w", "v"):
        assert a.best == b.best and a.population == b.population and sp.valid(a.best) and all(sp.valid(s) for s in a.population)
        assert a.chosen == (a.best if a.accepted else sp.prior)
    else:
        np.testing.assert_array_equal(a.best, b.best)
        assert (np.abs(a.best) <= 1).all() and len(a.population) == 8 and (a.chosen is None) == (not a.accepted)
        assert not np.array_equal(a.best, c.best)
    assert {"inner_best", "outer_best", "optimism", "groups", "empty", "colony_distinct"} <= set(a.diag)


def test_zero_start_begins_at_the_empty_formula_and_spread_start_contains_the_prior():
    ctx, sp, ev = setup()
    gev = GradedEvaluator(ev)
    z = abc_graded(gev, budget=9, seed=0, colony=8, start="zero")       # the prior and the 8 sources, no move yet
    assert z.n_evals == 9 and all(not (gev.inclusion(x) > 0).any() for x in z.population) and z.diag["empty"] == 1.0
    ctx, sp, ev = setup()
    gev = GradedEvaluator(ev)
    g = abc_graded(gev, budget=8, seed=0, colony=8, start="spread")
    np.testing.assert_array_equal(g.population[0], gev.prior_w)
    assert all((np.abs(x) > 0.1).mean() > 0.5 for x in g.population[1:])  # uniform positions in the box


def test_whole_space_searches_improve_the_inner_fitness_of_a_planted_signal():
    for algo in ("w", "v", "g"):
        ctx, sp, ev = setup(allow_empty=algo != "w", strength=0.05)
        if algo == "w":
            r = abc_full(ev, sp, budget=600, seed=0)
        elif algo == "v":
            r = abc_vector(ev, sp, budget=600, seed=0, mr=0.1)
        else:
            r = abc_graded(GradedEvaluator(ev), budget=600, seed=0)
        assert r.diag["inner_best"] < 0.97 * r.diag["inner_prior"], algo


@pytest.mark.parametrize("task", [Task("T1", "return", 4), Task("T1", "logrv", 1), Task("T1", "tail_loss", 4, 0.2)])
def test_new_methods_run_in_the_engine_without_look_ahead(task):
    methods = ["iba_e1", "iba_ar", "iba_ac", "iba_w", "iba_v", "iba_g", "iba_z"]
    pa, meta = run_cell(panel(), task, methods, estimators=("lin",), cfg=ENGINE_CFG, seeds=(0,), with_garch=False)
    cut = pa["date"].iloc[len(pa) // 2 - 1]
    pb, _ = run_cell(panel(perturb_after=cut), task, methods, estimators=("lin",), cfg=ENGINE_CFG, seeds=(0,), with_garch=False)
    cols = [c for c in pa.columns if c not in ("date", "y", "y_eval", "block")]
    want = {"iba_ar.s0|lin", "iba_ac.s0|lin"} | {f"iba_{m}{t}.s0|lin" for m in "wvgz" for t in ("", "r")} | {f"iba_{m}b.s0" for m in "wvgz"}
    assert want <= set(cols) and np.isfinite(pa[cols].values).all()
    early = (pa["date"] <= cut).values
    np.testing.assert_array_equal(pa.loc[early, cols].values, pb.loc[early, cols].values)
    assert not np.allclose(pa.loc[~early, cols].values, pb.loc[~early, cols].values)
    for b in meta["blocks"]:                                            # a winner that is not accepted is the prior: E1's forecasts
        rows = (pa["block"] == b["block"]).values
        for m in ("ac", "w", "v", "g", "z"):
            info = b["methods"][f"iba_{m}.s0"]
            assert info["n_evals"] <= ENGINE_CFG.search_budget and "clean_best" in info
            if not info["accepted"]:
                np.testing.assert_allclose(pa.loc[rows, f"iba_{m}.s0|lin"].values, pa.loc[rows, "iba_e1|lin"].values, rtol=1e-9, atol=1e-12)


def test_clean_outer_rows_share_no_label_with_the_search_and_the_test_uses_only_them():
    for h in (1, 4, 13):
        ctx = context(planted_panel(n=900), Task("T1", "return", h))
        sp = SearchSpace(ctx.ds.group_cols, ctx.prior)
        ev = FitnessEvaluator(ctx, sp, mode="A", clean_outer=True)
        outer_rows = ctx.folds[ev.outer][1]
        used = np.concatenate([ctx.folds[f][1] for f in ev.fit_folds])
        assert len(set(outer_rows) & set(used)) > 0                      # the whole fold is NOT clean (overlapping windows)
        clean = outer_rows[ev.clean]
        assert len(clean) >= 2 and clean.min() >= used.max() + h           # label windows (j+1..j+h) are disjoint
        cand = sp.neighbour(sp.prior, np.random.default_rng(0))
        d = ev.outer_pointwise(sp.prior) - ev.outer_pointwise(cand)
        got = ev.acceptance(cand)
        from iba.search.fitness import one_se_test
        assert got == one_se_test(d[ev.clean], h)
        r = ev.evaluate(cand, with_outer=True)
        assert r["clean"] == pytest.approx(float(np.mean(ev.outer_pointwise(cand)[ev.clean])))
        whole = FitnessEvaluator(ctx, sp, mode="A")                      # the first spec's test: the whole fold
        assert whole.acceptance(cand) == one_se_test(d, h)
        dd = FitnessEvaluator(ctx, sp, mode="D", clean_outer=True)       # with a penalty fold, its rows are excluded too
        assert ctx.folds[dd.outer][1][dd.clean].min() >= ctx.folds[dd.penalty][1].max() + h
