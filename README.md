# iba-interpretable

Interpretable-by-construction factor reduction with Interpolative Boolean Algebra (IBA) for
forecasting the risk and performance of financial index time series.

Forecasts of index risk and return use many market and macroeconomic factors. The usual
reductions (PCA, LASSO, autoencoders) give features with no meaning of their own. Here every
feature is a short logical statement about one economic group of factors, for example

    broad dollar return is high  AND  USD/JPY return is NOT high

whose degree of truth, a number between 0 and 1, is computed with IBA. A linear model combines
about nine such statements. The statements are elicited from a large language model under a
knowledge cut-off; an artificial bee colony (ABC) search can refine them; a last step writes an
explanation of a forecast in which every number is checked against the model.

The Python package is `iba`.

## Installation

Python 3.11 and [uv](https://docs.astral.sh/uv/). The run scripts expect the environment at
`.venv` in the repository root.

```bash
git clone https://github.com/aleksa-r/iba-interpretable.git
cd iba-interpretable
uv venv .venv --python 3.11
uv pip install -e '.[dev,data,paper]'
.venv/bin/python -m pytest -n 4          # about 6 minutes; all tests should pass
```

Without uv: `python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev,data]'`.

### Dependencies

| Group | Packages | Needed for |
|---|---|---|
| core | numpy, pandas, scipy, scikit-learn, xgboost, lightgbm, arch, statsmodels, pyyaml, tabulate | the engine and every study |
| `dev` | pytest, hypothesis, pytest-xdist, ruff | tests |
| `data` | yfinance, requests, xlrd | downloading ETF prices; reading the BarclayHedge spreadsheets |
| `llm` | anthropic | eliciting formulas and writing explanations |
| `paper` | matplotlib, markdown | figures |

Versions used for the stored results: Python 3.11, NumPy 2.4, pandas 3.1, SciPy 1.17,
scikit-learn 1.9, LightGBM 4.7, XGBoost 3.2, arch 9.0. Numeric libraries are run
single-threaded (`OMP_NUM_THREADS=1`), one process per series.

### Keys (`.env`)

No key is needed to run the studies: all factor data are in the repository as CSV, so there is
no FRED or other data key. Only the two steps that call a language model need one. Copy
`.env.example` to `.env` (it is git-ignored) and set

```
ANTHROPIC_API_KEY=...
```

for `scripts/elicit_priors.py` (formulas) and `scripts/explain.py` (explanations). The formulas
used by the method are already stored under `priors/`, so these steps are optional.

## Data

| Data | Source | In the repository |
|---|---|---|
| Weekly factors | FRED, Kenneth French data library, Yahoo Finance | `data/panels/weekly_2026-11-11/` |
| Monthly factors | FRED, Kenneth French data library, Fung–Hsieh trend-following factors, one MSCI index | `data/panels/monthly_2026-11-11/factors.csv` |
| ETF and index series (weekly returns, realised variance) | Yahoo Finance, daily adjusted closes | `data/panels/weekly_dev_2026-11-13/`, `data/panels/weekly_confirmation/` |
| Hedge-fund strategy indices, development (monthly) | CISDM | **not included** (licensed) |
| Hedge-fund indices, confirmation (monthly) | BarclayHedge | **not included** (licensed) |

The hedge-fund index returns are licensed by their providers and are not redistributed. With
access to them, save the CISDM monthly returns as `data/panels/monthly_2026-11-11/targets.csv`
(first column `Date`, month ends; columns `CTA, CA, DS, ELS, EMN, EDMS, FIA, GM, MA, FOF, EWHF`)
and the BarclayHedge "historical data" spreadsheets under `data/raw/barclayhedge_2026_11/` with
the file names of `data/universe_hf_confirmation.yaml`; `scripts/ingest_barclayhedge.py --check`
verifies them. Without these files everything on the weekly series runs; the monthly
hedge-fund studies do not, and three tests are skipped.
`data/universe.yaml` and `data/split_manifest.json` define the series and the one-time split
into development and confirmation series.

## Reproduce the paper

```bash
.venv/bin/python scripts/reproduce_paper.py --check    # environment, engine hashes, data, stored results
.venv/bin/python scripts/reproduce_paper.py            # rebuilds the paper: paper/reduced/paper_full.md and the LaTeX project paper/reduced/overleaf/
.venv/bin/python scripts/reproduce_paper.py --full     # first re-runs every study whose results are missing
```

The paper is `paper/reduced/draft.md`; its tables are generated and inserted by the script, and
`paper/reduced/overleaf/template.tex` compiles with any LaTeX distribution (or on Overleaf:
upload `paper/reduced/overleaf.zip`). There are three levels of reproduction.

1. **From the stored reports (seconds).** A clone holds the report of every study
   (`docs/results/`) and the generated tables (`paper/results_tables.md`); the script assembles
   the paper from them.
2. **From the forecasts.** With the forecasts of the studies under `artifacts/` (2.3 GB, not in
   git; produced by level 3), every table and figure is recomputed, including the bootstrap
   intervals.
3. **From the data (`--full`, about 17 hours on 8 cores).** Every study is re-run from its
   frozen specification; a study whose results are present is not run again. The engine must
   first reproduce three hashes of a synthetic test case (`paper/paper.yaml`). The hedge-fund
   studies need the licensed data (see Data).

The requests to the language model are not repeated, because a new request gives a new text;
their records are under `priors/llm/`.

## Use

```python
import numpy as np
from iba.algebra.gbp import conjunction
from iba.algebra.predicates import PredicateScaler

z = np.random.default_rng(0).normal(size=(500, 2))      # trailing z-scores of two factors
x = PredicateScaler().fit(z[:400]).transform(z)         # "factor is high", in [0.01, 0.99], scaled on training rows
feature = conjunction(x, asserted=[0], negated=[1])     # "factor 0 is high AND factor 1 is NOT high" = x0 * (1 - x1)
```

A study is run from its frozen specification in `specs/`; the runner refuses a spec that is not
frozen and committed. Forecasts go to `artifacts/` (not stored here) and reports to
`docs/results/`.

```bash
bash scripts/run_all_stages.sh       # first development study: benchmarks, fixed formulas, exhaustive search, ABC
bash scripts/run_abc2.sh             # ABC over wider search spaces
bash scripts/run_abc3.sh             # pooled fitness per asset class, acceptance test, colony ensemble
bash scripts/run_wrapup.sh           # elicited, generic and random formulas; five search algorithms; the final method
bash scripts/run_kpca_ae.sh          # kernel PCA and autoencoder benchmarks
bash scripts/run_confirmation.sh     # the frozen method on the 21 held-out weekly series
bash scripts/run_confirmation_hf.sh  # the frozen method on the 23 held-out hedge-fund indices
```

The studies build on each other in this order and take about 17 hours on 8 cores in total.

## Layout

```
src/iba/
  algebra/      IBA: generalized Boolean polynomials, graded predicates
  protocol/     information rule, walk-forward evaluation, frozen-spec check, studies and stages
  models/       ridge and logistic regression, LightGBM, XGBoost; reducers (raw, PCA, group PCA, LASSO, kernel PCA, autoencoder, IBA); GARCH references
  search/       ABC, GA, PSO, SA, DE, exhaustive search; pooled fitness; acceptance test
  priors/       elicitation of formulas from a language model
  explain/      traces of a forecast, verified explanations, component ablations
  eval/         block bootstrap, SPA and MCS, financial and classification measures, trial registry, fingerprints
  data/         universe, development/confirmation split and guard, panels
scripts/        runs, reports, paper tables and figures, reproduce_paper.py
specs/          one dated, frozen specification per study
priors/         elicited formulas (every draw and rationale), consensus files, random controls
docs/protocol/  the manual given to the language model and the protocols of elicitation, explanation and domain measures
data/           universe, split manifest, panels
docs/results/   per study: SUMMARY.md, the pre-written report, tables of tests
paper/          the paper (reduced/draft.md), its configuration (paper.yaml), generated tables and figures
tests/          unit and property tests
```

Rules the code enforces: a row with features at the end of period j and a label over
j + 1 … j + h enters a fit, tuning, threshold or selection at forecast date t only if
j + h ≤ t (`protocol/information_rule.py`); development code cannot load a confirmation series
(`data/split.py`); every evaluated configuration is written to `registry/trials.jsonl`.

## Citation and licence

See `CITATION.cff`. Code: Apache License 2.0 (`LICENSE`).
