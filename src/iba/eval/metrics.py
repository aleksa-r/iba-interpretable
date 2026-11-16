"""Measures per target type, computed from forecasts and labels only."""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np


def return_metrics(y, f, f_mean, h: int, ppy: int) -> Dict[str, float]:
    y, f = np.asarray(y, float), np.asarray(f, float)
    up, long = y > 0, f >= 0
    out = {"n": int(len(y)), "sign_acc": float(np.mean(up == long)), "always_long_acc": float(np.mean(up)),
           "mse": float(np.mean((f - y) ** 2)),
           "r2_vs_mean": float(1 - np.sum((f - y) ** 2) / max(np.sum((np.asarray(f_mean, float) - y) ** 2), 1e-18))}
    # gate: long when the forecast is non-negative, held h periods; one decision every h periods.
    # Reported for every phase 0..h-1 (the published "realizable" figure was phase 0 only).
    g_ann, b_ann, g_sh, b_sh, wins = [], [], [], [], 0
    for o in range(h):
        yy, ll = y[o::h], long[o::h].astype(float)
        if len(yy) < 2:
            continue
        g, b = ll * yy, yy
        ga = np.prod(1 + g) ** (ppy / (h * len(g))) - 1; ba = np.prod(1 + b) ** (ppy / (h * len(b))) - 1
        g_ann.append(ga); b_ann.append(ba); wins += int(ga > ba + 1e-12)
        g_sh.append(g.mean() / g.std() * np.sqrt(ppy / h) if g.std() > 1e-12 else 0.0)
        b_sh.append(b.mean() / b.std() * np.sqrt(ppy / h) if b.std() > 1e-12 else 0.0)
    out.update({"gate_ann": float(np.mean(g_ann)), "bh_ann": float(np.mean(b_ann)), "gate_sharpe": float(np.mean(g_sh)),
                "bh_sharpe": float(np.mean(b_sh)), "gate_phases_won": int(wins), "phases": int(len(g_ann)),
                "gate_ann_phase0": float(g_ann[0]), "bh_ann_phase0": float(b_ann[0])})
    return out


def vol_metrics(y_log, f_log, f_var, f_har) -> Dict[str, float]:
    """y_log: realised log variance; f_log: forecast of it; f_var: forecast of the variance level."""
    y, f, v, hh = (np.asarray(a, float) for a in (y_log, f_log, f_var, f_har))
    rv = np.exp(y)
    ratio = rv / np.maximum(v, 1e-300)
    return {"n": int(len(y)), "mse_log": float(np.mean((f - y) ** 2)),
            "r2_vs_har": float(1 - np.sum((f - y) ** 2) / max(np.sum((hh - y) ** 2), 1e-18)),
            "qlike": float(np.mean(ratio - np.log(ratio) - 1.0)), "mse_var": float(np.mean((v - rv) ** 2))}


def tail_metrics(e, p, p_base, bins: int = 10) -> Dict[str, float]:
    e, p, pb = np.asarray(e, float), np.clip(np.asarray(p, float), 1e-3, 1 - 1e-3), np.clip(np.asarray(p_base, float), 1e-3, 1 - 1e-3)
    brier, brier_b = np.mean((p - e) ** 2), np.mean((pb - e) ** 2)
    ll, ll_b = -np.mean(e * np.log(p) + (1 - e) * np.log(1 - p)), -np.mean(e * np.log(pb) + (1 - e) * np.log(1 - pb))
    order = np.argsort(p, kind="stable"); ece = 0.0
    for chunk in np.array_split(order, bins):
        if len(chunk):
            ece += len(chunk) / len(p) * abs(p[chunk].mean() - e[chunk].mean())
    pos, neg = p[e == 1], p[e == 0]
    auc = float("nan")
    if len(pos) and len(neg):
        from scipy.stats import rankdata
        rk = rankdata(np.r_[pos, neg])
        auc = float((rk[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))
    return {"n": int(len(e)), "event_rate": float(e.mean()), "brier": float(brier), "logloss": float(ll),
            "bss": float(1 - brier / max(brier_b, 1e-18)), "log_skill": float(1 - ll / max(ll_b, 1e-18)),
            "ece": float(ece), "auc": auc}
