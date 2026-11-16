---
spec_id: SPEC-2026-11-14-wrapup
status: frozen     # frozen by Claude Code on 2026-11-14 on the owner's agreement (section 9); no change after this without a new version
version: 1 (2026-11-14; the four owner decisions of 14 November and the owner's agreement to version 0; details by Claude Code)
fingerprint: 2bcaa0ad64aaa3ab35c5455d
xgb_hash: c6e501978f15890d889f6075
authors: Aleksa Radosavčević; drafted by Claude Code
depends_on: specs/SPEC-2026-11-14-abc-v3.md, docs/results/SPEC-2026-11-14-abc-v3/SUMMARY.md, docs/protocol/IBA_MANUAL.md, docs/protocol/PRIORS_LLM.md
scope: DEVELOPMENT series only. Last development spec before the confirmation run.
---

# Wrap-up: LLM-elicited priors, XGBoost, five search algorithms, the final method

## 0. Why

Three specs on the development series ended with the same picture: the IBA representation with a
fixed formula is at parity with group PCA, no search finds a formula that forecasts better than
the fixed prior, and averaging formulas next to the prior gains up to 0.7 %. Two things were
open. The prior itself was a generic set written by a Claude session after earlier results had
been seen, the same for every asset class and target. And the paper's protocol needs the
equal-budget comparison of the search algorithms on the fitness that worked best (pooled, with
the clean test), including differential evolution, the algorithm of the published IBA hybrids.

Owner decisions of 2026-11-14, which this spec carries out:
1. The prior formulas of the method are elicited from a language model under a written protocol
   (role, knowledge cut-off, manual), in two procedures: K knowledge only, S with simple
   statistics of the training sample. The generic formulas stay as a benchmark. The owner does
   not supply formulas.
2. XGBoost joins the estimators, without column sampling. An explanation step written by a
   language model follows the final method (not part of this spec's experiments).
3. Differential evolution joins the search comparison; ABC is the default on a tie.
4. The paper's structure (not part of this spec).

## 1. Questions and expectations (written before any result of this spec)

Q1 Priors. Do the elicited formulas forecast better than the generic ones, and than random
   formulas of the same shape? Does S (statistics-informed) differ from K (knowledge only)? How
   large is the spread between draws of one procedure compared with the difference between
   procedures?
Q2 Estimators. Does XGBoost on IBA features, on raw factors and on group PCA differ from
   LightGBM and from the linear model?
Q3 Search. At equal budget on the pooled fitness with the clean test, do ABC, GA, PSO, simulated
   annealing and DE differ in the gain on unused rows or in how often their winner passes the
   test? With the elicited prior as the starting point, does the ABC winner or the ABC colony
   beat the fixed prior and the no-search colony?
Q4 What is the final method that goes to the confirmation series?

Expected. The draws agree with each other moderately (mean pairwise agreement about 0.7) and
reverse about a third of the generic literals (`docs/protocol/PRIORS_LLM.md`, which reads no
outcome data), and the consensus formulas of the two procedures share under a third of their
literals, so the three sets are really different formulas. Even so, from the three
earlier studies the likely result is parity: differences to the generic prior under 1 % of the
loss, none on returns and tails where nothing has been predictable, possibly a small one on
volatility. An average of random formulas was 2 % worse than the generic prior on volatility in
the last study; the elicited ones should be at least as good as the generic there. XGBoost without
sampling should be level with LightGBM. The five algorithms should be indistinguishable (the
first comparison gave Friedman p = 0.63 for four of them). A null result on every question is an
acceptable outcome and is reported as such.

## 2. Data and cells

Development series only. The 458 cells and 18 tasks of SPEC-2026-11-14-abc-v2 (every return and
volatility cell; tails at q = 10 %). Protocol, labels, folds and the linear and LightGBM
estimators as SPEC-2026-11-13. Pools for the pooled fitness: each asset class (weekly: 8 classes
with 5, 8, 2, 8, 5, 3, 5 and 1 series; monthly: the 11 hedge-fund indices). The whole-frequency
pool is not used: with one formula set per asset class its members no longer share a prior.

## 3. Prior formulas (stage 7)

Elicitation is finished and documented before this spec is frozen: 95 requests to
`claude-opus-5-5` on 2026-11-14, five independent draws per procedure and asset class, every
record under `priors/llm/raw/` (prompt hash, response id, usage, answer). The model was told the
date is 30 September 2017, one month before the first forecast origin of any series. The
statistics of procedure S are rank correlations on rows admissible at the first forecast origin,
development series only. Limits that the paper must state: the cut-off cannot be enforced (the
model was trained on later data); `hedge_fund_daily` has no development series, so it has K
formulas only and uses them under either procedure.

Formula sets (each is one file in the per-asset-class layout; one formula per asset class and
target type, used for every series of the class and every horizon):

| set | what | files |
|---|---|---|
| G | the generic formulas of the earlier specs (incumbent benchmark) | 1 |
| K1 … K5 | the five draws of the knowledge-only procedure | 5 |
| S1 … S5 | the five draws of the statistics-informed procedure | 5 |
| Kc, Sc | consensus of a procedure: the literals given by more than half of its valid draws; if more than two remain in a group, the two with the most votes (ties: order of the factor dictionary) | 2 |
| R1 … R5 | random formulas: per asset class and target, in every group two distinct factors drawn uniformly with states drawn uniformly (the own-behaviour group: its one factor, random state); seeds 1–5 | 5 |

The files are `priors/llm/{K,S}_draw1..5.yaml`, `priors/llm/{K,S}_consensus.yaml` and
`priors/random/R_draw1..5.yaml` (`scripts/make_prior_files.py`; no outcome data is read), named in
`ibanext.protocol.study.PRIOR_SETS`. The S consensus file carries the K consensus for
`hedge_fund_daily`. Every set gives every development series a formula with at least three groups
(tested).

Readings per set P, all with the engine of the earlier specs:
- `P|lin`, `P|gbt`, `P|xgb`: the fixed formula with the linear model, LightGBM and XGBoost;
- `P_nb`: the no-search colony of SPEC-2026-11-14-abc-v3 (the formula and 19 random one- or
  two-move neighbours, linear forecasts averaged), seeds 0–2, for G, Kc and Sc only;
- derived in the report: `K@5` and `S@5`, the average of the five draws' linear forecasts, and
  `Rm`, the mean loss of the five random sets.

Stage 7 is 18 sets × 458 cells = 8,244 cell runs. G is run again here with all three estimators;
its linear forecasts must equal the first study's, and the report states the largest difference.

Benchmarks re-run once with the third estimator: raw factors, PCA, group PCA and LASSO with
`lin`, `gbt`, `xgb`; the references of each target type (historical mean, HAR, base rate, the
volatility-based tail model) come from the same runs.

## 4. XGBoost (`ibanext.models.estimators.XGBEstimator`)

No row sampling and no column sampling at any level, histogram method, one thread; grid and
shrinkage as the LightGBM estimator (depth 2 or 4, 100 or 300 rounds, learning rate 0.05,
λ = 1). Column sampling is the setting whose draws differed between the Dell and the Mac
(`docs/VERIFICATION.md`); without it the two machines agreed. The engine fingerprint does not
cover XGBoost, so XGBoost has its own hash of the fingerprint cell's forecasts
(`ibanext.eval.fingerprint.fingerprint_xgb`, recorded above as `xgb_hash`, measured on the Mac).
`scripts/run_wrapup.sh` stops if the machine does not reproduce it, and the confirmation run must
reproduce it on the machine it runs on.

## 5. Search comparison and the ABC readings (stages 8 and 9)

Run with the prior P* chosen by the rule of section 7.2.
- **Stage 8, five algorithms as search.** ABC, GA, PSO, simulated annealing and DE
  (`ibanext.search.algorithms`; DE/rand/1/bin, F = 0.5, CR = 0.9, population 20) on the pooled
  fitness of every asset-class pool, every task and block: anchored space (at most 4 status
  changes from P*, at most 3 literals per group), greedy replacement, budget 2 000 distinct
  formulas, 3 seeds, κ = 0.005, linear estimator; 88 pools × 4 blocks = 352 pool-blocks. GA, PSO
  and annealing are the comparators of the first study, unchanged; DE works on PSO's encoding
  made continuous. For each: gain of the winner on the fitness folds and on the clean outer
  rows, and whether it passes the one-standard-error test on the clean rows. No forecast is made
  from GA, PSO, annealing or DE.
- **Stage 9, forecasts from ABC.** The class-pooled anchored greedy arm of
  SPEC-2026-11-14-abc-v3 (`iba_ca`) with P*: tested winner, untested winner and colony ensemble,
  3 seeds, linear estimator.

No setting is tuned here; every constant is the one of the earlier specs.

## 6. Final method (decided mechanically, section 7.4)

The method that goes to confirmation has two readings: the interpretable one (one fixed formula
per asset class and target, linear model) and the accuracy one (an average over formulas). Which
formula set and which average is decided by the rules below, not after looking at the map.

## 7. Statistics, reporting and decision rules (`scripts/make_wrapup_report.py`, written before the run and tested on synthetic cells)

All comparisons per (frequency, task), all development series of the frequency pooled on the
same dates, paired date-block-bootstrap 95 % intervals (2 000 draws, block ≥ h) of the relative
difference in the primary loss, as in the earlier specs.

1. **Priors.** Every set's `|lin` reading against G, against the type's reference and against
   group PCA; Kc against Sc; K@5 against Kc, S@5 against Sc; each `P_nb` against its `P|lin`.
   Spread: standard deviation of the task-mean loss across the five draws of a procedure, next
   to the difference between the procedures and next to the same spread of R1–R5. The elicited
   sets against random: Kc and Sc (and G) against Rm. Also reported: S@5 against K@5, the
   colonies of Kc and Sc against the colony of G.
2. **Choice of P\*.** K is the default: it uses no data. Sc replaces Kc only if it is
   significantly better than Kc in more tasks than it is significantly worse AND its mean loss is
   lower in at least 3 of the 4 target types. G is never chosen (it is a benchmark with a
   disclosed defect); if P* is significantly worse than G in more tasks than better, that is
   reported as a negative finding and P* stays.
3. **Estimators.** `xgb` against `gbt`, and `xgb` and `gbt` against `lin`, for P*, G, raw
   factors and group PCA.
4. **Search.** Friedman test across the five algorithms on the seed-averaged gain on clean rows,
   unit = (pool, task, block), and on the pass rate; pairwise sign tests of each algorithm
   against ABC. ABC is the algorithm of the method unless another one is better than ABC on the
   clean-row gain (positive mean difference, more units better than worse) with a pairwise p
   below 0.05 after Holm correction over the four comparisons; among several, the largest mean
   difference. The units share dates and are not independent, so these p-values are too small
   rather than too large: that favours replacing ABC, not keeping it. ABC readings of stage 9
   against `P*|lin`, `P*_nb`, G, group PCA and the reference.
5. **Final method.** Interpretable reading: `P*|lin`. Accuracy reading: `P*_nb`, unless the
   ABC colony ensemble of stage 9 qualifies against `P*_nb` by the rule of the earlier specs
   (significantly better in more tasks than worse AND lower mean loss in at least 3 of the 4
   target types). The tested ABC winner replaces `P*|lin` only if it qualifies against it the
   same way.
6. Best-of-many test per task over all new configurations against G, group PCA and the reference.
   Every configuration is in the registry.

## 8. Compute (measured on real development cells before the freeze; seconds only, no forecast read, nothing evaluated: `scripts/time_wrapup.py`)

| stage | units | core-hours | wall on 8 workers |
|---|---|---|---|
| 7 formula sets | 8,244 cell runs (G: 9.3 core-h because of the benchmarks with three estimators; a consensus set 1.2; a plain set 0.6) | 21.1 | 2.6 h |
| 8 five algorithms | 352 pool-blocks, 15 searches each | 10.8 | 1.4 h |
| 9 ABC forecasts | 458 cells | about 1.5 (not measured: it needs stage 8) | 0.2 h |
| reports | two passes of the bootstrap | | 0.3 h |

About 4.5 hours on the Mac (`scripts/run_wrapup.sh`: each stage twice, the second pass retries
failures), started on Saturday 14 November in the evening.

## 9. The owner's decisions

Version 0 of this spec put four points to the owner: the consensus formulas as the formula of the
method with the five draws as the spread; K as the default and S only if it qualifies; the search
comparison on the chosen elicited prior, on class pools only; and when the run may start. The
owner's answer of 2026-11-14: "ok, I agree with the proposal." The owner also asked whether
kernel PCA had been tested (it was a benchmark of the r6 study only); it is not part of this spec.

## 10. Freeze

Frozen by Claude Code on the owner's agreement quoted in section 9. Details decided here and
flagged in the report: the exact construction of the consensus and random formula files, the
derived readings (`K@5`, `S@5`, `Rm`), the extra comparisons of sections 7.1 and 7.3, the
tie-breaks of the algorithm rule in 7.4, and XGBoost's own hash.

## 11. Deviations

Appended to `docs/DEVIATIONS.md` before the deviating run; the count for this spec is written
into every registry row of the run.
