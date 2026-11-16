"""The target panel of SPEC-2026-11-15-confirmation-hf from the BarclayHedge spreadsheets (data/raw/barclayhedge_2026_11).

  .venv/bin/python scripts/ingest_barclayhedge.py --check     # layout and coverage of every file; no value of any series is written or printed
  .venv/bin/python scripts/ingest_barclayhedge.py             # builds data/panels/monthly_confirmation_bh/ (refuses unless the spec is frozen and committed)

A series enters if its history has every month of the monthly factor panel (January 2005 to September 2026).
The spreadsheets were downloaded by hand by the owner; nothing is fetched here."""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from iba.data.panel import HF_TARGETS, build_monthly_hf_targets
from iba.data.universe import HF_CONFIRMATION_SPEC, REPO

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = os.path.join(REPO, "data", "panels", HF_TARGETS)
    if not a.check and os.path.exists(os.path.join(out, "manifest.json")):
        sys.exit("the panel exists: it is built once")
    man = build_monthly_hf_targets(out, confirmation_run=None if a.check else HF_CONFIRMATION_SPEC, check_only=a.check)
    rows = man["rows_as_development"]
    for r in man["files"]:
        print(f"{r['code']:8s} {'IN ' if r['included'] else 'OUT'} {r.get('first', '?')} .. {r.get('last', '?')}  months {r.get('months', '?'):>4}  "
              f"scale {r.get('scale', '?')}  years checked against their YTD {r.get('years_verified', '?')} (without one: {len(r.get('years_unverified', []))})  "
              f"estimates in the panel: {', '.join(r.get('estimated_in_panel', [])) or 'none'}  "
              + (f"rows per task as in development: {'yes' if rows[r['code']] else 'NO'}  " if r["code"] in rows else "") + r["reason"])
    if not all(rows.values()):
        print("series whose rows differ from the development panel's:", [c for c, ok in rows.items() if not ok])
    print(f"{len(man['series'])} of {len(man['files'])} series enter; panel {man['first']} .. {man['last']} ({man['months']} months)"
          + ("" if a.check else f"; written to {os.path.relpath(out, REPO)}"))
