---
spec_id: SPEC-2026-11-15-confirmation-hf
status: frozen     # frozen by Claude Code on 2026-11-15 on the owner's word (section 9), after the review of section 8; no change after this without a new version
version: 1 (2026-11-15; version 0 was a draft written before the data existed; this version is written with the files on disk and before any of them was used in a forecast)
fingerprint: 2bcaa0ad64aaa3ab35c5455d
xgb_hash: c6e501978f15890d889f6075
bench_hash: 6e8fef997182e116c313a365
authors: Aleksa Radosavčević; drafted by Claude Code
depends_on: specs/SPEC-2026-11-14-confirmation.md, specs/SPEC-2026-11-14-wrapup.md, docs/results/SPEC-2026-11-14-wrapup/SUMMARY.md, docs/protocol/EXTRA_METRICS.md
scope: CONFIRMATION series. One run of the frozen final method on monthly hedge-fund indices of a second provider.
---

# Confirmation of the hedge-fund results on BarclayHedge indices

## 0. What this is

The paper presents hedge-fund strategy indices as the institutional half of its data. The
confirmation run of SPEC-2026-11-14-confirmation had none: the 11 CISDM indices are all
development data. This spec runs the frozen final method once on monthly hedge-fund indices of
another provider, BarclayHedge, that were never used in this study.

On the development hedge-fund indices the method showed no advantage: no factor method was
better than the reference in any task, the interpretable reading was behind the historical mean
on returns, and tail events stayed at their base rate. The claims below are therefore about the
absence of an advantage and about parity, not about a gain. A confirmed absence is the expected
outcome and is what the paper would report.

## 1. Series and data

**Files.** On 2026-11-15 the owner downloaded by hand, with their own access, every BarclayHedge
index history they could find: 26 spreadsheets, saved unchanged under
`data/raw/barclayhedge_2026_11/` (not in git). Nothing was or will be fetched by a script; the
provider's terms forbid automated gathering. The 26 files, their codes and names are listed in
`data/universe_hf_confirmation.yaml`. The Barclay CTA Index named in version 0 is not among them.

**An extension, not part of the split.** These series were added after the one-time split of
2026-11-13. `data/universe.yaml` and `data/split_manifest.json` are unchanged. All 26 are
confirmation series of the asset class "hedge-fund strategy indices, monthly": the data guard
refuses them to development code and opens for them only under this spec, frozen and committed
(and under this spec it opens for them alone, not for the weekly confirmation series).

**Coverage rule (mechanical).** A series enters the run if its history has every month of the
monthly factor panel, January 2005 to September 2026. `scripts/ingest_barclayhedge.py --check`,
which reads the layout and the dates of each file and writes or prints no value of any series,
gives: 23 series enter (17 with history from 1997, 6 from 2002); 3 are left out because their
history starts in 2009 (Balanced, Emerging Markets MENA, Volatility Trading). The 23 include
sector and regional indices (Technology, Healthcare & Biotechnology, European and Pacific Rim
equities, five emerging-market regions) beside the strategy indices. All 23 are run; none is
selected or dropped by judgement. Thirteen of them are the indices named in version 0 of this
spec before any file existed; results for that subset are not reported separately. The catalogue
records the sha256 of every file and the 23 codes; the panel is written only if every file has
its recorded checksum and exactly these 23 pass the rule.

**Reading the files.** Each sheet has one row per year with twelve monthly returns and the
year's return. The parser checks every file against itself: the months of every year, the
incomplete year 2026 with its two estimates included, must compound to the year's stated return
(to rounding); the months must be contiguous; a month may appear once; a value written as text
must carry a per-cent sign. Otherwise the file is left out and reported, never repaired. The
check found all 26 files consistent in every year (30, 25 or 18 years each).

**The September 2026 value is the provider's estimate.** In every file the last two months
(September and October 2026) are marked as estimates. October is outside the panel. September is
used as published. Reason: the development colonies of the accuracy reading were selected on the
rows of the development panel, and the engine refuses a stored colony at a block origin with a
different number of rows; dropping September would shift every block by one month. The estimate
is the label of one of the 96 test forecasts of a task and series, at every horizon. Its scale is
verified by the 2026 yearly return of the same file. The check also confirms, without reporting
a value, that each of the 23 series gives every task the number of rows of a development
series, so that the stored colonies are admissible.

**What has been seen.** While the layout of the files was inspected, the yearly returns of two
indices for a few years (Balanced 2009 to 2012 and 2026; Convertible Arbitrage 1997 to 2000 and
2026) were printed. No monthly value, no forecast and no loss of any BarclayHedge series has
been computed or seen.

**Overlap with the development data.** A BarclayHedge index and the CISDM index of the same
strategy average many of the same funds. The run tests robustness to the provider and to the
construction of the index, and adds sector and regional indices; it is not a test on independent
series, and it covers the same years as the development data.

## 2. The frozen method

Unchanged from SPEC-2026-11-14-confirmation, in its monthly form:
- Formula set Kc (consensus of the five knowledge-only draws), asset class
  `hedge_fund_monthly`; every series gets that class's formulas.
- Interpretable reading `Kc|lin`: the consensus formulas with the linear model.
- Accuracy reading `iba_ca_b`: the average over the final ABC colony. The colonies are those
  found on the development hedge-fund pool in stage 8 of SPEC-2026-11-14-wrapup, read unchanged
  at the same block origins. No search, no tuning of any setting on the new series.
- Monthly protocol: test period the last 96 months, four blocks of 24, refit every month,
  minimum training sample 110 months, five validation folds of 18 months; information rule
  j + h ≤ t.
- Tasks: return at 1, 3, 6 and 12 months; large loss and large gain (10 % quantile) at 3 and 6
  months. 8 tasks × 23 series = 184 cells. No volatility target (monthly data).

## 3. Benchmarks and controls (in the same cells)

As in SPEC-2026-11-14-confirmation: raw factors, PCA, group PCA, LASSO, kernel PCA, autoencoder;
generic formulas (G) and five random formula sets (R1 to R5); each with the linear model, and
the IBA sets, raw factors and group PCA also with LightGBM and XGBoost; the no-search colony of
Kc; references: historical mean and time-series momentum for returns, base rate,
volatility-based logit and GARCH-based probability for tail events. Stage 12 of
`src/ibanext/protocol/study.py`.

## 4. Claims (written before any number of these series exists)

Relative difference in the primary loss, all 23 series pooled on the same dates, 95 % date-block
bootstrap per task, as in every other report. "Significantly" = the interval excludes zero.
Development values (11 CISDM indices, the same 8 tasks) are given for orientation.

**Primary.**
- H1. No factor method is significantly better than the reference (historical mean, base rate)
  in any of the 8 tasks. Factor methods: the two IBA readings and the six reductions, linear
  model. Development: none in any task. CONFIRMED if there is none.
- H2. Group PCA is significantly better than the interpretable reading in at most 1 of the 8
  tasks. Development: 1 (large loss at 6 months). CONFIRMED if the count is 0 or 1. The number
  of tasks in which the upper end of the interval is below +3 % of the loss is reported without
  a rule: on the development indices it was 4 of 8, so the parity margin of the weekly claims is
  not claimed here.

**Secondary** (hold or do not hold; they cannot rescue a primary claim).
- H3. The accuracy reading is significantly better than the interpretable one in more tasks
  than it is significantly worse. Development: 2 better, 0 worse.
- H4. Elicited formulas are at parity with generic and with random formulas: at most 1 task with
  a significant difference against each. "Random" is the mean loss of the five random sets, as
  in the other reports. Development: 0 and 0.
- H5. Trees do not help: in each of the six comparisons (XGBoost and LightGBM against the linear
  model, on Kc, on raw factors and on group PCA) the tree ensemble is significantly worse in
  more tasks than it is significantly better. Holds only if all six do.

**Reported without a rule.**
- H6. The interpretable reading against the reference by target (development: returns +2.9 %,
  large losses +0.1 %, large gains +0.9 %).
- The financial and classification measures of `docs/protocol/EXTRA_METRICS.md`: the long/flat
  rule (the indices are not investable, so it is a reading of the forecasts and not a strategy),
  the tail probabilities as a classifier, the crisis and drawdown periods. No claim rests on
  them.

**Not claimed:** predictability of hedge-fund returns or tail events; any advantage of the
method over group PCA; anything about volatility. H3 and H5 would also hold on series without
any structure, because averaging lowers the variance of a forecast and trees raise it; they say
how the estimators behave, not that the formulas find something.

A claim whose comparison lacks one of its tasks is not decided (primary: NOT RUN).

**Series that cannot be run.** If a cell of a series has no forecasts or no evaluation after the
second pass in any formula set, or holds a non-finite forecast, or lacks one of the three seeds
of a seeded configuration, that series is dropped from every task and every configuration. The
report names the dropped series and the reason, the drop is recorded in `docs/DEVIATIONS.md`,
and the claims are decided on the remaining series. If more than 3 of the 23 series are dropped,
no claim is decided.

## 5. Reporting

`scripts/make_confirmation_hf_report.py`, written before the run and rehearsed on the
development hedge-fund indices (`--rehearsal`, which reads no confirmation series), writes
`docs/results/SPEC-2026-11-15-confirmation-hf/`: the claims with their decisions, every
configuration against the reference, group PCA and the interpretable reading, the paired tests,
and the extra measures. The report is kept as produced. Results are reported whatever they are.

## 6. One run

`bash scripts/run_confirmation_hf.sh`, once: hashes of the machine, the panel built from the
spreadsheets (`data/panels/monthly_confirmation_bh/`, with a manifest of files, checksums,
coverage and the months marked as estimates), stage 12, a second pass that re-runs only cells
that failed for a technical reason, a count of the cells with forecasts and with an evaluation,
the report. The script stops if a step fails. A cell is never re-run because of its result.
Compute: 70 to 100 CPU-seconds per series and task, 184 cells, 30 to 40 minutes on 8 cores.

## 7. Built before the freeze (none of it used a value of a confirmation series)

- `data/universe_hf_confirmation.yaml`; guard, panel builder and parser
  (`src/ibanext/data/universe.py`, `panel.py`); stage 12 and its tasks
  (`src/ibanext/protocol/study.py`); asset class of the new codes (`models/reducers.py`).
- `scripts/ingest_barclayhedge.py`, `scripts/run_confirmation_hf.sh`,
  `scripts/make_confirmation_hf_report.py`; one robustness change in
  `scripts/make_extra_metrics.py` (a run without a volatility target).
- Tests: `tests/test_hf_confirmation.py` (parser on synthetic sheets, guard, stage and tasks).
- Checks: stage 12's configuration run on development hedge-fund cells reproduces the stored
  development forecasts exactly (fixed formula and colony: largest difference 0.0); the report
  code run on the development hedge-fund indices decides the claims as section 4 states their
  development values; the full test suite; the three hashes.
- `scripts/ingest_barclayhedge.py --check` on the 26 files: layout, coverage, the yearly
  consistency of every file, the rows each series gives the engine. It writes nothing.
- A review of the changes for logical errors before the freeze; its findings and what was done
  about them are listed in section 8.

## 8. Review before the freeze

An independent review of the changes (2026-11-15; it opened no raw file and ran only the layout
check, the tests, and experiments on synthetic and development data) found no error in the claim
logic, the stage or the alignment. Its findings, all acted on before the freeze:

| # | Finding | What was done |
|---|---|---|
| 1 | A series with one row fewer than the development panel (equal returns in its first two months give an undefined z-score) would fail every cell of the method's formula set, and the report would stop with no rule for what follows | The check now compares the rows of every series with the development panel's: all 23 agree. The rule for a series that cannot be run is written in section 4 and the report applies it |
| 2 | Nothing verified the scale of the September 2026 estimate: text without a per-cent sign was read as per cent, and the incomplete year was not checked against its yearly return | Text without a per-cent sign is refused; a year with estimates is checked against its stated return; all files pass |
| 3 | Nothing tied the built panel to the files and series of the spec; a missing spreadsheet reader would have produced an empty panel | Checksums of the 26 files and the 23 expected codes are in the catalogue and enforced at the build; the reader is imported before any file is opened; the report refuses a panel with other series |
| 4 | A non-finite forecast in one seed of a seeded configuration would shrink that configuration to fewer seeds without notice | The report checks every forecast of every cell for finiteness and every seeded configuration for its three seeds; a series that fails is dropped under the rule of section 4 |
| 5 | The texts of H3, H4 and H5 were looser than the code ("significantly", the meaning of "random", each of six comparisons) | The texts now state what the code does |
| 6 | The guard, once open for one confirmation run, let the series of the other through (no live path used it) | Each run opens the guard for its own series only; tested |
| 7 | The run script printed "ALL DONE" whatever happened and did not list cells that failed twice | Exit checks after every step; cells without forecasts or evaluation are counted and listed before the report |
| 8 | The development column of H1 in the report rests on five of the eight methods (the development reports hold no paired test for raw factors, PCA and LASSO on these tasks) | Left as it is; the rehearsal on all eight methods also gives none, which is the value section 4 states |
| 9 | The built panel of BarclayHedge returns would have gone into a release | Listed as licensed data in `paper/paper.yaml`; a release leaves it out |
| 10 | Parser: a numeric yearly return in per cent was not scaled; a second table on a sheet would overwrite the first; the number of years verified was not reported | Scaled; refused; reported by the check |
| 11 | H3 and H5 would also hold on series without structure | Said under "Not claimed" |
| 12 | Compute was under-estimated | Section 6 corrected |

## 9. Freeze

Frozen on 2026-11-15, 12:47, by Claude Code on the owner's word of the same day: "I added all BH
indices I could find. [...] Rewrite rerun and let me know when I can review before I send this
to supervisor". Before the freeze: the review of section 8 and its changes; the full test suite
(passes); the three hashes of the front matter (reproduced on this machine); the layout check on
the 26 files. No value of a BarclayHedge series has entered a forecast, a loss or a table.

## 10. Deviations

None so far. Anything that cannot be run as specified is recorded in `docs/DEVIATIONS.md` first.
