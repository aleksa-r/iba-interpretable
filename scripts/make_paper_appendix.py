"""Static appendix tables of the paper (data, factor dictionary, elicited formulas); nothing is fitted or evaluated.

  .venv/bin/python scripts/make_paper_appendix.py     # writes paper/appendix_tables.md (sections marked '## <name>')"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import pandas as pd, yaml
from iba.data.universe import load_manifest, load_universe
from iba.priors import elicit as E
from iba.protocol.study import confirmation_series

REPO = E.REPO
GROUP = {"IR": "Interest rates", "B": "Credit", "V": "Volatility", "AP": "Equity factors", "TF": "Trend-following", "ST": "Styles", "FX": "Currencies",
         "COM": "Commodities", "MC": "Macro-financial conditions", "ENDG": "Own behaviour"}
CLASS = {"equity_us_broad": "US equity, broad", "equity_us_sectors": "US equity, sectors", "equity_developed_exus": "Developed markets ex-US", "equity_emerging": "Emerging markets",
         "bonds_gov_ig": "Government and investment-grade bonds", "credit_em_debt": "High-yield and emerging-market debt", "commodities": "Commodities", "real_estate": "Real estate",
         "hedge_fund_monthly": "Hedge-fund strategy indices (monthly)"}
SOURCE = {"fred": "FRED", "ken_french": "Kenneth French data library", "yahoo": "market prices (Yahoo Finance)", "fung_hsieh": "Fung–Hsieh trend-following factors", "msci": "MSCI"}


def main():
    out = []
    series, _ = load_universe(); m = load_manifest(); conf = set(confirmation_series())
    from iba.data.universe import load_hf_catalogue
    from iba.protocol.study import hf_confirmation_series
    names = {s["code"]: s["name"] for s in load_hf_catalogue()["series"]}
    hf = {c: names[c] for c in hf_confirmation_series()}          # empty until the hedge-fund confirmation panel exists
    rows = []
    for cls, name in CLASS.items():
        dev = sorted(m.development.get(cls, [])); cf = sorted(t for t in m.confirmation.get(cls, []) if t in conf)
        if cls == "hedge_fund_monthly" and hf:                     # the indices of the second provider, by name
            cf = ["BarclayHedge indices: " + ", ".join(sorted(hf[c].replace("Barclay ", "").replace(" Index", "") for c in hf))]
        rows.append([name, ", ".join(dev) or "–", ", ".join(cf) or "–"])
    out += ["## series", "", pd.DataFrame(rows, columns=["Asset class", "Development series", "Confirmation series"]).to_markdown(index=False), ""]
    for freq in ("weekly", "monthly"):
        d = pd.read_csv(os.path.join(REPO, "data", "panels", f"{freq}_2026-11-11", "factor_dictionary.csv"))
        t = pd.DataFrame({"Group": d.group.map(GROUP), "Factor": d.label, "Definition": d.description, "Source": d.source.map(SOURCE).fillna(d.source)})
        out += [f"## factors_{freq}", "", t.to_markdown(index=False), ""]
    lab = {f: {**dict(zip(E.load_dictionary(f)["code"], E.load_dictionary(f)["label"])), "__target__": "own recent behaviour"} for f in ("weekly", "monthly")}
    doc = yaml.safe_load(open(os.path.join(REPO, "priors", "llm", "K_consensus.yaml")))

    def words(lits, freq):
        return " AND ".join(f"{lab[freq][c]} {'high' if s == 'high' else 'NOT high'}" for c, s in lits)

    for freq, kind, title in (("weekly", "logrv", "formulas_volatility"), ("weekly", "return", "formulas_return"), ("monthly", "return", "formulas_hf_return")):
        classes = [c for c in CLASS if c in doc["classes"][freq]]
        groups = [g for g in GROUP if any(g in doc["classes"][freq][c][kind]["groups"] for c in classes)]
        rows = [[GROUP[g]] + [words(doc["classes"][freq][c][kind]["groups"].get(g, []), freq) or "–" for c in classes] for g in groups]
        out += [f"## {title}", "", pd.DataFrame(rows, columns=["Group"] + [CLASS[c] for c in classes]).to_markdown(index=False), ""]
    p = os.path.join(REPO, "paper", "appendix_tables.md")
    open(p, "w").write("\n".join(out)); print("written", os.path.relpath(p, REPO), len(out), "lines")


if __name__ == "__main__":
    main()
