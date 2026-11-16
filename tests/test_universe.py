import json

import pytest

from iba.data.universe import (FACTOR_PANEL_TICKERS, MANIFEST, UNIVERSE, file_sha256, guard, load_manifest,
                                   load_universe)


def test_manifest_matches_the_universe_file_and_covers_every_series_once():
    series, cfg = load_universe()
    raw = json.load(open(MANIFEST))
    assert raw["universe_file_sha256"] == file_sha256(UNIVERSE) and raw["salt"] == cfg["salt"]
    m = load_manifest()
    dev = {t for v in m.development.values() for t in v}
    conf = {t for v in m.confirmation.values() for t in v}
    assert dev.isdisjoint(conf) and dev | conf == {s.ticker for s in series}
    assert set(cfg["forced_development"]) <= dev


def test_no_confirmation_series_is_a_factor_or_was_an_earlier_target():
    m = load_manifest()
    conf = {t for v in m.confirmation.values() for t in v}
    assert conf.isdisjoint(FACTOR_PANEL_TICKERS)
    assert conf.isdisjoint({"SPY", "IWM", "EFA", "AGG", "TLT", "VNQ", "XLE", "GLD", "HYG", "EMB", "EEM"})
    g = guard()
    for t in conf:
        with pytest.raises(PermissionError):
            g.check(t)
    g.check("EEM"); g.check("SLV")


def test_amendments_only_move_series_out_of_confirmation():
    raw = json.load(open(MANIFEST))
    m = load_manifest()
    for a in raw.get("amendments", []):
        for t in a["move_to_development"]:
            assert any(t in v for v in raw["confirmation"].values())          # it was confirmation ...
            assert any(t in v for v in m.development.values())                # ... and is development now
