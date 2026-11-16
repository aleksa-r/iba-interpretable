"""Financial and classification views of the forecasts (docs/protocol/EXTRA_METRICS.md), computed from
stored forecasts and labels only.

  value at risk / expected shortfall from a variance forecast, with their backtests and scores;
  risk measures of a return series (historical VaR, CVaR, maximum drawdown);
  the confusion matrix of a probability forecast at a threshold, and the decomposition of its Brier score."""
from __future__ import annotations

from typing import Dict

import numpy as np
from scipy.stats import chi2, norm


def var_es_normal(variance, alpha: float):
    """(q, e): the alpha-quantile of the return and its expected value below that quantile, for a
    zero-mean normal return with the forecast variance. Both are negative; VaR = -q, ES = -e."""
    s = np.sqrt(np.maximum(np.asarray(variance, float), 1e-300))
    z = norm.ppf(alpha)
    return z * s, -s * norm.pdf(z) / alpha


def tick_loss(r, q, alpha: float) -> np.ndarray:
    """Quantile (pinball) loss of the quantile forecast q for the realised return r: proper for the quantile."""
    r, q = np.asarray(r, float), np.asarray(q, float)
    return (alpha - (r < q)) * (r - q)


def fz0_loss(r, q, e, alpha: float) -> np.ndarray:
    """Fissler-Ziegel loss FZ0 (Patton, Ziegel and Chen 2019) for the pair (quantile q, expected
    shortfall e), both negative: a proper joint score of VaR and ES. Lower is better."""
    r, q, e = np.asarray(r, float), np.asarray(q, float), np.asarray(e, float)
    return -(r <= q).astype(float) * (q - r) / (alpha * e) + q / e + np.log(-e) - 1.0


def kupiec(viol, alpha: float) -> Dict[str, float]:
    """Unconditional coverage: is the share of violations alpha? Likelihood-ratio test, chi-square(1)."""
    v = np.asarray(viol, bool); n, x = len(v), int(v.sum())
    p = x / n
    ll0 = (n - x) * np.log(1 - alpha) + x * np.log(alpha)
    ll1 = (n - x) * np.log(1 - p) if x == 0 else x * np.log(p) if x == n else (n - x) * np.log(1 - p) + x * np.log(p)
    lr = max(0.0, -2 * (ll0 - ll1))
    return {"n": n, "violations": x, "rate": p, "lr": lr, "p": float(chi2.sf(lr, 1))}


def christoffersen(viol) -> Dict[str, float]:
    """Independence of violations (first-order Markov alternative). Likelihood-ratio test, chi-square(1).
    Only meaningful for non-overlapping returns."""
    v = np.asarray(viol, int)
    a, b = v[:-1], v[1:]
    n00, n01, n10, n11 = (int(((a == i) & (b == j)).sum()) for i, j in ((0, 0), (0, 1), (1, 0), (1, 1)))
    if n01 + n11 == 0 or n00 + n10 == 0:
        return {"lr": 0.0, "p": 1.0}
    p01, p11, p = n01 / max(n00 + n01, 1), n11 / max(n10 + n11, 1), (n01 + n11) / (n00 + n01 + n10 + n11)
    xl = lambda k, q: 0.0 if k == 0 else k * np.log(q)
    ll0 = xl(n00 + n10, 1 - p) + xl(n01 + n11, p)
    ll1 = xl(n00, 1 - p01) + xl(n01, p01) + xl(n10, 1 - p11) + xl(n11, p11)
    lr = max(0.0, -2 * (ll0 - ll1))
    return {"lr": lr, "p": float(chi2.sf(lr, 1))}


def max_drawdown(returns) -> float:
    """Largest peak-to-trough loss of the compounded path of simple returns (a positive number)."""
    w = np.cumprod(1.0 + np.asarray(returns, float))
    peak = np.maximum.accumulate(np.r_[1.0, w])[1:]
    return float(np.max(1.0 - w / peak)) if len(w) else 0.0


def hist_var_cvar(returns, alpha: float = 0.05) -> Dict[str, float]:
    """Historical VaR and CVaR of a return series, as positive losses."""
    r = np.asarray(returns, float)
    q = np.quantile(r, alpha)
    return {"var": float(-q), "cvar": float(-r[r <= q].mean())}


def mcc(tp, fp, fn, tn) -> float:
    """Matthews correlation from the four counts; 0 when a row or column of the table is empty (no signal, or no event)."""
    den = np.sqrt(float(tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return float((tp * tn - fp * fn) / den) if den > 0 else 0.0


def confusion(event, signal) -> Dict[str, float]:
    e, s = np.asarray(event, bool), np.asarray(signal, bool)
    tp, fp, fn, tn = int((e & s).sum()), int((~e & s).sum()), int((e & ~s).sum()), int((~e & ~s).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    spec = tn / (tn + fp) if tn + fp else float("nan")
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "signal_rate": (tp + fp) / len(e), "precision": prec, "recall": rec, "specificity": spec,
            "f1": 2 * prec * rec / (prec + rec) if tp else (0.0 if tp + fp + fn else float("nan")),
            "balanced_accuracy": (rec + spec) / 2, "mcc": mcc(tp, fp, fn, tn)}


def brier_decomposition(event, p, bins: int = 10) -> Dict[str, float]:
    """Murphy's decomposition on bins of the forecast with edges at its quantiles (equal forecasts stay
    in one bin): Brier = reliability - resolution + uncertainty (up to the within-bin variance of the
    forecasts). Lower reliability and higher resolution are better; sharpness is the standard
    deviation of the forecasts."""
    e, p = np.asarray(event, float), np.asarray(p, float)
    edges = np.unique(np.quantile(p, np.linspace(0, 1, bins + 1)[1:-1]))
    which = np.searchsorted(edges, p, side="right")
    base = e.mean(); rel = res = 0.0
    for k in np.unique(which):
        chunk = which == k
        w = chunk.mean()
        rel += w * (p[chunk].mean() - e[chunk].mean()) ** 2
        res += w * (e[chunk].mean() - base) ** 2
    return {"brier": float(np.mean((p - e) ** 2)), "reliability": float(rel), "resolution": float(res), "uncertainty": float(base * (1 - base)),
            "sharpness": float(p.std())}
