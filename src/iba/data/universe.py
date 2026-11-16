"""The universe catalogue (data/universe.yaml) and the committed split manifest."""
from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Tuple

import yaml

from .split import ConfirmationGuard, Series, SplitManifest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
UNIVERSE = os.path.join(REPO, "data", "universe.yaml")
MANIFEST = os.path.join(REPO, "data", "split_manifest.json")


def load_universe(path: str = UNIVERSE) -> Tuple[List[Series], dict]:
    with open(path) as fh:
        doc = yaml.safe_load(fh)
    out = []
    for stratum, members in doc["strata"].items():
        for m in members:
            out.append(Series(ticker=str(m["ticker"]), asset_class=stratum, source=m.get("source", "yahoo"),
                              frequency=m.get("frequency", "daily"), first_date=str(m["first"])))
    return out, doc["split"]


def file_sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_manifest(path: str = MANIFEST) -> SplitManifest:
    """The committed split with its amendments applied. Amendments only ever move a series from
    confirmation to development (a series already seen cannot serve as confirmation)."""
    with open(path) as fh:
        d = json.load(fh)
    amendments = d.pop("amendments", [])
    for k in ("universe_file_sha256", "created", "note"):
        d.pop(k, None)
    m = SplitManifest(**d)
    for a in amendments:
        for t in a["move_to_development"]:
            for cls, conf in m.confirmation.items():
                if t in conf:
                    conf.remove(t)
                    m.development[cls] = sorted(m.development[cls] + [t])
    return m


# Series that enter a factor panel as predictors (source yahoo). They are loaded by development
# code whenever a panel is read, so they can never be confirmation series (tested).
FACTOR_PANEL_TICKERS = ["HYG", "EMB", "EEM", "DBC", "SLV"]
# target ticker -> factor codes dropped from its group for that target (exclusion rule)
EXCLUDE_FACTORS = {"HYG": ["HYG_RET"], "EMB": ["EMB_RET"], "EEM": ["EEM_RET"], "DBC": ["DBC_RET"], "SLV": ["SLV_RET"]}


def development_series(stratum: str | None = None) -> Dict[str, List[str]]:
    m = load_manifest()
    return {k: v for k, v in m.development.items() if stratum in (None, k)}


CONFIRMATION_SPEC = "SPEC-2026-11-14-confirmation"       # the weekly confirmation series of the split
HF_CONFIRMATION_SPEC = "SPEC-2026-11-15-confirmation-hf" # the monthly hedge-fund indices of the extension below
HF_CATALOGUE = os.path.join(REPO, "data", "universe_hf_confirmation.yaml")


def load_hf_catalogue(path: str = HF_CATALOGUE) -> dict:
    """The extension of the universe: monthly hedge-fund indices of a second provider, all confirmation series.
    Names and file names only; no series is read."""
    with open(path) as fh:
        return yaml.safe_load(fh)


def hf_confirmation_codes() -> List[str]:
    return [s["code"] for s in load_hf_catalogue()["series"]]


def guard(confirmation_run: str | None = None) -> ConfirmationGuard:
    """The guard of the loaders. It opens for confirmation series only when ``confirmation_run`` is the id of one of
    the two confirmation specs AND that spec is frozen and committed; any other non-empty id is an error. The series
    of the hedge-fund extension are confirmation series like those of the split."""
    if confirmation_run:
        if confirmation_run not in (CONFIRMATION_SPEC, HF_CONFIRMATION_SPEC):
            raise PermissionError(f"the confirmation guard opens only for {CONFIRMATION_SPEC} and {HF_CONFIRMATION_SPEC}, not for '{confirmation_run}'")
        from ..protocol.spec import require_frozen
        require_frozen(confirmation_run, check_fingerprint=False)
    g = ConfirmationGuard(load_manifest(), confirmation_run)
    split, hf = set(g.conf), set(hf_confirmation_codes())
    g.conf = split | hf
    if confirmation_run:                                           # each run opens the guard for its own series only
        g.allowed = hf if confirmation_run == HF_CONFIRMATION_SPEC else split
    return g
