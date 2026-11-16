"""Elicitation of prior IBA formulas from a language model (protocol step of the ML system).

Two procedures, one request per (panel, asset class, draw); each answer holds the formulas for
every target type of that asset class:
  K  knowledge only: the manual, the factor dictionary, a description of the asset class;
  S  the same plus simple statistics computed on the rows admissible at the FIRST forecast
     origin (rank correlation of every factor's z-score with the training label, averaged over
     the development series of the class, and the share of series that agree in sign).
The model is told the date of the knowledge cut-off (before the first forecast origin of any
series) and asked to use nothing later. This cannot be enforced: a model trained on later data
may carry hindsight. The limitation is stated wherever these formulas are reported.

Nothing here calls the API at import; ``elicit`` does, with the caller's client."""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MANUAL = os.path.join(REPO, "docs", "protocol", "IBA_MANUAL.md")
MODEL = "claude-opus-5-5"
CUTOFF = "30 September 2017"            # before the first forecast origin of any series (31 October 2017)
TARGETS = {"weekly": ["return", "volatility", "large_loss", "large_gain"], "monthly": ["return", "large_loss", "large_gain"]}
KIND_OF = {"return": "return", "volatility": "logrv", "large_loss": "tail_loss", "large_gain": "tail_gain"}
STAT_H = {"weekly": 4, "monthly": 3}    # horizon of the statistics table (procedure S)
CLASS_TEXT = {
    "equity_us_broad": "broad US equity indices (large-cap, small-cap and blue-chip index funds)",
    "equity_us_sectors": "US equity sector indices (energy, industrials, consumer staples, health care, consumer discretionary and the like)",
    "equity_developed_exus": "equity indices of developed markets outside the US (a broad EAFE index and single-country indices of Europe and developed Asia)",
    "equity_emerging": "emerging-market equity indices (a broad index and single-country indices)",
    "bonds_gov_ig": "US government and investment-grade bond indices (aggregate, intermediate and long Treasuries, inflation-linked)",
    "credit_em_debt": "US high-yield corporate bond and US-dollar emerging-market sovereign bond indices",
    "commodities": "commodity indices (broad baskets, energy, base metals, agriculture, gold and silver, natural gas)",
    "real_estate": "listed US real-estate (REIT) indices",
    "hedge_fund_monthly": "monthly hedge-fund strategy indices (CTA, global macro, equity long/short, market neutral, event driven, distressed, convertible and fixed-income arbitrage, merger arbitrage, funds of funds)",
    "hedge_fund_daily": "daily investable indices of trend-following and CTA hedge-fund strategies",
}
SYSTEM = (
    "You are a senior researcher in macro-finance and asset pricing with long experience of how interest rates, credit, "
    "volatility, currencies, commodities and financial conditions relate to the returns and risks of asset classes. "
    "You are contributing expert judgement to a forecasting study that follows a strict information rule.\n\n"
    "The date is {cutoff}. Use only what was known by that date: economic theory, and empirical regularities documented "
    "in research published by then. Do not use, mention or rely on any market event, data release or publication after "
    "that date; if you are not sure something was known by then, leave it out. Your rationales should rest on mechanisms, "
    "not on particular episodes."
)


def load_dictionary(frequency: str) -> pd.DataFrame:
    d = pd.read_csv(os.path.join(REPO, "data", "panels", f"{frequency}_2026-11-11", "factor_dictionary.csv"))
    return d[["code", "label", "description", "group"]]


def groups_of(dictionary: pd.DataFrame) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for code, g in zip(dictionary["code"], dictionary["group"]):
        out.setdefault(g, []).append(code)
    out["ENDG"] = ["__target__"]
    return out


def schema(frequency: str, groups: Dict[str, List[str]]) -> Dict[str, Any]:
    """JSON schema of an answer: per target, per group, a list of literals and a rationale.
    The shape is defined once and referenced; the factor is a plain string, not an enumeration per
    group, because the API refuses the larger grammar (400 "compiled grammar is too large": every
    inlined variant on both panels, and the referenced one with enumerations on the monthly panel).
    That a factor belongs to its group is checked by ``validate``."""
    literal = {"type": "object", "additionalProperties": False, "required": ["factor", "state"],
               "properties": {"factor": {"type": "string"}, "state": {"type": "string", "enum": ["high", "not_high"]}}}
    group = {"type": "object", "additionalProperties": False, "required": ["literals", "rationale"],
             "properties": {"literals": {"type": "array", "items": literal}, "rationale": {"type": "string"}}}
    target = {"type": "object", "additionalProperties": False, "required": list(groups),
              "properties": {g: {"$ref": "#/$defs/group"} for g in groups}}
    return {"type": "object", "additionalProperties": False, "required": TARGETS[frequency],
            "$defs": {"group": group, "target": target},
            "properties": {t: {"$ref": "#/$defs/target"} for t in TARGETS[frequency]}}


def build_prompt(frequency: str, asset_class: str, dictionary: pd.DataFrame, stats: Optional[pd.DataFrame] = None) -> Tuple[str, str]:
    """(system, user) of one request. ``stats`` switches on procedure S."""
    with open(MANUAL) as fh:
        manual = fh.read()
    period = "week" if frequency == "weekly" else "month"
    lines = [manual, "", "# Your task", "",
             f"Asset class: {CLASS_TEXT[asset_class]}. Data are {frequency}; horizons run from one {period} to "
             f"{'thirteen weeks' if frequency == 'weekly' else 'twelve months'}. Give one set of formulas for each target "
             f"({', '.join(TARGETS[frequency])}); the same set is used for every index of the class and every horizon.", "",
             "Factor groups (code: what it is). Every factor enters as its trailing z-score.", ""]
    for g, sub in dictionary.groupby("group", sort=False):
        lines.append(f"## {g}")
        lines += [f"- {r.code}: {r.label}. {r.description}" for r in sub.itertuples()]
        lines.append("")
    lines += ["## ENDG", "- __target__: the index's own recent behaviour (manual, section 4)", ""]
    if stats is not None:
        lines += ["# Statistics from the training sample", "",
                  f"Computed only on data up to the first forecast date. For every factor and target: the rank correlation of the "
                  f"factor's z-score with the target over the next {STAT_H[frequency]} {period}s, averaged over the indices of the class, "
                  f"and in brackets the share of indices whose correlation has that sign. Small samples and overlapping "
                  f"windows make these noisy: weigh them against what you know.", "", stats.to_markdown(index=False), ""]
    lines += ["Answer in the required JSON format."]
    return SYSTEM.format(cutoff=CUTOFF), "\n".join(lines)


def training_statistics(panel, frequency: str, targets: Sequence[str], dictionary: pd.DataFrame) -> pd.DataFrame:
    """Procedure S: rank correlation of each factor's longer-window z-score with the training label
    on the rows admissible at the first block origin, averaged over ``targets`` (series)."""
    from scipy.stats import spearmanr
    from ..protocol.dataset import Task
    from ..protocol.walkforward import block_contexts, protocol_for
    h, rows = STAT_H[frequency], {}
    for name in TARGETS[frequency]:
        kind = KIND_OF[name]
        per_series = []
        for tgt in targets:
            _, ctx = next(iter(block_contexts(panel, Task(tgt, kind, h, 0.10 if kind.startswith("tail") else None, frequency), protocol_for(frequency))))
            w = max(ctx.ds.windows)
            X, y = ctx.ds.X.iloc[ctx.rows], ctx.y_block
            col = {c: f"{c}_{w}m_zs" for c in dictionary["code"]}
            col["__target__"] = f"{tgt}_{w}m_zs"
            per_series.append({c: (spearmanr(X[k].values, y)[0] if k in X and np.std(y) > 0 else np.nan) for c, k in col.items()})
        R = pd.DataFrame(per_series)
        m = R.mean()
        agree = (np.sign(R) == np.sign(m)).mean()
        rows[name] = {c: ("n/a" if not np.isfinite(m[c]) else f"{m[c]:+.2f} ({100 * agree[c]:.0f} %)") for c in R.columns}
    out = pd.DataFrame(rows)
    out.insert(0, "factor", out.index)
    grp = dict(zip(dictionary["code"], dictionary["group"])); grp["__target__"] = "ENDG"
    out.insert(1, "group", [grp[c] for c in out["factor"]])
    return out.reset_index(drop=True)


def validate(answer: Dict[str, Any], frequency: str, groups: Dict[str, List[str]]) -> List[str]:
    """Problems of an answer against the manual (empty list = valid)."""
    bad = []
    for t in TARGETS[frequency]:
        if t not in answer:
            bad.append(f"{t}: missing"); continue
        used = 0
        for g, codes in groups.items():
            lits = answer[t].get(g, {}).get("literals")
            if lits is None:
                bad.append(f"{t}/{g}: missing"); continue
            f = [x["factor"] for x in lits]
            if len(lits) > 2 or len(set(f)) != len(f) or any(c not in codes for c in f) or any(x["state"] not in ("high", "not_high") for x in lits):
                bad.append(f"{t}/{g}: {lits}")
            used += len(lits)
        if used == 0:
            bad.append(f"{t}: every group empty")
    text = json.dumps(answer)
    late = sorted({y for y in re.findall(r"\b(20[12]\d)\b", text) if int(y) >= 2018})
    if late:
        bad.append(f"mentions years after the cut-off: {late}")
    return bad


def to_formulas(answer: Dict[str, Any], frequency: str) -> Dict[str, Dict[str, list]]:
    """Answer -> the formula-file sections of one asset class: {kind: {"groups": {G: [[code, state], ...]}}}."""
    return {KIND_OF[t]: {"groups": {g: [[x["factor"], x["state"]] for x in v["literals"]] for g, v in answer[t].items() if v["literals"]}}
            for t in TARGETS[frequency]}


def elicit(client, frequency: str, asset_class: str, dictionary: pd.DataFrame, stats: Optional[pd.DataFrame] = None,
           model: str = MODEL, retries: int = 2) -> Dict[str, Any]:
    """One request (re-asked at most ``retries`` times if the answer breaks the manual). Returns the
    record that is stored: prompts' hash, model, response id, usage, answer, problems, attempts.
    No fallback model is configured on purpose: a formula set must come from the named model, so a
    refusal is recorded as a failed draw."""
    groups = groups_of(dictionary)
    system, user = build_prompt(frequency, asset_class, dictionary, stats)
    record: Dict[str, Any] = {"frequency": frequency, "asset_class": asset_class, "procedure": "S" if stats is not None else "K",
                              "model": model, "cutoff": CUTOFF, "prompt_sha256": hashlib.sha256((system + "\n" + user).encode()).hexdigest(),
                              "attempts": []}
    for _ in range(retries + 1):
        with client.messages.stream(model=model, max_tokens=32000, system=system, messages=[{"role": "user", "content": user}],
                                    thinking={"type": "adaptive"}, output_config={"effort": "high", "format": {"type": "json_schema", "schema": schema(frequency, groups)}}) as stream:
            resp = stream.get_final_message()
        att = {"id": resp.id, "stop_reason": resp.stop_reason, "served_model": resp.model,
               "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}}
        if resp.stop_reason == "end_turn":
            answer = json.loads(next(b.text for b in resp.content if b.type == "text"))
            att["problems"] = validate(answer, frequency, groups)
            record["attempts"].append(att)
            if not att["problems"]:
                record["answer"] = answer
                return record
        else:
            att["problems"] = [f"stop_reason {resp.stop_reason}"]
            record["attempts"].append(att)
    record["answer"] = None
    return record
