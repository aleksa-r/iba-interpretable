"""From traces and stored forecasts to the prepared numbers of an explanation (no file access, no API).

``cell_numbers``  one cell: what the explanation step keeps of a trace, the stored losses, and the
                  check that the trace reproduces the stored forecasts.
``forecast_case`` the numbers of one forecast (the last forecast origin of a cell).
``class_case``    the numbers of one asset class and target over the test period."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from ..eval.map import REFERENCE, pointwise
from .narrate import TARGET_OF, horizon_text
from .trace import check_against, literals_at

VERDICT = {"better": "significantly better than the reference", "worse": "significantly worse than the reference",
           "n.s.": "not significantly different from the reference"}


def cell_numbers(trace: Dict[str, Any], pred: pd.DataFrame, accuracy_cols: Sequence[str], lin: str = "iba_e1|lin", xgb: str = "iba_e1|xgb") -> Dict[str, Any]:
    t, kind = trace["task"], trace["task"].kind
    last = len(trace["dates"]) - 1
    ref = REFERENCE[kind]
    return {"target": t.target, "task": t.name, "kind": kind, "h": t.h, "frequency": t.frequency,
            "first": str(pd.Timestamp(trace["dates"][0]).date()), "last": str(pd.Timestamp(trace["dates"][last]).date()),
            "groups": list(trace["groups"]), "value": trace["value"], "coef": trace["coef"], "contrib": trace["contrib"], "shap": trace["shap"],
            "train_mean_last": trace["train_mean"][last], "intercept_last": float(trace["intercept"][last]), "raw_last": float(trace["raw"][last]),
            "forecast_last": float(trace["forecast"][last]), "forecast_xgb_last": float(trace["forecast_xgb"][last]), "shap_bias_last": float(trace["shap_bias"][last]),
            "reference_last": float(pred[ref].values[last]), "literals_last": literals_at(trace, last),
            "diffs": check_against(trace, pred, lin, xgb),
            "loss": {"fixed": float(pointwise(pred, kind, lin).mean()), "reference": float(pointwise(pred, kind, ref).mean()),
                     "accuracy": float(np.mean([pointwise(pred, kind, c).mean() for c in accuracy_cols])) if accuracy_cols else float("nan")}}


def rationales(literals: Sequence[Dict[str, Any]], draws: Dict[int, Dict[str, Any]], target_name: str) -> Dict[str, str]:
    """Per group the rationale given at elicitation: of the lowest-numbered draw whose literals for the
    group are exactly the formula's; failing that, of the draw sharing most literals (said so)."""
    want: Dict[str, set] = {}
    for r in literals:
        want.setdefault(r["group"], set()).add((r["factor"], r["state"]))
    out = {}
    for g, lits in want.items():
        best, exact = None, False
        for k in sorted(draws):
            sec = draws[k].get(target_name, {}).get(g)
            if not sec:
                continue
            have = {(x["factor"], x["state"]) for x in sec["literals"]}
            score = len(have & lits)
            if have == lits:
                best, exact = (k, sec["rationale"]), True
                break
            if score and (best is None or score > best[2]):
                best = (k, sec["rationale"], score)
        if best is None:
            out[g] = "(no rationale on record for this formula)"
        else:
            out[g] = (f"(draw {best[0]}) " if exact else f"(draw {best[0]}, whose formula for the group differed in part) ") + best[1].strip()
    return out


def _test_row(tests: Optional[pd.DataFrame], config: str, frequency: str, task: str):
    if tests is None:
        return None
    g = tests[(tests.a == config) & (tests.b == "REF") & (tests.frequency == frequency) & (tests.task == task)]
    return None if g.empty else g.iloc[0]


def forecast_case(cell: Dict[str, Any], class_text: str, labels: Dict[str, str], draws: Dict[int, Dict[str, Any]],
                  tests: Optional[pd.DataFrame] = None, config: str = "") -> Dict[str, Any]:
    from .narrate import f
    tname = TARGET_OF[cell["kind"]]
    last = cell["value"].shape[0] - 1
    lo = cell["loss"]
    track = [f"- This series, this target and horizon: fixed formulas {f(100 * (lo['fixed'] / lo['reference'] - 1), 1, True)} %"
             + (f", averaged formulas {f(100 * (lo['accuracy'] / lo['reference'] - 1), 1, True)} %." if np.isfinite(lo["accuracy"]) else ".")]
    row = _test_row(tests, config, cell["frequency"], cell["task"])
    if row is not None:
        track.append(f"- All {int(row.series)} series of the frequency, fixed formulas: {f(100 * row.rel_diff, 1, True)} % "
                     f"(95 % interval {f(100 * row.ci_low, 1, True)} % to {f(100 * row.ci_high, 1, True)} %): {VERDICT[row.verdict]}.")
    return {"series": cell["target"], "class_text": class_text, "target_name": tname, "h": cell["h"], "frequency": cell["frequency"], "date": cell["last"],
            "forecast": cell["forecast_last"], "reference": cell["reference_last"], "raw": cell["raw_last"], "literals": cell["literals_last"],
            "labels": labels, "rationales": rationales(cell["literals_last"], draws, tname), "groups": cell["groups"],
            "value": cell["value"][last], "train_mean": cell["train_mean_last"], "coef": cell["coef"][last], "contrib": cell["contrib"][last],
            "intercept": cell["intercept_last"], "shap": cell["shap"][last] if np.isfinite(cell["shap"][last]).all() else None,
            "forecast_xgb": cell["forecast_xgb_last"], "shap_bias": cell["shap_bias_last"], "track": track}


def class_case(cells: Sequence[Dict[str, Any]], class_text: str, labels: Dict[str, str], draws: Dict[int, Dict[str, Any]],
               tests: Optional[pd.DataFrame] = None, config: str = "") -> Dict[str, Any]:
    """``cells``: every cell of one asset class and one target type (all its series and horizons)."""
    kind, freq = cells[0]["kind"], cells[0]["frequency"]
    tname = TARGET_OF[kind]
    groups: List[str] = []
    for c in cells:
        groups += [g for g in c["groups"] if g not in groups]
    acc: Dict[str, Dict[str, list]] = {g: {"value": [], "share": [], "positive": [], "shap": []} for g in groups}
    for c in cells:
        tot, stot = np.abs(c["contrib"]).sum(axis=1), np.abs(c["shap"]).sum(axis=1)
        for j, g in enumerate(c["groups"]):
            acc[g]["value"].append(c["value"][:, j])
            acc[g]["positive"].append((c["coef"][:, j] > 0).astype(float))
            acc[g]["share"].append(np.abs(c["contrib"][:, j])[tot > 0] / tot[tot > 0])
            ok = np.isfinite(stot) & (stot > 0)
            acc[g]["shap"].append(np.abs(c["shap"][:, j])[ok] / stot[ok])
    rows = []
    for g in groups:
        v = np.concatenate(acc[g]["value"]); cat = lambda k: np.concatenate(acc[g][k]) if acc[g][k] else np.array([np.nan])
        sh, shp = cat("share"), cat("shap")
        rows.append({"group": g, "mean": float(v.mean()), "p10": float(np.percentile(v, 10)), "p90": float(np.percentile(v, 90)),
                     "share": 100 * float(sh.mean()) if len(sh) else float("nan"), "positive": 100 * float(cat("positive").mean()),
                     "shap_share": 100 * float(shp.mean()) if len(shp) else float("nan")})
    skill = []
    for h in sorted({c["h"] for c in cells}):
        cs = [c for c in cells if c["h"] == h]
        ref = sum(c["loss"]["reference"] for c in cs)
        row = _test_row(tests, config, freq, cs[0]["task"])
        skill.append({"horizon": horizon_text(h, freq), "class_fixed": 100 * (sum(c["loss"]["fixed"] for c in cs) / ref - 1),
                      "class_accuracy": 100 * (sum(c["loss"]["accuracy"] for c in cs) / ref - 1),
                      "all": 100 * row.rel_diff if row is not None else float("nan"), "lo": 100 * row.ci_low if row is not None else float("nan"),
                      "hi": 100 * row.ci_high if row is not None else float("nan"), "verdict": VERDICT[row.verdict] if row is not None else "n/a"})
    full = max(cells, key=lambda c: (len(c["literals_last"]), -sorted(x["target"] for x in cells).index(c["target"])))
    series = sorted({c["target"] for c in cells})
    return {"class_text": class_text, "n_series": len(series), "series": series, "target_name": tname, "frequency": freq,
            "first": min(c["first"] for c in cells), "last": max(c["last"] for c in cells), "literals": full["literals_last"], "labels": labels,
            "rationales": rationales(full["literals_last"], draws, tname), "group_rows": rows, "skill_rows": skill}
