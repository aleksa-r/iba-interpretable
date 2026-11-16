"""Schematic figures of the paper (no data): Figure 1, the system; Figure 2, the walk-forward backtest.

  .venv/bin/python scripts/make_paper_figures.py     # writes paper/figures/fig1_system.{pdf,png}, fig2_backtest.{pdf,png}"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper", "figures")
INK, MUTED, LINE = "#1f2933", "#52606d", "#9aa5b1"
FILL, ACCENT, ACCENT_FILL, SOFT = "#f5f7fa", "#1f5fa8", "#e3edf8", "#fdf3e1"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "pdf.fonttype": 42})


def box(ax, x, y, w, h, title, lines=(), fill=FILL, edge=LINE, tc=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge, lw=1.1))
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", weight="bold", color=tc, fontsize=9)
    for i, s in enumerate(lines):
        ax.text(x + w / 2, y + h - 0.68 - 0.34 * i, s, ha="center", va="top", color=MUTED, fontsize=7.4)


def arrow(ax, a, b, color=LINE, style="-|>", ls="-"):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle=style, color=color, lw=1.3, ls=ls, shrinkA=2, shrinkB=2))


def fig1(plain=False):
    """The overview flowchart, in the plain black-and-white style of a draw.io diagram: a data store and four framed
    stages, nine boxes in all. Left column: how the features are built; right column: what is done with them."""
    from matplotlib.patches import Ellipse
    K = "#111111"
    W, H = 7.3, 6.1
    fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    font = {"family": ["Arial", "Helvetica", "DejaVu Sans"]}
    import re
    sec = (lambda s: re.sub(r"\s*\(§[^)]*\)", "", s)) if plain else (lambda s: s)      # the plain variant carries no section numbers

    def rect(x0, y0, x1, y1, title, body=(), fs=7.6):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="white", ec=K, lw=0.9, zorder=2))
        n = len(body)
        block = 0.15 + (0.06 + 0.14 * n if n else 0.0)                 # title line, a gap, the body lines
        ty = (y0 + y1) / 2 + block / 2 - 0.075
        ax.text((x0 + x1) / 2, ty, title, ha="center", va="center", fontsize=fs, color=K, zorder=3, **font)
        for i, line in enumerate(body):
            ax.text((x0 + x1) / 2, ty - 0.21 - 0.14 * i, line, ha="center", va="center", fontsize=fs - 1.3, color="#333333", zorder=3, **font)

    def frame(x0, y0, x1, y1, title):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec=K, lw=1.1, zorder=1))
        ax.text(x0 + 0.09, y1 - 0.08, sec(title), ha="left", va="top", fontsize=8.2, weight="bold", color=K, zorder=3, **font)

    def arr(pts, label=None, at=None, ha="left", rot=0, fs=6.4, head=True):
        segs = list(zip(pts[:-1], pts[1:]))
        for (xa, ya), (xb, yb) in (segs[:-1] if head else segs):
            ax.plot([xa, xb], [ya, yb], color=K, lw=0.9, zorder=4, solid_capstyle="butt")
        if head:
            ax.annotate("", xy=pts[-1], xytext=pts[-2], zorder=4, arrowprops=dict(arrowstyle="-|>", color=K, lw=0.9, shrinkA=0, shrinkB=0, mutation_scale=9))
        if label:
            ax.text(at[0], at[1], label, ha=ha, va="center", fontsize=fs, color=K, rotation=rot, zorder=5, linespacing=1.15,
                    bbox=dict(fc="white", ec="none", pad=0.8), **font)

    L0, L1, R0, R1 = 0.30, 3.50, 3.92, 7.12                             # the two columns
    T0, T1, B0, B1 = 2.78, 5.30, 0.62, 2.46                             # the two rows of frames
    mid = (L1 + R0) / 2                                                 # the channel between the columns

    # ---- data store
    cx, cy, cw, ch = (L0 + L1) / 2, 5.74, 2.3, 0.30
    ax.plot([cx - cw / 2] * 2, [cy - ch / 2, cy + ch / 2], color=K, lw=0.9, zorder=3); ax.plot([cx + cw / 2] * 2, [cy - ch / 2, cy + ch / 2], color=K, lw=0.9, zorder=3)
    ax.add_patch(Ellipse((cx, cy + ch / 2), cw, 0.16, fc="white", ec=K, lw=0.9, zorder=3))
    ax.add_patch(Ellipse((cx, cy - ch / 2), cw, 0.16, fc="white", ec=K, lw=0.9, zorder=2))
    ax.add_patch(Rectangle((cx - cw / 2 + 0.01, cy - ch / 2), cw - 0.02, ch / 2, fc="white", ec="none", zorder=2.5))
    ax.text(cx, cy - 0.06, "Data:  factors by group  ·  index series", ha="center", va="center", fontsize=7.0, color=K, zorder=4, **font)
    arr([(cx, cy - ch / 2 - 0.08), (cx, T1)])

    # ---- 1: the logical layer
    frame(L0, T0, L1, T1, "1  Logical layer  (§4.1–4.3)")
    rect(0.44, 4.08, 1.82, 4.78, "Elicited formulas", ["language model as expert,", "knowledge cut-off"])
    rect(1.98, 4.08, 3.36, 4.78, "Graded predicates", ["\"factor F is high\"", "as a value in [0, 1]"])
    rect(0.80, 2.94, 3.00, 3.60, "Group formulas (IBA)", ["one readable feature per factor group:", "the product of its literal values"])
    arr([(1.13, 4.08), (1.55, 3.60)]); arr([(2.67, 4.08), (2.25, 3.60)])

    # ---- 2: structure refinement
    frame(L0, B0, L1, B1, "2  Structure refinement  (§3.2, §4.5)")
    rect(0.44, 0.84, 1.84, 1.74, "ABC search", ["around the elicited formulas;", "fitness pooled over", "the asset class"])
    rect(2.04, 0.84, 3.36, 1.74, "Acceptance test", ["a new formula is kept", "only if better on rows", "the search never used"])
    arr([(1.84, 1.29), (2.04, 1.29)])
    arr([(2.70, 2.94), (2.70, B1)], "formulas, group values", (2.63, 2.62), ha="right")

    # ---- 3: forecasting and evaluation
    frame(R0, T0, R1, T1, "3  Forecasting and evaluation  (§4.4, §5)")
    rect(4.30, 4.36, 6.74, 4.92, "Linear forecast model", ["on the group values; HAR first for volatility"])
    rect(4.30, 3.64, 6.74, 4.20, "Walk-forward forecasts", ["return, volatility, large loss, large gain"])
    rect(4.30, 2.92, 6.74, 3.48, "Evaluation", ["references and benchmarks; held-out series"])
    arr([(5.52, 4.36), (5.52, 4.20)]); arr([(5.52, 3.64), (5.52, 3.48)])
    arr([(3.00, 3.27), (mid, 3.27), (mid, 4.64), (4.30, 4.64)], "elicited formulas", (mid, 3.96), ha="center", rot=90)
    arr([(3.36, 1.29), (mid, 1.29), (mid, 3.27)], "refined formulas  ·  colony average", (mid, 2.12), ha="center", rot=90, head=False)

    # ---- 4: explanation
    frame(R0, B0, R1, B1, "4  Explanation  (§4.6)")
    rect(4.30, 1.46, 6.74, 2.02, "Fitted model", ["formulas, group values, coefficients"])
    rect(4.30, 0.76, 6.74, 1.32, "Verified narrative", ["written by a language model; every number checked"])
    arr([(5.52, 1.46), (5.52, 1.32)])
    arr([(6.30, T0), (6.30, B1)], "fitted model, forecasts", (6.23, 2.62), ha="right")

    # ---- the rule that holds everywhere
    ax.add_patch(Rectangle((L0, 0.10), R1 - L0, 0.36, fc="white", ec=K, lw=0.9, ls=(0, (4, 3)), zorder=1))
    ax.text((L0 + R1) / 2, 0.28, sec("Every stage uses only rows whose label is already known at the forecast date t:  j + h ≤ t   (§5.3)"),
            ha="center", va="center", fontsize=6.8, color=K, **font)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig1_system{'_plain' if plain else ''}.{ext}"), dpi=220)
    plt.close(fig)


def fig2():
    fig, ax = plt.subplots(figsize=(13.6, 5.0))
    T, test0, blk = 956, 540, 104
    ax.set_xlim(-10, T + 10); ax.set_ylim(-0.4, 6.9); ax.axis("off")
    # (a) the whole sample
    ya = 5.6
    ax.add_patch(Rectangle((0, ya), test0, 0.55, fc=FILL, ec=LINE))
    for b in range(4):
        ax.add_patch(Rectangle((test0 + b * blk, ya), blk, 0.55, fc=ACCENT_FILL, ec=ACCENT))
        ax.text(test0 + b * blk + blk / 2, ya + 0.275, f"block {b + 1}", ha="center", va="center", color=ACCENT, fontsize=7.6)
    ax.text(test0 / 2, ya + 0.275, "initial training sample", ha="center", va="center", color=MUTED, fontsize=7.6)
    ax.text(0, ya + 0.78, "(a) Walk-forward backtest: 956 weeks, test period = last 416 weeks in four blocks of 104", color=INK, fontsize=8.6, weight="bold")
    # (b) one block
    yb, t0 = 3.2, test0 + blk
    ax.text(0, yb + 1.5, "(b) At the start of block 2 (date t): formulas, scalers and penalties are set on admissible rows only", color=INK, fontsize=8.6, weight="bold")
    ax.add_patch(Rectangle((0, yb + 0.55), t0 - 13, 0.5, fc=FILL, ec=LINE))
    ax.text((t0 - 13) / 2, yb + 0.8, "admissible rows: label realised by t  (j + h ≤ t)", ha="center", va="center", color=MUTED, fontsize=7.6)
    ax.add_patch(Rectangle((t0 - 13, yb + 0.55), 13, 0.5, fc="white", ec=LINE, hatch="////", lw=0.6))
    ax.add_patch(Rectangle((t0, yb + 0.55), blk, 0.5, fc=ACCENT_FILL, ec=ACCENT))
    ax.text(t0 + blk / 2, yb + 0.8, "block 2 forecasts", ha="center", va="center", color=ACCENT, fontsize=7.4)
    ax.plot([t0, t0], [yb + 0.35, yb + 1.25], color=INK, lw=1.2); ax.text(t0, yb + 1.3, "t", ha="center", color=INK, fontsize=8.6)
    ax.text(t0 - 20, yb + 0.36, "last h rows: label not yet known", ha="right", va="top", color=MUTED, fontsize=7)
    ax.plot([t0 - 18, t0 - 6.5], [yb + 0.24, yb + 0.5], color=LINE, lw=0.7)
    for k in range(0, blk, 8):
        ax.plot([t0 + k, t0 + k], [yb + 0.42, yb + 0.55], color=ACCENT, lw=0.8)
    ax.text(t0 + blk + 8, yb + 0.8, "model refitted every 4 weeks\non the rows admissible then", ha="left", va="center", color=ACCENT, fontsize=7)
    # (c) folds
    yc, n, val, step = 0.0, t0 - 13, 78, 43
    ax.text(0, yc + 2.05, "(c) Five validation folds inside the admissible rows (78 weeks each, purged by the horizon h)", color=INK, fontsize=8.6, weight="bold")
    starts = [n - val - step * (4 - k) for k in range(5)]
    for k, v0 in enumerate(starts):
        y = yc + 1.5 - 0.36 * k
        ax.add_patch(Rectangle((0, y), v0 - 13, 0.24, fc=FILL, ec=LINE, lw=0.7))
        ax.add_patch(Rectangle((v0 - 13, y), 13, 0.24, fc="white", ec=LINE, hatch="////", lw=0.5))
        last = k == 4
        ax.add_patch(Rectangle((v0, y), val, 0.24, fc=SOFT if last else ACCENT_FILL, ec="#c98a1b" if last else ACCENT, lw=0.9))
        ax.text(v0 + val + 8, y + 0.12, "outer fold: acceptance test of a searched formula" if last else ("fitness folds: tuning, and the fitness of the search" if k == 1 else ""),
                va="center", color="#8a5d0c" if last else ACCENT, fontsize=7)
    ax.text(starts[0] / 2 - 6, yc + 1.62, "training rows of the fold", ha="center", va="center", color=MUTED, fontsize=6.8)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig2_backtest.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------- result figures (stored forecasts and tests)
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SURF, MUT, GRD, BLUE, ORANGE, REAL = "#fcfcfb", "#52514e", "#e6e5e1", "#2a78d6", "#eb6834", "#8a8983"


def _axes(ax, ygrid=True):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(GRD)
    ax.grid(axis="y" if ygrid else "x", color=GRD, lw=0.7); ax.set_axisbelow(True)
    ax.tick_params(length=0, colors=MUT, labelsize=8)


def fig3():
    """Out-of-sample volatility forecasts on confirmation series (the alphabetically first of four asset classes)."""
    import numpy as np, pandas as pd
    import matplotlib.dates as mdates
    base = os.path.join(REPO, "artifacts", "SPEC-2026-11-14-confirmation", "stage11")
    names = {"MDY": "US equity, broad (MDY)", "EWA": "Developed markets ex-US (EWA)", "LQD": "Investment-grade bonds (LQD)", "DBP": "Commodities (DBP)"}
    fig, axes = plt.subplots(2, 2, figsize=(7.3, 4.6), sharex=True, facecolor="white")
    vol = lambda v: 100 * np.sqrt(v * 52 / 4)
    for ax, (tk, title) in zip(axes.ravel(), names.items()):
        k = pd.read_csv(os.path.join(base, "prior_Kc", "weekly", "logrv_h4", tk, "predictions.csv"), parse_dates=["date"])
        g = pd.read_csv(os.path.join(base, "prior_G", "weekly", "logrv_h4", tk, "predictions.csv"))
        real, iba, har = vol(np.exp(k["y"])), vol(k["iba_e1|lin::var"]), vol(g["bench|har::var"])
        ax.plot(k["date"], real, color=REAL, lw=0.8, label="Realised")
        ax.plot(k["date"], har, color=ORANGE, lw=1.1, label="HAR")
        ax.plot(k["date"], iba, color=BLUE, lw=1.4, label="IBA (interpretable reading)")
        mse = lambda f: np.mean((np.log(f) - np.log(real)) ** 2)
        ax.set_title(f"{title}: {100 * (mse(iba) / mse(har) - 1):+.0f} % vs HAR", loc="left", fontsize=8.2, color="#111111", pad=4)
        _axes(ax); ax.set_ylim(0, None)
        ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for ax in axes[:, 0]:
        ax.set_ylabel("annualised volatility, %", fontsize=8, color=MUT)
    axes[0, 0].legend(frameon=False, fontsize=7.5, loc="upper right", labelcolor=MUT)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig4_forecasts.{ext}"), dpi=220)
    plt.close(fig)


def fig4():
    """Relative loss of the interpretable reading against the reference and against group PCA, per task, with 95 % intervals."""
    import pandas as pd
    c = pd.read_csv(os.path.join(REPO, "docs", "results", "SPEC-2026-11-14-confirmation", "paired_tests.csv"))
    d = pd.read_csv(os.path.join(REPO, "docs", "results", "SPEC-2026-11-14-wrapup", "paired_tests_priors.csv"))
    d = d[d.frequency == "weekly"]
    order = [("logrv_h1", "Volatility, 1 w"), ("logrv_h4", "Volatility, 4 w"), ("logrv_h13", "Volatility, 13 w"), ("return_h1", "Return, 1 w"), ("return_h4", "Return, 4 w"),
             ("return_h13", "Return, 13 w"), ("tail_loss_q10_h4", "Large loss, 4 w"), ("tail_loss_q10_h13", "Large loss, 13 w"), ("tail_gain_q10_h4", "Large gain, 4 w"), ("tail_gain_q10_h13", "Large gain, 13 w")]
    fig, axes = plt.subplots(1, 2, figsize=(7.3, 3.6), sharey=True, facecolor="white")
    for ax, (b, title) in zip(axes, (("REF", "against the reference (mean / HAR / base rate)"), ("gpca|lin", "against group PCA"))):
        for i, (task, _) in enumerate(order):
            y = len(order) - 1 - i
            for P, col, dy, lab in ((d, REAL, 0.16, "Development (37 series)"), (c, BLUE, -0.16, "Confirmation (21 series)")):
                r = P[(P.a == "Kc|lin") & (P.b == b) & (P.task == task)].iloc[0]
                ax.plot([100 * r.ci_low, 100 * r.ci_high], [y + dy, y + dy], color=col, lw=1.6, solid_capstyle="round")
                ax.plot(100 * r.rel_diff, y + dy, "o", color=col, ms=4.5, mec="white", mew=0.6, label=lab if i == 0 else None)
        ax.axvline(0, color="#111111", lw=0.8)
        if b == "gpca|lin":
            ax.axvline(3, color=ORANGE, lw=0.9, ls=(0, (4, 3))); ax.text(3.1, len(order) - 0.55, "parity margin", fontsize=7, color=MUT, va="center")
        ax.set_title(title, loc="left", fontsize=8.2, color="#111111", pad=4)
        ax.set_xlabel("relative difference in loss, %", fontsize=8, color=MUT)
        _axes(ax, ygrid=False)
    axes[0].set_yticks(range(len(order))); axes[0].set_yticklabels([n for _, n in order][::-1], fontsize=8, color="#111111")
    axes[0].legend(frameon=False, fontsize=7.5, loc="lower left", labelcolor=MUT)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig3_intervals.{ext}"), dpi=220)
    plt.close(fig)


def fig5():
    """Search algorithms: gain of the winner on the selection folds against its gain on unused rows."""
    import pandas as pd
    u = pd.read_csv(os.path.join(REPO, "docs", "results", "SPEC-2026-11-14-wrapup", "search_units.csv"))
    g = u.groupby("algorithm")[["inner_gain", "clean_gain"]].mean().mul(100).reindex(["ABC", "GA", "PSO", "SA", "DE"])
    fig, ax = plt.subplots(figsize=(4.6, 2.6), facecolor="white")
    y = range(len(g))[::-1]
    for yi, (a, r) in zip(y, g.iterrows()):
        ax.plot([r.clean_gain, r.inner_gain], [yi, yi], color=GRD, lw=2.2, zorder=1)
        ax.plot(r.inner_gain, yi, "o", color=ORANGE, ms=6.5, mec="white", mew=0.8, zorder=2, label="on the selection folds" if a == "ABC" else None)
        ax.plot(r.clean_gain, yi, "o", color=BLUE, ms=6.5, mec="white", mew=0.8, zorder=2, label="on unused rows" if a == "ABC" else None)
    ax.axvline(0, color="#111111", lw=0.8)
    ax.set_yticks(list(y)); ax.set_yticklabels(["ABC", "GA", "PSO", "Simulated annealing", "DE"], fontsize=8, color="#111111")
    ax.set_xlabel("gain of the searched formula set over the prior, %", fontsize=8, color=MUT)
    _axes(ax, ygrid=False); ax.set_ylim(-0.6, len(g) - 0.4)
    ax.legend(frameon=False, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, labelcolor=MUT)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig5_search.{ext}"), dpi=220)
    plt.close(fig)


def fig_crisis():
    """One development series (SPY), one-week volatility, in two stress episodes: realised value, HAR and the
    interpretable reading. Forecasts are plotted at the week they refer to."""
    import numpy as np, pandas as pd
    import matplotlib.dates as mdates
    p = pd.read_csv(os.path.join(REPO, "artifacts", "SPEC-2026-11-14-wrapup", "stage7", "prior_Kc", "weekly", "logrv_h1", "SPY", "predictions.csv"), parse_dates=["date"])
    vol = lambda x: 100 * np.sqrt(52 * np.exp(x))
    week = p["date"] + pd.Timedelta(days=7)                       # the week the forecast is for
    fig, axes = plt.subplots(1, 2, figsize=(7.3, 2.9), facecolor="white")
    for ax, (title, a, b) in zip(axes, (("(a) COVID-19 crash, 2020", "2020-02-01", "2020-05-08"), ("(b) Sell-off of late 2018", "2018-10-26", "2019-02-01"))):
        m = (week >= a) & (week <= b)
        ax.plot(week[m], vol(p["y"][m]), color=REAL, lw=1.0, marker="o", ms=2.6, label="Realised")
        ax.plot(week[m], vol(p["bench|har"][m]), color=ORANGE, lw=1.2, marker="o", ms=2.6, label="HAR")
        ax.plot(week[m], vol(p["iba_e1|lin"][m]), color=BLUE, lw=1.5, marker="o", ms=2.6, label="IBA (interpretable reading)")
        ax.set_title(title, loc="left", fontsize=8.4, color="#111111", pad=4)
        _axes(ax); ax.set_ylim(0, None)
        ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    axes[0].set_ylabel("annualised volatility, %", fontsize=8, color=MUT)
    axes[0].legend(frameon=False, fontsize=7.5, loc="upper left", labelcolor=MUT)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_crisis.{ext}"), dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1(); fig1(plain=True); fig2()
    for f in (fig3, fig4, fig5, fig_crisis):
        try:
            f()
        except FileNotFoundError as exc:                       # the result figures need the finished runs
            print("skipped", f.__name__, exc)
    print("written:", sorted(os.listdir(OUT)))
