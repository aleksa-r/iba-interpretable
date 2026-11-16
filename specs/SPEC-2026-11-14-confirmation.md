---
spec_id: SPEC-2026-11-14-confirmation
status: frozen     # frozen by Claude Code on 2026-11-15 on the owner's word (section 10), after the code review of section 9; no change after this without a new version
version: 2 (2026-11-15; version 1 plus the crisis-period table asked for by the owner and the changes of the code review, section 9)
fingerprint: 2bcaa0ad64aaa3ab35c5455d
xgb_hash: c6e501978f15890d889f6075
bench_hash: 6e8fef997182e116c313a365
authors: Aleksa Radosavčević; drafted by Claude Code
depends_on: specs/SPEC-2026-11-14-wrapup.md, specs/SPEC-2026-11-14-benchmarks-kpca-ae.md, docs/results/SPEC-2026-11-14-wrapup/SUMMARY.md, docs/protocol/EXTRA_METRICS.md
scope: CONFIRMATION series. The one run of the frozen final method on the series held out since the split of 2026-11-13.
---

# Confirmation run of the final method

## 0. What this is

The universe was split once, on 2026-11-13, into 48 development and 23 confirmation series,
stratified by asset class. Four specs were run on the development series, and every choice of the
method was made there: the representation, the elicited formula set, the estimator, the search
and its use as an ensemble. Development results can flatter a method whose choices were made on
them. The confirmation series have never been downloaded or loaded
(`ibanext.data.split.ConfirmationGuard` refuses them without a frozen spec id). This spec fixes,
before they are touched, what is run on them, what is claimed, and how each claim is decided. It
is run once, and its results are reported whatever they are.

## 1. Series and data

**21 series** (all daily, read weekly): US broad equity MDY, QQQ; US sectors XLB, XLF, XLK, XLU;
developed ex-US EWA, EWC, EWD, EWJ, EWS, EWU; emerging EWW, EWZ; government and investment-grade
bonds LQD, MUB, SHY; commodities DBP, USO, ^SPGSCI; real estate IYR.

**Not in the run: the two daily hedge-fund indices (SG CTA, SG Trend).** They were confirmation
series "if their download is obtainable" (owner's decision of 2026-11-13). Checked on 2026-11-14:
Société Générale's page offers no download of the daily history; full daily data is "on request"
through its Capital Consulting team or its SG Markets platform, and the page says the data is
"for information purposes only" and that to "reference the index returns" one must contact them.
Without that permission the series are not used. Consequences, to be stated in the paper:
- no hedge-fund series is confirmed (the 11 monthly CISDM indices are all development data);
- high-yield and emerging-market debt has no confirmation series (both its series are
  development data);
- every confirmation task is weekly.

**Download.** One dated Yahoo download of the 21 tickers (adjusted closes), made after the
freeze with this spec's id, hashed and recorded as the development download was. Weekly returns,
realised variance and daily log returns are built by the same code
(`ibanext.data.panel.build_weekly_targets`) on the index of the factor panel
`data/panels/weekly_2026-11-11` (956 weeks, 2008-06-06 to 2026-09-25; `factors.csv` sha256
`9fbee0db…06aff50`), which is not changed.

**Tasks.** Those of the wrap-up spec: return at 1, 4 and 13 weeks; log realised variance at 1, 4
and 13 weeks; large loss and large gain (10 %) at 4 and 13 weeks. 10 tasks × 21 series = 210
cells. Protocol, labels, folds, the 416-week test period and the estimators are unchanged.

**What kind of evidence this is.** The confirmation series cover the same calendar period as the
development series. They are a held-out cross-section, not a later period: they share the market
events of the development series and are correlated with them (QQQ with SPY, LQD with AGG). The
run can show that the results were not produced by choices fitted to particular series; it cannot
show that they hold in a period that no part of the study has seen.

## 2. The frozen method

Fixed by the rules of SPEC-2026-11-14-wrapup (`docs/results/SPEC-2026-11-14-wrapup/final_method.json`):
- **Formula set Kc**: `priors/llm/K_consensus.yaml`, sha256 `cc74b25c…63e81e`. One formula per
  group for each asset class and target, used for every series of the class and every horizon.
- **Interpretable reading (`Kc|lin`)**: the fixed formula with the linear model.
- **Accuracy reading (`iba_ca_b`)**: the colony of the class-pooled ABC, linear forecasts
  averaged, seeds 0–2. The colonies are those found on the DEVELOPMENT pools in stage 8 of the
  wrap-up run, per task, asset class and block origin
  (`artifacts/SPEC-2026-11-14-wrapup/stage8/prior_Kc`), applied unchanged to the confirmation
  series of the class at the same block origin. No search is run on a confirmation series. Each
  colony was found from rows admissible at its block origin, so the information rule holds for
  the confirmation forecasts as it did for the development ones. If a confirmation series does
  not share the block origins of its class's development pool, that is recorded as a deviation
  before the run and the series' accuracy reading is the no-search colony (`Kc_nb`).

Nothing is tuned, selected or re-fitted on confirmation results. The linear model's
regularisation is tuned per block on admissible rows, as always.

## 3. Benchmarks and controls (all run in the same cells)

- References: historical mean and trailing momentum; HAR, GARCH and GJR-GARCH; base rate, the
  volatility-based logit and the GARCH-based probability.
- Factor benchmarks with the linear model, LightGBM and XGBoost: raw factors, PCA, group PCA,
  LASSO, kernel PCA, the autoencoder (settings as in their specs).
- Controls: the generic formulas (G), the five random formula sets (R1–R5, read as their mean
  loss Rm), the no-search colony of Kc (`Kc_nb`) and the tested ABC winner of the development
  pools; Kc, G and the random sets also with LightGBM and XGBoost.

## 4. Claims (written before any confirmation number exists)

All tests per task, the 21 series pooled on the same dates, paired date-block bootstrap, 2 000
draws, block ≥ h, as in every earlier report. "Relative difference" = (loss of a − loss of b) /
loss of b.

**Primary claims.** Three; the family is controlled by Holm at 5 % on the bootstrap p-values of
P1 and P2, and P3 is decided by its own interval rule.
- **P1. Volatility at 1 week.** `Kc|lin` has a lower squared error of log realised variance than
  HAR. Development: −7.3 % (95 % interval −11.6 to −3.8).
- **P2. Volatility at 4 weeks.** The same. Development: −7.8 % (−15.7 to −2.7).
- **P3. Parity with group PCA.** `Kc|lin` is not worse than group PCA with the linear model by
  more than 3 % of the loss: the upper end of the 95 % interval of the relative difference is
  below +3 % in at least 9 of the 10 tasks, and group PCA is significantly better in none.
  (Development: differences between −1.7 % and +0.1 %, interval half-widths 0.6–1.8 % on 37
  series; with 21 series they will be wider.)

P1 and P2 are each CONFIRMED if the Holm-adjusted p-value is below 0.05 and the difference is
negative; otherwise NOT CONFIRMED. P3 is CONFIRMED or NOT CONFIRMED by its rule. These three
words are used in the report and the paper exactly as decided here.

**Secondary claims.** Reported with their intervals and the count of tasks, each marked as
"holds" or "does not hold" by the stated criterion; no multiplicity control, and none of them can
rescue a primary claim.
- S1. Volatility at 13 weeks: `Kc|lin` against HAR (development −2.5 %, just significant). No
  direction is claimed.
- S2. The accuracy reading is not worse than the interpretable one: better in more tasks than
  worse.
- S3. On volatility `Kc|lin` is better than PCA, than kernel PCA and than the autoencoder in at
  least 2 of the 3 horizons each.
- S4. Knowledge matters only where there is signal: Kc is better than Rm on volatility in at
  least 2 of 3 horizons, and not distinguishable from Rm in the 7 return and tail tasks (at most
  1 significant difference in either direction).
- S5. No factor method is significantly better than the reference in any return task or any
  large-loss task (IBA readings and the six factor benchmarks, linear model).
- S6. Kc and G are at parity: at most 1 of 10 tasks with a significant difference in either
  direction.
- S7. Trees do not help: for Kc, raw factors and group PCA, XGBoost and LightGBM are
  significantly worse than the linear model in more tasks than better.
- S8. Large gains: the volatility-based logit has the lower loss than `Kc|lin` in both large-gain
  tasks (the development finding against the method).

**Financial and classification measures** (`docs/protocol/EXTRA_METRICS.md`, unchanged). All of
them are computed and reported. Three are declared as secondary claims because the development
tables, which were descriptive, suggested them:
- S9. One-week 1 % value at risk from `Kc|lin` has a lower quantile loss than from HAR.
- S10. The long/flat rule on the one-week return forecast of `Kc|lin` has a higher Sharpe ratio
  than buy-and-hold in at least 15 of the 21 series (one-sided sign test at 5 %) and a smaller
  maximum drawdown in at least 15. Without transaction costs; the report also gives the Sharpe
  ratio after 10 basis points per switch.
- S11. As a classifier of large gains at the base-rate threshold, `Kc|lin` has a Matthews
  correlation below that of the volatility-based logit.
- S12. Crisis and drawdown periods (section 5 of the measures document: the fourth quarter of
  2018, the COVID-19 crash, 2022, and the 10 % drawdown state of each series): the loss against
  the reference in each period is reported for every method. The subsamples are short; no test
  is attached and no direction is claimed.

**Not claimed anywhere:** predictability of returns or of large losses; any advantage of a
searched single formula; any result for hedge-fund indices or for high-yield and emerging-market
debt.

## 5. Reporting

`scripts/make_confirmation_report.py`, written before the run and tested on synthetic cells
(claim rules on constructed cases; the whole report on cells laid out like the run), producing:
the decision of every claim of section 4; every configuration against the reference, group PCA
and `Kc|lin`; the loss against the reference by asset class (descriptive: 1 to 6 series per
class); the extra measures; and, next to each claim, the same quantity on the weekly development
series where a development report has it. Null and negative results are reported in the same tables as the others. Every
configuration is written to the registry with split `confirmation`.

## 6. One run

The guard is opened with this spec's id for the download and for the run, and nowhere else. The
run is started once. A cell that fails for a technical reason is re-run with the same code. No
code that affects a forecast or a test is changed after the first confirmation forecast exists;
if a defect makes that unavoidable, it is written to `docs/DEVIATIONS.md` first, with the numbers
obtained before the change kept in the report. Nothing learned from this run is used to change
the method and run it again on these series: after this run they are development data.

## 7. Machine

The run is made on the Mac. `fingerprint`, `xgb_hash` and `bench_hash` above must reproduce
before the first cell; the runner stops otherwise.

## 8. Compute

It cannot be measured on confirmation cells before the freeze. From the development timings
(about 75 s per cell for the benchmarks with three estimators, 20 s for kernel PCA and the
autoencoder, 5–10 s per formula set, plus GARCH): about 2.5 minutes per cell, 210 cells, roughly
9 core-hours, a little over an hour on 8 workers. No language-model request is made.

## 9. Built before the freeze (none of it touched a confirmation series)

Stage 11 and the task list (`ibanext.protocol.study`: 210 cells × 7 formula sets = 1,470 cell
runs); the guarded download and target panel (`scripts/download_confirmation.py`, refused until
this spec is frozen, as is every read of the confirmation panel); the development colonies read
for a confirmation series of the same class, with a check that a colony belongs to the same block
origin; the report script and its tests; the 10-basis-point variant of the long/flat rule; the
runner `scripts/run_confirmation.sh`.

A code review of the whole path was made on 2026-11-15, before the freeze. Its findings were
fixed and tested: the data guard now opens only for this spec's id and only when it is frozen;
daily log returns are taken between consecutive prices of each series (the development panel
rebuilds to identical files); the download is checked for coverage of the panel's period before
the panel is built and is never repeated; a claim whose comparison lacks one of its tasks is not
decided, and a comparison that lacks a task stops the report; series of a task must share their
forecast dates; the per-class table averages over tasks; forecasts are written atomically and a
cell whose forecasts exist is evaluated, not recomputed; references and benchmarks are
registered once per cell.

## 10. The owner's decisions (2026-11-14: "run with 21 series, use dev colonies, 3% is fine"; 2026-11-15: "please freeze, run what needs to be run")

1. **21 series, no hedge funds.** The run is made without the SG indices; Société Générale is not
   asked first.
2. **The accuracy reading on new series:** the development colonies applied unchanged (section 2).
3. **The primary claims** stand as written, with the 3 % margin for parity with group PCA.
4. Still open, and not part of this spec: whether to plan a later run of the same frozen method on
   data after September 2026.

## 11. Freeze

Frozen by Claude Code on the owner's word of 2026-11-15, after the code review the owner asked
for. Details decided by Claude Code and flagged in the report: the criteria of the secondary
claims, the named crisis periods and the drawdown threshold, the coverage check of the download.

## 12. Deviations

Appended to `docs/DEVIATIONS.md` before the deviating run; the count for this spec is written
into every registry row of the run.
