"""ABC over the WHOLE space of formulas (SPEC-2026-11-14-abc-v2). Same fitness, same budget unit
(fitness evaluations of distinct candidates) and the same single acceptance test of the winner
against the prior on the outer fold as ``algorithms.abc``; what changes is where the colony
starts, how a candidate is produced and what a candidate is.

  abc_full    (W) the discrete ABC without the leash to the prior: the colony starts at the prior
              and at random formulas of the whole space, a neighbour is one move, an exhausted
              source restarts at a random formula.
  abc_vector  (V) ABC in its real-vector form on CRISP formulas. A food source is one vector x in
              [-1, 1]^D with a coordinate for every predicate of every group. Decoding: a
              predicate is in its group's conjunction iff |x_j| >= tau, asserted if x_j > 0,
              negated otherwise; a group with more than ``max_literals`` such predicates keeps
              the largest |x_j|; a group without any is off (zero = not used).
  abc_graded  (G, Z) the same vector search on GRADED formulas: |x_j| is the degree to which the
              literal is in the conjunction (``models.reducers.GradedIBAReducer``), so the
              fitness is continuous in the vector and nothing is decoded.
A vector move changes many coordinates at once (each with probability ``mr``; ``mr = 1`` is the
whole vector):   v_j = x_ij + phi_j (x_ij - x_kj) + psi_j (g_j - x_ij),  phi ~ U(-1, 1), psi ~ U(0, 1.5),
with k another food source and g the best vector so far (gbest-guided ABC), clipped to the box.
``start="spread"``: the prior and random positions of the whole space; ``start="zero"``: every
coordinate of every source below the "used" threshold, i.e. the colony starts at the empty formula.
The prior is always the first evaluation: it fixes the scale of the literal penalty and is the
reference of the acceptance test; with ``start="zero"`` it is not a food source."""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from ..models.reducers import graded_conjunction
from .algorithms import SearchResult, _finish, _Tracker
from .fitness import FitnessEvaluator, one_se_test
from .space import SearchSpace, Solution


class VectorCodec:
    def __init__(self, space: SearchSpace, tau: float = 0.5):
        self.space, self.tau = space, tau
        self.sizes = [len(c) for c in space.cols]
        self.off = np.cumsum([0] + self.sizes)
        self.D = int(self.off[-1])

    def decode(self, x: np.ndarray) -> Solution:
        sol: List = []
        for gi in range(len(self.sizes)):
            seg = x[self.off[gi]: self.off[gi + 1]]
            on = np.flatnonzero(np.abs(seg) >= self.tau)
            if len(on) > self.space.max_literals:
                on = on[np.argsort(-np.abs(seg[on]), kind="stable")[: self.space.max_literals]]
            sol.append(frozenset((int(j), bool(seg[j] > 0)) for j in on) if len(on) else None)
        if all(s is None for s in sol) and not self.space.allow_empty:
            j = int(np.argmax(np.abs(x)))                      # the strongest coordinate is the single literal
            gi = int(np.searchsorted(self.off, j, side="right") - 1)
            sol[gi] = frozenset([(j - int(self.off[gi]), bool(x[j] > 0))])
        return tuple(sol)

    def encode(self, sol: Solution, rng: np.random.Generator) -> np.ndarray:
        """A vector that decodes to ``sol``: its literals in +-[tau, 1], every other coordinate inside (-tau, tau)."""
        x = rng.uniform(-self.tau, self.tau, size=self.D) * 0.999
        for gi, s in enumerate(sol):
            for j, pol in sorted(s or ()):
                x[self.off[gi] + j] = (1.0 if pol else -1.0) * rng.uniform(self.tau, 1.0)
        return x

    def exact(self, sol: Solution) -> np.ndarray:
        """The corner of the box that IS the crisp formula: +-1 on its literals, 0 elsewhere."""
        x = np.zeros(self.D)
        for gi, s in enumerate(sol):
            for j, pol in (s or ()):
                x[self.off[gi] + j] = 1.0 if pol else -1.0
        return x

    def below(self, rng: np.random.Generator, bound: float) -> np.ndarray:
        return rng.uniform(-bound, bound, size=self.D) * 0.999


def _move(X: np.ndarray, i: int, g: np.ndarray, rng: np.random.Generator, mr: float) -> np.ndarray:
    colony, D = X.shape
    k = int(rng.integers(colony - 1)); k += int(k >= i)
    v = np.clip(X[i] + rng.uniform(-1.0, 1.0, D) * (X[i] - X[k]) + rng.uniform(0.0, 1.5, D) * (g - X[i]), -1.0, 1.0)
    if mr >= 1.0:
        return v
    mask = rng.uniform(size=D) < mr
    mask[int(rng.integers(D))] = True
    return np.where(mask, v, X[i])


def _colony_diag(res: SearchResult, space: SearchSpace) -> SearchResult:
    res.diag["groups"] = float(sum(s is not None for s in res.best))
    res.diag["empty"] = float(all(s is None for s in res.best))
    res.diag["colony_distinct"] = float(len({space.key(s) for s in res.population}))
    res.diag["colony_literals"] = float(np.mean([space.n_literals(s) for s in res.population]))
    res.diag["colony_empty"] = float(sum(all(g is None for g in s) for s in res.population))
    return res


# ----------------------------------------------------------------------------- W: discrete, whole space
def abc_full(ev: FitnessEvaluator, space: SearchSpace, budget: int = 2000, seed: int = 0, colony: int = 20,
             limit: int = 10, use_acceptance: bool = True) -> SearchResult:
    rng = np.random.default_rng(seed)
    tr = _Tracker(ev)
    sources: List[Solution] = [space.prior] + [space.random_solution(rng) for _ in range(colony - 1)]
    fit = [ev.evaluate(s)["fitness"] for s in sources]
    for s, f in zip(sources, fit):
        tr.see(s, f)
    trials = [0] * colony
    stall = 0
    while ev.n_evals < budget and stall < 50:
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
        order = np.argsort(np.argsort(fit))
        prob = (colony - order).astype(float); prob /= prob.sum()
        for _ in range(colony):                                    # onlooker bees (rank-proportional)
            if ev.n_evals >= budget:
                break
            attempt(int(rng.choice(colony, p=prob)))
        for i in range(colony):                                    # scouts: a random formula of the whole space
            if trials[i] > limit and ev.n_evals < budget:
                sources[i] = space.random_solution(rng)
                fit[i] = ev.evaluate(sources[i])["fitness"]; trials[i] = 0
                tr.see(sources[i], fit[i])
        stall = stall + 1 if ev.n_evals == before else 0
    return _colony_diag(_finish("abc_full", ev, space, tr.best, list(sources), tr.hist, use_acceptance), space)


# ----------------------------------------------------------------------------- V: vector moves, crisp formulas
def abc_vector(ev: FitnessEvaluator, space: SearchSpace, budget: int = 2000, seed: int = 0, colony: int = 20,
               limit: int = 10, mr: float = 0.1, tau: float = 0.5, use_acceptance: bool = True) -> SearchResult:
    rng = np.random.default_rng(seed)
    codec = VectorCodec(space, tau)
    tr = _Tracker(ev)
    tr.see(space.prior, ev.evaluate(space.prior)["fitness"])
    X = np.array([codec.encode(space.prior, rng)] + [codec.encode(space.random_solution(rng), rng) for _ in range(colony - 1)])
    sols = [codec.decode(x) for x in X]
    fit = [ev.evaluate(s)["fitness"] for s in sols]
    for s, f in zip(sols, fit):
        tr.see(s, f)
    b = int(np.argmin(fit))
    g, gf = X[b].copy(), fit[b]
    trials = [0] * colony
    stall = 0
    while ev.n_evals < budget and stall < 50:
        before = ev.n_evals

        def attempt(i):
            nonlocal g, gf
            v = _move(X, i, g, rng, mr)
            s = codec.decode(v)
            f = ev.evaluate(s)["fitness"]
            tr.see(s, f)
            if f < fit[i] - 1e-15:
                X[i], sols[i], fit[i], trials[i] = v, s, f, 0
                if f < gf - 1e-15:
                    g, gf = v.copy(), f
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
                X[i] = codec.encode(space.random_solution(rng), rng)
                sols[i] = codec.decode(X[i])
                fit[i] = ev.evaluate(sols[i])["fitness"]; trials[i] = 0
                tr.see(sols[i], fit[i])
        stall = stall + 1 if ev.n_evals == before else 0
    return _colony_diag(_finish("abc_vector", ev, space, tr.best, list(sols), tr.hist, use_acceptance), space)


# ----------------------------------------------------------------------------- G, Z: vector moves, graded formulas
class GradedEvaluator:
    """Fitness of a graded formula (one weight in [-1, 1] per predicate) with the folds, the linear
    model at fixed regularisation and the fold roles of a ``FitnessEvaluator`` in mode A:
    fitness = mean fitness-fold loss + kappa * max(0, total inclusion - literals of the prior) * L_fit(prior).
    Every call of ``evaluate`` is one unit of the budget. The crisp prior must be evaluated first."""

    def __init__(self, base: FitnessEvaluator, delta: float = 0.1):
        if base.penalty is not None:
            raise ValueError("the graded evaluator uses the fold roles of mode A")
        self.base, self.delta, self.space = base, delta, base.space
        self.codec = VectorCodec(base.space)
        self.D, self.off = self.codec.D, self.codec.off
        self.prior_w = self.codec.exact(base.space.prior)
        self.prior_literals = float(base.space.n_literals(base.space.prior))
        self.n_evals = 0
        self._prior_inner: Optional[float] = None

    def inclusion(self, w: np.ndarray) -> np.ndarray:
        u = np.abs(w)
        return np.where(u >= self.delta, u, 0.0)

    def features(self, f: int, w: np.ndarray) -> np.ndarray:
        cols = []
        for gi in range(len(self.off) - 1):
            seg = w[self.off[gi]: self.off[gi + 1]]
            if (np.abs(seg) >= self.delta).any():
                cols.append(graded_conjunction(self.base.S[f][gi], seg, self.delta))
        return np.column_stack(cols) if cols else np.zeros((self.base.S[f][0].shape[0], 0))

    def outer_pointwise(self, w: np.ndarray) -> np.ndarray:
        return self.base._fold_pointwise(self.base.outer, self.features(self.base.outer, w))

    def evaluate(self, w: np.ndarray, with_outer: bool = False, count: bool = True) -> Dict[str, float]:
        inner = float(np.mean([np.mean(self.base._fold_pointwise(f, self.features(f, w))) for f in self.base.fit_folds]))
        if count:
            self.n_evals += 1
        if self._prior_inner is None:
            self._prior_inner = inner
        r = {"inner": inner,
             "fitness": inner + self.base.kappa * max(0.0, float(self.inclusion(w).sum()) - self.prior_literals) * self._prior_inner}
        if with_outer and self.base.outer is not None:
            pw = self.outer_pointwise(w)
            r["outer"] = float(np.mean(pw))
            r["clean"] = float(np.mean(pw[self.base.clean])) if len(self.base.clean) else float("nan")
        return r

    def acceptance(self, w: np.ndarray) -> Dict[str, float]:
        if self.base.outer is None or np.array_equal(w, self.prior_w):
            return {"accepted": False, "gain": 0.0, "se": 0.0}
        d = self.outer_pointwise(self.prior_w) - self.outer_pointwise(w)
        if self.base.clean_outer:
            if len(self.base.clean) < 2:
                return {"accepted": False, "gain": float("nan"), "se": float("nan")}
            d = d[self.base.clean]
        return one_se_test(d, self.base.h)

    def text(self, w: np.ndarray, top: int = 3) -> str:
        parts = []
        for gi, g in enumerate(self.space.groups):
            seg = w[self.off[gi]: self.off[gi + 1]]
            on = [j for j in np.argsort(-np.abs(seg), kind="stable") if abs(seg[j]) >= self.delta][:top]
            if on:
                parts.append(f"{g}: " + " AND ".join(f"{self.space.cols[gi][j]} {'high' if seg[j] > 0 else 'NOT high'} ({abs(seg[j]):.2f})" for j in on))
        return "; ".join(parts)


def abc_graded(gev: GradedEvaluator, budget: int = 2000, seed: int = 0, colony: int = 20, limit: int = 10,
               start: str = "spread", mr: float = 1.0) -> SearchResult:
    """``best`` / ``population`` are weight vectors; ``chosen`` is the winner if it passed the
    acceptance test, else None (= the crisp prior)."""
    if start not in ("spread", "zero"):
        raise ValueError(start)
    rng = np.random.default_rng(seed)
    D = gev.D
    f_prior = gev.evaluate(gev.prior_w)["fitness"]
    if start == "spread":                                         # the prior and uniform positions in the box
        X = np.array([gev.prior_w] + [rng.uniform(-1.0, 1.0, D) for _ in range(colony - 1)])
        fit = [f_prior] + [gev.evaluate(x)["fitness"] for x in X[1:]]
    else:                                                         # every weight below "used": the empty formula
        X = np.array([gev.codec.below(rng, gev.delta) for _ in range(colony)])
        fit = [gev.evaluate(x)["fitness"] for x in X]
    b = int(np.argmin(fit))
    g, gf = X[b].copy(), fit[b]
    trials = [0] * colony
    hist, nxt = [], 100

    def attempt(i):
        nonlocal g, gf
        v = _move(X, i, g, rng, mr)
        f = gev.evaluate(v)["fitness"]
        if f < fit[i] - 1e-15:
            X[i], fit[i], trials[i] = v, f, 0
            if f < gf - 1e-15:
                g, gf = v.copy(), f
        else:
            trials[i] += 1

    while gev.n_evals < budget:
        for i in range(colony):
            if gev.n_evals >= budget:
                break
            attempt(i)
        order = np.argsort(np.argsort(fit))
        prob = (colony - order).astype(float); prob /= prob.sum()
        for _ in range(colony):
            if gev.n_evals >= budget:
                break
            attempt(int(rng.choice(colony, p=prob)))
        for i in range(colony):
            if trials[i] > limit and gev.n_evals < budget:
                X[i] = rng.uniform(-1.0, 1.0, D) if start == "spread" else gev.codec.below(rng, gev.delta)
                fit[i] = gev.evaluate(X[i])["fitness"]; trials[i] = 0
                if fit[i] < gf - 1e-15:
                    g, gf = X[i].copy(), fit[i]
        while gev.n_evals >= nxt:
            hist.append(gf); nxt += 100
    acc = gev.acceptance(g)
    rb, rp = gev.evaluate(g, with_outer=True, count=False), gev.evaluate(gev.prior_w, with_outer=True, count=False)
    u = gev.inclusion(g)
    groups = sum(bool((u[gev.off[k]: gev.off[k + 1]] > 0).any()) for k in range(len(gev.off) - 1))
    pop_u = [gev.inclusion(x) for x in X]
    diag = {"inner_best": rb["inner"], "outer_best": rb.get("outer", float("nan")), "inner_prior": rp["inner"],
            "outer_prior": rp.get("outer", float("nan")), "fitness_best": rb["fitness"], "fitness_prior": rp["fitness"],
            "gain_outer": acc["gain"], "se_outer": acc["se"], "distance": float(np.abs(g - gev.prior_w).sum()),
            "clean_best": rb.get("clean", float("nan")), "clean_prior": rp.get("clean", float("nan")), "clean_rows": float(len(gev.base.clean)),
            "literals": float(u.sum()), "optimism": (rb.get("outer", np.nan) - rb["inner"]) - (rp.get("outer", np.nan) - rp["inner"]),
            "groups": float(groups), "empty": float(groups == 0), "used": float((u > 0).sum()),
            "colony_distinct": float(len({x.tobytes() for x in X})), "colony_literals": float(np.mean([p.sum() for p in pop_u])),
            "colony_empty": float(sum(not (p > 0).any() for p in pop_u))}
    return SearchResult(f"abc_graded/{start}", g, g if acc["accepted"] else None, bool(acc["accepted"]),
                        [x.copy() for x in X], gev.n_evals, diag, hist)
