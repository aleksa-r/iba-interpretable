"""The hedge-fund confirmation extension: the spreadsheet parser, the guard and the stage (no series is read)."""
import numpy as np
import pandas as pd
import pytest

from iba.data.panel import MONTHS, parse_year_month_grid

from .conftest import needs_monthly_targets


def grid(years, scale=1.0, estimate_last=2, drop=None):
    """A sheet as the provider lays it out: title, header, one row per year, a note. Returns (rows, monthly returns)."""
    rng = np.random.default_rng(0)
    rows, truth = [[None] * 5 + ["Some Index"] + [None] * 8, [None] + list(MONTHS) + ["YTD"]], {}
    for i, y in enumerate(years):
        last = i == len(years) - 1
        n = 10 if last else 12
        vals = np.round(rng.normal(0.004, 0.02, n), 4)
        cells = []
        for m, v in enumerate(vals):
            end = pd.Timestamp(year=y, month=m + 1, day=1) + pd.offsets.MonthEnd(0)
            truth[end] = v
            if last and m >= n - estimate_last:
                cells.append(f"{100 * v:.2f}%" + "*" * (m - (n - estimate_last) + 1))
            else:
                cells.append(v / scale)
        if drop == (y,):
            cells[5] = None
        rows.append([float(y)] + cells + [None] * (12 - n) + [f"{100 * (np.prod(1 + vals) - 1):.2f}%"])
    rows += [[None] * 14, [None, "* Estimated performance"] + [None] * 12]
    return rows, pd.Series(truth).sort_index()


def test_parser_reads_fractions_and_marks_estimates():
    rows, truth = grid(range(2019, 2027))
    g = parse_year_month_grid(rows)
    assert g["scale"] == 1.0 and len(g["returns"]) == len(truth)
    assert np.allclose(g["returns"].values, truth.values, atol=1e-12) and (g["returns"].index == truth.index).all()
    assert [d.strftime("%Y-%m") for d in g["estimated"]] == ["2026-09", "2026-10"]


def test_parser_detects_per_cent_numbers_by_the_stated_ytd():
    rows, truth = grid(range(2019, 2027), scale=0.01)
    g = parse_year_month_grid(rows)
    assert g["scale"] == 0.01 and np.allclose(g["returns"].values, truth.values, atol=1e-12)


def test_parser_refuses_what_it_cannot_verify():
    rows, _ = grid(range(2019, 2027), drop=(2021,))
    with pytest.raises(ValueError, match="contiguous|compound"):      # a missing month: refused by whichever check sees it first
        parse_year_month_grid(rows)
    rows, _ = grid(range(2019, 2027))
    rows[3][4] = rows[3][4] + 0.05                                 # one month no longer agrees with the year's YTD
    with pytest.raises(ValueError, match="YTD"):
        parse_year_month_grid(rows)
    with pytest.raises(ValueError, match="header"):
        parse_year_month_grid([[None, "a", "b"]])
    rows, _ = grid(range(2025, 2027))
    with pytest.raises(ValueError, match="complete years"):
        parse_year_month_grid(rows)


def test_parser_verifies_the_year_with_estimates_and_refuses_ambiguous_text():
    rows, truth = grid(range(2019, 2027))
    g = parse_year_month_grid(rows)
    assert g["years_verified"] == 8 and g["years_unverified"] == []          # the incomplete year 2026 is checked as well
    bad = [list(r) for r in rows]
    bad[9][9] = "0.0123*"                                                     # an estimate written without a per-cent sign
    with pytest.raises(ValueError, match="per-cent sign"):
        parse_year_month_grid(bad)
    bad = [list(r) for r in rows]
    bad[9][3] = bad[9][3] + 0.03                                              # a month of 2026 that contradicts the 2026 YTD
    with pytest.raises(ValueError, match="2026"):
        parse_year_month_grid(bad)
    twice = rows[:4] + rows[2:]                                               # a second table on the sheet
    with pytest.raises(ValueError, match="twice"):
        parse_year_month_grid(twice)
    numeric = [list(r) for r in grid(range(2019, 2027), scale=0.01)[0]]       # per-cent numbers with a numeric per-cent YTD
    for r in numeric[2:9]:
        r[13] = float(r[13].rstrip("%"))
    g = parse_year_month_grid(numeric)
    assert g["scale"] == 0.01 and np.allclose(g["returns"].values, truth.values, atol=1e-12)


@needs_monthly_targets          # the rows are compared with those of a development hedge-fund index
def test_panel_check_applies_the_coverage_rule_without_a_frozen_spec(monkeypatch):
    """The layout check on synthetic sheets: a series with every month of the factor panel enters, a shorter one does not;
    the rows it gives the engine are those of a development series."""
    from iba.data import panel as P
    full, _ = grid(range(2003, 2027))
    short, _ = grid(range(2012, 2027))
    sheets = {"a.xls": full, "b.xls": short}
    monkeypatch.setattr(P, "load_hf_catalogue", lambda: {"raw_dir": "data/raw/none", "asset_class": "hedge_fund_monthly", "expected_series": ["BH_A"],
                                                           "series": [{"code": "BH_A", "name": "A", "file": "a.xls"}, {"code": "BH_B", "name": "B", "file": "b.xls"}]})
    monkeypatch.setattr(P, "read_xls_rows", lambda path: sheets[path.rsplit("/", 1)[1]])
    monkeypatch.setattr(P, "_sha", lambda path: "0" * 64)
    man = P.build_monthly_hf_targets("/nonexistent", check_only=True)
    assert man["series"] == ["BH_A"] and man["rows_as_development"] == {"BH_A": True}
    out = {r["code"]: r for r in man["files"]}
    assert out["BH_A"]["included"] and out["BH_A"]["estimated_in_panel"] == ["2026-09-30"]
    assert not out["BH_B"]["included"] and "missing" in out["BH_B"]["reason"]
    with pytest.raises(Exception):                                            # writing the panel needs the frozen spec
        P.build_monthly_hf_targets("/nonexistent", confirmation_run="SPEC-2026-11-14-wrapup")


def test_extension_series_are_confirmation_series_of_the_hedge_fund_class():
    from iba.data.universe import CONFIRMATION_SPEC, HF_CONFIRMATION_SPEC, guard, hf_confirmation_codes, load_manifest, load_universe
    from iba.models.reducers import class_of
    from iba.protocol import study
    codes = hf_confirmation_codes()
    assert len(codes) == len(set(codes)) == 26 and all(c.startswith("BH_") for c in codes)
    assert not set(codes) & {s.ticker for s in load_universe()[0]}            # the split's universe is unchanged
    assert not set(codes) & {t for v in load_manifest().development.values() for t in v}
    g = guard()
    for c in codes:
        with pytest.raises(PermissionError):
            g.check(c)                                                        # development code cannot load them
    with pytest.raises(PermissionError):
        guard("SPEC-2026-11-14-wrapup")
    g = guard()
    g.spec, g.allowed = CONFIRMATION_SPEC, {t for v in load_manifest().confirmation.values() for t in v}   # as the weekly run opens it
    with pytest.raises(PermissionError):
        g.check("BH_HF")                                                      # each run opens the guard for its own series only
    g.check(sorted(g.allowed)[0])
    assert class_of("BH_HF") == ("monthly", "hedge_fund_monthly") and study.stratum_of()["BH_GM"] == "hedge_fund_monthly"
    assert study.STAGES[12]["spec"] == HF_CONFIRMATION_SPEC != CONFIRMATION_SPEC and study.STAGES[12]["split"] == "confirmation"
    assert study.STAGES[12]["pooled_store"] == study.STAGES[11]["pooled_store"]   # the development colonies, no search
    assert not {t.target for t in study.development_tasks()} & set(codes)
    assert not set(study.confirmation_series()) & set(codes)


def test_hf_tasks_follow_the_panel_manifest():
    from iba.protocol import study
    tasks = study.hf_confirmation_tasks()
    series = study.hf_confirmation_series()
    assert len(tasks) == 8 * len(series)
    for t in tasks:
        assert t.frequency == "monthly" and (t.kind, t.h) in {("return", 1), ("return", 3), ("return", 6), ("return", 12),
                                                              ("tail_loss", 3), ("tail_loss", 6), ("tail_gain", 3), ("tail_gain", 6)}
        assert t.q in (None, 0.10)
    if series:                                                                # the names match the development colonies' task names
        dev = {t.name for t in study.stage_tasks(7) if t.frequency == "monthly"}
        assert {t.name for t in tasks} == dev
