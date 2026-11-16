import pytest

from .conftest import needs_monthly_targets

from iba.protocol.spec import SpecNotFrozen, read_front_matter, require_frozen
from iba.protocol.study import STAGES, development_tasks, search_comparison_cells, stratum_of

SPEC = "SPEC-2026-11-13-multitarget-study"


def test_study_has_the_cells_the_spec_counts():
    tasks = development_tasks()
    weekly = [t for t in tasks if t.frequency == "weekly"]; monthly = [t for t in tasks if t.frequency == "monthly"]
    assert len({t.target for t in weekly}) == 37 and len({t.target for t in monthly}) == 11
    primary = [t for t in weekly if not (t.kind == "logrv" and t.h == 13)]
    assert len(primary) == 37 * 17 and len(monthly) == 11 * 16 and len(primary) + len(monthly) == 805
    assert len(search_comparison_cells()) == 24
    assert set(stratum_of()[t.target] for t in weekly) == {"bonds_gov_ig", "commodities", "credit_em_debt", "equity_developed_exus",
                                                           "equity_emerging", "equity_us_broad", "equity_us_sectors", "real_estate"}
    assert STAGES[1]["seeds"] == (0,) and STAGES[2]["seeds"] == (0, 1, 2)


def test_an_unfrozen_spec_cannot_run():
    fm = read_front_matter(SPEC)
    assert fm["spec_id"] == SPEC
    if fm["status"] != "frozen":
        with pytest.raises(SpecNotFrozen):
            require_frozen(SPEC, check_fingerprint=False)


def test_wrapup_stages_formula_sets_and_pools(tmp_path, monkeypatch):
    import json, os
    from iba.protocol import study as S
    assert len(S.PRIOR_SETS) == 18 and S.PRIOR_SETS["G"] is None and S.prior_file(None) is None and S.prior_file("G") is None
    for name, rel in S.PRIOR_SETS.items():
        assert rel is None or os.path.exists(S.prior_file(name)), name
    assert S.stage_priors(1) == [None] and S.stage_priors(7) == list(S.PRIOR_SETS) and len(S.stage_tasks(7)) == 458
    assert S.STAGES[7]["estimators"] == ("lin", "gbt", "xgb") and set(S.STAGES[7]["extra"]) == {"G", "Kc", "Sc"}
    class_pools = S.pool_units(all_pool=False)
    assert len(class_pools) == 88 and all(u[5] != "ALL" for u in class_pools) and len(S.pool_units()) == 106
    monkeypatch.setattr(S, "prior_choice_path", lambda: str(tmp_path / "prior_choice.json"))
    with pytest.raises(FileNotFoundError):
        S.stage_priors(9)                                                    # stage 9 cannot run before the choice is written
    (tmp_path / "prior_choice.json").write_text(json.dumps({"chosen": "G"}))
    with pytest.raises(ValueError):
        S.chosen_prior()                                                     # the generic set is never the method's prior
    (tmp_path / "prior_choice.json").write_text(json.dumps({"chosen": "Kc"}))
    assert S.stage_priors(9) == ["Kc"]


@needs_monthly_targets
def test_every_formula_set_gives_every_development_series_a_prior():
    from iba.data.panel import load_panel
    from iba.models.reducers import prior_formula
    from iba.protocol import study as S
    from iba.protocol.dataset import build_dataset
    tasks = {(t.frequency, t.target, t.kind): t for t in S.stage_tasks(7)}
    datasets = {}
    for name in ("Kc", "Sc", "R1", "S3"):
        panels = {f: load_panel(f, formulas=S.prior_file(name)) for f in ("weekly", "monthly")}
        for (freq, tgt, kind), t in tasks.items():
            if (freq, tgt) not in datasets:
                datasets[(freq, tgt)] = build_dataset(panels[freq], t)
            ds = datasets[(freq, tgt)]
            f = prior_formula(panels[freq].formulas, tgt, ds.group_cols, ds.windows, kind)
            assert len(f) >= 3 and all(len(a) + len(n) <= 2 for a, n in f.values()), (name, tgt, kind)
