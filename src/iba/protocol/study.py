"""The study's cells and stages (SPEC-2026-11-13-multitarget-study, sections 3, 6 and 9)."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from ..data.universe import load_manifest, load_universe
from .dataset import Task

TAIL_Q = (0.05, 0.10, 0.20)
STAGES: Dict[int, dict] = {
    1: dict(methods=["raw", "pca", "gpca", "lasso", "iba_e1", "iba_x", "iba_xlo"], estimators=("lin", "gbt"), seeds=(0,), garch=True),
    2: dict(methods=["iba_a", "iba_b", "iba_c", "iba_d"], estimators=("lin", "gbt"), seeds=(0, 1, 2), garch=False),
    # SPEC-2026-11-14-abc-v2: ABC over the whole space (stage 3 of the first spec is the search comparison)
    4: dict(methods=["iba_ar", "iba_ac", "iba_w", "iba_v", "iba_g", "iba_z"], estimators=("lin",), seeds=(0, 1, 2), garch=False,
            spec="SPEC-2026-11-14-abc-v2"),
    # SPEC-2026-11-14-abc-v3: pooled fitness, noise-aware replacement, ensembles (stage 5 = the pooled searches)
    6: dict(methods=["iba_rnda", "iba_rndw", "iba_sna", "iba_snw", "iba_ca", "iba_cw", "iba_cna", "iba_cnw",
                     "iba_fa", "iba_fw", "iba_fna", "iba_fnw"], estimators=("lin",), seeds=(0, 1, 2), garch=False,
            spec="SPEC-2026-11-14-abc-v3", pooled_stage=5),
}
FIRST_SPEC = "SPEC-2026-11-13-multitarget-study"
WRAPUP = "SPEC-2026-11-14-wrapup"
# SPEC-2026-11-14-wrapup, section 3: formula set -> formula file relative to the repo (None = the panel's generic formulas)
PRIOR_SETS: Dict[str, Optional[str]] = {
    "G": None,
    **{f"K{k}": f"priors/llm/K_draw{k}.yaml" for k in range(1, 6)}, **{f"S{k}": f"priors/llm/S_draw{k}.yaml" for k in range(1, 6)},
    "Kc": "priors/llm/K_consensus.yaml", "Sc": "priors/llm/S_consensus.yaml",
    **{f"R{k}": f"priors/random/R_draw{k}.yaml" for k in range(1, 6)}}
CHOSEN = "P*"                              # the formula set chosen by the rule of section 7.2 (written by the report, part A)
# stage 7: every formula set as a fixed formula with three estimators; the no-search colony for G and the consensus
# sets; the benchmarks with the third estimator once (set G). Stage 8 = the five algorithms on the pooled fitness,
# stage 9 = forecasts from the pooled ABC, both with the chosen set.
STAGES[7] = dict(methods=["iba_e1"], estimators=("lin", "gbt", "xgb"), seeds=(0, 1, 2), garch=False, spec=WRAPUP, priors=list(PRIOR_SETS),
                 extra={"G": ["raw", "pca", "gpca", "lasso", "iba_rnda"], "Kc": ["iba_rnda"], "Sc": ["iba_rnda"]})
STAGES[9] = dict(methods=["iba_ca"], estimators=("lin",), seeds=(0, 1, 2), garch=False, spec=WRAPUP, pooled_stage=8, priors=[CHOSEN])
# SPEC-2026-11-14-benchmarks-kpca-ae: two more benchmark reducers (kernel PCA, autoencoder) on the same cells
BENCH2 = "SPEC-2026-11-14-benchmarks-kpca-ae"
STAGES[10] = dict(methods=["kpca", "ae"], estimators=("lin", "gbt", "xgb"), seeds=(0,), garch=False, spec=BENCH2)
# SPEC-2026-11-14-confirmation: the one run of the frozen final method on the held-out series. The formula set of
# the method, the generic and the random sets; benchmarks and GARCH once (set G); for Kc the no-search colony and the
# ABC readings, whose formulas are the DEVELOPMENT colonies of the wrap-up's stage 8 (no search on a confirmation series).
from ..data.universe import CONFIRMATION_SPEC as CONFIRM    # noqa: E402  (the id the data guard opens for)
CONFIRM_SOURCES = ("yahoo",)               # the SG indices (source socgen) are not obtainable: not in the run
CONFIRM_DOWNLOAD = dict(start="2007-01-01", end="2026-10-01")      # as the development download
STAGES[11] = dict(methods=["iba_e1"], estimators=("lin", "gbt", "xgb"), seeds=(0, 1, 2), garch=False, spec=CONFIRM, split="confirmation",
                  priors=["G", "Kc"] + [f"R{k}" for k in range(1, 6)], garch_sets=["G"],
                  extra={"G": ["raw", "pca", "gpca", "lasso", "kpca", "ae"], "Kc": ["iba_rnda", "iba_ca"]},
                  pooled_store=(WRAPUP, 8, "Kc"))
# SPEC-2026-11-15-confirmation-hf: the same frozen method on monthly hedge-fund indices of a second provider (an
# extension of the universe, all confirmation series). As stage 11; the colonies are those of the development
# hedge-fund pool. GARCH-based probabilities once (set G), as in the development monthly cells.
from ..data.universe import HF_CONFIRMATION_SPEC as CONFIRM_HF    # noqa: E402
STAGES[12] = dict(methods=["iba_e1"], estimators=("lin", "gbt", "xgb"), seeds=(0, 1, 2), garch=False, spec=CONFIRM_HF, split="confirmation",
                  priors=["G", "Kc"] + [f"R{k}" for k in range(1, 6)], garch_sets=["G"],
                  extra={"G": ["raw", "pca", "gpca", "lasso", "kpca", "ae"], "Kc": ["iba_rnda", "iba_ca"]},
                  pooled_store=(WRAPUP, 8, "Kc"))
# the pooled-search stages: forecasting stage that shares their seeds, arms, whether the whole-frequency pool is searched
POOLED_STAGES: Dict[int, dict] = {5: dict(forecast_stage=6, arms=("a", "w", "na", "nw"), all_pool=True),
                                  8: dict(forecast_stage=9, arms=("a", "ga", "pso", "sa", "de"), all_pool=False)}


def prior_choice_path() -> str:
    import os
    from ..data.universe import REPO
    return os.path.join(REPO, "docs", "results", WRAPUP, "prior_choice.json")


def chosen_prior() -> str:
    """The formula set chosen mechanically by the report (part A); an error until that has run."""
    import json
    with open(prior_choice_path()) as fh:
        name = json.load(fh)["chosen"]
    if name not in PRIOR_SETS or name == "G":
        raise ValueError(f"prior_choice.json names '{name}'")
    return name


def stage_priors(stage: int) -> List[Optional[str]]:
    """Formula sets a stage runs over ([None] for the stages of the earlier specs)."""
    ps = STAGES[stage].get("priors")
    if not ps:
        return [None]
    return [chosen_prior() if x == CHOSEN else x for x in ps]


def prior_file(name: Optional[str]) -> Optional[str]:
    import os
    from ..data.universe import REPO
    rel = PRIOR_SETS[name] if name else None
    return os.path.join(REPO, rel) if rel else None


def stratum_of() -> Dict[str, str]:
    from ..data.universe import load_hf_catalogue
    series, _ = load_universe()
    cat = load_hf_catalogue()
    return {**{s.ticker: s.asset_class for s in series}, **{s["code"]: cat["asset_class"] for s in cat["series"]}}


def development_tasks() -> List[Task]:
    """Every development cell: 37 daily series x 17 weekly tasks (+ the secondary 13-week
    volatility target) and 11 monthly series x 16 monthly tasks."""
    series, _ = load_universe()
    m = load_manifest()
    dev = {t for v in m.development.values() for t in v}
    tasks: List[Task] = []
    for s in sorted(series, key=lambda s: (s.asset_class, s.ticker)):
        if s.ticker not in dev:
            continue
        if s.frequency == "daily":
            tasks += [Task(s.ticker, "return", h) for h in (1, 4, 13)]
            tasks += [Task(s.ticker, "logrv", h) for h in (1, 4, 13)]
            tasks += [Task(s.ticker, k, h, q) for k in ("tail_loss", "tail_gain") for h in (4, 13) for q in TAIL_Q]
        else:
            tasks += [Task(s.ticker, "return", h, frequency="monthly") for h in (1, 3, 6, 12)]
            tasks += [Task(s.ticker, k, h, q, "monthly") for k in ("tail_loss", "tail_gain") for h in (3, 6) for q in TAIL_Q]
    return tasks


def confirmation_series() -> List[str]:
    """The confirmation series of the run: those of the split whose source can be downloaded (names only; nothing is loaded)."""
    series, _ = load_universe()
    conf = {t for v in load_manifest().confirmation.values() for t in v}
    return sorted(s.ticker for s in series if s.ticker in conf and s.source in CONFIRM_SOURCES)


def confirmation_tasks() -> List[Task]:
    """SPEC-2026-11-14-confirmation: the weekly tasks of the wrap-up spec on every confirmation series (tails at q = 10 %)."""
    strata = stratum_of()
    out: List[Task] = []
    for t in sorted(confirmation_series(), key=lambda t: (strata[t], t)):
        out += [Task(t, "return", h) for h in (1, 4, 13)] + [Task(t, "logrv", h) for h in (1, 4, 13)]
        out += [Task(t, k, h, 0.10) for k in ("tail_loss", "tail_gain") for h in (4, 13)]
    return out


def hf_confirmation_series() -> List[str]:
    """The hedge-fund confirmation series of the run: those the panel's manifest lists as included (names only).
    The manifest is written when the panel is built under the frozen spec; before that there is no series."""
    import json, os
    from ..data.panel import HF_TARGETS
    from ..data.universe import REPO
    path = os.path.join(REPO, "data", "panels", HF_TARGETS, "manifest.json")
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return list(json.load(fh)["series"])


def hf_confirmation_tasks() -> List[Task]:
    """SPEC-2026-11-15-confirmation-hf: the monthly tasks of the wrap-up spec on every series of the panel (tails at q = 10 %)."""
    out: List[Task] = []
    for t in sorted(hf_confirmation_series()):
        out += [Task(t, "return", h, frequency="monthly") for h in (1, 3, 6, 12)]
        out += [Task(t, k, h, 0.10, "monthly") for k in ("tail_loss", "tail_gain") for h in (3, 6)]
    return out


def abc2_tasks() -> List[Task]:
    """SPEC-2026-11-14-abc-v2: every return and volatility cell; of the tail cells those at q = 10 %."""
    return [t for t in development_tasks() if t.q is None or abs(t.q - 0.10) < 1e-12]


def stage_tasks(stage: int) -> List[Task]:
    if STAGES[stage].get("spec") == CONFIRM:
        return confirmation_tasks()
    if STAGES[stage].get("spec") == CONFIRM_HF:
        return hf_confirmation_tasks()
    return abc2_tasks() if STAGES[stage].get("spec") in ("SPEC-2026-11-14-abc-v2", "SPEC-2026-11-14-abc-v3", WRAPUP, BENCH2) else development_tasks()


def pool_units(frequency: str = None, all_pool: bool = True) -> List[Tuple[str, str, Optional[float], int, str, str, List[str]]]:
    """SPEC-2026-11-14-abc-v3, stage 5: (frequency, kind, q, h, task name, pool, members) for every
    task of the spec and every pool: each asset class and "ALL" (every development series of the
    frequency; left out with ``all_pool=False``, SPEC-2026-11-14-wrapup stage 8)."""
    strata, out = stratum_of(), []
    by: Dict[tuple, List[str]] = {}
    for t in abc2_tasks():
        by.setdefault((t.frequency, t.kind, t.q, t.h, t.name), []).append(t.target)
    for (freq, kind, q, h, name), targets in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][4])):
        if frequency and freq != frequency:
            continue
        for st in sorted({strata[t] for t in targets}):
            out.append((freq, kind, q, h, name, st, sorted(t for t in targets if strata[t] == st)))
        if all_pool:
            out.append((freq, kind, q, h, name, "ALL", sorted(targets)))
    return out


def search_comparison_cells() -> List[Task]:
    """Fixed sample for the equal-budget comparison of search algorithms: the alphabetically first
    development series of each daily stratum x {return h=4, volatility h=1, large loss 10 % h=4}."""
    series, _ = load_universe()
    m = load_manifest()
    out: List[Task] = []
    for cls in sorted(m.development):
        daily = sorted(t for t in m.development[cls] if any(s.ticker == t and s.frequency == "daily" for s in series))
        if daily:
            t = daily[0]
            out += [Task(t, "return", 4), Task(t, "logrv", 1), Task(t, "tail_loss", 4, 0.10)]
    return out
