"""The analysis of SPEC-2026-11-14-abc-v3 (section 6), written BEFORE the run.

  .venv/bin/python scripts/make_abc3_report.py            # writes docs/results/SPEC-2026-11-14-abc-v3/

Twelve search arms = data behind the fitness (S one series, C the asset class, F every series of
the frequency) x replacement (greedy, noise-aware) x start (anchored at the prior, spread over the
whole space). The two per-series greedy arms are the earlier specs' (A with the clean test / W);
the other ten are new. Every arm is read three ways: the winner after the acceptance test, the
winner without it, the final colony as an ensemble. Controls: the STARTING colonies as ensembles
(no search). Derived: every ensemble averaged over its three seeds ("@3").

 1. search diagnostics per arm and target type;
 2. per (frequency, task), all development series of the frequency pooled on the same dates: paired
    date-block-bootstrap differences in the primary loss against E1, B, group PCA, the reference;
 3. the three factors: pooled against single-series fitness, noise-aware against greedy, at fixed
    levels of the other factors;
 4. SPA over all new configurations; 5. the decision rule of the spec, evaluated mechanically."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.eval.bootstrap import default_block, paired_block_test
from iba.eval.map import REFERENCE, base_name, configs_of, pointwise
from iba.eval.mcs import spa_test
from iba.protocol.study import FIRST_SPEC, abc2_tasks

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SPEC, SPEC2 = "SPEC-2026-11-14-abc-v3", "SPEC-2026-11-14-abc-v2"
KINDS = ("return", "logrv", "tail_loss", "tail_gain")
E1, B, WB, GPCA = "iba_e1|lin", "iba_b", "iba_wb", "gpca|lin"


def arm(level, repl, start):
    """(label, tested winner, winner without the test, ensemble, name of the search in the block metadata)."""
    label = f"{level} {'noise-aware' if repl == 'n' else 'greedy'} {'anchored' if start == 'a' else 'spread'}"
    if level == "S" and repl == "g":
        return (label,) + (("iba_ac|lin", "iba_ar|lin", "iba_b", "iba_ac") if start == "a" else ("iba_w|lin", "iba_wr|lin", "iba_wb", "iba_w"))
    m = f"iba_{level.lower()}{'n' if repl == 'n' else ''}{start}"
    return (label, f"{m}|lin", f"{m}_r|lin", f"{m}_b", m)


ARMS = [arm(l, r, s) for l in "SCF" for r in "gn" for s in "aw"]
NEW = [a for a in ARMS if not (a[0].startswith("S greedy"))]
CONTROLS = ["iba_rnda", "iba_rndw"]
ENS_ALL = [a[3] for a in ARMS] + CONTROLS
NEW_CONFIGS = [c for a in NEW for c in a[1:4]] + CONTROLS


def cell_dirs(t):
    name = t.target.replace("^", "_")
    return ([os.path.join(REPO, "artifacts", FIRST_SPEC, f"stage{s}", t.frequency, t.name, name) for s in (1, 2)]
            + [os.path.join(REPO, "artifacts", SPEC2, "stage4", t.frequency, t.name, name),
               os.path.join(REPO, "artifacts", SPEC, "stage6", t.frequency, t.name, name)])


def load():
    by, diag = {}, []
    names = {a[4]: a[0] for a in ARMS}
    for t in abc2_tasks():
        pred = None
        for d in cell_dirs(t):
            p = pd.read_csv(os.path.join(d, "predictions.csv"), parse_dates=["date"])
            if pred is None:
                pred = p
            else:
                if len(p) != len(pred) or (p["date"].values != pred["date"].values).any() or not np.allclose(p["y_eval"].values, pred["y_eval"].values, equal_nan=True):
                    raise ValueError(f"{t.name} {t.target}: stages do not share dates and labels")
                pred = pd.concat([pred, p[[c for c in p.columns if c not in pred.columns]]], axis=1)
            meta = json.load(open(os.path.join(d, "meta.json")))
            for b in meta["blocks"]:
                for name, info in b["methods"].items():
                    m = re.match(r"^(iba_\w+)\.s(\d+)$", name)
                    if m and m.group(1) in names and isinstance(info, dict) and "inner_best" in info:
                        diag.append({"frequency": t.frequency, "task": t.name, "kind": t.kind, "target": t.target, "block": b["block"],
                                     "arm": names[m.group(1)], "seed": int(m.group(2)), "accepted": float(info["accepted"]),
                                     "inner_gain": 1 - info["inner_best"] / info["inner_prior"],
                                     "clean_gain": 1 - info["clean_best"] / info["clean_prior"] if info.get("clean_rows", 0) > 0 else np.nan,
                                     "literals": info["literals"], "groups": info.get("groups", np.nan), "moved": float(info.get("distance", 0) > 0)})
        for e in ENS_ALL:                                        # every ensemble averaged over its seeds
            cols = [c for c in pred.columns if base_name(c) == e and not c.endswith("::var")]
            pred[e + "@3"] = pred[cols].mean(axis=1)
        by.setdefault((t.frequency, t.name, t.kind, t.h), []).append((t.target, pred))
    return by, pd.DataFrame(diag)


def main():
    out = os.path.join(REPO, "docs", "results", SPEC); os.makedirs(out, exist_ok=True)
    by, diag = load()
    md = [f"# {SPEC}: pooled fitness, noise-aware replacement, ensembles (development series)", "",
          "Arms: S = fitness on one series, C = on the asset class, F = on every series of the frequency; greedy or noise-aware replacement; "
          "colony anchored at the prior or spread over the whole space. `S greedy anchored` and `S greedy spread` are the earlier specs' ABC "
          "(clean test) and W. Readings: tested = the winner if it passed the acceptance test on clean rows, else the prior; untested = the "
          "winner; ensemble = the final colony. E1 = fixed prior formulas; B = the first ensemble.", ""]

    # 1. diagnostics
    unit = diag.groupby(["kind", "frequency", "task", "target", "block", "arm"]).mean(numeric_only=True).reset_index()
    d1 = unit.groupby(["arm", "kind"])[["inner_gain", "clean_gain", "accepted", "moved", "literals", "groups"]].mean().round(4)
    diag.groupby(["kind", "arm"]).mean(numeric_only=True).round(5).to_csv(os.path.join(out, "search_diagnostics.csv"))
    rows = []
    for a in ARMS:
        row = {"arm": a[0]}
        for k in KINDS:
            if (a[0], k) not in d1.index:
                row[k] = ""; continue
            x = d1.loc[(a[0], k)]
            row[k] = f"{100 * x.inner_gain:+.1f} / {100 * x.clean_gain:+.1f} / {100 * x.accepted:.0f} % / {x.literals:.1f}"
        rows.append(row)
    md += ["## 1. What the searches do", "",
           "Cell: gain of the winner over the prior on the fitness folds / on the clean outer rows (before the test) / share of winners that pass the "
           "test / literals of the winner. Units = (cell, block), seeds averaged; pooled arms count once per member series.", "",
           pd.DataFrame(rows).to_markdown(index=False), ""]

    # paired tests
    pairs = []
    for a in ARMS:
        pairs += [(a[1], E1), (a[2], E1), (a[3], E1), (a[3], B), (a[3], GPCA), (a[1], "REF"), (a[3], "REF"), (a[3] + "@3", E1), (a[3] + "@3", GPCA)]
    for c in CONTROLS:
        pairs += [(c, E1), (c, B), (c, WB), (c, GPCA), (c, "REF"), (c + "@3", E1), (c + "@3", GPCA)]
    pairs += [(E1, "REF"), (B, "REF"), (GPCA, "REF"), (E1, GPCA)]
    lookup = {(l, r, s): arm(l, r, s) for l in "SCF" for r in "gn" for s in "aw"}
    contrasts = []                                                # (reading, factor, a, b)
    for ri, reading in ((1, "tested"), (2, "untested"), (3, "ensemble")):
        for r in "gn":
            for s in "aw":
                for l in "CF":
                    contrasts.append((reading, f"{l} against S", lookup[(l, r, s)][ri], lookup[("S", r, s)][ri]))
        for l in "SCF":
            for s in "aw":
                contrasts.append((reading, "noise-aware against greedy", lookup[(l, "n", s)][ri], lookup[(l, "g", s)][ri]))
            for r in "gn":
                contrasts.append((reading, "spread against anchored", lookup[(l, r, "w")][ri], lookup[(l, r, "a")][ri]))
    pairs += [(a, b) for _, _, a, b in contrasts]
    pairs = list(dict.fromkeys(pairs))

    rows, spa, sd = [], [], []
    for (freq, task, kind, h), cells in sorted(by.items()):
        preds = [p for _, p in cells]
        common = sorted(set.intersection(*[set(configs_of(p)) for p in preds]))
        bases = sorted({base_name(c) for c in common})
        per_seed = {b: [np.column_stack([pointwise(p, kind, m) for p in preds]) for m in common if base_name(m) == b] for b in bases}
        L = {b: np.mean(v, axis=0) for b, v in per_seed.items()}
        T = L[bases[0]].shape[0]; block = default_block(h, T)
        ref = REFERENCE[kind]
        for a, b in pairs:
            bb = ref if b == "REF" else b
            r = paired_block_test(L[a] - L[bb], block=block, reps=2000, seed=h)
            rows.append({"frequency": freq, "task": task, "kind": kind, "a": a, "b": b, "series": len(preds), "rel_diff": r.mean / L[bb].mean(),
                         "ci_low": r.ci_low / L[bb].mean(), "ci_high": r.ci_high / L[bb].mean(), "p": r.p_value})
        models = pd.DataFrame({c: L[c].mean(axis=1) for c in NEW_CONFIGS})
        for bench in (E1, B, WB, GPCA, ref):
            s = spa_test(pd.Series(L[bench].mean(axis=1)), models, block=block, reps=2000, seed=h)
            spa.append({"frequency": freq, "task": task, "kind": kind, "benchmark": "REF" if bench == ref else bench, "variants": s["k"],
                        "best_variant": models.mean().idxmin(), "p_consistent": s["consistent"]})
        for c in ENS_ALL:
            sd.append({"kind": kind, "config": c, "rel_seed_sd": float(np.std([x.mean() for x in per_seed[c]]) / L[c].mean())})
    P, S, SD = pd.DataFrame(rows), pd.DataFrame(spa), pd.DataFrame(sd)
    P.to_csv(os.path.join(out, "paired_tests.csv"), index=False); S.to_csv(os.path.join(out, "spa_tests.csv"), index=False)
    P["verdict"] = np.where(P.ci_high < 0, "better", np.where(P.ci_low > 0, "worse", "n.s."))
    key = {k: g for k, g in P.groupby(["a", "b", "kind"])}

    def cells(a, b):
        row, tb, tw, tn = {}, 0, 0, 0
        for k in KINDS:
            if (a, b, k) not in key:
                row[k] = ""; continue
            g = key[(a, b, k)]
            nb, nw = int((g.verdict == "better").sum()), int((g.verdict == "worse").sum())
            row[k] = f"{100 * g.rel_diff.mean():+.2f} % ({nb}b {nw}w / {len(g)})"
            tb, tw, tn = tb + nb, tw + nw, tn + len(g)
        row["all tasks"] = f"{tb} better, {tw} worse of {tn}"
        return row

    note = "Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse)."

    def table(title, items):
        return [f"## {title}", "", note, "", pd.DataFrame([{"a": lab, "against": b, **cells(a, b)} for lab, a, b in items]).to_markdown(index=False), ""]

    md += table("2a. Tested winner against E1", [(a[0], a[1], E1) for a in ARMS])
    md += table("2b. Winner WITHOUT the test against E1", [(a[0], a[2], E1) for a in ARMS])
    md += table("2c. Colony ensemble against E1", [(a[0], a[3], E1) for a in ARMS] + [(f"control: starting colony, {c[-1]}", c, E1) for c in CONTROLS])
    md += table("2d. Colony ensemble against the first ensemble (B)", [(a[0], a[3], B) for a in ARMS if a[3] != B] + [(f"control: starting colony, {c[-1]}", c, B) for c in CONTROLS])
    md += table("2e. Colony ensemble against group PCA", [(a[0], a[3], GPCA) for a in ARMS] + [(f"control: starting colony, {c[-1]}", c, GPCA) for c in CONTROLS])
    md += table("2f. Ensembles averaged over the three seeds, against E1 and against group PCA",
                [(a[0] + " @3", a[3] + "@3", E1) for a in ARMS] + [(f"control {c[-1]} @3", c + "@3", E1) for c in CONTROLS]
                + [(a[0] + " @3", a[3] + "@3", GPCA) for a in ARMS] + [(f"control {c[-1]} @3", c + "@3", GPCA) for c in CONTROLS])
    md += table("2g. Against the type's reference (historical mean / HAR / base rate)",
                [("E1", E1, "REF"), ("B", B, "REF"), ("group PCA", GPCA, "REF")] + [(a[0] + ", tested", a[1], "REF") for a in ARMS] + [(a[0] + ", ensemble", a[3], "REF") for a in ARMS])
    md += table("2h. The controls: starting colonies as ensembles (no search)", [(f"starting colony, {c[-1]}", c, b) for c in CONTROLS for b in (E1, B, WB, GPCA, "REF")])

    # 3. factors
    md += ["## 3. The three factors (a against b at fixed levels of the other two)", "", note, ""]
    for reading in ("tested", "untested", "ensemble"):
        items = [(f"{f}: {a}", a, b) for rd, f, a, b in contrasts if rd == reading]
        md += [f"### {reading}", "", pd.DataFrame([{"contrast": lab, "against": b, **cells(a, b)} for lab, a, b in items]).to_markdown(index=False), ""]
        eff = []
        for f in dict.fromkeys(c[1] for c in contrasts):
            g = pd.concat([P[(P.a == a) & (P.b == b)] for rd, ff, a, b in contrasts if rd == reading and ff == f])
            eff.append({"factor": f, **{k: f"{100 * g[g.kind == k].groupby(['a', 'b']).rel_diff.mean().mean():+.2f} %" for k in KINDS},
                        "tasks better / worse": f"{int((g.verdict == 'better').sum())} / {int((g.verdict == 'worse').sum())} of {len(g)}"})
        md += ["Averaged over the contrasts of each factor:", "", pd.DataFrame(eff).to_markdown(index=False), ""]

    # 4. SPA, seed spread
    s1 = S.assign(sig=S.p_consistent < 0.05).groupby(["benchmark", "kind"]).agg(tasks=("task", "count"), significant=("sig", "sum"), median_p=("p_consistent", "median")).round(4).reset_index()
    s2 = S[S.benchmark == "REF"].groupby(["kind", "best_variant"]).size().unstack(fill_value=0).reset_index()
    md += [f"## 4. SPA: does any of the {len(NEW_CONFIGS)} new configurations beat the benchmark? (consistent p-value; tasks with p < 0.05)", "", s1.to_markdown(index=False), "",
           "New configuration with the lowest pooled loss per task:", "", s2.to_markdown(index=False), "",
           "Seed spread of the ensembles (standard deviation over the three seeds of the pooled loss, relative to the loss):", "",
           SD.pivot_table(index="config", columns="kind", values="rel_seed_sd").round(4).reset_index().to_markdown(index=False), ""]

    # 5. decision rule
    dec = []
    for lab, cand, inc in [(a[0] + ", tested", a[1], E1) for a in NEW] + [(a[0] + ", ensemble", a[3], B) for a in NEW] + [(f"control {c[-1]}, ensemble", c, B) for c in CONTROLS]:
        g = P[(P.a == cand) & (P.b == inc)]
        better, worse = int((g.verdict == "better").sum()), int((g.verdict == "worse").sum())
        by_kind = g.groupby("kind").rel_diff.mean()
        dec.append({"candidate": lab, "config": cand, "incumbent": inc, "tasks better": better, "tasks worse": worse,
                    "types with lower mean loss": f"{int((by_kind < 0).sum())}/4", "mean rel. diff % (types equally weighted)": round(100 * by_kind.mean(), 3),
                    "qualifies": bool(better > worse and (by_kind < 0).sum() >= 3)})
    D = pd.DataFrame(dec)
    D.to_csv(os.path.join(out, "decision.csv"), index=False)
    md += ["## 5. Decision rule (spec section 6)", "",
           "A candidate qualifies if it is significantly better than its incumbent in more tasks than it is significantly worse AND its mean loss is lower in at least 3 of the 4 target types.", "",
           D.to_markdown(index=False), ""]
    q = D[D.qualifies]
    md += ["Qualifying: " + ("; ".join(q.candidate) if len(q) else "none; E1 and the ensembles of the earlier specs stay.")
           + (f" Lowest mean relative loss among them: {q.sort_values('mean rel. diff % (types equally weighted)').candidate.iloc[0]}." if len(q) else ""), ""]
    open(os.path.join(out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
