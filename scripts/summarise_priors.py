"""Describe the LLM-elicited prior formulas (no outcome data is read): the run's records, how
much the draws of a procedure agree, how the two procedures differ, and how both differ from the
generic formulas.

  .venv/bin/python scripts/summarise_priors.py > docs/protocol/PRIORS_LLM.md
A formula is read as its set of literals (target, group, factor, state). Agreement of two formulas
= shared literals / literals in either (Jaccard). Consensus of a procedure = the literals given by
more than half of its valid draws."""
import glob, itertools, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np
import yaml
from iba.priors import elicit as E

RAW = os.path.join(E.REPO, "priors", "llm", "raw")
SECTION = {"return": "return", "volatility": "volatility", "large_loss": "tail", "large_gain": "tail"}


def literals(answer, target=None):
    return {(t, g, x["factor"], x["state"]) for t, v in answer.items() if target in (None, t) for g, d in v.items() for x in d["literals"]}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def generic(frequency):
    doc = yaml.safe_load(open(os.path.join(E.REPO, "data", "panels", f"{frequency}_2026-11-11", "expert_formulas.yaml")))
    out = set()
    for t in E.TARGETS[frequency]:
        groups = (doc.get(SECTION[t]) or {}).get("groups") or doc["groups"]
        out |= {(t, g, c, s) for g, lits in groups.items() for c, s in lits}
    return out


def consensus(sets):
    return {x for x in set().union(*sets) if sum(x in s for s in sets) > len(sets) / 2} if sets else set()


if __name__ == "__main__":
    recs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(RAW, "*", "*", "*", "draw*.json")))]
    by = {}
    for r in recs:
        by.setdefault((r["procedure"], r["frequency"], r["asset_class"]), []).append(r)
    att = [a for r in recs for a in r["attempts"]]
    print("# LLM-elicited prior formulas: what was obtained\n")
    print("Written by `scripts/summarise_priors.py` from the records under `priors/llm/raw/`. No outcome data is read here.\n")
    print(f"- Model requested: {sorted({r['model'] for r in recs})}; model that served: {sorted({a['served_model'] for a in att})}; knowledge cut-off told to the model: {recs[0]['cutoff']}.")
    print(f"- Records: {len(recs)} ({sum(r['procedure'] == 'K' for r in recs)} knowledge-only, {sum(r['procedure'] == 'S' for r in recs)} statistics-informed); "
          f"valid: {sum(r['answer'] is not None for r in recs)}; failed: {sum(r['answer'] is None for r in recs)}.")
    print(f"- Requests: {len(att)}; re-asked after an answer broke the manual: {len(att) - len(recs)}; "
          f"tokens in / out: {sum(a['usage']['input_tokens'] for a in att):,} / {sum(a['usage']['output_tokens'] for a in att):,}.")
    bad = [(r["procedure"], r["frequency"], r["asset_class"], r["draw"], a["problems"]) for r in recs for a in r["attempts"] if a["problems"]]
    for b in bad:
        print(f"  - rejected attempt: procedure {b[0]}, {b[1]} / {b[2]}, draw {b[3]}: {'; '.join(b[4])[:300]}")
    print("\n## Agreement between draws, between procedures and with the generic formulas\n")
    print("Mean pairwise agreement of the draws (1 = identical formulas); agreement of the two consensus formulas; "
          "share of the generic formula's literals kept by the consensus, and share kept with the opposite state.\n")
    print("| panel | asset class | draws K / S | agreement K | agreement S | K vs S | literals K / S / generic | generic kept by K / S | generic reversed by K / S |")
    print("|---|---|---|---|---|---|---|---|---|")
    rows = []
    for (freq, cls) in sorted({(f, c) for _, f, c in by}):
        gen, cons, agree, n = generic(freq), {}, {}, {}
        for proc in ("K", "S"):
            sets = [literals(r["answer"]) for r in by.get((proc, freq, cls), []) if r["answer"]]
            n[proc] = len(sets)
            agree[proc] = float(np.mean([jaccard(a, b) for a, b in itertools.combinations(sets, 2)])) if len(sets) > 1 else float("nan")
            cons[proc] = consensus(sets)
        flip = lambda x: (x[0], x[1], x[2], "not_high" if x[3] == "high" else "high")
        kept = {p: (len(cons[p] & gen) / len(gen) if n[p] else float("nan")) for p in cons}
        rev = {p: (len({flip(x) for x in cons[p]} & gen) / len(gen) if n[p] else float("nan")) for p in cons}
        ks = jaccard(cons["K"], cons["S"]) if n["K"] and n["S"] else float("nan")
        rows.append((agree["K"], agree["S"], ks, kept["K"], kept["S"], rev["K"], rev["S"]))
        f = lambda v: "–" if v != v else f"{v:.2f}"
        print(f"| {freq} | {cls} | {n['K']} / {n['S']} | {f(agree['K'])} | {f(agree['S'])} | {f(ks)} | {len(cons['K'])} / {len(cons['S']) if n['S'] else '–'} / {len(gen)} | "
              f"{f(kept['K'])} / {f(kept['S'])} | {f(rev['K'])} / {f(rev['S'])} |")
    m = np.nanmean(np.array(rows, dtype=float), axis=0)
    print(f"| **mean** | | | {m[0]:.2f} | {m[1]:.2f} | {m[2]:.2f} | | {m[3]:.2f} / {m[4]:.2f} | {m[5]:.2f} / {m[6]:.2f} |")
    print("\n## Agreement between draws by target\n")
    print("| procedure | " + " | ".join(E.TARGETS["weekly"]) + " |")
    print("|---|" + "---|" * len(E.TARGETS["weekly"]))
    for proc in ("K", "S"):
        cells = []
        for t in E.TARGETS["weekly"]:
            v = []
            for (p, freq, cls), rs in by.items():
                sets = [literals(r["answer"], t) for r in rs if r["answer"]]
                if p == proc and t in E.TARGETS[freq] and len(sets) > 1:
                    v.append(np.mean([jaccard(a, b) for a, b in itertools.combinations(sets, 2)]))
            cells.append(f"{np.mean(v):.2f}" if v else "–")
        print(f"| {proc} | " + " | ".join(cells) + " |")
    print("\n## Consensus formulas (literals given by more than half of the valid draws)\n")
    for (proc, freq, cls), rs in sorted(by.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        sets = [literals(r["answer"]) for r in rs if r["answer"]]
        if not sets:
            print(f"**{freq} / {cls} / {proc}**: no valid draw\n"); continue
        c = consensus(sets)
        print(f"**{freq} / {cls} / {proc}** ({len(sets)} draws)\n")
        for t in E.TARGETS[freq]:
            parts = {}
            for (tt, g, code, state) in sorted(c):
                if tt == t:
                    parts.setdefault(g, []).append(f"{code} {'high' if state == 'high' else 'NOT high'}")
            print(f"- {t}: " + "; ".join(f"{g}: {' AND '.join(v)}" for g, v in parts.items()))
        print()
