"""Search algorithms over IBA structures, all behind one signature and one budget unit
(distinct fitness evaluations): ``search(ev, space, budget, seed, ...) -> SearchResult``.

  abc         modified Artificial Bee Colony anchored at the prior (employed / onlooker / scout)
  ga, pso, sa, de comparators at the same budget and fitness
  exhaustive_atoms, exhaustive_low_order   the published search and its low-order variant
The selected structure is ALWAYS the best by inner fitness; the outer fold is used once, for the
acceptance test against the prior (``ev.acceptance``), never for ranking candidates. The
"global validation" variant of the literature (rank everything on the outer fold) is available
as ``select="outer"`` and is a labelled secondary variant."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from .fitness import FitnessEvaluator
from .space import SearchSpace, Solution


@dataclass
class SearchResult:
    algorithm: str
    best: Solution                       # best by inner fitness
    chosen: Solution                     # after the acceptance rule (best or prior)
    accepted: bool
    population: List[Solution]           # final colony / population (for the ensemble)
    n_evals: int
    diag: Dict[str, float] = field(default_factory=dict)
    history: List[float] = field(default_factory=list)   # best fitness after each 100 evaluations


def _finish(name: str, ev: FitnessEvaluator, space: SearchSpace, best: Solution, pop: List[Solution],
            history: List[float], use_acceptance: bool = True, select: str = "inner") -> SearchResult:
    if select == "outer":                                     # "global validation" (secondary variant)
        scored = [(ev.evaluate(_unkey(k), with_outer=True)["outer"], k) for k in list(ev.cache)]
        best = _unkey(min(scored, key=lambda t: t[0])[1])
    acc = ev.acceptance(best) if use_acceptance else {"accepted": best != space.prior, "gain": float("nan"), "se": float("nan")}
    chosen = best if acc["accepted"] else space.prior
    rb, rp = ev.evaluate(best, with_outer=True), ev.evaluate(space.prior, with_outer=True)
    diag = {"inner_best": rb["inner"], "outer_best": rb.get("outer", float("nan")), "inner_prior": rp["inner"],
            "outer_prior": rp.get("outer", float("nan")), "fitness_best": rb["fitness"], "fitness_prior": rp["fitness"],
            "gain_outer": acc["gain"], "se_outer": acc["se"], "distance": space.distance(best),
            "clean_best": rb.get("clean", float("nan")), "clean_prior": rp.get("clean", float("nan")), "clean_rows": float(len(getattr(ev, "clean", ()))),
            "literals": space.n_literals(best),
            # optimism of the search: how much more the winner loses from inner to outer than the prior does
            "optimism": (rb.get("outer", np.nan) - rb["inner"]) - (rp.get("outer", np.nan) - rp["inner"])}
    return SearchResult(name, best, chosen, bool(acc["accepted"]), pop, ev.n_evals, diag, history)


def _unkey(k) -> Solution:
    return tuple(None if s is None else frozenset(s) for s in k)


class _Tracker:
    def __init__(self, ev):
        self.ev, self.best, self.best_fit, self.hist, self._next = ev, None, np.inf, [], 100

    def see(self, sol, fit):
        if fit < self.best_fit - 1e-15:
            self.best, self.best_fit = sol, fit
        while self.ev.n_evals >= self._next:
            self.hist.append(self.best_fit); self._next += 100


# ----------------------------------------------------------------------------- ABC
def abc(ev: FitnessEvaluator, space: SearchSpace, budget: int = 2000, seed: int = 0, colony: int = 20,
        limit: int = 10, use_acceptance: bool = True, select: str = "inner") -> SearchResult:
    rng = np.random.default_rng(seed)
    tr = _Tracker(ev)
    sources: List[Solution] = [space.prior]
    seen = {space.key(space.prior)}
    guard = 0
    while len(sources) < colony and guard < 50 * colony:
        s = space.near_prior(rng, steps=1 + int(guard > 10 * colony))
        guard += 1
        if space.key(s) not in seen:
            seen.add(space.key(s)); sources.append(s)
    while len(sources) < colony:
        sources.append(space.prior)
    fit = [ev.evaluate(s)["fitness"] for s in sources]
    for s, f in zip(sources, fit):
        tr.see(s, f)
    trials = [0] * colony
    stall = 0
    while ev.n_evals < budget and stall < 20:
        before = ev.n_evals

        def attempt(i):
            cand = space.neighbour(sources[i], rng)
            f = ev.evaluate(cand)["fitness"]
            tr.see(cand, f)
            if f < fit[i] - 1e-15:
                sources[i], fit[i], trials[i] = cand, f, 0
            else:
                trials[i] += 1

        for i in range(colony):                                   # employed bees
            if ev.n_evals >= budget:
                break
            attempt(i)
        order = np.argsort(np.argsort(fit))                        # rank 0 = best
        prob = (colony - order).astype(float); prob /= prob.sum()
        for _ in range(colony):                                    # onlooker bees (rank-proportional)
            if ev.n_evals >= budget:
                break
            attempt(int(rng.choice(colony, p=prob)))
        for i in range(colony):                                    # scouts
            if trials[i] > limit and ev.n_evals < budget:
                sources[i] = space.near_prior(rng, steps=1 + int(rng.integers(2)))
                fit[i] = ev.evaluate(sources[i])["fitness"]; trials[i] = 0
                tr.see(sources[i], fit[i])
        stall = stall + 1 if ev.n_evals == before else 0           # neighbourhood exhausted
    return _finish("abc", ev, space, tr.best, list(sources), tr.hist, use_acceptance, select)


# ----------------------------------------------------------------------------- comparators
def _fresh(ev, space, sol, rng, tries: int = 8):
    """If ``sol`` was already evaluated, walk a few random moves to an unevaluated neighbour.
    Used by the comparators so that a converged population does not waste the budget on repeats
    (the budget unit is distinct evaluations for every algorithm)."""
    for _ in range(tries):
        if space.key(sol) not in ev.cache:
            return sol
        sol = space.neighbour(sol, rng)
    return sol


def sa(ev, space, budget=2000, seed=0, **_) -> SearchResult:
    rng = np.random.default_rng(seed)
    tr = _Tracker(ev)
    cur = space.prior; fc = ev.evaluate(cur)["fitness"]; tr.see(cur, fc)
    t0, t1 = 0.01 * abs(fc) + 1e-12, 1e-4 * abs(fc) + 1e-14
    stall = 0
    while ev.n_evals < budget and stall < 2000:
        before = ev.n_evals
        T = t0 * (t1 / t0) ** (ev.n_evals / budget)
        cand = space.neighbour(cur, rng)
        if stall > 30:                                             # neighbourhood exhausted: restart near the prior
            cand = _fresh(ev, space, space.near_prior(rng, 1 + int(rng.integers(3))), rng)
        f = ev.evaluate(cand)["fitness"]; tr.see(cand, f)
        if f < fc or rng.uniform() < np.exp(-(f - fc) / T) or stall > 30:
            cur, fc = cand, f
        stall = stall + 1 if ev.n_evals == before else 0
    return _finish("sa", ev, space, tr.best, [tr.best], tr.hist)


def ga(ev, space, budget=2000, seed=0, pop_size=20, p_mut=0.3, **_) -> SearchResult:
    rng = np.random.default_rng(seed)
    tr = _Tracker(ev)
    pop = [space.prior] + [space.near_prior(rng, 1 + i % 2) for i in range(pop_size - 1)]
    fit = [ev.evaluate(s)["fitness"] for s in pop]
    for s, f in zip(pop, fit):
        tr.see(s, f)
    stall = 0
    while ev.n_evals < budget and stall < 2000:
        before = ev.n_evals
        a, b = (min(rng.choice(pop_size, 2, replace=False), key=lambda i: fit[i]) for _ in range(2))
        child = tuple(pop[a][g] if rng.uniform() < 0.5 else pop[b][g] for g in range(len(space.groups)))
        child = space.repair(child, rng)
        if rng.uniform() < p_mut:
            child = space.neighbour(child, rng)
        child = _fresh(ev, space, child, rng)
        f = ev.evaluate(child)["fitness"]; tr.see(child, f)
        w = int(np.argmax(fit))
        if f < fit[w]:
            pop[w], fit[w] = child, f
        stall = stall + 1 if ev.n_evals == before else 0
    return _finish("ga", ev, space, tr.best, list(pop), tr.hist)


def pso(ev, space, budget=2000, seed=0, swarm=20, w=0.7, c1=1.5, c2=1.5, **_) -> SearchResult:
    """Binary PSO: two bits per predicate (present, polarity), sigmoid transfer, repair to the space."""
    rng = np.random.default_rng(seed)
    tr = _Tracker(ev)
    sizes = [len(c) for c in space.cols]
    D = 2 * sum(sizes)
    off = np.cumsum([0] + [2 * n for n in sizes])

    def encode(sol):
        x = np.zeros(D)
        for gi, s in enumerate(sol):
            for j, pol in (s or ()):
                x[off[gi] + 2 * j] = 1.0; x[off[gi] + 2 * j + 1] = float(pol)
        return x

    def decode(x):
        sol = []
        for gi, n in enumerate(sizes):
            lits = [(j, bool(x[off[gi] + 2 * j + 1] > 0.5)) for j in range(n) if x[off[gi] + 2 * j] > 0.5]
            sol.append(frozenset(lits) if lits else None)
        return space.repair(tuple(sol), rng)

    X = np.array([encode(space.prior)] + [encode(space.near_prior(rng, 1 + i % 2)) for i in range(swarm - 1)])
    V = rng.normal(0, 0.1, size=X.shape)
    sols = [decode(x) for x in X]
    fit = np.array([ev.evaluate(s)["fitness"] for s in sols])
    for s, f in zip(sols, fit):
        tr.see(s, f)
    P, pf = X.copy(), fit.copy()
    stall = 0
    while ev.n_evals < budget and stall < 200:
        before = ev.n_evals
        g = P[int(np.argmin(pf))]
        for i in range(swarm):
            if ev.n_evals >= budget:
                break
            V[i] = np.clip(w * V[i] + c1 * rng.uniform(size=D) * (P[i] - X[i]) + c2 * rng.uniform(size=D) * (g - X[i]), -4, 4)
            # velocities start near zero: flip a bit with probability |tanh(V)| (a V-shaped transfer keeps the swarm near the prior)
            flip = rng.uniform(size=D) < np.abs(np.tanh(V[i])) * 0.5
            x = np.where(flip, 1.0 - X[i], X[i])
            s = _fresh(ev, space, decode(x), rng); X[i] = encode(s)
            f = ev.evaluate(s)["fitness"]; tr.see(s, f)
            if f < pf[i]:
                P[i], pf[i] = X[i].copy(), f
        stall = stall + 1 if ev.n_evals == before else 0
    return _finish("pso", ev, space, tr.best, [tr.best], tr.hist)


def de(ev, space, budget=2000, seed=0, pop_size=20, F=0.5, CR=0.9, **_) -> SearchResult:
    """Differential evolution (DE/rand/1/bin) on the PSO encoding made continuous: two coordinates
    in [0, 1] per predicate (present, polarity), a coordinate reads as 1 above 0.5; a formula is
    stored at 0.75 / 0.25 so that a scaled difference of two members can cross the threshold in
    either direction. Greedy one-to-one replacement, as in the IBA-DE literature."""
    rng = np.random.default_rng(seed)
    tr = _Tracker(ev)
    sizes = [len(c) for c in space.cols]
    D = 2 * sum(sizes)
    off = np.cumsum([0] + [2 * n for n in sizes])

    def encode(sol):
        x = np.full(D, 0.25)
        for gi, s in enumerate(sol):
            for j, pol in (s or ()):
                x[off[gi] + 2 * j] = 0.75; x[off[gi] + 2 * j + 1] = 0.75 if pol else 0.25
        return x

    def decode(x):
        sol = []
        for gi, n in enumerate(sizes):
            lits = [(j, bool(x[off[gi] + 2 * j + 1] > 0.5)) for j in range(n) if x[off[gi] + 2 * j] > 0.5]
            sol.append(frozenset(lits) if lits else None)
        return space.repair(tuple(sol), rng)

    sols = [space.prior] + [space.near_prior(rng, 1 + i % 2) for i in range(pop_size - 1)]
    X = np.array([encode(s) for s in sols])
    fit = np.array([ev.evaluate(s)["fitness"] for s in sols])
    for s, f in zip(sols, fit):
        tr.see(s, f)
    stall = 0
    while ev.n_evals < budget and stall < 200:
        before = ev.n_evals
        for i in range(pop_size):
            if ev.n_evals >= budget:
                break
            r1, r2, r3 = rng.choice([k for k in range(pop_size) if k != i], size=3, replace=False)
            v = np.clip(X[r1] + F * (X[r2] - X[r3]), 0.0, 1.0)
            cross = rng.uniform(size=D) < CR
            cross[int(rng.integers(D))] = True
            s = _fresh(ev, space, decode(np.where(cross, v, X[i])), rng)
            f = ev.evaluate(s)["fitness"]; tr.see(s, f)
            if f < fit[i]:
                sols[i], X[i], fit[i] = s, encode(s), f
        stall = stall + 1 if ev.n_evals == before else 0
    return _finish("de", ev, space, tr.best, list(sols), tr.hist)


# ----------------------------------------------------------------------------- exhaustive references
def exhaustive_atoms(ev: FitnessEvaluator, space: SearchSpace) -> SearchResult:
    """The published search with this fitness: per group the best ATOM (every predicate asserted or
    negated), then the best non-empty subset of the groups' atoms. No acceptance rule."""
    G = len(space.groups)
    best_atom: List[frozenset] = []
    for gi, cols in enumerate(space.cols):
        best, bf = None, np.inf
        for bits in itertools.product((False, True), repeat=len(cols)):
            s = frozenset((j, pol) for j, pol in enumerate(bits))
            sol = tuple(s if k == gi else None for k in range(G))
            f = ev.evaluate(sol)["inner"]
            if f < bf - 1e-15:
                best, bf = s, f
        best_atom.append(best)
    best, bf = None, np.inf
    for r in range(1, G + 1):
        for sub in itertools.combinations(range(G), r):
            sol = tuple(best_atom[k] if k in sub else None for k in range(G))
            f = ev.evaluate(sol)["inner"]
            if f < bf - 1e-15:
                best, bf = sol, f
    return _finish("exhaustive_atoms", ev, space, best, [best], [], use_acceptance=False)


def exhaustive_low_order(ev: FitnessEvaluator, space: SearchSpace, max_order: int = 2) -> SearchResult:
    """Per group the best conjunction of at most ``max_order`` literals; then the SMALLEST group
    subset whose mean fitness-fold loss is within one standard error of the best (the rule of the earlier code base)."""
    G = len(space.groups)
    best_g: List[frozenset] = []
    for gi, cols in enumerate(space.cols):
        best, bf = None, np.inf
        for k in range(1, max_order + 1):
            for idx in itertools.combinations(range(len(cols)), k):
                for pols in itertools.product((True, False), repeat=k):
                    s = frozenset(zip(idx, pols))
                    f = ev.evaluate(tuple(s if j == gi else None for j in range(G)))["inner"]
                    if f < bf - 1e-15:
                        best, bf = s, f
        best_g.append(best)
    board = []
    for r in range(1, G + 1):
        for sub in itertools.combinations(range(G), r):
            sol = tuple(best_g[k] if k in sub else None for k in range(G))
            e = ev.evaluate(sol)
            fl = np.asarray(e["fold_losses"])
            board.append((e["inner"], float(fl.std(ddof=1) / np.sqrt(len(fl))) if len(fl) > 1 else 0.0, r, sol))
    top = min(board, key=lambda t: t[0])
    ok = [t for t in board if t[0] <= top[0] + top[1]]
    chosen = min(ok, key=lambda t: (t[2], t[0]))[3]
    return _finish("exhaustive_low_order", ev, space, chosen, [chosen], [], use_acceptance=False)


ALGORITHMS = {"abc": abc, "ga": ga, "pso": pso, "sa": sa, "de": de}
