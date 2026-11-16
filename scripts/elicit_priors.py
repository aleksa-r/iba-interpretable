"""Elicit prior IBA formulas from a language model (the protocol of docs/protocol/IBA_MANUAL.md).

  .venv/bin/python scripts/elicit_priors.py --dry-run                 # print one prompt of each procedure, call nothing
  .venv/bin/python scripts/elicit_priors.py --draws 5                 # needs ANTHROPIC_API_KEY (or .env in the repo root)
For every panel, asset class, procedure (K knowledge only; S with training-sample statistics) and
draw: one request. Every record (prompt hash, model, response id, usage, answer, problems) is
kept under priors/llm/raw/; valid draws are compiled into priors/llm/<procedure>_draw<k>.yaml in
the formula-file format with one section per asset class. Development series only: statistics use
rows admissible at the first forecast origin; asset classes without development series get
procedure K only. Resumable (an existing record is not requested again)."""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import yaml
from iba.priors import elicit as E

REPO = E.REPO
OUT = os.path.join(REPO, "priors", "llm")


def classes():
    from iba.data.universe import load_manifest, load_universe
    series, _ = load_universe()
    dev = {t for v in load_manifest().development.values() for t in v}
    out = {}
    for s in series:
        freq = "weekly" if s.frequency == "daily" else "monthly"
        out.setdefault((freq, s.asset_class), [])
        if s.ticker in dev:
            out[(freq, s.asset_class)].append(s.ticker)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=5); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--procedures", default="K,S"); ap.add_argument("--model", default=E.MODEL)
    a = ap.parse_args()
    env = os.path.join(REPO, ".env")
    if os.path.exists(env) and not os.environ.get("ANTHROPIC_API_KEY"):
        for line in open(env):
            if line.strip().startswith("ANTHROPIC_API_KEY="):
                os.environ["ANTHROPIC_API_KEY"] = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    import warnings; warnings.filterwarnings("ignore")
    from iba.data.panel import load_panel
    panels, dicts = {}, {f: E.load_dictionary(f) for f in ("weekly", "monthly")}
    client = None
    if not a.dry_run:
        import anthropic
        client = anthropic.Anthropic(max_retries=6)              # transient errors (429, 5xx, overloaded) are retried with back-off
    todo = sorted(classes().items())
    shown = set()
    for (freq, cls), members in todo:
        for proc in a.procedures.split(","):
            if proc == "S" and not members:
                continue                                        # no development series: knowledge only
            stats = None
            if proc == "S":
                if freq not in panels:
                    panels[freq] = load_panel(freq)
                stats = E.training_statistics(panels[freq], freq, members, dicts[freq])
            if a.dry_run:
                if (freq, proc) not in shown:
                    shown.add((freq, proc))
                    system, user = E.build_prompt(freq, cls, dicts[freq], stats)
                    print(f"===== {freq} / {cls} / procedure {proc}: system =====\n{system}\n===== user ({len(user)} characters) =====\n{user}\n")
                continue
            for k in range(1, a.draws + 1):
                path = os.path.join(OUT, "raw", proc, freq, cls, f"draw{k}.json")
                if os.path.exists(path):
                    continue
                rec = E.elicit(client, freq, cls, dicts[freq], stats, model=a.model)
                rec["draw"] = k
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as fh:
                    json.dump(rec, fh, indent=1)
                print(f"{proc} {freq} {cls} draw {k}: {'ok' if rec['answer'] else 'FAILED'} ({len(rec['attempts'])} attempt(s))", flush=True)
    if a.dry_run:
        sys.exit()
    for proc in a.procedures.split(","):                        # compile one formula file per procedure and draw
        for k in range(1, a.draws + 1):
            doc = {"source": f"LLM-elicited, procedure {proc}, draw {k}, model {a.model}, knowledge cut-off {E.CUTOFF}", "classes": {}}
            for (freq, cls), _ in todo:
                path = os.path.join(OUT, "raw", proc, freq, cls, f"draw{k}.json")
                if os.path.exists(path):
                    rec = json.load(open(path))
                    if rec["answer"]:
                        doc["classes"].setdefault(freq, {})[cls] = E.to_formulas(rec["answer"], freq)
            with open(os.path.join(OUT, f"{proc}_draw{k}.yaml"), "w") as fh:
                yaml.safe_dump(doc, fh, sort_keys=False)
    print("compiled", flush=True)
