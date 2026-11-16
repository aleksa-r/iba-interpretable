"""Generalized Boolean polynomials (GBPs) of Interpolative Boolean Algebra (IBA).

Theory (Radojevic 2000, 2008). A Boolean expression over predicates x_1..x_G is first
reduced on the STRUCTURAL level to a sum of atoms (minterms); only then are values
inserted. The atom with asserted set S (every other predicate negated) is realised as

    atom_S(x) = sum over T subseteq complement(S) of (-1)^|T| * GP(S union T)

where GP(U) is the GENERALIZED PRODUCT (an operator ⊗ satisfying the IBA axioms) of the
predicates in U. The choice of ⊗ encodes attribute dependence:

    product      x*y                 independent attributes (the published paper's choice)
    minimum      min(x, y)           positively dependent attributes (one quantity measured twice)
    lukasiewicz  max(0, x + y - 1)   the lower bound; valid for TWO predicates only: with three
                                     predicates at 0.5 the all-negated atom is 1 - 1.5 + 0 - 0 < 0,
                                     so it is not an admissible generalized product for G >= 3
                                     (kept for the two-literal case and for the test that shows this)

With the product ⊗ the inclusion-exclusion sum factorises to prod_S x * prod_{not S} (1-x),
which is the formula the published code computes; with min or Lukasiewicz it does NOT
factorise and must be computed by inclusion-exclusion. For every admissible ⊗ the 2^G atoms
of a group lie in [0, 1] and sum to 1 (a partition of unity). A low-order conjunction over
the literals A (asserted) and N (negated) is the sum of all atoms that agree with it, i.e.
the same inclusion-exclusion with T ranging over subsets of N only.

The GEOMETRIC MEAN of the literals, (prod)^(1/k), used by the `IBAReducer` of the earlier code base, is not a GBP
and not a t-norm: gm(0.5, 0.5) = 0.5 is not below the weakest literal, the atoms of a group
do not sum to 1, and its value is not a degree of truth of the stated conjunction. It is
kept here only as `legacy_geometric_mean` so that numbers of the earlier code base can be reproduced and compared.
"""
from __future__ import annotations

from itertools import combinations
from typing import Callable, Dict, List, Sequence

import numpy as np

Array = np.ndarray


def _tn_product(M: Array) -> Array:
    return np.prod(M, axis=1)


def _tn_minimum(M: Array) -> Array:
    return M.min(axis=1)


def _tn_lukasiewicz(M: Array) -> Array:
    return np.maximum(0.0, M.sum(axis=1) - (M.shape[1] - 1))


TNORMS: Dict[str, Callable[[Array], Array]] = {
    "product": _tn_product,
    "minimum": _tn_minimum,
    "lukasiewicz": _tn_lukasiewicz,
}


def generalized_product(X: Array, cols: Sequence[int], tnorm: str = "product") -> Array:
    """GP of the predicates in ``cols`` (rows of X); the empty product is 1."""
    X = np.asarray(X, dtype=np.float64)
    if len(cols) == 0:
        return np.ones(X.shape[0])
    return TNORMS[tnorm](X[:, list(cols)])


def conjunction(X: Array, asserted: Sequence[int], negated: Sequence[int], tnorm: str = "product") -> Array:
    """GBP of  AND_{i in asserted} x_i  AND  AND_{j in negated} NOT x_j  (other predicates: don't care).

    Inclusion-exclusion over the negated literals; exact for every t-norm. Values are clipped
    to [0, 1] only to remove floating-point noise (the theory guarantees the range)."""
    X = np.asarray(X, dtype=np.float64)
    asserted, negated = list(asserted), list(negated)
    if set(asserted) & set(negated):
        return np.zeros(X.shape[0])          # x AND NOT x is structurally 0 in IBA
    if tnorm == "product":                   # factorised fast path
        a = np.prod(X[:, asserted], axis=1) if asserted else np.ones(X.shape[0])
        n = np.prod(1.0 - X[:, negated], axis=1) if negated else np.ones(X.shape[0])
        return a * n
    out = np.zeros(X.shape[0])
    for r in range(len(negated) + 1):
        for T in combinations(negated, r):
            out += (-1) ** r * generalized_product(X, asserted + list(T), tnorm)
    return np.clip(out, 0.0, 1.0)


def atom(X: Array, asserted: Sequence[int], tnorm: str = "product") -> Array:
    """Atom (minterm): the listed predicates asserted, every other predicate negated."""
    G = np.asarray(X).shape[1]
    negated = [j for j in range(G) if j not in set(asserted)]
    return conjunction(X, list(asserted), negated, tnorm)


def all_atoms(X: Array, tnorm: str = "product") -> Array:
    """All 2^G atoms, columns ordered by the binary mask (bit i set = predicate i asserted)."""
    G = np.asarray(X).shape[1]
    cols = []
    for m in range(2 ** G):
        S = [i for i in range(G) if (m >> i) & 1]
        cols.append(atom(X, S, tnorm))
    return np.column_stack(cols)


def legacy_geometric_mean(X: Array, asserted: Sequence[int], negated: Sequence[int]) -> Array:
    """What the earlier `IBAReducer.transform` returned: (prod_A x * prod_N (1-x))^(1/(|A|+|N|)).
    Not a GBP (see module docstring); provided for reproduction only."""
    X = np.asarray(X, dtype=np.float64)
    k = max(len(asserted) + len(negated), 1)
    logs = np.log(X[:, list(asserted)]).sum(axis=1) + np.log(1.0 - X[:, list(negated)]).sum(axis=1)
    return np.exp(logs / k)


def logical_aggregation(gbps: Array, weights: Sequence[float]) -> Array:
    """Convex combination of GBP columns (the IBA 'logical aggregation' / pseudo-logical
    aggregation): weights >= 0 summing to 1, result stays in [0, 1]."""
    w = np.asarray(weights, dtype=np.float64)
    if (w < 0).any() or not np.isclose(w.sum(), 1.0):
        raise ValueError("weights must be non-negative and sum to 1")
    return np.asarray(gbps, dtype=np.float64) @ w


def describe(names: Sequence[str], asserted: Sequence[int], negated: Sequence[int]) -> str:
    """Readable formula, e.g. 'VIX_12m high AND NFCI_18m NOT high'."""
    parts = [f"{names[i]} high" for i in asserted] + [f"{names[j]} NOT high" for j in negated]
    return " AND ".join(parts) if parts else "TRUE"
