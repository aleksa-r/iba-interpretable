import pytest
from iba.data.split import ConfirmationGuard, Series, stratified_split

U = [Series(t, "equity_us", "yahoo", "daily", "2000-01-03") for t in ["SPY", "QQQ", "IWM", "DIA", "MDY"]] + \
    [Series(t, "bonds", "yahoo", "daily", "2003-01-03") for t in ["AGG", "TLT", "IEF", "SHY", "LQD", "TIP", "MUB"]] + \
    [Series(t, "hedge_fund_monthly", "cisdm", "monthly", "1990-01-31") for t in ["CTA", "CA", "DS"]]


def test_split_is_deterministic_stratified_and_respects_forcing():
    a = stratified_split(U, salt="iba-next-2026-11-13", forced_development=["SPY", "AGG", "TLT", "CTA", "CA", "DS"])
    b = stratified_split(U, salt="iba-next-2026-11-13", forced_development=["SPY", "AGG", "TLT", "CTA", "CA", "DS"])
    assert a.to_json() == b.to_json()
    assert {"SPY"} <= set(a.development["equity_us"]) and {"AGG", "TLT"} <= set(a.development["bonds"])
    for cls in ("equity_us", "bonds"):
        assert len(a.confirmation[cls]) >= 2
        assert set(a.development[cls]).isdisjoint(a.confirmation[cls])
        assert set(a.development[cls]) | set(a.confirmation[cls]) == {s.ticker for s in U if s.asset_class == cls}
    c = stratified_split(U, salt="another salt", forced_development=["SPY"])
    assert c.development != a.development          # the salt matters, so it must be fixed in advance


def test_guard_refuses_confirmation_series_without_frozen_spec():
    m = stratified_split(U, salt="s", forced_development=["SPY"])
    conf = next(iter(m.confirmation["bonds"]))
    with pytest.raises(PermissionError):
        ConfirmationGuard(m).check(conf)
    ConfirmationGuard(m, confirmation_run="SPEC-2027-01-01-final").check(conf)
    ConfirmationGuard(m).check("SPY")


def test_the_data_guard_opens_only_for_the_frozen_confirmation_spec():
    import pytest
    from iba.data.universe import CONFIRMATION_SPEC, guard
    from iba.protocol.spec import SpecNotFrozen, read_front_matter
    with pytest.raises(PermissionError, match="opens only for"):
        guard("SPEC-2026-11-14-wrapup")                                  # a frozen spec, but not the confirmation spec
    with pytest.raises(PermissionError):
        guard("x")
    if read_front_matter(CONFIRMATION_SPEC)["status"] != "frozen":
        with pytest.raises(SpecNotFrozen):
            guard(CONFIRMATION_SPEC)
    assert guard().spec is None
