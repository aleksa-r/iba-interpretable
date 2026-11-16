"""The study's deliverable: target type x asset class (stratum) x method.

For every (frequency, task, stratum): the pooled mean loss of every configuration, its skill
against the type's reference, the rank of each IBA configuration among the benchmarks, its
difference to the BEST benchmark with a date-block-bootstrap interval, Model Confidence Set
membership, the optimism gap (score at selection vs realised) and, for the searches, the
inner-minus-outer optimism and the acceptance rate. Written before any result existed
(SPEC-2026-11-13, section 8); it changes nothing about which configurations are headline.

Primary loss per type: squared error (return, log RV), Brier (tails). Secondary: sign error,
QLIKE, log score. Seeded configurations ("iba_a.s0|lin") are reported as their seed average
("iba_a|lin") with the spread across seeds."""
from __future__ import annotations

import re
from typing import Dict, List

import numpy as np
import pandas as pd

from ..models.estimators import pointwise_loss
from .bootstrap import default_block, paired_block_test

REFERENCE = {"return": "bench|mean", "logrv": "bench|har", "tail_loss": "bench|base", "tail_gain": "bench|base"}
BENCH_PREFIX = ("raw|", "pca|", "gpca|", "lasso|", "kpca|", "ae|", "bench|")
HEADLINE = ("iba_e1|lin", "iba_a|lin", "iba_b", "iba_c")
META_COLS = ("date", "y", "y_eval", "block", "threshold")


def base_name(config: str) -> str:
    return re.sub(r"\.s\d+", "", config)


def is_benchmark(config: str) -> bool:
    return config.startswith(BENCH_PREFIX)


def pointwise(pred: pd.DataFrame, kind: str, config: str, which: str = "primary") -> np.ndarray:
    f = pred[config].values.astype(float)
    if kind == "return":
        y = pred["y"].values
        return (f - y) ** 2 if which == "primary" else ((y > 0) != (f >= 0)).astype(float)
    if kind == "logrv":
        y = pred["y"].values
        if which == "primary":
            return (f - y) ** 2
        ratio = np.exp(y) / np.maximum(pred[config + "::var"].values.astype(float), 1e-300)
        return ratio - np.log(ratio) - 1.0
    e = pred["y_eval"].values
    return (np.clip(f, 0, 1) - e) ** 2 if which == "primary" else pointwise_loss("clf", e, f)


def configs_of(pred: pd.DataFrame) -> List[str]:
    return [c for c in pred.columns if c not in META_COLS and not c.endswith("::var") and np.isfinite(pred[c].values).all()]


def _cell_optimism(pred: pd.DataFrame, meta: dict, kind: str) -> Dict[str, List[float]]:
    """Realised block loss (in the tuning loss) minus the cross-validated loss at tuning."""
    out: Dict[str, List[float]] = {}
    task = "clf" if kind.startswith("tail") else "reg"
    target = pred["y_eval"].values
    for b in meta["blocks"]:
        m = (pred["block"] == b["block"]).values
        for cfg, t in b.get("tuning", {}).items():
            if cfg in pred:
                out.setdefault(base_name(cfg), []).append(float(np.mean(pointwise_loss(task, target[m], pred[cfg].values[m]))) - t["cv_loss"])
    return out


def build_map(cells: List[dict], reps: int = 2000, mcs: bool = True) -> pd.DataFrame:
    """``cells``: dicts with stratum, frequency, task (name), kind, h, target, pred (DataFrame), meta."""
    rows = []
    groups: Dict[tuple, List[dict]] = {}
    for c in cells:
        groups.setdefault((c["frequency"], c["task"], c["stratum"]), []).append(c)
    for (freq, task, stratum), cs in sorted(groups.items()):
        kind, h = cs[0]["kind"], cs[0]["h"]
        common = sorted(set.intersection(*[set(configs_of(c["pred"])) for c in cs]))
        bases = sorted({base_name(c) for c in common})
        dates = cs[0]["pred"]["date"].values
        if any(len(c["pred"]) != len(dates) or (c["pred"]["date"].values != dates).any() for c in cs):
            raise ValueError(f"{task} {stratum}: cells do not share their forecast dates")
        L = {w: {} for w in ("primary", "secondary")}
        seed_sd = {}
        for b in bases:
            members = [c for c in common if base_name(c) == b]
            for w in L:
                per_seed = [np.column_stack([pointwise(c["pred"], kind, m, w) for c in cs]) for m in members]
                L[w][b] = np.mean(per_seed, axis=0)                       # dates x targets, averaged over seeds
                if w == "primary":
                    seed_sd[b] = float(np.std([p.mean() for p in per_seed])) if len(per_seed) > 1 else 0.0
        mean = {b: float(L["primary"][b].mean()) for b in bases}
        sec = {b: float(L["secondary"][b].mean()) for b in bases}
        ref = REFERENCE[kind]
        bench = [b for b in bases if is_benchmark(b)]
        best = min(bench, key=lambda b: mean[b])
        in_mcs = {}
        if mcs and len(bases) > 2:
            try:
                from .mcs import model_confidence_set
                m = model_confidence_set(pd.DataFrame({b: L["primary"][b].mean(axis=1) for b in bases}), size=0.10,
                                         block=default_block(h, len(dates)), reps=min(reps, 1000))
                in_mcs = m["in_mcs"].to_dict()
            except Exception:
                in_mcs = {}
        opt: Dict[str, List[float]] = {}
        srch: Dict[str, List[dict]] = {}
        for c in cs:
            for k, v in _cell_optimism(c["pred"], c["meta"], kind).items():
                opt.setdefault(k, []).extend(v)
            for b in c["meta"]["blocks"]:
                for name, info in b.get("methods", {}).items():
                    if isinstance(info, dict) and "optimism" in info:
                        srch.setdefault(re.sub(r"\.s\d+", "", name), []).append(info)
        for b in bases:
            row = {"frequency": freq, "task": task, "kind": kind, "h": h, "stratum": stratum, "config": b, "cells": len(cs),
                   "benchmark": is_benchmark(b), "headline": b in HEADLINE, "mean_loss": mean[b], "secondary_loss": sec[b],
                   "skill_vs_reference": 1.0 - mean[b] / max(mean[ref], 1e-300), "seed_sd": seed_sd[b],
                   "in_mcs": in_mcs.get(b, np.nan), "best_benchmark": best,
                   "optimism_gap": float(np.mean(opt[b])) if b in opt else np.nan}
            if not is_benchmark(b):
                row["rank_among_benchmarks"] = 1 + sum(mean[x] < mean[b] for x in bench)
                row["n_benchmarks"] = len(bench)
                t = paired_block_test(L["primary"][b] - L["primary"][best], block=default_block(h, len(dates)), reps=reps, seed=h)
                row.update({"diff_to_best_benchmark": t.mean, "ci_low": t.ci_low, "ci_high": t.ci_high, "p_block_boot": t.p_value})
                s = srch.get(b.split("|")[0])
                if s:
                    row.update({"search_optimism": float(np.nanmean([x["optimism"] for x in s])),
                                "search_accept_rate": float(np.mean([bool(x["accepted"]) for x in s])),
                                "search_evals": float(np.mean([x["n_evals"] for x in s]))})
            rows.append(row)
    return pd.DataFrame(rows)


def headline_table(m: pd.DataFrame) -> pd.DataFrame:
    """One row per (task, stratum): for each headline method "rank/benchmarks  diff [ci]"."""
    out = []
    for (freq, task, stratum), g in m.groupby(["frequency", "task", "stratum"], sort=True):
        row = {"frequency": freq, "task": task, "stratum": stratum, "cells": int(g["cells"].iloc[0]),
               "best benchmark": g["best_benchmark"].iloc[0],
               "its skill": round(float(g.loc[g.config == g["best_benchmark"].iloc[0], "skill_vs_reference"].iloc[0]), 4)}
        for hname in HEADLINE:
            r = g[g.config == hname]
            if len(r):
                r = r.iloc[0]
                star = "*" if (r["ci_low"] > 0 or r["ci_high"] < 0) else ""
                row[hname] = f"{int(r['rank_among_benchmarks'])}/{int(r['n_benchmarks']) + 1}  {r['diff_to_best_benchmark']:+.3g} [{r['ci_low']:+.3g}, {r['ci_high']:+.3g}]{star}"
        out.append(row)
    return pd.DataFrame(out)
