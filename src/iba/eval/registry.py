"""Trial registry: every evaluated configuration is logged, automatically, append-only.

A trial is (spec_id, split, config) -> metrics. The config is hashed (sha256 of its canonical
JSON) so the same configuration evaluated twice is visible as such. The paper reports the
count of trials per spec and corrects for it. Never edit ``registry/trials.jsonl`` by hand.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def config_hash(config: Dict[str, Any]) -> str:
    s = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _git_head(repo: str) -> Optional[str]:
    try:
        return subprocess.check_output(["git", "-C", repo, "rev-parse", "--short", "HEAD"],
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


class TrialRegistry:
    def __init__(self, path: str, repo: Optional[str] = None):
        self.path = path
        self.repo = repo or os.path.dirname(os.path.dirname(os.path.abspath(path)))
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    def record(self, spec_id: str, split: str, config: Dict[str, Any], metrics: Dict[str, Any],
               note: str = "") -> Dict[str, Any]:
        if split not in ("development", "confirmation", "smoke", "bridge"):
            raise ValueError(f"split must be development|confirmation|smoke|bridge, got {split}")
        row = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "spec_id": spec_id, "split": split, "config_hash": config_hash(config),
            "config": config, "metrics": metrics, "note": note,
            "git": _git_head(self.repo), "host": platform.node(),
        }
        with open(self.path, "a") as fh:
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
        return row

    def rows(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path) as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def count(self, spec_id: Optional[str] = None, split: Optional[str] = None) -> int:
        return sum(1 for r in self.rows() if (spec_id is None or r["spec_id"] == spec_id)
                   and (split is None or r["split"] == split))

    def distinct_configs(self, spec_id: Optional[str] = None) -> int:
        return len({r["config_hash"] for r in self.rows() if spec_id is None or r["spec_id"] == spec_id})
