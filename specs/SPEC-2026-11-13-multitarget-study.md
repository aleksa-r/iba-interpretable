---
spec_id: SPEC-2026-11-13-multitarget-study
status: frozen     # frozen by the owner on 2026-11-13 ("freeze"); no change after this without a new version
version: 3 (2026-11-13; owner agreed the universe, split, sources and formula format; engine built and tested)
fingerprint: 2bcaa0ad64aaa3ab35c5455d
authors: Aleksa Radosavčević; drafted by Claude Code
depends_on: docs/VERIFICATION.md, docs/UNIVERSE.md, data/universe.yaml, data/split_manifest.json,
            docs/REPO_DESIGN.md, docs/literature/literature_pass_2026-11-13.md
scope: DEVELOPMENT series only. The confirmation run gets its own frozen spec after development is closed.
---

# Simultaneous multi-target study of IBA feature reduction on index time series (development)

## 1. Questions (pre-registered)

Q1 Representation without search: is IBA with FIXED prior formulas (one conjunction of ≤ 2 literals
   per group, product realisation) level with group PCA on each target type? Expected: parity on
   returns, close to parity on volatility (verification: +6.6 % / +6.4 % vs +8.1 % / +6.4 %).
Q2 Constrained search: does an ABC refinement of the prior formulas in a small neighbourhood improve
   on them WITHOUT re-opening the optimism gap (inner − outer score inside the benchmark range)?
Q3 Population as ensemble: is the colony's averaged forecast at least as good as its best member
   out of sample, with a smaller gap?
Q4 Simple mathematical model: does a convex logical aggregation of ≤ 3 GBPs with a two-parameter
   link (no ML layer) reach the accuracy of the estimator-based variants on any target type?
Q5 The map: target type × asset class × method — rank among benchmarks, difference to the best
   benchmark with a date-block-bootstrap interval, optimism gap. A mixed outcome is expected.
   Expected nulls, stated in advance: nothing beats always-long on return direction; 10 % tails at
   short horizons are not predictable; volatility is where the factors add information.

## 1b. Position against the literature ("not found" = targeted searches, not proof)

IBA structure has been learned from data only by VNS, GA and differential evolution (2018–2024),
on the 2^n structure vector with training MSE and generic hold-out guards; no IBA + ABC exists.
No binary-ABC feature selector uses a validation-ranked archive, an over-fitting-penalised fitness
or the colony as an ensemble. Reality Check / SPA / StepM / MCS have not been applied to models
chosen by a metaheuristic. No fuzzy or logical forecaster has been tested against tree ensembles
and naive references with formal tests on index returns or realised volatility. The defensible
headline is parity at interpretable complexity inside the confidence set plus a measured optimism
gap, not superiority.

## 2. Data

Universe and split: `data/universe.yaml`, `data/split_manifest.json` (with its amendment of
2026-11-13). Development: 37 daily series in eight strata and the 11 monthly CISDM indices.
Daily prices: Yahoo adjusted close, one dated download, hashed. Weekly rows: W-FRI; sample
2008-06-06 .. 2026-09-25 (the weekly factor panel's span, 956 weeks; later-starting series use
their own first full week). Monthly: 2005-01 .. 2026-09 (261 months).
Factors: `panel_weekly_2026-11-11` (8 groups × 4 factors) and `panel_2026-11-11` (9 groups × 4),
copied into `data/panels/` with their hashes. A target that is itself a factor has that factor
dropped from its group for that target (HYG, EMB, EEM, DBC, SLV).

## 3. Targets (per series, horizon h, origin t; every quantity fitted on admissible rows j + h ≤ t)

| Type | Label | Horizons | Measures | Type-specific benchmarks |
|---|---|---|---|---|
| Return | compounded return over t+1..t+h | weekly 1, 4, 13; monthly 1, 3, 6, 12 | sign accuracy; out-of-sample R² vs historical mean; MSE; gated Sharpe and return (long/flat, held h periods, ALL h phases, phase-averaged headline) | always-long, historical mean, time-series momentum (sign of trailing 52 w / 12 m return) |
| Volatility (daily series only) | log of realised variance summed over t+1..t+h; weekly RV = sum of squared daily log returns | weekly 1, 4 (13 secondary) | MSE of log RV; QLIKE and MSE of the variance (forecast exp(f + s²/2), s² from training residuals); R² vs HAR | last value, HAR(1, 4, 13), GARCH(1,1), GJR-GARCH(1,1) (daily, expanding, refit every 4 weeks) |
| Large loss | 1[return over t+1..t+h < q-quantile of admissible training returns], q ∈ {0.05, 0.10, 0.20} | weekly 4, 13; monthly 3, 6 | Brier, log score (probabilities clipped to [0.001, 0.999]), Brier skill vs base rate, reliability / ECE (10 bins), AUC (secondary) | base rate; logistic on HAR volatility terms; GARCH-implied probability (normal, h-step variance) |
| Large gain | 1[return > (1−q)-quantile], same q | same | same | same |

Thresholds are recomputed on the admissible rows of every fit. One-week tails are left out: r7
found them unpredictable for every method and the owner asked for longer horizons. For monthly
series the volatility terms of the tail benchmarks use sums of squared monthly returns over 3, 6
and 12 months and GARCH on monthly returns.

Low-power cells, stated in advance: monthly 5 % tails rest on about eight training events in the
first block (weekly 5 % tails on about 26); they are reported and flagged, not dropped.

Task count: 37 daily series × (3 + 2 + 12) + 11 monthly × (4 + 12) = 629 + 176 = 805 cells, plus the
37 secondary 13-week volatility cells (`ibanext.protocol.study.development_tasks`).

## 4. Features and predicates

Rolling z-scores at two windows (weekly 26 and 52; monthly by horizon as in r6); ENDG = the
target's own return z-scores (own log-RV z-scores for volatility). Predicates: MinMax to
[0.01, 0.99] fitted on admissible rows (published method). Declared sensitivity, not headline:
ECDF scaling; minimum as generalized product.

## 5. Training objectives and estimators

- Objective: squared error for returns and for the volatility residual; logistic loss for tails.
  The composite objective of the published method is NOT used (r6: no benefit; scale-inconsistent).
- Volatility is two-stage as in r7: HAR on the admissible rows (re-fitted in every fold and at
  every refit), then each reducer × estimator forecasts the HAR residual; forecast = HAR + residual.
- Linear estimator: ridge (8 α, log-spaced 10⁻² .. 10³) on standardised features; logistic with
  L2 (8 C, log-spaced 10⁻³ .. 10²) for tails.
- Trees: LightGBM, deterministic (no bagging, no feature sub-sampling, one thread): max_depth
  {2, 4} × rounds {100, 300}, learning rate 0.05, min_child_samples 10. Same grid for every reducer;
  tuned per block on the selection folds. No random element, hence no seed for these.
- Fingerprint: a fixed synthetic cell is run before every experiment; its forecast hash is stored
  in the registry and must equal the value recorded at freeze.

## 6. Methods (as implemented in `ibanext.search`; every search sees only the block's admissible rows)

IBA family (product generalized product):
- **E1** fixed prior formulas, one conjunction (≤ 2 literals) per group, no search. Until the
  owner's formulas arrive: the r8 generic formulas, labelled "generic" in every table.
- **A** ABC neighbourhood refinement. A solution assigns to each group a conjunction of 1–3
  literals or "off". Moves: flip one literal's polarity; switch its window; replace its factor by
  another of the group; add a literal; drop a literal; switch a group off / back to its prior
  formula. Solutions stay within DISTANCE 4 of the prior, the distance being the number of
  predicates whose status (absent / asserted / negated) differs (a flip, an addition or a removal
  counts 1; a window or factor replacement 2). Colony of 20 food sources started at the prior and
  its one-move neighbours; employed, onlooker (rank-proportional) and scout phases (abandon after
  10 failures, restart one or two moves from the prior). Budget **B = 2 000 distinct fitness
  evaluations per block** (the unit for every algorithm).
  Fold roles (five purged expanding folds in time order): folds 1–4 = FITNESS, fold 5 (the most
  recent) = OUTER. Fitness = mean fitness-fold loss of the linear estimator at fixed
  regularisation (ridge α = 1 / logistic C = 1, standardised features) + 0.5 % of the prior's
  fitness per literal in excess of the prior. The colony optimises the fitness only. The single
  winner (best fitness) then gets ONE test on the outer fold: it replaces the prior for the block
  only if its outer loss is lower by more than one block standard error of the pointwise loss
  difference (blocks of max(h, 4) rows); otherwise the prior is kept. The outer fold never ranks
  candidates: choosing the best of 2 000 on it would move the selection problem onto that fold.
- **B** the final colony as an ensemble: each of the 20 food sources gets its own tuned linear
  estimator; forecasts are averaged; no acceptance rule. Also reported: the literals present in
  ≥ 50 % of the colony.
- **D** A with an over-fitting-penalised fitness: folds 1–3 = fitness, fold 4 = penalty, fold 5 =
  outer; fitness = L̄(1–3) + max(0, L(4) − L̄(1–3)) (+ the literal term); same acceptance test.
- **C** logical aggregation without an estimator: a convex combination (weights on a 0.1 grid) of
  ≤ 3 GBPs, each within 2 status changes of its group's prior formula; started from the three
  prior formulas with the best single-formula fitness (weights 0.4 / 0.3 / 0.3); ABC at budget B
  with A's fold roles and acceptance test (against the starting aggregation); forecast =
  a + b·aggregate by least squares (returns; volatility: HAR + a + b·aggregate; tails: logit
  p = a + b·aggregate by maximum likelihood).
- **X** references at the same fitness and fold roles, without an acceptance rule: exhaustive
  atoms per group plus exhaustive group subsets (the published search), and the low-order
  exhaustive search (≤ 2 literals, smallest subset within one standard error of the best). The
  XGBoost-screened published numbers are quoted from r6, not re-run.
- Search comparison (stage 3) on a fixed sample — the alphabetically first development series of
  each daily stratum × {return h = 4, volatility h = 1, large loss q = 0.10 h = 4} = 24 cells:
  ABC, GA, binary PSO and simulated annealing at the same budget, fitness and acceptance test,
  20 seeds each; inner and outer scores relative to the prior; Friedman and Wilcoxon with Holm.
  Secondary, same sample: ABC with "global validation" (the pick is the best on the outer fold),
  to measure the optimism that rule creates.
- Estimators on top: E1, A, D and X with ridge/logistic and with LightGBM (for seeded variants the
  trees use the first seed only); B and C as defined.
- ABC variants (A, B, C, D) run with 3 seeds on every cell; the map reports their seed average
  and the spread across seeds.
- Reading note: for a group with a single literal the polarity is not identified under a linear
  estimator (x and 1 − x differ by sign); formulas are read together with the coefficient's sign.

Benchmarks on every target type: RAW (all predicates' z-scores), PCA (6 components, standardised),
group PCA (first component per group), LASSO selection (purged inner folds), each with the linear
estimator and with LightGBM; plus the type-specific benchmarks of section 3.

## 7. Protocol

Information rule (`ibanext.protocol.information_rule`). Weekly: last 416 weeks out of sample, four
blocks of 104, refit every 4 weeks, at least 300 training weeks; selection folds 0.7 / 78 / 43 / 5
purged by h. Monthly: 96 / 24 / 1, at least 110 months; folds 0.7 / 18 / 10 / 5. Representation,
search and tuning are redone at each block start on admissible rows; within a block the
representation is frozen. Every (cell, configuration, seed) is a row of `registry/trials.jsonl`.
Development results may be looked at and methods may be revised after them; each revision is a
new dated spec and every look is in the registry. The guard against this iteration is the
confirmation run, not this spec.

## 8. Statistics and reporting (pre-written in `ibanext.eval.map` and `scripts/run_search_comparison.py`)

Unit of the map: (frequency, task, stratum). Primary loss: squared error (returns, log RV), Brier
(tails); secondary: sign error, QLIKE, log score. For every configuration: pooled mean loss, skill
against the type's reference (historical mean / HAR / base rate), Model Confidence Set membership
(10 %, cross-series mean loss per date). For every IBA configuration: rank among the benchmarks,
difference to the BEST benchmark with a date-block-bootstrap 95 % interval (block ≥ h; all series
of the stratum at the same dates), optimism gap (loss realised in a block − cross-validated loss
at tuning), and for the searches the inner-to-outer optimism relative to the prior and the
acceptance rate. SPA / StepM for "any IBA variant vs benchmark" with the variant count declared
(E1, A, B, C, D, X, X-low-order × estimators = 12); Diebold–Mariano (HAC lag h − 1, HLN) and
Clark–West against the historical mean as descriptives; Holm as a cross-check. Headline
configurations are declared here (E1, A, B, C with the linear estimator); no test result changes
them. One success and one failure walk-through per target type; registry counts.

## 9. Compute plan (measured on a synthetic panel of the real shape, one core per cell)

Stage 1 (benchmarks, E1, X; GARCH paths cached once): 40 s per return or volatility cell, 50 s
per tail cell → about 12 core-hours, 1.5 h on 8 workers. Stage 2 (A, B, C, D, 3 seeds): 40 s and
90 s → about 16 core-hours, 2 h. Stage 3 (search comparison, 24 cells × 4 blocks × 5 variants ×
20 seeds): about 4 core-hours, 0.5 h. Each stage is announced before it starts; a stage is
started only from a frozen, committed spec whose fingerprint reproduces on the machine
(`ibanext.protocol.spec.require_frozen`), and every evaluated configuration is written to
`registry/trials.jsonl` by the runner.

## 10. Owner inputs

Prior formulas (optional before freeze; a later spec can replace the generic ones): a YAML per
panel, `groups: {GROUP: [[factor_code, high|not_high], ...]}`, ≤ 2 literals per group, the same
for every target; optional variants per target type under `return:`, `volatility:`, `tail:`.
Freeze: the owner replies "freeze"; the status line is changed to `frozen` and committed, and only
then does `scripts/run_study.py` accept the spec. After the freeze any change to the engine that
alters the fingerprint blocks further runs until a new spec version records it.

## 11. Deviations

Appended to `docs/DEVIATIONS.md` before the deviating run; their count goes into every registry row.
