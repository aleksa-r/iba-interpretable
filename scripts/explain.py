"""The explanation step of the method (docs/protocol/EXPLANATION.md): asset-class summaries and a few
worked examples of single forecasts, written by a language model from exact numbers and checked.

  .venv/bin/python scripts/explain.py --dry-run             # build every input, print one payload of each level, call nothing
  .venv/bin/python scripts/explain.py                       # needs ANTHROPIC_API_KEY (or .env in the repo root)
  .venv/bin/python scripts/explain.py --what examples       # only the worked examples (or: summaries)
Needs the finished wrap-up run: the formula set and the readings come from its final_method.json, the
forecasts from its stage 7. Every forecast is first repeated here and must equal the stored one; then
the numbers of each case are prepared, sent, and the answer is kept only if every number in it is in
the material. Records under explanations/raw/<set>/, the compiled text in docs/explanations/. Resumable."""
import argparse, glob, json, os, pickle, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from concurrent.futures import ProcessPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOL = {"lin": 1e-9, "xgb": 1e-5}
# the worked examples, fixed before any explanation was written: the last forecast date of the alphabetically
# first development series of the class, at the middle horizon
EXAMPLES = [("weekly", "equity_us_broad", "return", 4), ("weekly", "equity_us_broad", "logrv", 4), ("weekly", "equity_us_broad", "tail_loss", 4),
            ("weekly", "equity_us_broad", "tail_gain", 4), ("monthly", "hedge_fund_monthly", "return", 3), ("monthly", "hedge_fund_monthly", "tail_loss", 3)]
_PANELS = {}


def stored(pset, t):
    from iba.protocol.study import WRAPUP
    return os.path.join(REPO, "artifacts", WRAPUP, "stage7", f"prior_{pset}", t.frequency, t.name, t.target.replace("^", "_"), "predictions.csv")


def _cell(args):
    pset, t, cache, accuracy = args
    import warnings; warnings.filterwarnings("ignore")
    import pandas as pd
    from iba.data.panel import load_panel
    from iba.explain.cases import cell_numbers
    from iba.explain.trace import trace_cell
    from iba.protocol.study import prior_file
    path = os.path.join(cache, t.frequency, t.name, t.target.replace("^", "_") + ".pkl")
    if os.path.exists(path):
        return pickle.load(open(path, "rb"))
    if t.frequency not in _PANELS:
        _PANELS[t.frequency] = load_panel(t.frequency, formulas=prior_file(pset))
    pred = pd.read_csv(stored(pset, t), parse_dates=["date"])
    stem = "iba_rnda" if accuracy.endswith("_nb") else accuracy            # the accuracy reading: the no-search colony or the ABC colony (stage 9)
    if stem != "iba_rnda":
        extra = pd.read_csv(stored(pset, t).replace(os.sep + "stage7" + os.sep, os.sep + "stage9" + os.sep), parse_dates=["date"])
        if (extra["date"].values != pred["date"].values).any():
            raise ValueError(f"{t.name} {t.target}: stage 9 and stage 7 do not share their dates")
        pred = pd.concat([pred, extra[[c for c in extra.columns if c.startswith(stem + ".s")]]], axis=1)
    cell = cell_numbers(trace_cell(_PANELS[t.frequency], t), pred, [c for c in pred.columns if c.startswith(stem + ".s") and "::" not in c])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "wb") as fh:
        pickle.dump(cell, fh)
    os.replace(path + ".tmp", path)
    return cell


def load_draws(pset, freq, cls):
    """Elicitation answers behind a formula set: {draw: answer}. A consensus set draws on all five; a class
    without statistics-informed draws (no development series) on the knowledge-only ones."""
    proc = pset[0]
    base = os.path.join(REPO, "priors", "llm", "raw", proc, freq, cls)
    if not os.path.isdir(base):
        base = os.path.join(REPO, "priors", "llm", "raw", "K", freq, cls)
    out = {}
    for p in sorted(glob.glob(os.path.join(base, "draw*.json"))):
        r = json.load(open(p))
        if r["answer"] and (pset.endswith("c") or r["draw"] == int(pset[1:])):
            out[r["draw"]] = r["answer"]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--what", choices=["all", "summaries", "examples"], default="all")
    ap.add_argument("--workers", type=int, default=8); ap.add_argument("--model")
    a = ap.parse_args()
    import pandas as pd
    from iba.explain import narrate as N
    from iba.explain.cases import class_case, forecast_case
    from iba.priors import elicit as E
    from iba.protocol.study import WRAPUP, stage_tasks, stratum_of
    res = os.path.join(REPO, "docs", "results", WRAPUP)
    final = json.load(open(os.path.join(res, "final_method.json")))
    pset, config = final["formula_set"], f"{final['formula_set']}|lin"
    if final["interpretable"] != config or final["accuracy"] not in (f"{pset}_nb", "iba_ca_b"):
        sys.exit(f"the final method reads {final['interpretable']} / {final['accuracy']}: this script explains the fixed formula only")
    accuracy_text = ("\"Averaged formulas\" is the same model averaged over the formula and nineteen close variants of it." if final["accuracy"].endswith("_nb") else
                     "\"Averaged formulas\" is the same model averaged over a colony of formulas that a search (artificial bee colony) built around these formulas.")
    tests = pd.read_csv(os.path.join(res, "paired_tests_priors.csv"))
    strata, tasks = stratum_of(), stage_tasks(7)
    cache = os.path.join(REPO, "artifacts", "explain", pset, f"cells_{final['accuracy']}")
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        cells = list(ex.map(_cell, [(pset, t, cache, final["accuracy"]) for t in tasks], chunksize=4))
    worst = {k: max(c["diffs"].get(k, 0.0) for c in cells) for k in TOL}
    print(f"formula set {pset}: {len(cells)} cells repeated; largest difference to the stored forecasts: linear {worst['lin']:.1e}, XGBoost {worst['xgb']:.1e}", flush=True)
    if any(worst[k] > TOL[k] for k in TOL):
        sys.exit("the stored forecasts are not reproduced: nothing is explained")
    labels = {f: {**dict(zip(E.load_dictionary(f)["code"], E.load_dictionary(f)["label"])), "__target__": "the index's own recent behaviour"} for f in ("weekly", "monthly")}
    jobs = []                                                     # (level, record path, title, payload)
    if a.what in ("all", "summaries"):
        by = {}
        for c in cells:
            by.setdefault((c["frequency"], strata[c["target"]], c["kind"]), []).append(c)
        for (freq, cls, kind), cs in sorted(by.items()):
            case = class_case(cs, E.CLASS_TEXT[cls], labels[freq], load_draws(pset, freq, cls), tests, config)
            case["accuracy_text"] = accuracy_text
            jobs.append(("class", os.path.join("class", freq, cls, N.TARGET_OF[kind] + ".json"), f"{E.CLASS_TEXT[cls]}: {N.TARGET_OF[kind]}", N.class_payload(case)))
    if a.what in ("all", "examples"):
        for freq, cls, kind, h in EXAMPLES:
            cs = sorted((c for c in cells if (c["frequency"], strata[c["target"]], c["kind"], c["h"]) == (freq, cls, kind, h)), key=lambda c: c["target"])
            c = cs[0]
            case = forecast_case(c, E.CLASS_TEXT[cls], labels[freq], load_draws(pset, freq, cls), tests, config)
            jobs.append(("forecast", os.path.join("forecast", freq, f"{c['target'].replace('^', '_')}_{c['task']}.json"),
                         f"{c['target']}, {N.TARGET_OF[kind]}, {N.horizon_text(h, freq)}, {c['last']}", N.forecast_payload(case)))
    out = os.path.join(REPO, "explanations", "raw", pset)
    print(f"{sum(j[0] == 'class' for j in jobs)} asset-class summaries, {sum(j[0] == 'forecast' for j in jobs)} worked examples; "
          f"payload characters: {sum(len(j[3]) for j in jobs):,}", flush=True)
    if a.dry_run:
        for level in ("class", "forecast"):
            j = next((j for j in jobs if j[0] == level), None)
            if j:
                print(f"\n===== {level}: {j[2]} =====\n{N.SYSTEM if level == 'class' else '(same system prompt)'}\n\n{j[3]}")
        sys.exit()
    env = os.path.join(REPO, ".env")
    if os.path.exists(env) and not os.environ.get("ANTHROPIC_API_KEY"):
        for line in open(env):
            if line.strip().startswith("ANTHROPIC_API_KEY="):
                os.environ["ANTHROPIC_API_KEY"] = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    import anthropic
    client = anthropic.Anthropic(max_retries=6)
    for level, rel, title, payload in jobs:
        path = os.path.join(out, rel)
        if os.path.exists(path):
            continue
        rec = N.explain(client, payload, model=a.model or N.MODEL)
        rec.update({"level": level, "title": title, "formula_set": pset})
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(rec, fh, indent=1)
        print(f"{level} {title}: {'ok' if rec['answer'] else 'FAILED'} ({len(rec['attempts'])} attempt(s))", flush=True)
    md = [f"# Explanations of the final method (formula set {pset})", "",
          "Written by a language model from exact numbers of the fitted model (`scripts/explain.py`, protocol in `docs/protocol/EXPLANATION.md`). "
          "Every number in a text is written in the material the model was given; a text with any other number was rejected. "
          "The texts describe development series only.", ""]
    att = tok_in = tok_out = failed = 0
    for level, head in (("class", "## Asset-class summaries"), ("forecast", "## Worked examples: single forecasts")):
        md += [head, ""]
        for lv, rel, title, _ in jobs:
            p = os.path.join(out, rel)
            if lv != level or not os.path.exists(p):
                continue
            rec = json.load(open(p))
            att += len(rec["attempts"]); tok_in += sum(x["usage"]["input_tokens"] for x in rec["attempts"]); tok_out += sum(x["usage"]["output_tokens"] for x in rec["attempts"])
            if not rec["answer"]:
                failed += 1
                md += [f"### {title}", "", "(no accepted text: " + "; ".join(x["problems"][0] for x in rec["attempts"] if x["problems"])[:300] + ")", ""]
                continue
            md += [f"### {title}", "", f"**{rec['answer']['headline']}**", "", rec["answer"]["explanation"], "", f"*Limits.* {rec['answer']['limits']}", ""]
    md += ["## Record", "", f"Model {a.model or N.MODEL}; {len(jobs)} cases, {failed} without an accepted text; {att} requests; tokens in / out: {tok_in:,} / {tok_out:,}.", ""]
    os.makedirs(os.path.join(REPO, "docs", "explanations"), exist_ok=True)
    open(os.path.join(REPO, "docs", "explanations", f"EXPLANATIONS_{pset}.md"), "w").write("\n".join(md))
    print(f"compiled docs/explanations/EXPLANATIONS_{pset}.md; requests {att}, tokens in/out {tok_in:,}/{tok_out:,}, failed {failed}", flush=True)
