"""Direction C: the simple mathematical model. Forecast = link(convex combination of <= 3 GBPs),
no estimator on top: weights on a 0.1 grid, a two-parameter link (a + b*aggregate; logit for
tails) fitted on the admissible rows. Structure and weights are searched with the same ABC,
budget unit and fold roles as direction A."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from ..models.estimators import Estimator, logistic_fit, logistic_predict, pointwise_loss, ridge_fit, ridge_predict
from .fitness import FitnessEvaluator
from .space import SearchSpace

AggSol = Tuple[Tuple[Tuple[int, frozenset], ...], Tuple[int, ...]]     # ((group, literals), ...), weights in tenths
MAX_COMPONENTS = 3


class LinkEstimator(Estimator):
    """a + b * aggregate (least squares), or logit p = a + b * aggregate (maximum likelihood)."""
    name = "link"
    grid = [{}]

    def fit(self, X, y, params):
        return ridge_fit(X, y, 1e-8) if self.task == "reg" else logistic_fit(X, y, 1e6)

    def predict(self, model, X):
        return ridge_predict(model, X) if self.task == "reg" else logistic_predict(model, X)


class AggSpace:
    def __init__(self, base: SearchSpace, prior: AggSol, max_component_distance: int = 2):
        self.base, self.prior, self.maxd = base, prior, max_component_distance
        self.groups = base.groups

    @staticmethod
    def key(sol: AggSol):
        return (tuple((g, tuple(sorted(s))) for g, s in sol[0]), tuple(sol[1]))

    def n_literals(self, sol): return sum(len(s) for _, s in sol[0])
    def excess_literals(self, sol): return max(0, self.n_literals(sol) - self.n_literals(self.prior))
    def distance(self, sol): return sum(self._cdist(g, s) for g, s in sol[0])

    def _cdist(self, g: int, s: frozenset) -> int:
        p = self.base.prior[g]
        if p is None:
            return len(s)
        a, b = dict(s), dict(p)
        return sum(1 for j in set(a) | set(b) if a.get(j) != b.get(j))

    def valid(self, sol: AggSol) -> bool:
        comps, w = sol
        if not (1 <= len(comps) <= MAX_COMPONENTS) or len({g for g, _ in comps}) != len(comps):
            return False
        if sum(w) != 10 or min(w) < 1 or len(w) != len(comps):
            return False
        for g, s in comps:
            if not (1 <= len(s) <= self.base.max_literals) or len({j for j, _ in s}) != len(s) or self._cdist(g, s) > self.maxd:
                return False
        return True

    def _start(self, g: int, rng) -> frozenset:
        p = self.base.prior[g]
        return p if p is not None else frozenset([(int(rng.integers(len(self.base.cols[g]))), bool(rng.integers(2)))])

    def neighbour(self, sol: AggSol, rng, tries: int = 60) -> AggSol:
        for _ in range(tries):
            comps, w = [list(c) for c in sol[0]], list(sol[1])
            k = int(rng.integers(len(comps)))
            move = int(rng.integers(5))
            if move == 0:                                              # change one component's formula
                full = tuple(dict(comps).get(g) for g in range(len(self.groups)))
                opts = [m for m in self.base._moves(full, comps[k][0], rng) if m is not None]
                if not opts:
                    continue
                comps[k][1] = opts[int(rng.integers(len(opts)))]
            elif move == 1 and len(comps) > 1:                          # shift one tenth of weight
                j = int(rng.integers(len(comps)))
                if j == k or w[k] < 2:
                    continue
                w[k] -= 1; w[j] += 1
            elif move == 2:                                             # swap a component for another group
                free = [g for g in range(len(self.groups)) if g not in {c[0] for c in comps}]
                if not free:
                    continue
                g = free[int(rng.integers(len(free)))]
                comps[k] = [g, self._start(g, rng)]
            elif move == 3 and len(comps) > 1:                          # drop a component
                gone = w.pop(k); comps.pop(k)
                w[int(np.argmax(w))] += gone
            elif move == 4 and len(comps) < MAX_COMPONENTS:             # add a component
                free = [g for g in range(len(self.groups)) if g not in {c[0] for c in comps}]
                big = int(np.argmax(w))
                if not free or w[big] < 2:
                    continue
                g = free[int(rng.integers(len(free)))]
                w[big] -= 1; comps.append([g, self._start(g, rng)]); w.append(1)
            else:
                continue
            order = np.argsort([c[0] for c in comps], kind="stable")
            new = (tuple((comps[i][0], comps[i][1]) for i in order), tuple(w[i] for i in order))
            if new != sol and self.valid(new):
                return new
        return sol

    def near_prior(self, rng, steps: int = 1) -> AggSol:
        s = self.prior
        for _ in range(steps):
            s = self.neighbour(s, rng)
        return s

    def text(self, sol: AggSol) -> str:
        parts = []
        for (g, s), w in zip(*sol):
            cols = self.base.cols[g]
            parts.append(f"{w / 10:.1f} * [{self.groups[g]}: " + " AND ".join(f"{cols[j]} {'high' if pol else 'NOT high'}" for j, pol in sorted(s)) + "]")
        return " + ".join(parts)


class AggEvaluator:
    """Fitness of an aggregation; same fold roles, scaling and budget unit as FitnessEvaluator."""

    def __init__(self, fe: FitnessEvaluator, space: AggSpace, kappa: float = 0.005):
        self.fe, self.space, self.kappa = fe, space, kappa
        self.task, self.h, self.outer = fe.task, fe.h, fe.outer
        self.cache: Dict = {}
        self.n_evals = 0
        self._prior_fit: Optional[float] = None
        self.link = LinkEstimator(fe.task)

    def aggregate(self, f: int, sol: AggSol) -> np.ndarray:
        S = self.fe.S[f]
        out = np.zeros(S[0].shape[0])
        for (g, s), w in zip(*sol):
            v = np.ones(S[g].shape[0])
            for j, pol in s:
                v = v * (S[g][:, j] if pol else 1.0 - S[g][:, j])
            out += (w / 10.0) * v
        return out.reshape(-1, 1)

    def _pointwise(self, f: int, sol: AggSol) -> np.ndarray:
        (tr, va), (ytr, yva) = self.fe.folds[f], self.fe.fold_y[f]
        Z = self.aggregate(f, sol)
        return pointwise_loss(self.task, yva, self.link.predict(self.link.fit(Z[tr], ytr, {}), Z[va]))

    def outer_pointwise(self, sol): return self._pointwise(self.outer, sol)

    def evaluate(self, sol: AggSol, with_outer: bool = False):
        k = self.space.key(sol)
        r = self.cache.get(k)
        if r is None:
            fl = [float(np.mean(self._pointwise(f, sol))) for f in self.fe.fit_folds]
            inner = float(np.mean(fl))
            self.n_evals += 1
            if self._prior_fit is None and sol == self.space.prior:
                self._prior_fit = inner
            base = self._prior_fit if self._prior_fit is not None else inner
            r = {"inner": inner, "fold_losses": fl, "penalty": None,
                 "fitness": inner + self.kappa * self.space.excess_literals(sol) * base}
            self.cache[k] = r
        if with_outer and "outer" not in r and self.outer is not None:
            r["outer"] = float(np.mean(self.outer_pointwise(sol)))
        return r

    acceptance = FitnessEvaluator.acceptance


def prior_aggregation(fe: FitnessEvaluator, base: SearchSpace) -> AggSol:
    """Equal-ish weights on the three prior group formulas with the best single-formula fitness."""
    G = len(base.groups)
    scored = []
    for g in range(G):
        if base.prior[g] is None:
            continue
        sol = tuple(base.prior[g] if k == g else None for k in range(G))
        scored.append((float(np.mean([fe.fold_loss(f, sol) for f in fe.fit_folds])), g))
    top = sorted(g for _, g in sorted(scored)[:MAX_COMPONENTS])
    w = {1: (10,), 2: (5, 5), 3: (4, 3, 3)}[len(top)]
    return (tuple((g, base.prior[g]) for g in top), w)
