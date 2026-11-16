"""Weekly and monthly panels: factor panels as built and verified with the earlier code base, plus target
panels built here from the dated daily download.

Weekly target panel (W-FRI rows, aligned to the factor panel's index):
  returns.csv       simple weekly return = last adjusted close of the week / previous week's − 1
  rv.csv            weekly realised variance = sum of squared daily log returns within the week
  daily_logret.csv  daily log returns (GARCH benchmarks only)
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from .universe import CONFIRMATION_SPEC, EXCLUDE_FACTORS, HF_CONFIRMATION_SPEC, REPO, guard, load_hf_catalogue

FREQ = "W-FRI"


def _sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def build_weekly_targets(raw_csv: str, factor_dir: str, out_dir: str, confirmation_run: str | None = None) -> Dict[str, str]:
    f = pd.read_csv(os.path.join(factor_dir, "factors.csv"), index_col=0, parse_dates=True)
    raw = pd.read_csv(raw_csv, parse_dates=["date"])
    g = guard(confirmation_run)
    for t in raw.symbol.unique():
        g.check(t)
    px = raw.pivot(index="date", columns="symbol", values="adj_close").sort_index()
    # log returns between consecutive prices OF EACH SERIES: on the union calendar a date that one series lacks
    # would otherwise blank two of its returns (they would drop out of realised variance and of the GARCH input)
    lr = pd.DataFrame({c: np.log(px[c].dropna()).diff() for c in px.columns}).reindex(px.index)
    lr = lr.loc[lr.index <= f.index.max()]
    ret = px.resample(FREQ).last().pct_change().reindex(f.index)
    rv = (lr ** 2).resample(FREQ).sum(min_count=1).reindex(f.index)
    os.makedirs(out_dir, exist_ok=True)
    ret.index.name = rv.index.name = "Date"; lr.index.name = "date"
    ret.round(8).to_csv(os.path.join(out_dir, "returns.csv"))
    rv.round(12).to_csv(os.path.join(out_dir, "rv.csv"))
    lr.round(10).to_csv(os.path.join(out_dir, "daily_logret.csv"))
    man = {"built": pd.Timestamp.now(tz="UTC").isoformat(), "raw": os.path.relpath(raw_csv, REPO), "raw_sha256": _sha(raw_csv),
           "factor_dir": os.path.relpath(factor_dir, REPO), "frequency": FREQ, "weeks": int(len(f)),
           "first": str(f.index.min().date()), "last": str(f.index.max().date()), "series": sorted(px.columns),
           "sha256": {n: _sha(os.path.join(out_dir, n)) for n in ("returns.csv", "rv.csv", "daily_logret.csv")}}
    with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
        json.dump(man, fh, indent=2)
    return man["sha256"]


MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
HF_TARGETS = "monthly_confirmation_bh"     # target panel of the hedge-fund confirmation series (built once, after the freeze)


def _pct(text: str) -> float:
    """'-2.18%*' -> -0.0218 (a percentage written as text; trailing asterisks mark the provider's estimates).
    Text without a per-cent sign is refused: its scale would be a guess."""
    if "%" not in text:
        raise ValueError(f"text cell without a per-cent sign: {text!r}")
    return float(text.replace("*", "").replace("%", "").replace(",", "").strip()) / 100.0


def parse_year_month_grid(rows: List[list]) -> Dict[str, object]:
    """Monthly returns from a sheet laid out as one row per year: a header row ``Jan .. Dec, YTD``, then rows
    ``year, twelve months, YTD``. A month is a number or a percentage written as text; text with an asterisk is an
    estimate of the provider. Numbers are either fractions or per cent: the scale is the one under which the months
    of every complete year compound to the year's stated YTD (anything else is an error, not a guess).
    A year that is incomplete or holds estimates is checked against its stated YTD as well when it has one.
    Returns {'returns': Series indexed by month end, 'estimated': [month ends], 'scale': 1.0 | 0.01,
    'years_verified': n, 'years_unverified': [years without a stated YTD]}."""
    hdr = next((i for i, r in enumerate(rows) if [str(c).strip() for c in r[1:13]] == list(MONTHS)), None)
    if hdr is None:
        raise ValueError("no header row 'Jan .. Dec'")
    raw, text_scale, est, ytd, ytd_is_text = {}, {}, [], {}, {}
    for r in rows[hdr + 1:]:
        try:
            year = int(float(r[0]))
        except (TypeError, ValueError):
            continue
        if not 1900 < year < 2100:
            continue
        for m in range(12):
            c = r[1 + m]
            if c is None or (isinstance(c, str) and not c.strip()):
                continue
            end = pd.Timestamp(year=year, month=m + 1, day=1) + pd.offsets.MonthEnd(0)
            if end in raw:
                raise ValueError(f"{end.date()} appears twice (a second table on the sheet?)")
            if isinstance(c, str):
                raw[end], text_scale[end] = _pct(c), True
                if "*" in c:
                    est.append(end)
            else:
                raw[end], text_scale[end] = float(c), False
        y = r[13] if len(r) > 13 else None
        if isinstance(y, str) and y.strip():
            ytd[year], ytd_is_text[year] = _pct(y), True
        elif y is not None and not isinstance(y, str):
            ytd[year], ytd_is_text[year] = float(y), False         # a number: in the scale of the numeric months
    if not raw:
        raise ValueError("no monthly value found")
    s = pd.Series(raw).sort_index()
    full = [y for y in sorted(ytd) if sum(1 for d in s.index if d.year == y) == 12 and not any(d.year == y for d in est)]
    if len(full) < 3:
        raise ValueError("fewer than three complete years with a stated YTD: the scale cannot be verified")

    def error(scale: float, years) -> float:
        worst = 0.0
        for y in years:
            vals = [s[d] * (1.0 if text_scale[d] else scale) for d in s.index if d.year == y]
            stated = ytd[y] * (1.0 if ytd_is_text[y] else scale)
            worst = max(worst, abs(float(np.prod([1.0 + v for v in vals])) - 1.0 - stated))
        return worst
    errs = {scale: error(scale, full) for scale in (1.0, 0.01)}
    scale = min(errs, key=errs.get)
    if errs[scale] > 1e-3:                                         # twelve months and the YTD, each rounded to 0.01 %
        raise ValueError(f"months do not compound to the stated YTD under either scale (largest gaps {errs})")
    partial = [y for y in sorted(ytd) if y not in full]            # incomplete years and years with estimates
    if partial and error(scale, partial) > 1e-3:
        raise ValueError(f"the months of {partial} do not compound to the stated YTD (gap {error(scale, partial):.5f})")
    s = pd.Series({d: s[d] * (1.0 if text_scale[d] else scale) for d in s.index})
    if not s.index.is_monotonic_increasing or len(pd.period_range(s.index[0], s.index[-1], freq="M")) != len(s):
        raise ValueError("months are not contiguous")
    years = sorted({d.year for d in s.index})
    return {"returns": s, "estimated": sorted(est), "scale": scale, "years_verified": len([y for y in years if y in ytd]),
            "years_unverified": [y for y in years if y not in ytd]}


def read_xls_rows(path: str) -> List[list]:
    """First sheet of an .xls file as rows of numbers, strings and None."""
    import xlrd
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    return [[(c.value if c.ctype in (1, 2) else None) for c in sh.row(r)] for r in range(sh.nrows)]


def build_monthly_hf_targets(out_dir: str, confirmation_run: str | None = None, check_only: bool = False) -> dict:
    """The target panel of the hedge-fund confirmation series, on the index of the monthly factor panel.
    A series enters if its history has every month of the factor panel (the coverage rule of the spec); the others
    are listed with the reason. ``check_only`` reads the files for their layout and coverage alone and writes and
    returns no value of any series (it needs no frozen spec: it is how the spec's series list is established)."""
    import xlrd  # noqa: F401  (a missing reader must stop the build, not make every file "not readable")
    cat = load_hf_catalogue()
    if not check_only:
        guard(confirmation_run)
        if confirmation_run != HF_CONFIRMATION_SPEC:
            raise PermissionError(f"the hedge-fund confirmation panel is built only under {HF_CONFIRMATION_SPEC}")
    f = pd.read_csv(os.path.join(REPO, "data", "panels", "monthly_2026-11-11", "factors.csv"), index_col=0, parse_dates=True)
    raw_dir = os.path.join(REPO, cat["raw_dir"])
    cols, report = {}, []
    for srs in cat["series"]:
        path = os.path.join(raw_dir, srs["file"])
        row = {"code": srs["code"], "name": srs["name"], "file": srs["file"]}
        try:
            g = parse_year_month_grid(read_xls_rows(path))
            s = g["returns"]
            missing = [d for d in f.index if d not in s.index]
            est = [d for d in g["estimated"] if d in f.index]
            row.update(first=str(s.index[0].date()), last=str(s.index[-1].date()), months=int(len(s)), scale=g["scale"],
                       years_verified=g["years_verified"], years_unverified=g["years_unverified"],
                       estimated_in_panel=[str(d.date()) for d in est], sha256=_sha(path),
                       included=not missing, reason="" if not missing else f"{len(missing)} months of the panel are missing (first: {missing[0].date()})")
            if not missing:
                cols[srs["code"]] = s.reindex(f.index)
        except Exception as exc:                                    # an unreadable file is left out and reported, never guessed
            row.update(included=False, reason=f"not readable: {exc}")
        report.append(row)
    man = {"spec": HF_CONFIRMATION_SPEC, "raw_dir": cat["raw_dir"], "factor_dir": "data/panels/monthly_2026-11-11", "frequency": "monthly",
           "months": int(len(f)), "first": str(f.index.min().date()), "last": str(f.index.max().date()),
           "series": [r["code"] for r in report if r["included"]], "files": report}
    # the rows each series gives the engine, per task, against the development panel's (values are not reported):
    # the stored development colonies are admissible only at block origins with the same number of rows
    man["rows_as_development"] = _rows_as_development(pd.DataFrame(cols), f)
    if check_only:
        return man
    # the panel is written only if it is the one the spec describes: the listed files, unchanged, and the listed series
    changed = [r["code"] for r, srs in zip(report, cat["series"]) if srs.get("sha256") and r.get("sha256") != srs["sha256"]]
    if changed or any(not srs.get("sha256") for srs in cat["series"]):
        raise ValueError(f"files differ from the checksums of the catalogue (or the catalogue has none): {changed}")
    if sorted(man["series"]) != sorted(cat["expected_series"]):
        raise ValueError(f"the series that pass the coverage rule are not those of the spec: {sorted(set(man['series']) ^ set(cat['expected_series']))}")
    ret = pd.DataFrame(cols)
    ret.index.name = "Date"
    os.makedirs(out_dir, exist_ok=True)
    ret.round(8).to_csv(os.path.join(out_dir, "returns.csv"))
    man.update(built=pd.Timestamp.now(tz="UTC").isoformat(), sha256={"returns.csv": _sha(os.path.join(out_dir, "returns.csv"))})
    with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
        json.dump(man, fh, indent=2)
    return man


def _rows_as_development(returns: pd.DataFrame, factors: pd.DataFrame) -> Dict[str, bool]:
    """For every series of ``returns``: does it give each monthly task as many rows as a development series does?"""
    from ..protocol.dataset import Task, build_dataset
    dev = load_panel("monthly")
    d = pd.read_csv(os.path.join(REPO, "data", "panels", "monthly_2026-11-11", "factor_dictionary.csv"))
    groups: Dict[str, List[str]] = {}
    for code, grp in zip(d["code"], d["group"]):
        groups.setdefault(grp, []).append(code)
    idx = factors.index.intersection(returns.index)
    new = Panel("monthly", factors.loc[idx], groups, returns.loc[idx], None, None, {}, 12)
    tasks = [("return", h, None) for h in (1, 3, 6, 12)] + [(k, h, 0.10) for k in ("tail_loss", "tail_gain") for h in (3, 6)]
    ref = dev.returns.columns[0]
    want = {(k, h): len(build_dataset(dev, Task(ref, k, h, q, "monthly"))) for k, h, q in tasks}
    out = {}
    for c in returns.columns:
        try:
            out[c] = all(len(build_dataset(new, Task(c, k, h, q, "monthly"))) == want[(k, h)] for k, h, q in tasks)
        except ValueError:
            out[c] = False
    return out


@dataclass
class Panel:
    """Everything one target needs. ``frequency`` is 'weekly' or 'monthly'."""
    frequency: str
    factors: pd.DataFrame              # raw factors, index = period end
    groups: Dict[str, List[str]]       # group -> factor codes
    returns: pd.DataFrame              # simple period returns of the target series
    rv: pd.DataFrame | None            # weekly realised variance (daily series only)
    daily: pd.DataFrame | None         # daily log returns (GARCH benchmarks)
    formulas: dict                     # prior formulas (the generic set unless another file is given)
    periods_per_year: int

    def groups_for(self, target: str) -> Dict[str, List[str]]:
        excl = set(EXCLUDE_FACTORS.get(target, []))
        out = {g: [c for c in cols if c not in excl] for g, cols in self.groups.items()}
        return {g: c for g, c in out.items() if c}


CONFIRMATION_TARGETS = "weekly_confirmation"      # target panel of the confirmation series (built once, after the freeze)


def load_panel(frequency: str, formulas: str | None = None, confirmation_run: str | None = None) -> Panel:
    """``formulas``: path of a formula file to use as the prior instead of the panel's generic
    ``expert_formulas.yaml`` (for example a per-asset-class file under ``priors/llm/``).
    ``confirmation_run``: the id of a FROZEN, committed confirmation spec; only then is a target panel of
    confirmation series read instead of the development one (the weekly series of the split under
    SPEC-2026-11-14-confirmation, the monthly hedge-fund indices under SPEC-2026-11-15-confirmation-hf)."""
    import yaml
    base = os.path.join(REPO, "data", "panels")
    if confirmation_run:
        guard(confirmation_run)                                   # a confirmation spec, frozen and committed, or an error
        if frequency != {CONFIRMATION_SPEC: "weekly", HF_CONFIRMATION_SPEC: "monthly"}[confirmation_run]:
            raise ValueError(f"{confirmation_run} has no {frequency} confirmation series")
    if frequency == "weekly":
        fdir = os.path.join(base, "weekly_2026-11-11")
        tdir = os.path.join(base, CONFIRMATION_TARGETS if confirmation_run else "weekly_dev_2026-11-13")
        returns = pd.read_csv(os.path.join(tdir, "returns.csv"), index_col=0, parse_dates=True)
        rv = pd.read_csv(os.path.join(tdir, "rv.csv"), index_col=0, parse_dates=True)
        daily = pd.read_csv(os.path.join(tdir, "daily_logret.csv"), index_col=0, parse_dates=True)
        ppy = 52
    elif frequency == "monthly":
        fdir = os.path.join(base, "monthly_2026-11-11")
        tfile = os.path.join(base, HF_TARGETS, "returns.csv") if confirmation_run else os.path.join(fdir, "targets.csv")
        returns = pd.read_csv(tfile, index_col=0, parse_dates=True)
        rv, daily, ppy = None, None, 12
    else:
        raise ValueError(frequency)
    g = guard(confirmation_run)
    for t in returns.columns:
        g.check(t)
    factors = pd.read_csv(os.path.join(fdir, "factors.csv"), index_col=0, parse_dates=True)
    d = pd.read_csv(os.path.join(fdir, "factor_dictionary.csv"))
    groups: Dict[str, List[str]] = {}
    for code, grp in zip(d["code"], d["group"]):
        groups.setdefault(grp, []).append(code)
    with open(formulas or os.path.join(fdir, "expert_formulas.yaml")) as fh:
        formulas = yaml.safe_load(fh)
    idx = factors.index.intersection(returns.index)
    return Panel(frequency, factors.loc[idx], groups, returns.loc[idx], None if rv is None else rv.loc[idx],
                 daily, formulas, ppy)
