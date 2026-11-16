import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from iba.protocol.information_rule import (FoldGeometry, assert_admissible, n_admissible,
                                               purged_folds, walk_forward_blocks)


@given(st.integers(20, 400), st.integers(1, 12))
def test_admissible_rows_realised_by_origin(t, h):
    n = n_admissible(t, h)
    assert n == t - h + 1
    rows = np.arange(n)
    assert_admissible(rows, t, h)                      # max row + h == t exactly
    with pytest.raises(AssertionError):
        assert_admissible(np.arange(n + 1), t, h)       # one more row and the label is unrealised


@settings(max_examples=60, deadline=None)
@given(st.integers(120, 300), st.integers(1, 12))
def test_every_fold_is_purged_and_anchored(n, h):
    folds = purged_folds(n, h, FoldGeometry())
    assert len(folds) == 5 and folds[-1][1][-1] == n - 1
    for tr, va in folds:
        assert tr[-1] + h <= va[0]
        assert len(set(tr) & set(va)) == 0


def test_blocks_cover_the_holdout_once():
    ho0, blocks = walk_forward_blocks(254, 96, 24, 110)
    assert ho0 == 254 - 96 and blocks == [(0, 24), (24, 48), (48, 72), (72, 96)]
    ho0, blocks = walk_forward_blocks(200, 96, 24, 110)
    assert ho0 == 110 and blocks[-1][1] == 90


def test_fold_geometry_equals_r6_examples():
    from iba.protocol.information_rule import fold_starts
    # monthly block 0 of the earlier code base (CTA, h = 6): 153 admissible rows -> M=95, N=10, Q=18, K=5
    assert fold_starts(153, FoldGeometry(0.7, 18, 10, 5)) == [95, 105, 115, 125, 135]
    # weekly geometry 0.7 / 78 / 43 / 5 on 540 rows: last validation window ends at the last row
    s = fold_starts(540, FoldGeometry(0.7, 78, 43, 5))
    assert s[-1] + 78 == 540 and len(s) == 5 and s[0] >= int((540 - 78) * 0.7)


def test_fold_geometry_matches_ibaml_when_available():
    import os, sys
    src = os.environ.get("IBAML_SRC", "")                 # source tree of the earlier code base, when available
    if not os.path.isdir(src):
        pytest.skip("earlier code base not present (set IBAML_SRC to its src directory)")
    sys.path.insert(0, src)
    from ibaml.validation.expanding_cv import adjust_split_ratios, make_anchored_folds
    for n, h, (share, Q, N, K) in [(153, 6, (0.7, 18, 10, 5)), (201, 1, (0.7, 18, 10, 5)), (540, 4, (0.7, 78, 43, 5)),
                                   (644, 13, (0.7, 78, 43, 5)), (129, 12, (0.7, 18, 10, 5)), (300, 4, (0.5, 36, 20, 5))]:
        M_, Q_, N_, K_ = adjust_split_ratios(n, share, Q, N, K)
        old = make_anchored_folds(n, M_, Q_, N_, K_, purge=h)
        new = purged_folds(n, h, FoldGeometry(share, Q, N, K), strict_minus_one=True)
        assert len(old) == len(new)
        for (a, b), (c, d) in zip(old, new):
            assert np.array_equal(a, c) and np.array_equal(b, d)
