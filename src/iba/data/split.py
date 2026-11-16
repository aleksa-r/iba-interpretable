"""One-time stratified development / confirmation split of the universe.

Deterministic: each series is assigned by the first byte of sha256(f"{salt}|{ticker}") compared
with the development share, within its stratum (asset class); forced members stay where the author
put them (the 8 ETFs and 11 CISDM indices are development data because they have been examined).
Every stratum keeps at least ``min_confirmation`` confirmation series. The result is written once
to ``data/split_manifest.json`` with the salt, the rule and the sha256 of the universe file, and
the loaders refuse confirmation tickers unless a frozen spec id is passed.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Series:
    ticker: str
    asset_class: str
    source: str
    frequency: str            # daily | monthly
    first_date: str


@dataclass
class SplitManifest:
    salt: str
    development_share: float
    min_confirmation: int
    forced_development: List[str]
    development: Dict[str, List[str]] = field(default_factory=dict)
    confirmation: Dict[str, List[str]] = field(default_factory=dict)
    universe_sha256: str = ""

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, sort_keys=True)


def _score(salt: str, ticker: str) -> float:
    h = hashlib.sha256(f"{salt}|{ticker}".encode()).digest()
    return int.from_bytes(h[:4], "big") / 2 ** 32


def stratified_split(universe: List[Series], salt: str, development_share: float = 0.6,
                     min_confirmation: int = 2, forced_development: Optional[List[str]] = None) -> SplitManifest:
    forced = set(forced_development or [])
    m = SplitManifest(salt=salt, development_share=development_share, min_confirmation=min_confirmation,
                      forced_development=sorted(forced))
    by_class: Dict[str, List[Series]] = {}
    for s in universe:
        by_class.setdefault(s.asset_class, []).append(s)
    for cls, members in sorted(by_class.items()):
        free = sorted([s for s in members if s.ticker not in forced], key=lambda s: _score(salt, s.ticker))
        dev = [s.ticker for s in members if s.ticker in forced]
        conf: List[str] = []
        n_dev_target = round(development_share * len(members))
        for s in free:                              # lowest scores go to development
            if len(dev) < n_dev_target and len(free) - (len(dev) - sum(1 for t in dev if t in forced)) > min_confirmation:
                dev.append(s.ticker)
            else:
                conf.append(s.ticker)
        if len(conf) < min_confirmation and len(members) > min_confirmation:
            # move the highest-scored non-forced development members to confirmation
            movable = sorted([t for t in dev if t not in forced], key=lambda t: -_score(salt, t))
            while len(conf) < min_confirmation and movable:
                t = movable.pop(0); dev.remove(t); conf.append(t)
        m.development[cls] = sorted(dev)
        m.confirmation[cls] = sorted(conf)
    m.universe_sha256 = hashlib.sha256(json.dumps([s.__dict__ for s in sorted(universe, key=lambda s: s.ticker)]).encode()).hexdigest()
    return m


class ConfirmationGuard:
    """Loaders call ``check(ticker)``; a confirmation ticker is refused unless the guard was
    opened with a frozen spec id (the engine opens it only for the one-shot final run)."""

    def __init__(self, manifest: SplitManifest, confirmation_run: Optional[str] = None):
        self.conf = {t for v in manifest.confirmation.values() for t in v}
        self.spec = confirmation_run
        self.allowed: Optional[set] = None        # the series the open guard lets through (None: every confirmation series)

    def check(self, ticker: str) -> None:
        if ticker in self.conf and not self.spec:
            raise PermissionError(f"{ticker} is a CONFIRMATION series; development code must not load it")
        if ticker in self.conf and self.allowed is not None and ticker not in self.allowed:
            raise PermissionError(f"{ticker} is a confirmation series of another run than {self.spec}")
