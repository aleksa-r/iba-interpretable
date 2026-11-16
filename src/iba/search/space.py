"""Search space of IBA structures around a prior formula.

A solution assigns to every group either None (group off) or a conjunction: a frozenset of
literals (column index within the group, polarity) with polarity True = asserted ("high").
Distance to the prior = number of predicates whose status (absent / asserted / negated) differs.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import numpy as np

Literal = Tuple[int, bool]
GroupSol = Optional[frozenset]
Solution = Tuple[GroupSol, ...]


class SearchSpace:
    def __init__(self, group_cols: Dict[str, List[str]], prior: Dict[str, Tuple[List[str], List[str]]],
                 max_literals: int = 3, max_distance: Optional[int] = 4, allow_empty: bool = False):
        """``max_distance=None`` removes the leash to the prior (the whole space of conjunctions
        with at most ``max_literals`` literals per group); ``allow_empty`` admits the formula with
        every group off (a model without any IBA feature)."""
        self.groups = list(group_cols)
        self.cols = [list(group_cols[g]) for g in self.groups]
        self.max_literals, self.max_distance, self.allow_empty = max_literals, max_distance, allow_empty
        p = []
        for g, cols in zip(self.groups, self.cols):
            if g in prior and (prior[g][0] or prior[g][1]):
                p.append(frozenset([(cols.index(c), True) for c in prior[g][0]] + [(cols.index(c), False) for c in prior[g][1]]))
            else:
                p.append(None)
        self.prior: Solution = tuple(p)
        # (factor code, window) of every column, for the window-switch and factor-replace moves
        self.info = []
        for cols in self.cols:
            row = []
            for c in cols:
                m = re.match(r"^(.*)_(\d+)m_zs$", c)
                row.append((m.group(1), int(m.group(2))) if m else (c, None))
            self.info.append(row)

    # ------------------------------------------------------------------ basic properties
    @staticmethod
    def key(sol: Solution):
        return tuple(None if s is None else tuple(sorted(s)) for s in sol)

    def n_literals(self, sol: Solution) -> int:
        return sum(len(s) for s in sol if s is not None)

    def excess_literals(self, sol: Solution) -> int:
        return max(0, self.n_literals(sol) - self.n_literals(self.prior))

    def distance(self, sol: Solution) -> int:
        d = 0
        for s, p in zip(sol, self.prior):
            a, b = dict(s or ()), dict(p or ())
            d += sum(1 for j in set(a) | set(b) if a.get(j) != b.get(j))
        return d

    def valid(self, sol: Solution, check_distance: bool = True) -> bool:
        if all(s is None for s in sol):
            return self.allow_empty
        for s in sol:
            if s is None:
                continue
            if not (1 <= len(s) <= self.max_literals) or len({j for j, _ in s}) != len(s):
                return False
        return (not check_distance) or self.max_distance is None or self.distance(sol) <= self.max_distance

    def to_formula(self, sol: Solution) -> Dict[str, Tuple[List[str], List[str]]]:
        out = {}
        for g, cols, s in zip(self.groups, self.cols, sol):
            if s is not None:
                out[g] = ([cols[j] for j, pol in sorted(s) if pol], [cols[j] for j, pol in sorted(s) if not pol])
        return out

    def text(self, sol: Solution) -> str:
        parts = []
        for g, (a, n) in self.to_formula(sol).items():
            parts.append(f"{g}: " + " AND ".join([f"{c} high" for c in a] + [f"{c} NOT high" for c in n]))
        return "; ".join(parts)

    # ------------------------------------------------------------------ moves
    def _moves(self, sol: Solution, gi: int, rng: np.random.Generator) -> List[GroupSol]:
        s, cols, info = sol[gi], self.cols[gi], self.info[gi]
        out: List[GroupSol] = []
        if s is None:                                          # switch the group on
            out.append(self.prior[gi] if self.prior[gi] is not None
                       else frozenset([(int(rng.integers(len(cols))), bool(rng.integers(2)))]))
            return out
        lits = sorted(s)
        present = {j for j, _ in lits}
        j, pol = lits[int(rng.integers(len(lits)))]
        out.append(frozenset((s - {(j, pol)}) | {(j, not pol)}))                        # flip polarity
        code, w = info[j]
        other_w = [k for k, (c, ww) in enumerate(info) if c == code and ww != w and k not in present]
        if other_w:
            out.append(frozenset((s - {(j, pol)}) | {(other_w[int(rng.integers(len(other_w)))], pol)}))   # switch window
        other_f = [k for k, (c, ww) in enumerate(info) if c != code and ww == w and k not in present]
        if other_f:
            out.append(frozenset((s - {(j, pol)}) | {(other_f[int(rng.integers(len(other_f)))], pol)}))   # replace factor
        absent = [k for k in range(len(cols)) if k not in present]
        if len(s) < self.max_literals and absent:
            out.append(frozenset(s | {(absent[int(rng.integers(len(absent)))], bool(rng.integers(2)))}))  # add
        if len(s) > 1:
            out.append(frozenset(s - {(j, pol)}))                                        # drop
        if self.allow_empty or sum(x is not None for x in sol) > 1:
            out.append(None)                                                             # switch the group off
        return out

    def neighbour(self, sol: Solution, rng: np.random.Generator, tries: int = 60) -> Solution:
        """A random valid neighbour (one move); the solution itself if none is found."""
        for _ in range(tries):
            gi = int(rng.integers(len(self.groups)))
            moves = self._moves(sol, gi, rng)
            if not moves:
                continue
            new = list(sol); new[gi] = moves[int(rng.integers(len(moves)))]
            new = tuple(new)
            if new != sol and self.valid(new):
                return new
        return sol

    def random_solution(self, rng: np.random.Generator, p_on: float = 0.5) -> Solution:
        """A formula drawn from the whole space: every group on with probability ``p_on``, then one
        or two predicates of the group with random polarity. Never the empty formula."""
        while True:
            sol = []
            for cols in self.cols:
                if rng.uniform() < p_on:
                    k = min(len(cols), 1 + int(rng.integers(2)))
                    idx = rng.choice(len(cols), size=k, replace=False)
                    sol.append(frozenset((int(j), bool(rng.integers(2))) for j in idx))
                else:
                    sol.append(None)
            if any(s is not None for s in sol):
                return tuple(sol)

    def near_prior(self, rng: np.random.Generator, steps: int = 1) -> Solution:
        s = self.prior
        for _ in range(steps):
            s = self.neighbour(s, rng)
        return s

    def repair(self, sol: Solution, rng: np.random.Generator) -> Solution:
        """Make an arbitrary assignment valid: cap the literals per group, guarantee one active
        group, then revert random differing groups to the prior until the distance bound holds."""
        new = []
        for s in sol:
            if s is not None:
                d = {}
                for j, pol in s:
                    d[j] = pol
                items = sorted(d.items())
                if len(items) > self.max_literals:
                    keep = rng.choice(len(items), size=self.max_literals, replace=False)
                    items = [items[k] for k in sorted(keep)]
                s = frozenset(items) if items else None
            new.append(s)
        if all(s is None for s in new):
            new = list(self.prior)
        guard = 0
        while self.max_distance is not None and self.distance(tuple(new)) > self.max_distance and guard < 200:
            diff = [i for i, (s, p) in enumerate(zip(new, self.prior)) if s != p]
            i = diff[int(rng.integers(len(diff)))]
            new[i] = self.prior[i]
            guard += 1
            if all(s is None for s in new):
                new = list(self.prior)
        out = tuple(new)
        return out if self.valid(out) else self.prior
