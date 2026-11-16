"""Build the map from the artifacts of a spec: docs/results/<spec>/map.csv and map.md."""
import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import pandas as pd
from iba.eval.map import build_map, headline_table
from iba.protocol.study import development_tasks, stratum_of

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
spec = sys.argv[1]
strata = stratum_of()
cells = []
for t in development_tasks():
    preds, metas = [], []
    for stage_dir in sorted(glob.glob(os.path.join(REPO, "artifacts", spec, "stage*", t.frequency, t.name, t.target.replace("^", "_")))):
        if os.path.exists(os.path.join(stage_dir, "predictions.csv")):
            preds.append(pd.read_csv(os.path.join(stage_dir, "predictions.csv"), parse_dates=["date"]))
            metas.append(json.load(open(os.path.join(stage_dir, "meta.json"))))
    if not preds:
        continue
    pred = preds[0]
    for p in preds[1:]:
        assert (p["date"].values == pred["date"].values).all()
        pred = pd.concat([pred, p[[c for c in p.columns if c not in pred.columns]]], axis=1)
    meta = {"blocks": [{"block": b["block"], "tuning": {k: v for m in metas for k, v in m["blocks"][i]["tuning"].items()},
                        "methods": {k: v for m in metas for k, v in m["blocks"][i]["methods"].items()}} for i, b in enumerate(metas[0]["blocks"])]}
    cells.append({"stratum": strata[t.target], "frequency": t.frequency, "task": t.name, "kind": t.kind, "h": t.h, "target": t.target,
                  "pred": pred, "meta": meta})
print(len(cells), "cells")
m = build_map(cells)
out = os.path.join(REPO, "docs", "results", spec); os.makedirs(out, exist_ok=True)
m.to_csv(os.path.join(out, "map.csv"), index=False)
h = headline_table(m)
with open(os.path.join(out, "map.md"), "w") as fh:
    fh.write(f"# Map for {spec}\n\nEach cell: rank among benchmarks / difference in primary loss to the best benchmark "
             "[95 % date-block-bootstrap interval]; * = interval excludes zero (negative = better than the best benchmark).\n\n")
    fh.write(h.to_markdown(index=False) + "\n")
print(h.to_string(index=False))
