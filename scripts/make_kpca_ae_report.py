"""The analysis of SPEC-2026-11-14-benchmarks-kpca-ae (section 5), written BEFORE the run.

  .venv/bin/python scripts/make_kpca_ae_report.py     # needs the finished wrap-up run; writes docs/results/<spec>/report.md

Kernel PCA (`kpca`) and an autoencoder (`ae`) as two more benchmark reducers on the 458 cells of
the wrap-up spec, each with the linear model, LightGBM and XGBoost. Paired date-block-bootstrap
differences per (frequency, task), all development series of the frequency pooled on the same
dates: the two benchmarks against the reference and the other benchmarks; the IBA readings of
the wrap-up's final method against them. No decision depends on this report."""
import importlib.util, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.protocol.study import BENCH2 as SPEC

_spec = importlib.util.spec_from_file_location("wrapup_report", os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_wrapup_report.py"))
wr = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(wr)
NEW = {"kpca": "kernel PCA", "ae": "autoencoder"}


def load(chosen):
    by = wr.load(chosen)
    index = {(t.frequency, t.name, t.target): t for t in wr.tasks()}
    for (freq, name, kind, h), cells in by.items():
        for i, (target, pred) in enumerate(cells):
            t = index[(freq, name, target)]
            p = pd.read_csv(os.path.join(wr.REPO, "artifacts", SPEC, "stage10", t.frequency, t.name, t.target.replace("^", "_"), "predictions.csv"), parse_dates=["date"])
            if len(p) != len(pred) or (p["date"].values != pred["date"].values).any() or not np.allclose(p["y_eval"].values, pred["y_eval"].values, equal_nan=True):
                raise ValueError(f"{name} {target}: stage 10 does not share dates and labels with the wrap-up run")
            cells[i] = (target, pd.concat([pred, p[[c for c in p.columns if c.startswith(("kpca|", "ae|"))]]], axis=1))
    return by


def main():
    out = os.path.join(wr.REPO, "docs", "results", SPEC); os.makedirs(out, exist_ok=True)
    final = json.load(open(os.path.join(wr.REPO, "docs", "results", wr.SPEC, "final_method.json")))
    chosen, interp, accur = final["formula_set"], final["interpretable"], final["accuracy"]
    by = load(chosen)
    pairs = []
    for b in NEW:
        pairs += [(f"{b}|lin", x) for x in ("REF", "pca|lin", "gpca|lin", "raw|lin", "lasso|lin")]
        pairs += [(f"{b}|xgb", f"{b}|lin"), (f"{b}|gbt", f"{b}|lin"), (f"{b}|xgb", "raw|xgb"), (f"{b}|xgb", "pca|xgb"), (f"{b}|xgb", "REF")]
        pairs += [(interp, f"{b}|lin"), (accur, f"{b}|lin"), ("G|lin", f"{b}|lin"), (f"{chosen}|xgb", f"{b}|xgb"), (f"{chosen}|gbt", f"{b}|gbt")]
    pairs += [("ae|lin", "kpca|lin")]
    P, _ = wr.paired(by, list(dict.fromkeys(pairs)))
    P.to_csv(os.path.join(out, "paired_tests.csv"), index=False)
    table = wr.table_maker(P)
    md = [f"# {SPEC}: kernel PCA and an autoencoder as benchmarks (development series)", "",
          "`kpca` = RBF kernel PCA, 6 components; `ae` = autoencoder with a 6-unit bottleneck; both fitted on admissible rows only, as every reducer. "
          f"IBA readings are those of the wrap-up's final method: interpretable `{interp}`, accuracy `{accur}` (formula set {chosen}); G = generic formulas.", "",
          "Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero "
          "(b = a better, w = a worse).", ""]
    md += table("1. The two benchmarks, linear model, against the reference and the other benchmarks",
                [(lab, f"{b}|lin", x) for b, lab in NEW.items() for x in ("REF", "pca|lin", "gpca|lin", "raw|lin", "lasso|lin")] + [("autoencoder", "ae|lin", "kpca|lin")])
    md += table("2. With trees", [(f"{lab} + {e}", f"{b}|{e}", f"{b}|lin") for b, lab in NEW.items() for e in ("xgb", "gbt")]
                + [(f"{lab} + xgb", f"{b}|xgb", x) for b, lab in NEW.items() for x in ("raw|xgb", "pca|xgb", "REF")])
    md += table("3. IBA against the two benchmarks",
                [(f"IBA {name}", cfg, f"{b}|lin") for b in NEW for name, cfg in (("interpretable", interp), ("accuracy", accur), ("generic formulas", "G|lin"))]
                + [(f"IBA {chosen} + {e}", f"{chosen}|{e}", f"{b}|{e}") for b in NEW for e in ("xgb", "gbt")])
    open(os.path.join(out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
