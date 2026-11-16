"""Pooled fitness and noise-aware replacement (SPEC-2026-11-14-abc-v3).

Pooled fitness. One formula for a POOL of series (an asset class, or every series of a frequency)
at one block origin. Within a frequency and task all series share their rows, so the selection
folds are the same rows for every member. A formula is written in generic column names (the
target's own columns are ``__target___<suffix>``) over the union of the members' columns; for a
member that lacks a column (a factor excluded for that target) the literal is dropped, exactly as
the prior formula is built. Every member keeps its own linear model. All losses are divided by
the member's fitness-fold loss under the prior, so that every member counts the same:
    fitness = mean over members of [fitness-fold loss / the prior's] + kappa * literals in excess of the prior
(with one member this orders formulas exactly as ``FitnessEvaluator`` does). The acceptance test
is the one-standard-error rule on the CLEAN outer rows of the per-date mean over members.

Noise-aware replacement. The per-date profile of a formula is its normalised pointwise loss on
the fitness folds' validation rows, averaged over the folds that contain the date and over the
members. A candidate replaces a food source only if the mean of (source profile - candidate
profile), less the change in the literal penalty, exceeds one standard error of non-overlapping
block means: the acceptance rule, applied inside the search. The winner is the best state the
colony has held that passes the same test against the prior; if none does, the prior."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .algorithms import ALGORITHMS, SearchResult, _finish, abc
from .fitness import FitnessEvaluator, one_se_test
from .space import SearchSpace, Solution
from .vector import _colony_diag, abc_full

TARGET = "__target__"
Formula = Dict[str, Tuple[List[str], List[str]]]


# ----------------------------------------------------------------------------- generic names
def generic_groups(datasets: Sequence) -> Dict[str, List[str]]:
    """Union of the members' group columns in order of first appearance; ENDG in generic names."""
    out: Dict[str, List[str]] = {}
    for ds in datasets:
        tgt = ds.task.target
        for g, cols in ds.group_cols.items():
            names = [TARGET + c[len(tgt):] for c in cols] if g == "ENDG" else list(cols)
            have = out.setdefault(g, [])
            have.extend(c for c in names if c not in have)
    return out


def generic_formula(formula: Formula, target: str) -> Formula:
    return {g: tuple([TARGET + c[len(target):] if g == "ENDG" else c for c in part] for part in (a, n)) for g, (a, n) in formula.items()}


def own_formula(gformula: Formula, ds) -> Formula:
    """A generic formula in one member's column names; literals on columns it lacks are dropped."""
    tgt, out = ds.task.target, {}
    for g, (a, n) in gformula.items():
        if g not in ds.group_cols:
            continue
        have = set(ds.group_cols[g])
        aa, nn = ([c for c in ([tgt + x[len(TARGET):] if g == "ENDG" else x for x in part]) if c in have] for part in (a, n))
        if aa or nn:
            out[g] = (aa, nn)
    return out


def pooled_prior(ctxs: Sequence) -> Formula:
    """Union of the members' priors in generic names (= the formula file on the union of columns)."""
    out: Dict[str, Tuple[List[str], List[str]]] = {}
    for ctx in ctxs:
        for g, (a, n) in generic_formula(ctx.prior, ctx.ds.task.target).items():
            ha, hn = out.setdefault(g, ([], []))
            ha.extend(c for c in a if c not in ha); hn.extend(c for c in n if c not in hn)
    return out


# ----------------------------------------------------------------------------- evaluation
class Member:
    """One series of a pool: its scaled predicates per fold and the map from generic to own columns."""

    def __init__(self, ctx, gspace: SearchSpace):
        self.fe = FitnessEvaluator(ctx, SearchSpace(ctx.ds.group_cols, ctx.prior), mode="A", clean_outer=True)
        tgt, own = ctx.ds.task.target, ctx.ds.group_cols
        own_groups = list(own)
        self.gmap, self.cmap = [], []
        for g, cols in zip(gspace.groups, gspace.cols):
            if g not in own:
                self.gmap.append(-1); self.cmap.append(np.full(len(cols), -1)); continue
            self.gmap.append(own_groups.index(g))
            names = [tgt + c[len(TARGET):] if g == "ENDG" else c for c in cols]
            self.cmap.append(np.array([own[g].index(c) if c in own[g] else -1 for c in names]))

    def features(self, f: int, sol: Solution) -> np.ndarray:
        cols = []
        for gi, s in enumerate(sol):
            if s is None or self.gmap[gi] < 0:
                continue
            Z, v = self.fe.S[f][self.gmap[gi]], None
            for j, pol in sorted(s):
                oj = self.cmap[gi][j]
                if oj >= 0:
                    x = Z[:, oj] if pol else 1.0 - Z[:, oj]
                    v = x if v is None else v * x
            if v is not None:
                cols.append(v)
        return np.column_stack(cols) if cols else np.zeros((self.fe.S[f][0].shape[0], 0))

    def pointwise(self, f: int, sol: Solution) -> np.ndarray:
        return self.fe._fold_pointwise(f, self.features(f, sol))


class PooledEvaluator:
    """The evaluator interface the ABC functions use (evaluate / acceptance / n_evals / cache / clean),
    for one or several members. ``n_evals`` counts distinct formulas: one unit of the budget is one
    formula evaluated on every member."""

    def __init__(self, members: List[Member], space: SearchSpace, kappa: float = 0.005):
        self.members, self.space, self.kappa = members, space, kappa
        fe = members[0].fe
        self.h, self.fit_folds, self.outer, self.clean, self.clean_outer = fe.h, fe.fit_folds, fe.outer, fe.clean, True
        for m in members[1:]:                                   # same rows for every member
            if len(m.fe.folds) != len(fe.folds) or any(not np.array_equal(a[1], b[1]) for a, b in zip(m.fe.folds, fe.folds)):
                raise ValueError("the members of a pool must share their selection folds")
        self.rows = np.unique(np.concatenate([fe.folds[f][1] for f in self.fit_folds]))
        self.pos = {f: np.searchsorted(self.rows, fe.folds[f][1]) for f in self.fit_folds}
        self.count = np.zeros(len(self.rows))
        for f in self.fit_folds:
            self.count[self.pos[f]] += 1.0
        self.cache: Dict = {}
        self.n_evals = 0
        self._prior_literals = space.n_literals(space.prior)
        inner, prof = self._raw(space.prior)                    # the prior fixes every member's scale
        self.norm = np.where(inner > 0, inner, 1.0)
        self._prior_raw = (inner, prof)

    def _raw(self, sol: Solution):
        inner = np.zeros(len(self.members))
        prof = np.zeros((len(self.members), len(self.rows)))
        for m, mem in enumerate(self.members):
            for f in self.fit_folds:
                pw = mem.pointwise(f, sol)
                inner[m] += float(pw.mean()) / len(self.fit_folds)
                prof[m, self.pos[f]] += pw
        return inner, prof / self.count

    def evaluate(self, sol: Solution, with_outer: bool = False) -> Dict[str, Any]:
        k = self.space.key(sol)
        r = self.cache.get(k)
        if r is None:
            inner, prof = self._prior_raw if sol == self.space.prior else self._raw(sol)
            rel = float(np.mean(inner / self.norm))
            excess = max(0, self.space.n_literals(sol) - self._prior_literals)
            r = {"inner": rel, "penalty_term": self.kappa * excess, "fitness": rel + self.kappa * excess,
                 "profile": (prof / self.norm[:, None]).mean(axis=0)}
            self.cache[k] = r
            self.n_evals += 1
        if with_outer and "outer" not in r and self.outer is not None:
            op = np.mean([mem.pointwise(self.outer, sol) / self.norm[m] for m, mem in enumerate(self.members)], axis=0)
            r["outer_profile"] = op
            r["outer"] = float(op.mean())
            r["clean"] = float(op[self.clean].mean()) if len(self.clean) else float("nan")
        return r

    def acceptance(self, cand: Solution) -> Dict[str, float]:
        if cand == self.space.prior or self.outer is None:
            return {"accepted": False, "gain": 0.0, "se": 0.0}
        if len(self.clean) < 2:
            return {"accepted": False, "gain": float("nan"), "se": float("nan")}
        d = self.evaluate(self.space.prior, with_outer=True)["outer_profile"] - self.evaluate(cand, with_outer=True)["outer_profile"]
        return one_se_test(d[self.clean], self.h)

    def better(self, cand: Solution, src: Solution) -> bool:
        """Noise-aware comparison on the fitness rows: cand beats src by more than one standard error."""
        rc, rs = self.evaluate(cand), self.evaluate(src)
        t = one_se_test(rs["profile"] - rc["profile"], self.h)
        return bool(t["gain"] - (rc["penalty_term"] - rs["penalty_term"]) > t["se"])


# ----------------------------------------------------------------------------- noise-aware ABC
def abc_noise_aware(ev: PooledEvaluator, space: SearchSpace, budget: int = 2000, seed: int = 0, colony: int = 20,
                    limit: int = 10, start: str = "anchored") -> SearchResult:
    """The discrete ABC with the replacement rule ``ev.better``. ``start="anchored"``: the colony of
    ``algorithms.abc`` (the prior and its neighbours, scouts next to the prior); ``"spread"``: the
    colony of ``vector.abc_full`` (the prior and random formulas, scouts at random formulas)."""
    if start not in ("anchored", "spread"):
        raise ValueError(start)
    rng = np.random.default_rng(seed)
    sources = initial_colony(space, rng, colony, start)
    fit = [ev.evaluate(s)["fitness"] for s in sources]
    held = {space.key(s): s for s in sources}
    trials = [0] * colony
    stall = 0
    while ev.n_evals < budget and stall < 50:
        before = ev.n_evals

        def attempt(i):
            cand = space.neighbour(sources[i], rng)
            f = ev.evaluate(cand)["fitness"]
            if cand != sources[i] and ev.better(cand, sources[i]):
                sources[i], fit[i], trials[i] = cand, f, 0
                held[space.key(cand)] = cand
            else:
                trials[i] += 1

        for i in range(colony):
            if ev.n_evals >= budget:
                break
            attempt(i)
        order = np.argsort(np.argsort(fit))
        prob = (colony - order).astype(float); prob /= prob.sum()
        for _ in range(colony):
            if ev.n_evals >= budget:
                break
            attempt(int(rng.choice(colony, p=prob)))
        for i in range(colony):
            if trials[i] > limit and ev.n_evals < budget:
                sources[i] = space.near_prior(rng, steps=1 + int(rng.integers(2))) if start == "anchored" else space.random_solution(rng)
                fit[i] = ev.evaluate(sources[i])["fitness"]; trials[i] = 0
                held[space.key(sources[i])] = sources[i]
        stall = stall + 1 if ev.n_evals == before else 0
    best, bf = space.prior, ev.evaluate(space.prior)["fitness"]
    for k in sorted(held, key=lambda k: ev.cache[k]["fitness"]):     # best fitness first; the first that passes wins
        s = held[k]
        if s != space.prior and ev.cache[k]["fitness"] < bf and ev.better(s, space.prior):
            best = s
            break
    res = _colony_diag(_finish(f"abc_noise_aware/{start}", ev, space, best, list(sources), []), space)
    res.diag["held"] = float(len(held))
    return res


def initial_colony(space: SearchSpace, rng: np.random.Generator, colony: int, start: str) -> List[Solution]:
    """The starting colony of ``algorithms.abc`` ("anchored") or of ``vector.abc_full`` ("spread")."""
    if start == "spread":
        return [space.prior] + [space.random_solution(rng) for _ in range(colony - 1)]
    sources, seen, guard = [space.prior], {space.key(space.prior)}, 0
    while len(sources) < colony and guard < 50 * colony:
        s = space.near_prior(rng, steps=1 + int(guard > 10 * colony))
        guard += 1
        if space.key(s) not in seen:
            seen.add(space.key(s)); sources.append(s)
    while len(sources) < colony:
        sources.append(space.prior)
    return sources


# ----------------------------------------------------------------------------- one pool, one block
ARMS = {"a": ("anchored", False), "w": ("spread", False), "na": ("anchored", True), "nw": ("spread", True)}
COMPARATORS = ("ga", "pso", "sa", "de")   # SPEC-2026-11-14-wrapup: the other algorithms, same pooled fitness, anchored space, greedy


def run_arm(ev: PooledEvaluator, arm: str, budget: int, seed: int, colony: int) -> SearchResult:
    if arm in COMPARATORS:
        return ALGORITHMS[arm](ev, ev.space, budget=budget, seed=seed)
    start, noise = ARMS[arm]
    if noise:
        return abc_noise_aware(ev, ev.space, budget=budget, seed=seed, colony=colony, start=start)
    if start == "anchored":
        return abc(ev, ev.space, budget=budget, seed=seed, colony=colony)
    return abc_full(ev, ev.space, budget=budget, seed=seed, colony=colony)


def make_evaluator(ctxs: Sequence, arm: str, members: Optional[List[Member]] = None) -> PooledEvaluator:
    """Evaluator of a pool for one arm: the first study's ball around the prior for anchored starts,
    the whole space for spread starts. ``members`` built for one arm can be reused for the others."""
    groups, prior = generic_groups([c.ds for c in ctxs]), pooled_prior(ctxs)
    anchored = arm in COMPARATORS or ARMS[arm][0] == "anchored"
    space = SearchSpace(groups, prior) if anchored else SearchSpace(groups, prior, max_distance=None)
    return PooledEvaluator(members or [Member(c, space) for c in ctxs], space)


def pooled_search_block(ctxs: Sequence, seeds: Sequence[int], budget: int, colony: int, arms: Sequence[str] = tuple(ARMS)) -> Dict[str, Any]:
    """Every arm and seed for one pool at one block origin. Formulas are returned in generic names."""
    out: Dict[str, Any] = {}
    members = None
    for arm in arms:
        out[arm] = {}
        for s in seeds:
            ev = make_evaluator(ctxs, arm, members)
            members = ev.members
            res = run_arm(ev, arm, budget, s, colony)
            sp = ev.space
            out[arm][str(s)] = {"best": sp.to_formula(res.best), "accepted": bool(res.accepted), "n_evals": int(res.n_evals),
                                "population": [sp.to_formula(x) for x in res.population], "best_text": sp.text(res.best),
                                "diag": {k: float(v) for k, v in res.diag.items()}, "members": len(ev.members)}
    return out


# ----------------------------------------------------------------------------- store (stage 5 -> stage 6)
STORE_DIR: Optional[str] = None           # set by the runner in every worker
POOL_OF: Dict[str, str] = {}              # target -> name of its asset-class pool (set by the runner)
ALL = "ALL"                               # the pool of every development series of the frequency
_LOADED: Dict[str, Any] = {}


def store_path(frequency: str, task_name: str, pool: str, block: int, base: Optional[str] = None) -> str:
    return os.path.join(base or STORE_DIR, frequency, task_name, pool, f"block{block}.json")


def load_block(frequency: str, task_name: str, pool: str, block: int) -> Dict[str, Any]:
    if STORE_DIR is None:
        raise RuntimeError("pooled formulas requested but iba.search.pooled.STORE_DIR is not set")
    p = store_path(frequency, task_name, pool, block)
    if p not in _LOADED:
        with open(p) as fh:
            _LOADED[p] = json.load(fh)
    return _LOADED[p]
