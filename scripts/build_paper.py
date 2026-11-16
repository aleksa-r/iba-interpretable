"""Assemble the paper: paper/draft.md with every marker <!-- T: key --> replaced by the generated table whose
heading starts with that key (paper/results_tables.md: '## Table 10.', '## Table 14 (Development).';
paper/appendix_tables.md: '## series'). A marker without a table is left in place and reported.

  .venv/bin/python scripts/build_paper.py     # writes paper/paper_full.md"""
import os, re

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper")


def sections(path):
    out, key = {}, None
    if not os.path.exists(path):
        return out
    for line in open(path).read().split("\n"):
        if line.startswith("## "):
            key = line[3:].strip(); out[key] = []
        elif key is not None:
            out[key].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def pick(table, blocks):
    """Of a generated table with several parts ("**Development, weekly**", ...), keep the parts whose heading starts with one of ``blocks``."""
    parts, cur = [], None
    for chunk in table.split("\n\n"):
        m = re.match(r"^\*\*([^*]+)\*\*$", chunk.strip())
        if m:
            cur = m.group(1)
        elif chunk.strip().startswith("|") and cur is not None and any(cur.startswith(b) for b in blocks):
            parts.append(chunk if len(blocks) == 1 else f"**{cur}**\n\n{chunk}")
    return "\n\n".join(parts)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=P, help="folder with draft.md; paper_full.md is written there (default: paper/)")
    a = ap.parse_args()
    D = os.path.abspath(a.dir)
    tabs = {**sections(os.path.join(P, "results_tables.md")), **sections(os.path.join(P, "appendix_tables.md"))}
    text = open(os.path.join(D, "draft.md")).read()
    missing = []

    def sub(m):
        key, _, blocks = m.group(1).partition("::")              # "key :: part; part" keeps only those parts of the table
        key = key.strip()
        hit = [k for k in tabs if k == key or k.startswith(key)]
        if not hit:
            missing.append(key); return m.group(0)
        out = pick(tabs[hit[0]], [b.strip() for b in blocks.split(";")]) if blocks.strip() else tabs[hit[0]]
        if not out:
            missing.append(m.group(1))
        return out or m.group(0)

    full = re.sub(r"<!-- T: (.*?) -->", sub, text)
    open(os.path.join(D, "paper_full.md"), "w").write(full)
    body = re.sub(r"<!--.*?-->", "", full, flags=re.S)
    main = body.split("## Appendix")[0]
    prose = lambda t: len(" ".join(l for l in t.split("\n") if not l.startswith("|")).split())
    print(f"{os.path.relpath(os.path.join(D, 'paper_full.md'), os.path.join(P, '..'))} written; main text {prose(main)} words of prose, appendix {prose(body[len(main):])}; markers without a table: {missing or 'none'}")
