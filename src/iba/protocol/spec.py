"""Spec discipline, enforced: an experiment runs on real series only if its spec file is frozen,
committed and unmodified, and the fingerprint cell reproduces the value recorded at freeze."""
from __future__ import annotations

import os
import subprocess
from typing import Dict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def spec_path(spec_id: str) -> str:
    return os.path.join(REPO, "specs", f"{spec_id}.md")


def read_front_matter(spec_id: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    with open(spec_path(spec_id)) as fh:
        lines = fh.read().split("\n")
    if lines[0].strip() != "---":
        raise ValueError("spec has no front matter")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.split("#")[0].strip()
    return out


class SpecNotFrozen(RuntimeError):
    pass


def require_frozen(spec_id: str, check_fingerprint: bool = True) -> Dict[str, str]:
    fm = read_front_matter(spec_id)
    if fm.get("spec_id") != spec_id:
        raise SpecNotFrozen(f"{spec_id}: spec_id in the file is {fm.get('spec_id')}")
    if fm.get("status") != "frozen":
        raise SpecNotFrozen(f"{spec_id}: status is '{fm.get('status')}', not 'frozen' (a spec is frozen by its author before the run)")
    rel = os.path.relpath(spec_path(spec_id), REPO)
    tracked = subprocess.run(["git", "-C", REPO, "ls-files", "--error-unmatch", rel], capture_output=True)
    dirty = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", rel], capture_output=True, text=True)
    if tracked.returncode != 0 or dirty.stdout.strip():
        raise SpecNotFrozen(f"{spec_id}: the spec file must be committed and unmodified")
    if check_fingerprint:
        from ..eval.fingerprint import fingerprint
        got = fingerprint()
        if got != fm.get("fingerprint"):
            raise SpecNotFrozen(f"{spec_id}: fingerprint {got} differs from the spec's {fm.get('fingerprint')}; "
                                "this machine or environment does not reproduce the frozen computation")
    return fm
