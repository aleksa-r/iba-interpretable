"""Shared test helpers."""
import os

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MONTHLY_TARGETS = os.path.join(REPO, "data", "panels", "monthly_2026-11-11", "targets.csv")

# The monthly hedge-fund indices are licensed and are not part of a public release (README, Data).
needs_monthly_targets = pytest.mark.skipif(not os.path.exists(MONTHLY_TARGETS), reason="needs the licensed monthly hedge-fund indices")
