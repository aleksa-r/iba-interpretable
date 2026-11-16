"""The derived prior formula files of SPEC-2026-11-14-wrapup (section 3). No outcome data is read.

  .venv/bin/python scripts/make_prior_files.py
  priors/llm/K_consensus.yaml, S_consensus.yaml   per asset class and target: the literals given by more than
      half of the procedure's valid draws; if more than two remain in a group, the two with the most votes
      (ties: order of the factor dictionary). A class without S draws (no development series) takes its K
      consensus in the S file.
  priors/random/R_draw1..5.yaml   per asset class and target, in every group two distinct factors drawn
      uniformly with states drawn uniformly (the own-behaviour group: its one factor, random state); seed = draw."""
import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np
import yaml
from iba.priors import elicit as E

LLM, RND = os.path.join(E.REPO, "priors", "llm"), os.path.join(E.REPO, "priors", "random")


def consensus(answers, frequency, groups):
    """Answers of one (procedure, class) -> the formula-file sections of the class."""
    out = {}
    for t in E.TARGETS[frequency]:
        sec = {}
        for g, codes in groups.items():
            votes = {}
            for a in answers:
                for x in a[t][g]["literals"]:
                    votes[(x["factor"], x["state"])] = votes.get((x["factor"], x["state"]), 0) + 1
            keep = [k for k, v in votes.items() if v > len(answers) / 2]
            keep.sort(key=lambda k: (-votes[k], codes.index(k[0])))
            keep = sorted(keep[:2], key=lambda k: codes.index(k[0]))
            if keep:
                sec[g] = [[c, s] for c, s in keep]
        out[E.KIND_OF[t]] = {"groups": sec}
    return out


def random_sections(frequency, groups, rng):
    out = {}
    for t in E.TARGETS[frequency]:
        sec = {}
        for g, codes in groups.items():
            idx = sorted(rng.choice(len(codes), size=min(2, len(codes)), replace=False))
            sec[g] = [[codes[int(j)], "high" if rng.integers(2) else "not_high"] for j in idx]
        out[E.KIND_OF[t]] = {"groups": sec}
    return out


if __name__ == "__main__":
    groups = {f: E.groups_of(E.load_dictionary(f)) for f in ("weekly", "monthly")}
    by = {}
    for p in sorted(glob.glob(os.path.join(LLM, "raw", "*", "*", "*", "draw*.json"))):
        r = json.load(open(p))
        if r["answer"]:
            by.setdefault((r["procedure"], r["frequency"], r["asset_class"]), []).append(r["answer"])
    classes = sorted({(f, c) for _, f, c in by})
    docs = {}
    for proc in ("K", "S"):
        doc = {"source": f"LLM-elicited, procedure {proc}, consensus of the valid draws (more than half; at most two literals per group), "
                         f"model {E.MODEL}, knowledge cut-off {E.CUTOFF}", "draws": {}, "classes": {}}
        for freq, cls in classes:
            src = proc if (proc, freq, cls) in by else "K"         # no development series: knowledge-only formulas
            doc["draws"][f"{freq}/{cls}"] = f"{len(by[(src, freq, cls)])} of procedure {src}"
            doc["classes"].setdefault(freq, {})[cls] = consensus(by[(src, freq, cls)], freq, groups[freq])
        docs[proc] = doc
        with open(os.path.join(LLM, f"{proc}_consensus.yaml"), "w") as fh:
            yaml.safe_dump(doc, fh, sort_keys=False)
    os.makedirs(RND, exist_ok=True)
    for k in range(1, 6):
        rng = np.random.default_rng(k)
        doc = {"source": f"random formulas, seed {k} (two factors per group, random states)", "classes": {}}
        for freq, cls in classes:
            doc["classes"].setdefault(freq, {})[cls] = random_sections(freq, groups[freq], rng)
        with open(os.path.join(RND, f"R_draw{k}.yaml"), "w") as fh:
            yaml.safe_dump(doc, fh, sort_keys=False)
    n = {p: sum(len(v) for f in d["classes"].values() for c in f.values() for s in c.values() for v in s["groups"].values()) for p, d in docs.items()}
    print(f"consensus literals: K {n['K']}, S {n['S']}; classes: {len(classes)}; random files: 5")
