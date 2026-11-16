"""The explanation step: exact numbers in, a short text out, every number in the text checked.

Two levels. ``forecast_payload``: one forecast of one series (formula, factor states at the forecast
date, group values, the linear model's contributions, exact XGBoost attributions, the reference
forecast, the measured track record). ``class_payload``: one asset class and target over the whole
test period (the formula and its rationale, how active each group was, what share of the forecast's
movement it carried, whether the fitted sign was stable, the measured skill per horizon).
``explain`` sends a payload and accepts the answer only if every number in it is written in the
payload (``check_numbers``); otherwise it asks again, at most ``retries`` times, and then records
the failure. No fallback model: an explanation comes from the named model or not at all.
Nothing here calls the API at import."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

MODEL = "claude-opus-5-5"
TARGET_OF = {"return": "return", "logrv": "volatility", "tail_loss": "large_loss", "tail_gain": "large_gain"}
TARGET_TEXT = {
    "return": "the index return over the next {h}",
    "volatility": "the log of the realised variance of the index over the next {h}; the model forecasts what a HAR model of the index's own past variance does not already predict",
    "large_loss": "the probability that the return over the next {h} falls below the lowest tenth of its past distribution",
    "large_gain": "the probability that the return over the next {h} rises above the highest tenth of its past distribution",
}
REFERENCE_TEXT = {"return": "the historical mean return", "volatility": "the HAR model of the index's own past variance",
                  "large_loss": "the historical frequency of the event (base rate)", "large_gain": "the historical frequency of the event (base rate)"}
UNIT = {"return": "percentage points of return", "volatility": "log-variance units, added to the HAR part",
        "large_loss": "log-odds of the event", "large_gain": "log-odds of the event"}
SYSTEM = (
    "You explain the output of a quantitative forecasting model to a reader with a finance background who has not seen the model.\n\n"
    "The model: market and macroeconomic factors are arranged in groups. For each group one logical statement (a formula) about the "
    "state of the group was written BEFORE the forecasting period by a language model acting as an expert, with a rationale. A formula "
    "is a conjunction of at most two literals (\"factor is high\" / \"factor is NOT high\"); each literal has a degree of truth between "
    "0 and 1 and the formula's value is their product. A small linear model turns the group values into the forecast; its coefficients "
    "are estimated on past data only and can have either sign.\n\n"
    "Rules.\n"
    "1. Use only the material in the message. Do not add market events, data, dates or facts that are not in it.\n"
    "2. Quote numbers exactly as they are written in the message, digit for digit. Do not compute new numbers: no sums, differences, "
    "ratios, rounding or rescaling. If you need a comparison, make it in words.\n"
    "3. The rationale given with a formula is an assumption made beforehand, not a finding. Where the fitted coefficient or the "
    "contribution agrees or disagrees with it, say so.\n"
    "4. Say plainly what the track record shows, including when the model has no measured advantage over the reference.\n"
    "5. Plain prose for a careful reader. No headings, no bullet lists, no factor codes without their description."
)
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["headline", "explanation", "limits"],
          "properties": {"headline": {"type": "string"}, "explanation": {"type": "string"}, "limits": {"type": "string"}}}
ALWAYS = {float(k) for k in range(0, 13)} | {95.0, 100.0}      # small counts and the usual percentages may be written freely
# a number is read wherever it starts after a non-letter, whatever follows it ("2.5x", "7.25bp" and "10Y" are numbers);
# only digits inside a code, after a letter or underscore, are not (T10Y2Y_CHG)
_NUM = re.compile(r"(?<![A-Za-z_\d.,])[-−–+]?\d+(?:,\d{3})*(?:\.\d+)?")


def numbers(text: str) -> List[float]:
    out = []
    for tok in _NUM.findall(text):
        tok = tok.lstrip("-−–+").replace(",", "")
        try:
            out.append(float(tok))
        except ValueError:
            pass
    return out


def check_numbers(answer: Dict[str, str], payload: str) -> List[str]:
    """Numbers written in the answer that are not written in the payload (compared by magnitude)."""
    allowed = set(numbers(payload)) | ALWAYS
    bad = []
    for field in ("headline", "explanation", "limits"):
        for tok in _NUM.findall(answer.get(field, "")):
            v = float(tok.lstrip("-−–+").replace(",", ""))
            if not any(abs(v - a) < 1e-9 for a in allowed):
                bad.append(tok)
    return sorted(set(bad))


def f(x: float, d: int = 2, sign: bool = False) -> str:
    """A number as it is shown to the model (and may be quoted back)."""
    if x is None or not np.isfinite(x):
        return "n/a"
    s = f"{x:+.{d}f}" if sign else f"{x:.{d}f}"
    return "0." + "0" * d if float(s) == 0 else s


def horizon_text(h: int, frequency: str) -> str:
    unit = "week" if frequency == "weekly" else "month"
    return f"{h} {unit}{'s' if h > 1 else ''}"


def formula_lines(literals: Sequence[Dict[str, Any]], labels: Dict[str, str], with_state: bool) -> List[str]:
    """One line per group: the formula in words (and, with ``with_state``, the factor states behind it)."""
    by: Dict[str, List[Dict[str, Any]]] = {}
    for r in literals:
        by.setdefault(r["group"], []).append(r)
    lines = []
    for g, rs in by.items():
        words = " AND ".join(f"\"{labels.get(r['factor'], r['factor'])}\" is {'high' if r['state'] == 'high' else 'NOT high'}" for r in rs)
        line = f"- Group {g}: {words}."
        if with_state:
            line += " " + "; ".join(f"z-score of \"{labels.get(r['factor'], r['factor'])}\" {f(r['zscore'], 2, True)}, degree of truth of \"is high\" {f(r['truth_high'])}, "
                                    f"value of the literal {f(r['literal'])}" for r in rs) + f". Value of the formula: {f(rs[0]['group_value'])}."
        lines.append(line)
    return lines


def forecast_payload(c: Dict[str, Any]) -> str:
    """``c``: the prepared numbers of one forecast (see scripts/explain.py: ``forecast_case``)."""
    tname, h = c["target_name"], horizon_text(c["h"], c["frequency"])
    scale = 100.0 if tname == "return" else 1.0
    L = [f"# One forecast", "",
         f"Series: {c['series']} ({c['class_text']}). Target: {TARGET_TEXT[tname].format(h=h)}. Forecast date: {c['date']}.", ""]
    if tname == "return":
        L += [f"Forecast: {f(100 * c['forecast'], 2, True)} % over the next {h}. Reference ({REFERENCE_TEXT[tname]}): {f(100 * c['reference'], 2, True)} %."]
    elif tname == "volatility":
        L += [f"Forecast of log realised variance: {f(c['forecast'], 3)}. Reference ({REFERENCE_TEXT[tname]}): {f(c['reference'], 3)}. "
              f"The factor model's addition to the HAR part: {f(c['raw'], 3, True)} log-variance units."]
    else:
        L += [f"Forecast probability: {f(100 * c['forecast'], 1)} %. Reference ({REFERENCE_TEXT[tname]}): {f(100 * c['reference'], 1)} %."]
    L += ["", "## The formulas and the factor states on the forecast date", ""] + formula_lines(c["literals"], c["labels"], True)
    L += ["", "## What was assumed when the formulas were written (rationale per group)", ""] + [f"- Group {g}: {r}" for g, r in c["rationales"].items()]
    L += ["", f"## The linear model on the forecast date (contributions in {UNIT[tname]})", "",
          f"Starting level (the model's output when every group is at its training average): {f(scale * c['intercept'], 3, True)}.", "",
          "| group | value of the formula today | its average in the training sample | coefficient per standard deviation | contribution today |", "|---|---|---|---|---|"]
    for g, v, mu, b, ct in zip(c["groups"], c["value"], c["train_mean"], c["coef"], c["contrib"]):
        L.append(f"| {g} | {f(v)} | {f(mu)} | {f(scale * b, 3, True)} | {f(scale * ct, 3, True)} |")
    L += ["", "The starting level plus the contributions gives the forecast" + {"return": ".", "volatility": "'s addition to the HAR part.",
                                                                                "large_loss": " in log-odds.", "large_gain": " in log-odds."}[tname]]
    if c.get("shap") is not None:
        L += ["", f"## A tree model (XGBoost) on the same group values, as a second view (exact attributions, in {UNIT[tname]})", "",
              (f"Its forecast: {f(100 * c['forecast_xgb'], 2, True)} %." if tname == "return" else
               f"Its forecast of log realised variance: {f(c['forecast_xgb'], 3)}." if tname == "volatility" else f"Its forecast probability: {f(100 * c['forecast_xgb'], 1)} %."), "",
              f"Its starting level: {f(scale * c['shap_bias'], 3, True)}.", "",
              "| group | attribution today |", "|---|---|"] + [f"| {g} | {f(scale * s, 3, True)} |" for g, s in zip(c["groups"], c["shap"])]
    L += ["", "## Track record on the test period (loss against the reference; negative = better than the reference)", "", *c["track"], "",
          "Write: a headline of one sentence; an explanation of 150 to 250 words saying what the forecast is, which groups move it and in which "
          "direction, what state of the factors lies behind the largest contributions, whether that agrees with the rationale, and whether the tree "
          "model leans on the same groups; and the limits in one to three sentences, with the track record."]
    return "\n".join(L)


def class_payload(c: Dict[str, Any]) -> str:
    """``c``: the prepared numbers of one asset class and target (see scripts/explain.py: ``class_case``)."""
    tname = c["target_name"]
    L = ["# One asset class and target over the whole test period", "",
         f"Asset class: {c['class_text']} ({c['n_series']} series: {', '.join(c['series'])}). Target: {TARGET_TEXT[tname].format(h='h periods')}. "
         f"Data are {c['frequency']}; test period {c['first']} to {c['last']}. The same formulas are used for every series of the class and every horizon.", "",
         "## The formulas", ""] + formula_lines(c["literals"], c["labels"], False)
    L += ["", "## What was assumed when the formulas were written (rationale per group)", ""] + [f"- Group {g}: {r}" for g, r in c["rationales"].items()]
    L += ["", "## How the groups behaved in the linear model (all series, horizons and forecast dates of the test period)", "",
          "Share of movement = the group's share of the absolute contributions to the forecast, averaged over forecasts. "
          "Positive coefficient = share of forecasts made with a positive fitted coefficient for the group.", "",
          "| group | average value of the formula | 10th to 90th percentile of the value | share of movement, linear model | positive coefficient | share of attribution, tree model |",
          "|---|---|---|---|---|---|"]
    for g in c["group_rows"]:
        L.append(f"| {g['group']} | {f(g['mean'])} | {f(g['p10'])} to {f(g['p90'])} | {f(g['share'], 1)} % | {f(g['positive'], 1)} % | {f(g['shap_share'], 1)} % |")
    L += ["", f"## Track record by horizon (relative difference in the loss against {REFERENCE_TEXT[tname]}; negative = better than the reference)", "",
          "| horizon | this asset class, fixed formulas | this asset class, averaged formulas | all series of the frequency, fixed formulas (95 % interval) | verdict for all series |", "|---|---|---|---|---|"]
    for r in c["skill_rows"]:
        L.append(f"| {r['horizon']} | {f(r['class_fixed'], 1, True)} % | {f(r['class_accuracy'], 1, True)} % | {f(r['all'], 1, True)} % ({f(r['lo'], 1, True)} % to {f(r['hi'], 1, True)} %) | {r['verdict']} |")
    L += ["", c.get("accuracy_text", "\"Averaged formulas\" is the same model averaged over the formula and nineteen close variants of it."), "",
          "Write: a headline of one sentence; an explanation of 200 to 300 words saying what states of the market the formulas describe for this asset "
          "class and target, which groups carry the forecast and which hardly matter, whether the fitted signs are stable and agree with the "
          "rationale, and whether the tree model leans on the same groups; and the limits in one to three sentences, with the track record by horizon."]
    return "\n".join(L)


def explain(client, payload: str, model: str = MODEL, retries: int = 2) -> Dict[str, Any]:
    """One explanation. The record that is stored: payload and its hash, model, attempts (response id,
    served model, usage, problems), the accepted answer or None."""
    record: Dict[str, Any] = {"model": model, "payload_sha256": hashlib.sha256((SYSTEM + "\n" + payload).encode()).hexdigest(), "payload": payload,
                              "attempts": [], "answer": None}
    note = ""
    for _ in range(retries + 1):
        with client.messages.stream(model=model, max_tokens=16000, system=SYSTEM, messages=[{"role": "user", "content": payload + note}],
                                    thinking={"type": "adaptive"}, output_config={"effort": "high", "format": {"type": "json_schema", "schema": SCHEMA}}) as stream:
            resp = stream.get_final_message()
        att = {"id": resp.id, "stop_reason": resp.stop_reason, "served_model": resp.model,
               "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}}
        if resp.stop_reason != "end_turn":
            att["problems"] = [f"stop_reason {resp.stop_reason}"]
            record["attempts"].append(att)
            continue
        answer = json.loads(next(b.text for b in resp.content if b.type == "text"))
        bad = check_numbers(answer, payload)
        att["problems"] = [f"numbers not in the material: {', '.join(bad)}"] if bad else []
        record["attempts"].append(att)
        if not bad:
            record["answer"] = answer
            return record
        att["rejected"] = answer
        note = ("\n\nNote: an earlier draft was rejected because it contained numbers that are not written in the material above: "
                + ", ".join(bad) + ". Quote only numbers that appear above, digit for digit, or describe the comparison in words.")
    return record
