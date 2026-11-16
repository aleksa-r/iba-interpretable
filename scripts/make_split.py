"""Run ONCE: write data/split_manifest.json from data/universe.yaml. Refuses to overwrite."""
import json, os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from iba.data.split import stratified_split
from iba.data.universe import MANIFEST, UNIVERSE, file_sha256, load_universe

if os.path.exists(MANIFEST):
    sys.exit(f"{MANIFEST} exists: the split is made once and never redone")
series, cfg = load_universe()
m = stratified_split(series, salt=cfg["salt"], development_share=cfg["development_share"],
                     min_confirmation=cfg["min_confirmation"], forced_development=cfg["forced_development"])
d = json.loads(m.to_json())
d["universe_file_sha256"] = file_sha256(UNIVERSE)
d["created"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
d["note"] = ("One-time split, approved by the owner 2026-11-13. Confirmation series are never loaded by "
             "development code; the frozen final spec runs on them once.")
with open(MANIFEST, "w") as fh:
    json.dump(d, fh, indent=2, sort_keys=True)
n_dev = sum(len(v) for v in m.development.values()); n_conf = sum(len(v) for v in m.confirmation.values())
print(f"development {n_dev}, confirmation {n_conf}")
for k in m.development:
    print(f"{k:24s} dev {m.development[k]}\n{'':24s} conf {m.confirmation[k]}")
