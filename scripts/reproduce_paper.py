"""Reproduce the paper from this repository, as configured in paper/paper.yaml. By default the reduced, submitted
version (paper/reduced/): its text with every table, and the LaTeX project.

  .venv/bin/python scripts/reproduce_paper.py            # rebuild tables, figures and the paper from the stored results
  .venv/bin/python scripts/reproduce_paper.py --check    # environment, hashes, data and which results are present; builds nothing
  .venv/bin/python scripts/reproduce_paper.py --full     # first run every study whose results are missing (about 17 hours on 8 cores)
  .venv/bin/python scripts/reproduce_paper.py --full --dry-run   # print what --full would run

Three levels, from cheap to complete:
1. Without `artifacts/` (a fresh clone): the tables and reports under paper/ and docs/results/ are assembled
   into the paper; nothing is recomputed.
2. With `artifacts/` (the stored forecasts, see README): every table and figure is recomputed from the forecasts.
3. `--full`: the forecasts themselves are recomputed from the data by the frozen specifications. A study whose
   results are present is never run again; the steps that call a language model are never repeated unless
   `--with-language-model` is given, because a new request gives a new text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PY = sys.executable


def say(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd: list[str] | str, dry: bool) -> int:
    shown = cmd if isinstance(cmd, str) else " ".join(cmd)
    say(("would run: " if dry else "run: ") + shown)
    if dry:
        return 0
    return subprocess.call(cmd, cwd=REPO, shell=isinstance(cmd, str))


def has(path: str) -> bool:
    return os.path.exists(os.path.join(REPO, path))


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_environment(cfg: dict) -> bool:
    """Versions and the three hashes of the synthetic test case. False if a hash differs."""
    import importlib.metadata as md
    say(f"python {sys.version.split()[0]} (paper: {cfg['engine']['python']}); " + ", ".join(
        f"{p} {md.version(p)}" for p in ("numpy", "pandas", "scipy", "scikit-learn", "lightgbm", "xgboost", "arch")))
    sys.path.insert(0, os.path.join(REPO, "src"))
    import warnings
    warnings.filterwarnings("ignore")
    from iba.eval.fingerprint import fingerprint, fingerprint_benchmarks, fingerprint_xgb
    got = {"fingerprint": fingerprint(), "xgb_hash": fingerprint_xgb(), "bench_hash": fingerprint_benchmarks()}
    same = True
    for k, v in got.items():
        ok = v == cfg["engine"][k]
        same &= ok
        say(f"{k}: {v} " + ("(as in the paper)" if ok else f"DIFFERS from the paper's {cfg['engine'][k]}"))
    if not same:
        say("a hash differs: stored results can still be rebuilt into the paper; a re-run would not be bit-identical")
    return same


def check_data() -> bool:
    """The panels against the checksums in their manifests."""
    ok = True
    for name in ("weekly_dev_2026-11-13", "weekly_confirmation"):
        d = os.path.join(REPO, "data", "panels", name)
        m = os.path.join(d, "manifest.json")
        if not os.path.exists(m):
            say(f"data: panel {name} is missing"); ok = False
            continue
        for fname, want in json.load(open(m)).get("sha256", {}).items():
            p = os.path.join(d, os.path.basename(fname))
            good = os.path.exists(p) and sha256(p) == want
            ok &= good
            if not good:
                say(f"data: {name}/{os.path.basename(fname)} is missing or differs from its manifest")
    for f in ("data/panels/weekly_2026-11-11/factors.csv", "data/panels/monthly_2026-11-11/factors.csv", "data/panels/monthly_2026-11-11/targets.csv",
              "data/panels/monthly_confirmation_bh/returns.csv"):
        if not has(f):
            licensed = f.endswith(("targets.csv", "monthly_confirmation_bh/returns.csv"))
            say(f"data: {f} is missing" + (" (licensed hedge-fund indices: see README, Data)" if licensed else "")); ok = False
    say("data: panels present and equal to their manifests" if ok else "data: incomplete (see above)")
    return ok


def check_studies(cfg: dict) -> list[dict]:
    missing = []
    for s in cfg["studies"]:
        present = has(s["done"])
        stored = has(os.path.join("artifacts", s["spec"])) or not s["spec"].startswith("SPEC-")
        say(f"study {s['spec']}: results {'present' if present else 'MISSING'}" + ("" if stored else "; forecasts (artifacts/) not present"))
        if not present:
            missing.append(s)
    return missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report the state of the environment, data and results; build nothing")
    ap.add_argument("--full", action="store_true", help="run every study whose results are missing before building the paper")
    ap.add_argument("--dry-run", action="store_true", help="print the commands instead of running them")
    ap.add_argument("--with-language-model", action="store_true", help="with --full: also repeat elicitation and explanations (needs ANTHROPIC_API_KEY; gives new texts)")
    ap.add_argument("--no-render", action="store_true", help="skip the HTML/PDF reading copy (full version)")
    ap.add_argument("--version", choices=["reduced", "full"], default="reduced",
                    help="reduced: the submitted paper in paper/reduced/ (default); full: the long version in paper/, where its draft is present")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(os.path.join(REPO, "paper", "paper.yaml")))

    say("1. environment"); same = check_environment(cfg)
    say("2. data"); data_ok = check_data()
    say("3. stored results"); missing = check_studies(cfg)
    artifacts = has("artifacts") and any(has(os.path.join("artifacts", s["spec"])) for s in cfg["studies"])
    if a.check:
        say("forecasts (artifacts/): " + ("present: tables and figures can be recomputed" if artifacts else "absent: the paper is assembled from the stored tables"))
        return 0 if not missing else 1

    if a.full:
        if not same and not a.dry_run:
            say("stop: --full needs the hashes of the paper (see step 1)"); return 1
        if not data_ok and not a.dry_run:
            say("stop: --full needs the complete data (see step 2)"); return 1
        if a.with_language_model:
            lm = cfg["language_model"]
            for cmd in lm["elicitation"]["run"]:
                if run(cmd, a.dry_run):
                    return 1
        hours = sum(s["hours"] for s in missing)
        say(f"4. studies to run: {len(missing)} of {len(cfg['studies'])}" + (f", about {hours:.0f} hours on 8 cores" if missing else " (all results are present; nothing is run again)"))
        for s in missing:
            say(f"--- {s['spec']} ({s['role']}): {s['what']}")
            for cmd in s["run"]:
                if run(cmd, a.dry_run):
                    say(f"stop: {cmd} failed"); return 1
        if a.with_language_model:
            for cmd in cfg["language_model"]["explanations"]["run"]:
                if run(cmd, a.dry_run):
                    return 1
        artifacts = artifacts or bool(missing)
    elif missing:
        say("stop: results of " + ", ".join(s["spec"] for s in missing) + " are missing; use --full to run them"); return 1

    say("5. the paper")
    build = cfg["build" if a.version == "full" else "build_reduced"]
    if not has(build["source"]):
        say(f"stop: {build['source']} is not in this copy of the repository"); return 1
    for step in build["steps"]:
        if step["needs_artifacts"] and not artifacts:
            say(f"{step['name']}: kept as stored ({step['writes']}); recomputing needs artifacts/")
            continue
        if step.get("optional") and a.no_render:
            continue
        code = run([PY] + step["run"].split(), a.dry_run)
        if code and not step.get("optional"):
            say(f"stop: {step['run']} failed"); return 1
        if code:
            say(f"{step['name']}: skipped (needs the `paper` extra and, for the PDF, Chrome)")
    say("done: " + build["steps"][-2]["writes"] if a.version == "full" else "done: paper/reduced/paper_full.md and the LaTeX project paper/reduced/overleaf/ (template.tex)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
