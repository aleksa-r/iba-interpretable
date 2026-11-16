"""paper/paper_full.md -> paper/overleaf/ : a LaTeX project for Overleaf (elsarticle), laid out like the earlier one.

  .venv/bin/python scripts/build_paper.py && .venv/bin/python scripts/make_overleaf.py [--template DIR]

Writes template.tex (preamble, front matter and the text), one file per table (tab_<id>.tex) and per pseudo-code
(alg_<n>.tex), figures/, sample.bib and the class and style files. ``--template`` is the earlier Overleaf project
from which the class, the styles, the bibliography, the author block and the closing statements are taken; without
it the files already in paper/overleaf/ are kept. Tables, figures, sections and pseudo-codes are numbered by LaTeX:
every "Table 9", "Appendix C" of the text becomes a \\ref. The source of the paper stays paper/draft.md.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PAPER = os.path.join(ROOT, "paper")
OUT = os.path.join(PAPER, "overleaf")
COPY = ("elsarticle.cls", "elsarticle-num.bst", "model5-names.bst", "numcompress.sty", "algorithm.sty", "algorithmic.sty",
        "algorithmicx.sty", "algpseudocode.sty", "sample.bib")

UNI = {"−": r"\ensuremath{-}", "–": "--", "—": "---", "×": r"\ensuremath{\times}", "∏": r"\ensuremath{\prod}", "∈": r"\ensuremath{\in}",
       "·": r"\ensuremath{\cdot}", "←": r"\ensuremath{\leftarrow}", "→": r"\ensuremath{\rightarrow}", "Φ": r"\ensuremath{\Phi}",
       "φ": r"\ensuremath{\varphi}", "α": r"\ensuremath{\alpha}", "κ": r"\ensuremath{\kappa}", "λ": r"\ensuremath{\lambda}",
       "ℓ": r"\ensuremath{\ell}", "ŷ": r"\ensuremath{\hat{y}}", "≤": r"\ensuremath{\le}", "≥": r"\ensuremath{\ge}", "±": r"\ensuremath{\pm}",
       "…": r"\ldots{}", "\u00a0": "~", "ć": r"\'c", "č": r"\v{c}", "š": r"\v{s}", "ž": r"\v{z}", "’": "'", "“": "``", "”": "''", "§": r"\S{}"}
SUP = str.maketrans("⁻¹²³⁴⁵⁶⁷⁸⁹⁰", "-1234567890")
SUB = re.compile(r"(?<![\w/.])([A-Za-zΦφℓβσŷ∏∑]|loss)_(\{[^}\n]+\}|[A-Za-z0-9]{1,2})(?!\w|\.\w)")
ID = {"Table": r"[A-I]?\d+b?", "Figure": r"\d+", "Algorithm": r"\d+", "Section": r"\d+(?:\.\d+)?", "Appendix": r"[A-I]"}
PREFIX = {"Table": "tab", "Figure": "fig", "Algorithm": "alg", "Section": "sec", "Appendix": "app"}
CITE = [("(Fung and Hsieh, 2004)", r"\citep{Fung2004}"), ("(Radojevi\\'c, 2008)", r"\citep{Radojevic2008_1}"),
        ("(Hansen, 2005; ", r"(\citealp{Hansen2005}; "), ("Patton et al. (2019) \\textcolor{red}{[REF]}", r"\citet{Patton2019}"),
        ("Fissler--Ziegel joint loss \\textcolor{red}{[REF]}", r"Fissler--Ziegel joint loss \citep{Fissler2016}"),
        ("joint loss of Fissler and Ziegel", r"joint loss of \citet{Fissler2016}")]
BIB = r"""
@article{Fung2004,
  author = "Fung, W. and Hsieh, D. A.",
  title = "Hedge Fund Benchmarks: A Risk-Based Approach",
  journal = "Financial Analysts Journal",
  volume = "60", number = "5", pages = "65--80", year = "2004"
}

@article{Hansen2005,
  author = "Hansen, P. R.",
  title = "A Test for Superior Predictive Ability",
  journal = "Journal of Business \& Economic Statistics",
  volume = "23", number = "4", pages = "365--380", year = "2005"
}

@article{Patton2019,
  author = "Patton, A. J. and Ziegel, J. F. and Chen, R.",
  title = "Dynamic semiparametric models for expected shortfall (and Value-at-Risk)",
  journal = "Journal of Econometrics",
  volume = "211", number = "2", pages = "388--413", year = "2019"
}

@article{Fissler2016,
  author = "Fissler, T. and Ziegel, J. F.",
  title = "Higher order elicitability and Osband's principle",
  journal = "The Annals of Statistics",
  volume = "44", number = "4", pages = "1680--1707", year = "2016"
}
"""


def refs(text: str) -> str:
    """'Tables F1 and F2', 'Appendices C to G', 'Section 4.5' -> the same words with \\ref."""
    for kind, pat in ID.items():
        plural = "Appendices" if kind == "Appendix" else kind + "s"
        rx = re.compile(rf"\b({plural}|{kind})\s+({pat})((?:(?:,|\s+and|\s+to)\s+{pat})*)(?![\w.]*\w)" if kind != "Figure"
                        else rf"\b({plural}|{kind})\s+({pat})((?:(?:,|\s+and|\s+to)\s+{pat})*)(?=[a-c]?\b)")

        def one(m, kind=kind, pat=pat):
            word = "" if kind == "Appendix" else m.group(1) + "~"          # elsarticle's \ref of an appendix already says "Appendix"
            first = rf"{word}\ref{{{PREFIX[kind]}:{m.group(2)}}}"
            rest = re.sub(rf"(,|\s+and|\s+to)\s+({pat})", lambda k: f"{k.group(1)}~\\ref{{{PREFIX[kind]}:{k.group(2)}}}", m.group(3))
            return first + rest
        text = rx.sub(one, text)
    return text


def inline(s: str, cross: bool = True) -> str:
    keep: list[str] = []

    def hold(x: str) -> str:
        keep.append(x)
        return f"\x00{len(keep) - 1}\x00"
    tt = lambda m: hold(r"\texttt{" + re.sub(r"([_&%$#{}])", r"\\\1", m.group(1)).replace("/", r"/\allowbreak{}").replace("~", r"\textasciitilde{}") + "}")
    s = re.sub(r"`([^`]+)`", tt, s)
    s = s.replace("\\*", hold("*"))
    mth = lambda c: (UNI[c].replace(r"\ensuremath", "").strip("{}") + " ") if c in UNI else c
    s = SUB.sub(lambda m: hold(r"\ensuremath{" + (r"\mathrm{loss}" if m.group(1) == "loss" else mth(m.group(1)))
                               + "_{" + "".join(mth(c) for c in m.group(2).strip("{}")) + "}}"), s)
    s = re.sub(r"[⁻¹²³⁴⁵⁶⁷⁸⁹⁰]+", lambda m: hold(r"\ensuremath{^{" + m.group(0).translate(SUP) + "}}"), s)
    s = re.sub(r"(\d)\^([A-Za-z0-9])", lambda m: m.group(1) + hold(r"\ensuremath{^{" + m.group(2) + "}}"), s)
    s = re.sub(r"(?<![\w)\]])-(?=\d)", lambda m: hold(r"\ensuremath{-}"), s)      # a minus sign, not a hyphen
    s = s.replace("\\", r"\textbackslash{}")
    s = re.sub(r"([&%$#_{}])", r"\\\1", s).replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")
    s = s.replace(r"\textbackslash\{\}", r"\textbackslash{}")
    s = re.sub(r"(\d) \\%", r"\1\\,\\%", s)                     # a number and its per-cent sign stay together
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"(?<![\w*])\*(?=\S)([^*]+?)(?<=\S)\*(?![\w*])", r"\\emph{\1}", s)
    s = re.sub(r'"([^"]*)"', r"``\1''", s)
    s = re.sub(r"\[(REF|AUTHOR)([^\]]*)\]", lambda m: r"\textcolor{red}{[" + m.group(1) + m.group(2) + "]}", s)
    s = "".join(UNI.get(c, c) for c in s)
    if cross:
        s = refs(s)
    for a, b in CITE:
        s = s.replace(a, b)
    s = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)
    bad = sorted({c for c in s if ord(c) > 127})
    if bad:
        raise ValueError(f"characters without a LaTeX form: {bad} in: {s[:80]}")
    return s


def blocks(lines: list[str]) -> list[tuple[str, list[str]]]:
    out, cur, kind = [], [], None

    def flush():
        nonlocal cur, kind
        if cur:
            out.append((kind, cur))
        cur, kind = [], None
    item = re.compile(r"^(- |\d+\. )")
    for ln in lines:
        if not ln.strip():
            flush(); continue
        k = ("head" if ln.startswith("#") else "table" if ln.startswith("|") else "quote" if ln.startswith(">") else "image" if ln.startswith("![")
             else "list" if item.match(ln) or (kind == "list" and ln.startswith("  ")) else "para")
        if k != kind or k in ("head", "image"):
            flush(); kind = k
        cur.append(ln)
    flush()
    return out


def render_list(lines: list[str]) -> str:
    items, numbered = [], bool(re.match(r"^\d+\. ", lines[0]))
    for ln in lines:
        m = re.match(r"^(- |\d+\. )(.*)", ln)
        if m:
            items.append(m.group(2))
        else:
            items[-1] += " " + ln.strip()
    env = "enumerate" if numbered else "itemize"
    return f"\\begin{{{env}}}\n" + "\n".join(r"\item " + inline(i) for i in items) + f"\n\\end{{{env}}}\n"


NAMES = {"return": "Return", "logrv": "Volatility", "tail_loss": "Large loss", "tail_gain": "Large gain", "kind": "Target", "method": "Method",
         "claim": "Claim", "statement": "Statement", "result": "Result", "decision": "Decision", "class": "Asset class", "series": "Series"}
# layouts tried in order: (landscape, font size, characters that fit across the table)
COMPACT = False          # --compact: no landscape pages, single-spaced appendix
LAYOUTS = [(False, r"\small", 72), (False, r"\footnotesize", 82), (False, r"\scriptsize", 96), (True, r"\footnotesize", 126), (True, r"\scriptsize", 148)]


def render_table(lines: list[str], caption: str | None, label: str | None) -> str:
    """A table that can be read: every column is at least as wide as its longest word, numbers keep their sign and
    per-cent sign, and a table too wide for the page at a readable size is set in landscape."""
    rows = [[c.strip() for c in re.split(r"\s\|(?=\s|$)", ln.strip()[1:].rstrip().removesuffix("|"))] for ln in lines]   # a bar inside a cell has no space before it
    rows = [r for r in rows if not re.fullmatch(r"[ |:-]+", "|".join(r))]                                      # the rule under the header
    n = len(rows[0])
    rows = [[NAMES.get(c, c) for c in r] + [""] * (n - len(r)) for r in rows]
    tie = lambda c: re.sub(r"\(([^()]{1,24})\)", lambda m: "(" + m.group(1).replace(" ", "\u00a0") + ")", c)   # a bracket is not broken
    rows = [rows[0]] + [[tie(c) for c in r] for r in rows[1:]]
    rows[0] = [c[:1].upper() + c[1:] for c in rows[0]]
    rows = [rows[0]] + [[r[0][:1].upper() + r[0][1:]] + r[1:] for r in rows[1:]]                                # row names start with a capital
    plain = lambda c: re.sub(r"(\d) %", r"\1%", c).replace("**", "")
    wlen = lambda s: sum(1.45 if ch.isupper() else 1.0 for ch in s)                                            # capitals are wide
    longest = [max(wlen(plain(r[j])) for r in rows) for j in range(n)]
    need = [1.1 * (longest[j] if longest[j] <= 20 else max((wlen(w) for r in rows for w in plain(r[j]).split(" ")), default=1)) + 2.0
            for j in range(n)]                                                                                  # a short cell stays on one line; else the longest word
    want = [max(need[j], min(longest[j], 44) + 1.5) for j in range(n)]                                           # one line per cell, up to 44 characters
    main = COMPACT or (bool(label) and label.split(":")[1].isdigit())   # main-text tables (all tables when compact) stay in portrait, in a smaller font if need be
    for landscape, size, cap in ([l for l in LAYOUTS if not l[0]] if main else LAYOUTS):
        if sum(want) <= cap or (n <= 4 and sum(need) <= cap and sum(min(w, max(nd, 30)) for w, nd in zip(want, need)) <= cap):
            break
    else:
        if main and sum(need) > cap:                                # still too wide: let the longer cells wrap at their longest word
            need = [1.1 * max((wlen(w) for r in rows for w in plain(r[j]).split(" ")), default=1) + 2.0 for j in range(n)]
    spare = cap - sum(need)
    extra = [max(0.0, w - nd) for w, nd in zip(want, need)]
    share = min(1.0, spare / sum(extra)) if sum(extra) > 0 and spare > 0 else 0.0
    width = [nd + share * e for nd, e in zip(need, extra)]
    used = max(sum(width), 0.55 * cap)                       # a small table is not stretched over the whole line, nor squeezed
    frac = [(0.985 - 0.008 * n) * w / max(used, cap) * (used / sum(width)) for w in width]
    unit = "\\linewidth"
    numeric = [sum(bool(re.match(r"^[-+−–]?[\d.]", plain(r[j]))) or not r[j] for r in rows[1:]) >= 0.8 * (len(rows) - 1) and longest[j] <= 14 for j in range(n)]
    cols = "".join(rf">{{\{'raggedleft' if num and j else 'raggedright'}\arraybackslash}}p{{{f:.3f}{unit}}}" for j, (f, num) in enumerate(zip(frac, numeric)))
    head = " & ".join(r"\textbf{" + inline(c) + "}" if c else "" for c in rows[0]) + r" \\"
    body = "\n".join(" & ".join(inline(c) for c in r) + r" \\" for r in rows[1:])
    cap_tex = (rf"\caption{{{caption}}}\label{{{label}}}\\" + "\n") if caption else ""
    tex = (f"{{{size}\\setlength{{\\tabcolsep}}{{4pt}}\\renewcommand{{\\arraystretch}}{{1.2}}\n\\begin{{longtable}}{{@{{}}{cols}@{{}}}}\n{cap_tex}"
           f"\\toprule\n{head}\n\\midrule\n\\endfirsthead\n\\toprule\n{head}\n\\midrule\n\\endhead\n\\bottomrule\n\\endlastfoot\n{body}\n\\end{{longtable}}}}\n"
           + ("" if caption else "\\addtocounter{table}{-1}\n"))
    return ("\\begin{landscape}\n" + tex + "\\end{landscape}\n") if landscape else tex


def render_quote(lines: list[str]) -> tuple[str, str | None]:
    """A block quote: a pseudo-code (returns its file name) or a plain quotation."""
    inner = [re.sub(r"^> ?", "", ln) for ln in lines]
    m = re.match(r"\*\*Algorithm (\d+)\. (.*?)\*\*\s*(.*)", inner[0])
    body = []
    for kind, bl in blocks(inner[1:] if m else inner):
        body.append(render_list(bl) if kind == "list" else inline(" ".join(x.strip() for x in bl)) + "\n")
    if not m:
        return "\\begin{quote}\n" + "\n".join(body) + "\\end{quote}\n", None
    title = inline(m.group(2), cross=False) + ((" " + inline(m.group(3))) if m.group(3) else "")
    tex = (f"\\begin{{algorithm}}[H]\n\\caption{{{title}}}\\label{{alg:{m.group(1)}}}\n\\small\n" + "\n".join(body) + "\\end{algorithm}\n")
    return tex, f"alg_{m.group(1)}"


def convert(md: str, out: str) -> tuple[str, str, str, str]:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    title = abstract = keywords = ""
    tex: list[str] = []
    pending_tab: tuple[str, str] | None = None
    pending_img: str | None = None
    appendix = False
    for kind, bl in blocks(md.split("\n")):
        text = " ".join(x.strip() for x in bl)
        if kind == "head":
            level, name = re.match(r"^(#+)\s+(.*)", bl[0]).groups()
            if level == "#":
                title = inline(name, cross=False); continue
            if name.strip() == "Appendix":
                appendix = True; tex.append("\\appendix\n" + ("\\renewcommand{\\baselinestretch}{1.0}\\small\n" if COMPACT else "")); continue
            m = re.match(r"^(\d+(?:\.\d+)?|[A-I])\.?\s+(.*)", name)
            num, name = m.groups()
            cmd = "section" if (appendix or "." not in num) else "subsection"
            tex.append(f"\\{cmd}{{{inline(name, cross=False)}}}\\label{{{'app' if appendix else 'sec'}:{num}}}\n")
            if appendix:
                tex.append("\\setcounter{table}{0}\n")
        elif kind == "image":
            pending_img = re.match(r"!\[.*?\]\((.*?)\)", bl[0]).group(1)
        elif kind == "table":
            body = render_table(bl, *(pending_tab or (None, None)))
            if pending_tab:
                name = "tab_" + pending_tab[1].split(":")[1]
                open(os.path.join(out, name + ".tex"), "w").write(body)
                tex.append(f"\\input{{{name}}}\n")
            else:
                last = [x for x in os.listdir(out) if x.startswith("tab_")]
                name = sorted(last, key=lambda x: os.path.getmtime(os.path.join(out, x)))[-1]
                open(os.path.join(out, name), "a").write("\n" + body)
            pending_tab = None
        elif kind == "quote":
            body, name = render_quote(bl)
            if name:
                open(os.path.join(out, name + ".tex"), "w").write(body)
                tex.append(f"\\input{{{name}}}\n")
            else:
                tex.append(body)
        elif kind == "list":
            tex.append(render_list(bl))
        else:
            m = re.match(r"^\*\*Table ([A-I]?\d+b?)\.\s*(.*?)\*\*\s*(.*)$", text)
            f = re.match(r"^\*\*Figure (\d+)\.\*\*\s*(.*)$", text)
            if text.startswith("**Abstract.**"):
                abstract = inline(text[len("**Abstract.**"):].strip())
            elif text.startswith("**Keywords:**"):
                keywords = r" \sep ".join(inline(k.strip().rstrip(".")) for k in text[len("**Keywords:**"):].split(";"))
            elif m:
                cap = inline(m.group(2).rstrip(".") + "." + ((" " + m.group(3)) if m.group(3) else ""))
                pending_tab = (cap, f"tab:{m.group(1)}")
            elif f and pending_img:
                stem = os.path.splitext(os.path.basename(pending_img))[0]
                tex.append(f"\\begin{{figure}}[htbp]\n\\centering\n\\includegraphics[width=\\linewidth]{{{stem}}}\n"
                           f"\\caption{{{inline(f.group(2))}}}\\label{{fig:{f.group(1)}}}\n\\end{{figure}}\n")
                pending_img = None
            elif re.fullmatch(r"\*\*[^*]+\*\*", text):
                tex.append("\\medskip\\noindent " + inline(text) + "\n")
            else:
                tex.append(inline(text) + "\n")
    return title, abstract, keywords, "\n".join(tex)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", help="the earlier Overleaf project (class, styles, sample.bib, template.tex with the author block)")
    ap.add_argument("--compact", action="store_true", help="every table in portrait and the appendix single-spaced, to save pages")
    ap.add_argument("--dir", help="folder with paper_full.md; overleaf/ and overleaf.zip are written there (default: paper/). "
                                  "Class, styles, bibliography, author block and statements are taken from paper/overleaf/ unless --template is given")
    a = ap.parse_args()
    global PAPER, OUT, COMPACT
    COMPACT = a.compact
    FIGS, BASE = os.path.join(PAPER, "figures"), OUT
    if a.dir:
        PAPER = os.path.abspath(a.dir); OUT = os.path.join(PAPER, "overleaf")
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith(("tab_", "alg_")):
            os.remove(os.path.join(OUT, f))
    if OUT != BASE and not a.template and os.path.isdir(BASE):      # without paper/overleaf/ the files already in the target are used
        for f in COPY + ("frontmatter_authors.tex", "statements.tex"):
            shutil.copy2(os.path.join(BASE, f), os.path.join(OUT, f))
    if a.template:
        for f in COPY:
            shutil.copy2(os.path.join(a.template, f), os.path.join(OUT, f))
        old = open(os.path.join(a.template, "template.tex")).read()
        front = old[old.index(r"\begin{frontmatter}"):old.index(r"\begin{abstract}")]
        back = old[old.index(r"\section*{CRediT"):old.index(r"\bibliography{")]
        open(os.path.join(OUT, "frontmatter_authors.tex"), "w").write(front)
        open(os.path.join(OUT, "statements.tex"), "w").write(back)
        bib = open(os.path.join(OUT, "sample.bib")).read()
        open(os.path.join(OUT, "sample.bib"), "w").write(bib.rstrip("\n") + "\n" + "".join(
            "\n" + e.strip() + "\n" for e in BIB.strip().split("\n\n") if re.search(r"@\w+\{(\w+),", e).group(1) + "," not in bib))
    source = open(os.path.join(PAPER, "paper_full.md")).read()
    for f in os.listdir(os.path.join(OUT, "figures")):
        os.remove(os.path.join(OUT, "figures", f))
    for stem in re.findall(r"!\[.*?\]\(figures/([\w-]+)\.\w+\)", source):       # the figures the text uses, as PDF
        shutil.copy2(os.path.join(FIGS, stem + ".pdf"), os.path.join(OUT, "figures", stem + ".pdf"))
    title, abstract, keywords, body = convert(source, OUT)
    front = open(os.path.join(OUT, "frontmatter_authors.tex")).read()
    front = re.sub(r"\\textbf\{\\large .*?\}\n", lambda m: "\\textbf{\\large " + title + "}\n", front, count=1, flags=re.S)
    pre = r"""\documentclass[review]{elsarticle}
\graphicspath{ {./figures/} }
\usepackage{algorithm}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{array}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{pdflscape}
\usepackage{float}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{hyperref}
\setlist{nosep}
\floatstyle{plaintop}
\restylefloat{table}

\journal{Expert Systems with Applications}

\bibliographystyle{model5-names}\biboptions{authoryear}

\begin{document}

"""
    tex = (pre + front + "\\begin{abstract}\n" + abstract + "\n\\end{abstract}\n\n\\begin{keyword}\n" + keywords + "\n\\end{keyword}\n\n\\end{frontmatter}\n\n"
           + body + "\n\\input{statements}\n\n\\bibliography{sample}\n\n\\end{document}\n")
    open(os.path.join(OUT, "template.tex"), "w").write(tex)
    zp = os.path.join(PAPER, "overleaf.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, names in os.walk(OUT):
            for n in sorted(names):
                if not n.endswith((".aux", ".log", ".out", ".bbl", ".blg", ".spl", ".pdf")) or root.endswith("figures"):
                    z.write(os.path.join(root, n), os.path.relpath(os.path.join(root, n), OUT))
    print(f"{os.path.relpath(OUT, ROOT)}: template.tex, {len([f for f in os.listdir(OUT) if f.startswith('tab_')])} table files, "
          f"{len([f for f in os.listdir(OUT) if f.startswith('alg_')])} pseudo-codes, {len(os.listdir(os.path.join(OUT, 'figures')))} figures; {os.path.relpath(zp, ROOT)}")


if __name__ == "__main__":
    main()
