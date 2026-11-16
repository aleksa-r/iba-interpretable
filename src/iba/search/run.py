"""Glue between the walk-forward engine and the searches: one call per (method, block).

Methods (names used in configurations):
  iba_x     exhaustive atoms (the published search) with the linear fitness   -> "iba_x|lin", "iba_x|gbt"
  iba_xlo   exhaustive low-order conjunctions with the one-standard-error rule
  iba_a     ABC refinement of the prior (A)              -> "iba_a.s<seed>|lin" (+ "|gbt" for the first seed)
  iba_d     A with the over-fitting-penalised fitness (D)
  iba_b     the final colony of A as an ensemble (B)     -> "iba_b.s<seed>"
  iba_c     logical aggregation with a two-parameter link (C)  -> "iba_c.s<seed>"
  iba_ga / iba_pso / iba_sa   comparators at the same budget; iba_agv = A with global validation
SPEC-2026-11-14-abc-v2 (ABC over the whole space; every search gives three configurations:
"<m>.s<seed>|lin" the winner if it passed the acceptance test, else the prior; "<m>r.s<seed>|lin"
the winner without the test (diagnostic); "<m>b.s<seed>" the final colony as an ensemble):
  iba_w     discrete moves, colony started at the prior and at random formulas, no leash
  iba_v     vector moves on crisp formulas, same start, empty formula allowed
  iba_g     vector moves on graded formulas, colony started at the prior and uniformly in the box
  iba_z     the same started at zero (the empty formula)
  iba_ar    the winner of A without the acceptance test (diagnostic)
  iba_ac    the winner of A with the acceptance test on the clean outer rows (the first spec's test
            used the whole outer fold, most of whose rows the search had already used)
SPEC-2026-11-14-abc-v3 (every search arm gives "<m>.s<seed>|lin" tested winner or prior,
"<m>_r.s<seed>|lin" winner without the test, "<m>_b.s<seed>" colony ensemble). Arm = start
(a anchored at the prior as A, w spread as W) with or without noise-aware replacement (n):
  iba_sna, iba_snw                     per series, noise-aware replacement
  iba_ca, iba_cw, iba_cna, iba_cnw     one formula per asset class (pooled fitness; read from stage 5)
  iba_fa, iba_fw, iba_fna, iba_fnw     one formula for every series of the frequency (stage 5)
  iba_rnda, iba_rndw                   controls: the STARTING colony of A / of W as an ensemble, no search
Searches see only the block's admissible rows through the BlockContext."""
from __future__ import annotations

import copy
import time
from typing import Any, Dict, Optional, Sequence

import numpy as np

from ..models.reducers import GradedIBAReducer, IBAReducer
from .aggregation import AggEvaluator, AggSpace, LinkEstimator, prior_aggregation
from .algorithms import ALGORITHMS, abc, exhaustive_atoms, exhaustive_low_order
from .fitness import FitnessEvaluator
from .space import SearchSpace
from .vector import GradedEvaluator, abc_full, abc_graded, abc_vector
from . import pooled

# SPEC-2026-11-14-abc-v2: the settings of the four whole-space searches (fixed in the spec)
WHOLE = {"w": dict(space=dict(max_distance=None)),
         "v": dict(space=dict(max_distance=None, allow_empty=True), mr=1.0, tau=0.5),
         "g": dict(space=dict(max_distance=None, allow_empty=True), start="spread", mr=1.0, delta=0.1),
         "z": dict(space=dict(max_distance=None, allow_empty=True), start="zero", mr=1.0, delta=0.1)}


def _evaluator(ctx, mode: str, space_kw: Optional[dict] = None, clean: bool = False) -> FitnessEvaluator:
    """One evaluator per (block, mode) holds the scaled predicate matrices; every search run gets
    a fresh copy with an empty cache so that budgets are counted per run. ``space_kw`` swaps in a
    space with other bounds around the same prior (the matrices do not depend on the bounds)."""
    store = ctx.__dict__.setdefault("_ev", {})
    if mode not in store:
        space = SearchSpace(ctx.ds.group_cols, ctx.prior)
        store[mode] = FitnessEvaluator(ctx, space, mode=mode)
    ev = copy.copy(store[mode])
    ev.cache, ev.n_evals, ev._prior_fit = {}, 0, None
    if space_kw:
        ev.space = SearchSpace(ctx.ds.group_cols, ctx.prior, **space_kw)
    ev.clean_outer = clean                                 # acceptance on the outer rows the search has not used
    return ev


def search(ctx, algo: str, mode: str, seed: int, select: str = "inner"):
    store = ctx.__dict__.setdefault("_res", {})
    key = (algo, mode, seed, select)
    if key not in store and algo in WHOLE:
        kw = WHOLE[algo]
        ev = _evaluator(ctx, mode, kw["space"], clean=True)
        tic = time.perf_counter()
        b, c = ctx.cfg.search_budget, ctx.cfg.colony
        if algo == "w":
            res = abc_full(ev, ev.space, budget=b, seed=seed, colony=c)
        elif algo == "v":
            res = abc_vector(ev, ev.space, budget=b, seed=seed, colony=c, mr=kw["mr"], tau=kw["tau"])
        else:
            gev = GradedEvaluator(ev, delta=kw["delta"])
            res = abc_graded(gev, budget=b, seed=seed, colony=c, start=kw["start"], mr=kw["mr"])
            res.diag["text_best"] = gev.text(res.best)
        res.diag["seconds"] = time.perf_counter() - tic
        store[key] = (res, ev.space)
    if key not in store:
        ev = _evaluator(ctx, mode)
        tic = time.perf_counter()
        if algo == "abc":
            res = abc(ev, ev.space, budget=ctx.cfg.search_budget, seed=seed, colony=ctx.cfg.colony, select=select)
        elif algo == "x":
            res = exhaustive_atoms(ev, ev.space)
        elif algo == "xlo":
            res = exhaustive_low_order(ev, ev.space)
        else:
            res = ALGORITHMS[algo](ev, ev.space, budget=ctx.cfg.search_budget, seed=seed)
        res.diag["seconds"] = time.perf_counter() - tic
        store[key] = (res, ev.space)
    return store[key]


def _info(res, space) -> Dict[str, Any]:
    return {"algorithm": res.algorithm, "accepted": res.accepted, "n_evals": res.n_evals,
            "chosen": space.text(res.chosen), "best": space.text(res.best), **{k: float(v) for k, v in res.diag.items()}}


def _pair(make, ctx):
    """A reducer fitted on the block's admissible rows and one per fold on that fold's training rows."""
    return make().fit(ctx.ds.X.iloc[ctx.rows]), [make().fit(ctx.ds.X.iloc[tr]) for tr, _ in ctx.folds]


def _pooled_method(method: str, ctx, seeds: Sequence[int], bmeta, red) -> Dict[str, Dict[str, Any]]:
    """An arm of SPEC-2026-11-14-abc-v3. Per-series arms (iba_s*) search here; pooled arms read the
    formulas that stage 5 found for the cell's pool at this block origin."""
    level, arm, task, out = method[4], method[5:], ctx.ds.task, {}
    if level == "s":
        store = ctx.__dict__.setdefault("_pooled", {})
        if arm not in store:
            store[arm] = pooled.pooled_search_block([ctx], seeds, ctx.cfg.search_budget, ctx.cfg.colony, arms=(arm,))[arm]
        found = store[arm]
    else:
        pool = pooled.POOL_OF[task.target] if level == "c" else pooled.ALL
        block = pooled.load_block(task.frequency, task.name, pool, bmeta["block"])
        rows = block.get("_meta", {}).get("train_rows")
        if rows is not None and int(rows) != len(ctx.rows):      # a formula found at another origin must not be used at this one
            raise ValueError(f"{task.target} {task.name} block {bmeta['block']}: the stored search of pool {pool} used {rows} rows, this cell has {len(ctx.rows)}")
        found = block[arm]
    for s in seeds:
        r = found[str(s)]
        best = pooled.own_formula(r["best"], ctx.ds)
        bmeta["methods"][f"{method}.s{s}"] = {"accepted": r["accepted"], "n_evals": r["n_evals"], "best": r["best_text"],
                                              "members": r["members"], **r["diag"]}
        for tag, formula in (("", best if r["accepted"] else ctx.prior), ("_r", best)):
            blk, fl = red("iba", formula)
            out[f"{method}{tag}.s{s}"] = {"type": "reducer", "block": blk, "folds": fl, "all_estimators": False}
        out[f"{method}_b.s{s}"] = {"type": "ensemble", "members": [red("iba", pooled.own_formula(f, ctx.ds)) for f in r["population"]]}
    return out


def _whole_space_method(method: str, ctx, seeds: Sequence[int], bmeta) -> Dict[str, Dict[str, Any]]:
    algo, out = method[4:], {}
    gc = ctx.ds.group_cols
    for s in seeds:
        res, space = search(ctx, algo, "A", s)
        if algo in ("g", "z"):                                # graded: candidates are weight vectors
            delta = WHOLE[algo]["delta"]
            off = np.cumsum([0] + [len(c) for c in space.cols])

            def graded(w, delta=delta, off=off, space=space):
                weights = {g: w[off[i]: off[i + 1]] for i, g in enumerate(space.groups)}
                return lambda: GradedIBAReducer(gc, weights, delta)

            prior = lambda space=space: IBAReducer(gc, space.to_formula(space.prior))
            makers = {"": graded(res.chosen) if res.chosen is not None else prior, "r": graded(res.best)}
            members = [_pair(graded(w), ctx) for w in res.population]
            text = res.diag.pop("text_best")
            info = {"algorithm": res.algorithm, "accepted": res.accepted, "n_evals": res.n_evals, "best": text,
                    "chosen": text if res.accepted else space.text(space.prior), **{k: float(v) for k, v in res.diag.items()}}
            res.diag["text_best"] = text
        else:
            crisp = lambda sol, space=space: (lambda: IBAReducer(gc, space.to_formula(sol)))
            makers = {"": crisp(res.chosen), "r": crisp(res.best)}
            members = [_pair(crisp(sol), ctx) for sol in res.population]
            info = _info(res, space)
        bmeta["methods"][f"{method}.s{s}"] = info
        for tag, make in makers.items():
            blk, fl = _pair(make, ctx)
            out[f"{method}{tag}.s{s}"] = {"type": "reducer", "block": blk, "folds": fl, "all_estimators": False}
        out[f"{method}b.s{s}"] = {"type": "ensemble", "members": members}
    return out


def build_search_method(method: str, ctx, seeds: Sequence[int], bmeta, red) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if method in ("iba_w", "iba_v", "iba_g", "iba_z"):
        return _whole_space_method(method, ctx, seeds, bmeta)
    if method in ("iba_rnda", "iba_rndw"):                    # the starting colony as an ensemble: no search, no fitness
        start = "anchored" if method.endswith("a") else "spread"
        space = SearchSpace(ctx.ds.group_cols, ctx.prior) if start == "anchored" else SearchSpace(ctx.ds.group_cols, ctx.prior, max_distance=None)
        for s in seeds:
            colony = pooled.initial_colony(space, np.random.default_rng(s), ctx.cfg.colony, start)
            out[f"{method}.s{s}"] = {"type": "ensemble", "members": [red("iba", space.to_formula(sol)) for sol in colony]}
        return out
    if method[:5] in ("iba_s", "iba_c", "iba_f") and method[5:] in pooled.ARMS:
        return _pooled_method(method, ctx, seeds, bmeta, red)
    if method in ("iba_ar", "iba_ac"):       # the winner of A without the acceptance test / with the test on clean rows
        for s in seeds:
            res, space = search(ctx, "abc", "A", s)
            sol = res.best
            if method == "iba_ac":
                acc = _evaluator(ctx, "A", clean=True).acceptance(res.best)
                sol = res.best if acc["accepted"] else space.prior
                bmeta["methods"][f"{method}.s{s}"] = {**_info(res, space), "accepted_whole_fold": res.accepted, "accepted": bool(acc["accepted"]),
                                                      "chosen": space.text(sol), "gain_outer": acc["gain"], "se_outer": acc["se"]}
            blk, fl = red("iba", space.to_formula(sol))
            out[f"{method}.s{s}"] = {"type": "reducer", "block": blk, "folds": fl, "all_estimators": False}
        return out
    if method in ("iba_x", "iba_xlo"):
        res, space = search(ctx, method[4:], "A", 0)
        blk, fl = red("iba", space.to_formula(res.chosen))
        bmeta["methods"][method] = _info(res, space)
        return {method: {"type": "reducer", "block": blk, "folds": fl}}
    if method in ("iba_a", "iba_d", "iba_ga", "iba_pso", "iba_sa", "iba_agv"):
        algo = {"iba_a": "abc", "iba_d": "abc", "iba_agv": "abc"}.get(method, method[4:])
        mode = "D" if method == "iba_d" else "A"
        for s in seeds:
            res, space = search(ctx, algo, mode, s, "outer" if method == "iba_agv" else "inner")
            blk, fl = red("iba", space.to_formula(res.chosen))
            name = f"{method}.s{s}"
            bmeta["methods"][name] = _info(res, space)
            out[name] = {"type": "reducer", "block": blk, "folds": fl,
                         "all_estimators": method in ("iba_a", "iba_d") and s == seeds[0]}
        return out
    if method == "iba_b":
        for s in seeds:
            res, space = search(ctx, "abc", "A", s)
            members = [red("iba", space.to_formula(sol)) for sol in res.population]
            name = f"{method}.s{s}"
            keys = [space.key(sol) for sol in res.population]
            lit_count: Dict = {}
            for sol in res.population:
                for gi, gs in enumerate(sol):
                    for lit in (gs or ()):
                        lit_count[(gi, lit)] = lit_count.get((gi, lit), 0) + 1
            stable = [f"{space.groups[gi]}:{space.cols[gi][j]}{'' if pol else ' NOT'}" for (gi, (j, pol)), c in sorted(lit_count.items())
                      if c >= 0.5 * len(res.population)]
            bmeta["methods"][name] = {"members": len(members), "distinct": len(set(keys)), "stable_literals": stable}
            out[name] = {"type": "ensemble", "members": members}
        return out
    if method == "iba_c":
        for s in seeds:
            fe = _evaluator(ctx, "A")
            aspace = AggSpace(fe.space, prior_aggregation(fe, fe.space))
            aev = AggEvaluator(fe, aspace)
            tic = time.perf_counter()
            res = abc(aev, aspace, budget=ctx.cfg.search_budget, seed=s, colony=ctx.cfg.colony)
            res.diag["seconds"] = time.perf_counter() - tic
            comps, w = res.chosen
            formula = {aspace.groups[g]: ([fe.space.cols[g][j] for j, pol in sorted(lits) if pol],
                                          [fe.space.cols[g][j] for j, pol in sorted(lits) if not pol]) for g, lits in comps}
            blk = IBAReducer(ctx.ds.group_cols, formula).fit(ctx.ds.X.iloc[ctx.rows])
            order = [list(blk.formula).index(aspace.groups[g]) for g, _ in comps]
            weights = np.array(w, dtype=float) / 10.0

            def feature(X, blk=blk, order=order, weights=weights):
                return (blk.transform(X)[:, order] @ weights).reshape(-1, 1)

            name = f"{method}.s{s}"
            bmeta["methods"][name] = {"algorithm": "abc/aggregation", "accepted": res.accepted, "n_evals": res.n_evals,
                                      "chosen": aspace.text(res.chosen), "best": aspace.text(res.best),
                                      **{k: float(v) for k, v in res.diag.items()}}
            out[name] = {"type": "direct", "model": LinkEstimator(ctx.est_task), "block_feature": feature}
        return out
    raise KeyError(f"unknown method '{method}'")
