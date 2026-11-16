"""The analysis of SPEC-2026-11-15-ablations, written BEFORE the run.

  .venv/bin/python scripts/make_ablation_report.py     # writes docs/results/SPEC-2026-11-15-ablations/
Each variant against the unchanged method, per (frequency, task), all development series pooled on the same
dates, with the paired date-block bootstrap of the other reports. Positive = the change makes the loss larger,
that is, the component that was removed or replaced was contributing."""
import importlib.util, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("wrapup_report", os.path.join(HERE, "make_wrapup_report.py"))
wr = importlib.util.module_from_spec(_s); _s.loader.exec_module(wr)
SPEC, BASE = "SPEC-2026-11-15-ablations", "abl_base|lin"
GROUPS = {"IR": "interest rates", "B": "credit", "V": "volatility", "AP": "equity factors", "TF": "trend-following", "ST": "styles", "FX": "currencies",
          "COM": "commodities", "MC": "macro-financial conditions", "ENDG": "own behaviour"}


def load():
    by = {}
    for t in wr.tasks():
        p = pd.read_csv(os.path.join(wr.REPO, "artifacts", SPEC, "stage12", t.frequency, t.name, t.target.replace("^", "_"), "predictions.csv"), parse_dates=["date"])
        by.setdefault((t.frequency, t.name, t.kind, t.h), []).append((t.target, p))
    # a series whose asset class has no formula in a group has no "without that group" variant: removing nothing
    # leaves the forecast unchanged, so the variant is the unchanged method's forecast (docs/DEVIATIONS.md, 2026-11-15)
    for cells in by.values():
        union = sorted({c for _, p in cells for c in p.columns if c.startswith("abl_wo_")})
        for i, (target, p) in enumerate(cells):
            add = {c: p[BASE].values for c in union if c not in p.columns}
            if add:
                cells[i] = (target, pd.concat([p, pd.DataFrame(add, index=p.index)], axis=1))
    return by


def main():
    out = os.path.join(wr.REPO, "docs", "results", SPEC); os.makedirs(out, exist_ok=True)
    by = load()
    names = sorted({c for cells in by.values() for _, p in cells for c in p.columns if c.startswith("abl_") and c != BASE})
    P, _ = wr.paired(by, [(c, BASE) for c in names] + [(BASE, "REF")], spread_table=False, skip_missing=True)
    P.to_csv(os.path.join(out, "paired_tests.csv"), index=False)
    table = wr.table_maker(P)
    label = lambda c: {"abl_one|lin": "one literal per group", "abl_ecdf|lin": "empirical-distribution scaling of predicates", "abl_nohar|lin": "no HAR first stage (volatility)"}.get(
        c, "without group: " + GROUPS.get(c[len("abl_wo_"):-len("|lin")], c))
    md = [f"# {SPEC}: component contribution analysis (development series)", "",
          "Each row changes one component of the interpretable reading (consensus formulas, linear model) and compares it with the unchanged method. "
          "Cell: mean relative difference in the primary loss, variant minus unchanged (positive = the change hurts, so the component contributes); "
          "tasks where the 95 % date-block-bootstrap interval excludes zero (b = variant better, w = variant worse).", ""]
    for freq in ("weekly", "monthly"):
        Pf = P[P.frequency == freq]
        t2 = wr.table_maker(Pf)
        groups = [c for c in names if c.startswith("abl_wo_") and len(Pf[Pf.a == c])]
        others = [c for c in names if not c.startswith("abl_wo_") and len(Pf[Pf.a == c])]
        md += t2(f"{freq}: removing one group's formula", [(label(c), c, BASE) for c in groups])
        md += t2(f"{freq}: formula order, predicate scaling, HAR stage", [(label(c), c, BASE) for c in others] + [("unchanged method against the reference", BASE, "REF")])
    open(os.path.join(out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
