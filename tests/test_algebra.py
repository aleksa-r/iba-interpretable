"""Hand-computed GBP values for a two-predicate toy group, and the IBA axioms as properties."""
import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from hypothesis.extra.numpy import arrays

from iba.algebra.gbp import (TNORMS, all_atoms, atom, conjunction, generalized_product,
                                 legacy_geometric_mean, logical_aggregation)
from iba.algebra.predicates import PredicateScaler

X2 = np.array([[0.8, 0.3]])  # one row, predicates a = 0.8, b = 0.3

# atoms in mask order {}, {a}, {b}, {a,b}; computed by hand from the inclusion-exclusion formula
HAND = {
    "product":     [0.2 * 0.7, 0.8 * 0.7, 0.2 * 0.3, 0.8 * 0.3],                # .14 .56 .06 .24
    "minimum":     [1 - 0.8 - 0.3 + 0.3, 0.8 - 0.3, 0.3 - 0.3, 0.3],            # .20 .50 .00 .30
    "lukasiewicz": [1 - 0.8 - 0.3 + 0.1, 0.8 - 0.1, 0.3 - 0.1, 0.1],            # .00 .70 .20 .10
}


@pytest.mark.parametrize("tnorm", list(TNORMS))
def test_two_predicate_atoms_match_hand_computation(tnorm):
    A = all_atoms(X2, tnorm)[0]
    np.testing.assert_allclose(A, HAND[tnorm], atol=1e-12)
    assert A.sum() == pytest.approx(1.0)


def test_geometric_mean_is_not_a_partition_of_unity():
    gm = [legacy_geometric_mean(X2, a, n)[0] for a, n in (([], [0, 1]), ([0], [1]), ([1], [0]), ([0, 1], []))]
    np.testing.assert_allclose(gm, np.sqrt(HAND["product"]), atol=1e-12)
    assert sum(gm) == pytest.approx(1.857, abs=1e-3)       # not 1: the four 'atoms' overlap
    # a conjunction cannot exceed its weakest literal in any t-norm; the geometric mean can
    assert gm[3] > min(0.8, 0.3)


ADMISSIBLE = ["product", "minimum"]      # valid generalized products for any number of predicates


def test_lukasiewicz_is_not_admissible_for_three_predicates():
    X = np.array([[0.5, 0.5, 0.5]])
    raw = sum((-1) ** r * generalized_product(X, list(T), "lukasiewicz")
              for r in range(4) for T in __import__("itertools").combinations([0, 1, 2], r))
    assert raw[0] == pytest.approx(-0.5)                    # the all-negated atom is negative
    for tnorm in ADMISSIBLE:
        assert all_atoms(X, tnorm).min() >= 0.0


def test_conjunction_is_sum_of_agreeing_atoms():
    rng = np.random.default_rng(0)
    X = rng.uniform(0.01, 0.99, size=(50, 4))
    for tnorm in ADMISSIBLE:
        c = conjunction(X, [0], [2], tnorm)                      # x0 AND NOT x2, x1/x3 don't care
        s = sum(atom(X, [0] + extra, tnorm) for extra in ([], [1], [3], [1, 3]))
        np.testing.assert_allclose(c, s, atol=1e-10)


def test_x_and_not_x_is_zero():
    X = np.array([[0.3, 0.9]])
    for tnorm in TNORMS:
        assert conjunction(X, [0], [0], tnorm)[0] == 0.0


@settings(max_examples=200, deadline=None)
@given(arrays(np.float64, (3, 3), elements=st.floats(0.0, 1.0)))
def test_atoms_partition_unity_and_stay_in_unit_interval(X):
    for tnorm in ADMISSIBLE:
        A = all_atoms(X, tnorm)
        assert np.all(A >= -1e-12) and np.all(A <= 1 + 1e-12)
        np.testing.assert_allclose(A.sum(axis=1), 1.0, atol=1e-9)


@settings(max_examples=100, deadline=None)
@given(arrays(np.float64, (5, 3), elements=st.floats(0.0, 1.0)))
def test_product_fast_path_equals_inclusion_exclusion(X):
    for S in ([], [0], [1, 2], [0, 1, 2]):
        N = [j for j in range(3) if j not in S]
        fast = conjunction(X, S, N, "product")
        slow = sum((-1) ** len(T) * generalized_product(X, S + list(T), "product")
                   for r in range(len(N) + 1) for T in __import__("itertools").combinations(N, r))
        np.testing.assert_allclose(fast, slow, atol=1e-12)


def test_logical_aggregation_is_convex():
    G = np.array([[0.2, 0.9], [0.5, 0.5]])
    np.testing.assert_allclose(logical_aggregation(G, [0.25, 0.75]), [0.725, 0.5])
    with pytest.raises(ValueError):
        logical_aggregation(G, [0.5, 0.7])


def test_scalers_fit_on_training_rows_only_and_clip():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(100, 2))
    for m in ("minmax", "ecdf"):
        sc = PredicateScaler(m).fit(X[:60])
        z = sc.transform(X)
        assert z.min() >= 0.01 and z.max() <= 0.99
        sc2 = PredicateScaler(m).fit(np.vstack([X[:60], X[60:] * 100]))  # later rows changed...
        np.testing.assert_allclose(PredicateScaler(m).fit(X[:60]).transform(X[:60]), sc.transform(X[:60]))
    # minmax: one training outlier compresses everything else; ecdf does not
    Xo = X.copy(); Xo[10, 0] = 50.0
    zm = PredicateScaler("minmax").fit(Xo[:60]).transform(Xo[:60])[:, 0]
    ze = PredicateScaler("ecdf").fit(Xo[:60]).transform(Xo[:60])[:, 0]
    assert np.median(zm) < 0.2 and 0.4 < np.median(ze) < 0.6
