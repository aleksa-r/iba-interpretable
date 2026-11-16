"""The report of SPEC-2026-11-15-confirmation-hf (section 4), written BEFORE the run.

  .venv/bin/python scripts/make_confirmation_hf_report.py                 # writes docs/results/SPEC-2026-11-15-confirmation-hf/
  .venv/bin/python scripts/make_confirmation_hf_report.py --rehearsal DIR # the same code on the DEVELOPMENT hedge-fund indices, written to DIR

Decides every claim of the spec by its written rule, then gives the tables behind the decisions: every
configuration against the reference, group PCA and the interpretable reading; the financial and classification
measures; and, next to each claim, the same quantity on the development hedge-fund indices.
The rehearsal exists to test this code before the freeze: it reads no confirmation series."""
import argparse, importlib.util, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from iba.protocol import study

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


cr = _load("make_confirmation_report")
em, wr = cr.em, cr.wr
SPEC = study.CONFIRM_HF
FIXED, ACC, GPCA, MARGIN, FACTOR = cr.FIXED, cr.ACC, cr.GPCA, cr.MARGIN, cr.FACTOR
sel, count, cell = cr.sel, cr.count, cr.cell


def claims(P, tasks=None):
    """Every claim of section 4 decided by its rule on the table of paired tests ``P``. Rows (claim, statement, result,
    decision). ``tasks``: the tasks of the run; a claim whose comparison lacks one of them is then NOT decided."""
    rows = []
    names = None if tasks is None else {t.name for t in tasks}

    def lacking(*groups):
        return set() if names is None else set().union(*[names - set(g.task) for g in groups])

    def add(cid, text, result, ok, gaps=()):
        if gaps:
            result, ok = f"{result}; MISSING TASKS: {', '.join(sorted(gaps))}", "NOT RUN" if cid in ("H1", "H2") else "not decided"
        rows.append({"claim": cid, "statement": text, "result": result, "decision": ok})
    conf = lambda ok: "CONFIRMED" if ok else "NOT CONFIRMED"
    hd = lambda ok: "holds" if ok else "does not hold"
    # ---- primary
    methods = [FIXED, ACC] + FACTOR
    wins = [(c, t) for c in methods for t in sel(P, c, "REF").query("verdict == 'better'").task]
    add("H1", "No factor method (the two IBA readings and the six reductions, linear model) is significantly better than the reference in any task",
        "none" if not wins else "; ".join(f"{a} in {t}" for a, t in wins), conf(not wins), lacking(*[sel(P, c, "REF") for c in methods]))
    g = sel(P, FIXED, GPCA)
    sig_worse, inside = int((g.verdict == "worse").sum()), int((g.ci_high < MARGIN).sum())
    add("H2", "Group PCA is significantly better than the interpretable reading in at most 1 task",
        f"group PCA significantly better in {sig_worse} of {len(g)}; interpretable reading significantly better in {int((g.verdict == 'better').sum())}; "
        f"mean difference {100 * g.rel_diff.mean():+.2f} %; upper end of the interval below +{100 * MARGIN:.0f} % in {inside} of {len(g)} (reported, no rule)",
        conf(len(g) > 0 and sig_worse <= 1), lacking(g))
    # ---- secondary
    c = count(P, ACC, FIXED)
    add("H3", "Accuracy reading better than the interpretable one in more tasks than worse", cell(c), hd(c["better"] > c["worse"]), lacking(sel(P, ACC, FIXED)))
    cg, crn = count(P, FIXED, "G|lin"), count(P, FIXED, "Rm")
    add("H4", "Elicited formulas at parity with generic and with random formulas: at most 1 task with a significant difference against each",
        f"against generic: {cell(cg)}; against random: {cell(crn)}", hd(cg["better"] + cg["worse"] <= 1 and crn["better"] + crn["worse"] <= 1),
        lacking(sel(P, FIXED, "G|lin"), sel(P, FIXED, "Rm")))
    res, ok, gaps = [], True, set()
    for x in ("Kc", "raw", "gpca"):
        for e in ("xgb", "gbt"):
            c = count(P, f"{x}|{e}", f"{x}|lin"); res.append(f"{x}+{e}: {c['better']} better, {c['worse']} worse of {c['n']}"); ok &= c["worse"] > c["better"]
            gaps |= lacking(sel(P, f"{x}|{e}", f"{x}|lin"))
    add("H5", "Trees do not help: XGBoost and LightGBM significantly worse than the linear model in more tasks than better (IBA, raw factors, group PCA)", "; ".join(res), hd(ok), gaps)
    # ---- reported, no rule
    res = [f"{lab}: {cell(count(P, FIXED, 'REF', k))}" for k, lab in (("return", "returns"), ("tail_loss", "large losses"), ("tail_gain", "large gains"))]
    add("H6", "The interpretable reading against the reference, by target (no direction claimed)", "; ".join(res), "reported")
    return pd.DataFrame(rows)


def development_tests(names):
    """Paired tests of the development reports on the monthly hedge-fund indices, the tasks of this run only."""
    files = [("docs", "results", study.WRAPUP, "paired_tests_priors.csv"), ("docs", "results", study.WRAPUP, "paired_tests_search.csv"),
             ("docs", "results", study.BENCH2, "paired_tests.csv")]
    parts = [pd.read_csv(os.path.join(wr.REPO, *f)) for f in files if os.path.exists(os.path.join(wr.REPO, *f))]
    if not parts:
        return None
    D = pd.concat(parts, ignore_index=True)
    D = D[(D.frequency == "monthly") & D.task.isin(names)].drop_duplicates(["task", "a", "b"])
    D["verdict"] = np.where(D.ci_high < 0, "better", np.where(D.ci_low > 0, "worse", "n.s."))
    return D


MAX_DROPPED = 3            # spec section 6: with more series dropped than this, no claim is decided
SEEDED = ("iba_ca_b", "iba_ca|lin", "iba_ca_r|lin", "Kc_nb")


def incomplete_series(tasks, sets):
    """Series with a cell that has no forecasts or no evaluation in some formula set -> the cells concerned."""
    out = {}
    for t in tasks:
        for prior in sets:
            d = wr.stage_dir(12, prior, t, SPEC)
            if not (os.path.exists(os.path.join(d, "predictions.csv")) and os.path.exists(os.path.join(d, "metrics.csv"))):
                out.setdefault(t.target, []).append(f"{t.name}/{prior}")
    return out


def defective_series(by):
    """Series with a non-finite forecast, or without all three seeds of a seeded configuration, in some cell."""
    out = {}
    for (freq, name, kind, h), cells in by.items():
        for target, p in cells:
            cols = [c for c in p.columns if c not in ("date", "y", "y_eval", "block", "threshold")]
            if not np.isfinite(p[cols].to_numpy(dtype=float)).all():
                out.setdefault(target, []).append(f"{name}: non-finite forecast")
            for base in SEEDED:
                stem, _, est = base.partition("|")
                want = [f"{stem}.s{s}" + (f"|{est}" if est else "") for s in (0, 1, 2)]
                if any(c not in p.columns for c in want):
                    out.setdefault(target, []).append(f"{name}: seeds of {base} missing")
    return out


def rehearsal_cells():
    """The development hedge-fund cells laid out as a confirmation run would be (for testing this code only)."""
    by = _load("make_paper_tables").development()
    return {k: v for k, v in by.items() if k[0] == "monthly"}


def main(rehearsal=None):
    if rehearsal:
        by = rehearsal_cells()
        tasks = [t for t in study.stage_tasks(7) if t.frequency == "monthly"]
        from iba.data.panel import load_panel
        returns, out, label = {"monthly": load_panel("monthly").returns}, rehearsal, "REHEARSAL on the development hedge-fund indices"
    else:
        from iba.data.universe import load_hf_catalogue
        tasks, expected = study.hf_confirmation_tasks(), sorted(load_hf_catalogue()["expected_series"])
        if sorted({t.target for t in tasks}) != expected or len(tasks) != 8 * len(expected):
            sys.exit("the panel of the run is not the one the spec describes (series or tasks differ): no report")
        sets = study.STAGES[12]["priors"]
        dropped = incomplete_series(tasks, sets)                   # spec section 6: such a series leaves every task
        by = wr.load(stage=12, sets=sets, spec=SPEC, task_list=[t for t in tasks if t.target not in dropped])
        dropped.update(defective_series(by))
        if dropped:
            tasks = [t for t in tasks if t.target not in dropped]
            by = wr.load(stage=12, sets=sets, spec=SPEC, task_list=tasks)
        if len(dropped) > MAX_DROPPED:
            sys.exit(f"{len(dropped)} series could not be run as specified ({sorted(dropped)}): no claim is decided (spec section 6)")
        from iba.data.panel import load_panel
        returns = {"monthly": load_panel("monthly", confirmation_run=SPEC).returns}
        out, label = os.path.join(wr.REPO, "docs", "results", SPEC), "the frozen final method on hedge-fund indices of a second provider"
    if rehearsal:
        dropped = {}
    os.makedirs(out, exist_ok=True)
    n_series = len({t.target for t in tasks})
    P, _ = wr.paired(by, cr.pairs(), spread_table=False, skip_missing=True)
    P.to_csv(os.path.join(out, "paired_tests.csv"), index=False)
    cr.check_complete(P, tasks)
    head = (f"CONFIRMATION series ({n_series} monthly hedge-fund indices), measures declared in the spec before the run (`docs/protocol/EXTRA_METRICS.md`). "
            "All factor methods with the linear model. The averaged reading is the ABC colony of the development run, applied unchanged. "
            "The indices are not investable: the long/flat rule is a reading of the forecasts, not a strategy.")
    em.tables(by, em.methods("Kc", ACC), os.path.join(out, "extra"), "Financial and classification measures (hedge-fund confirmation series)", head, returns)
    C = claims(P, tasks)
    D = None if rehearsal else development_tests({t.name for t in tasks})
    if D is not None:
        dev = claims(D).set_index("claim").result.to_dict()
        C["development (11 CISDM indices; decisions were not made there)"] = C.claim.map(lambda c: dev.get(c, ""))
    C.to_csv(os.path.join(out, "claims.csv"), index=False)
    table = wr.table_maker(P)
    dates = next(iter(by.values()))[0][1]["date"]
    md = [f"# {SPEC}: {label}", "",
          f"{n_series} series, {len(tasks)} cells, test period {dates.min().date()} to {dates.max().date()}. One run. "
          + ("No series was dropped. " if not dropped else "DROPPED from every task under the rule of spec section 6 (to be recorded in docs/DEVIATIONS.md): "
             + "; ".join(f"{s} ({', '.join(sorted(set(v))[:4])})" for s, v in sorted(dropped.items())) + ". ")
          + "Decisions below are made by the rules written in the spec before any "
          "of these numbers existed. Relative differences in the primary loss, a minus b (negative = a better), all series pooled on the same dates, 95 % date-block bootstrap.", "",
          "## 1. The claims", "", "### Primary", "", C[C.claim.isin(["H1", "H2"])].to_markdown(index=False), "",
          "### Secondary and reported", "", C[~C.claim.isin(["H1", "H2"])].to_markdown(index=False), "",
          "## 2. Every configuration", "", "Cell: mean relative difference; tasks where the interval excludes zero (b = a better, w = a worse).", ""]
    present = [(lab, c) for lab, c in cr.SHOW if len(P[P.a == c])]
    md += table("2a. Against the type's reference (historical mean / base rate)", [(lab, c, "REF") for lab, c in present])
    md += table("2b. Against group PCA", [(lab, c, GPCA) for lab, c in present if c != GPCA and len(sel(P, c, GPCA))])
    md += table("2c. Against the interpretable reading", [(lab, c, FIXED) for lab, c in present if c != FIXED and len(sel(P, c, FIXED))])
    md += ["## 3. Financial and classification measures", "", "In `extra/extra_metrics.md` (descriptive; no claim rests on them).", ""]
    open(os.path.join(out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))
    return C


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehearsal", metavar="DIR")
    main(ap.parse_args().rehearsal)
