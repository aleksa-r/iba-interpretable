# Results of SPEC-2026-11-13-multitarget-study (development series only)

Run 2026-11-13 19:40–23:52 on the Mac from the frozen spec (fingerprint `2bcaa0ad64aaa3ab35c5455d`).
842 cells (48 development series × target type × horizon), 160 map units (task × asset class),
27,757 registry rows, no failed cell. No confirmation series was loaded. All estimators are
deterministic (numpy ridge / logistic, LightGBM without sampling), so the numbers do not depend
on the machine. Files: `map.md` / `map.csv` (the map), `tests.md` (paired tests, SPA,
Diebold–Mariano, Clark–West, walk-throughs, registry counts), `search_comparison.md`.

Names: **E1** = IBA with the fixed generic prior formulas (no search); **A** = ABC refinement of
the prior in a small neighbourhood, winner kept only if it passes one acceptance test on the outer
fold; **D** = A with the over-fitting penalty in the fitness; **B** = the ABC colony averaged as an
ensemble; **C** = logical aggregation of ≤ 3 polynomials with a two-parameter link, no ML layer;
**X** = exhaustive atoms with an estimator. Benchmarks: raw, PCA, group PCA, LASSO × linear and
trees, plus the type's own (historical mean and time-series momentum; HAR, GARCH, GJR; base rate,
logit on volatility, GARCH probability). Losses are relative to the type's reference (historical
mean / HAR / base rate); negative difference = better.

## 1. One paragraph

IBA with fixed formulas is level with group PCA on every target type and never significantly
better than the best benchmark in any of the 160 units. Both add information only for volatility
(about 7 % lower squared error than HAR at 1 and 4 weeks, nothing reliable at 13 weeks). Returns
and large losses are not predictable by any method; large gains are predicted by the
volatility-based benchmarks and the factor methods add nothing there. Searching for a better
formula does not pay: the ABC winner fails the acceptance test about three times in four and the
refined method is never better than the prior and worse in 12 of 34 tasks; at equal budget ABC, GA,
PSO and SA are indistinguishable out of sample. The colony used as an ensemble is the one
direction that helps: at least as good as the refined winner everywhere, better in 21 of 34
tasks, a third of the seed spread, but the gain over the fixed prior is below 1 % of the loss.

## 2. The pre-registered questions

| | Question | Answer | Evidence (34 tasks pooled over series; 160 units) |
|---|---|---|---|
| Q1 | Fixed-formula IBA level with group PCA? | **Yes, parity** (as expected) | E1 − group PCA: not significant in 33 tasks, worse in 1 (large gains). Mean relative loss difference: return −0.03 %, volatility −0.4 %, large loss −0.6 %, large gain +0.2 %. Units won 87–73. |
| Q2 | Does ABC refinement improve on the prior without re-opening the optimism gap? | **No improvement, and the gap is a little wider** than the benchmarks' although the acceptance test sends most blocks back to the prior | A − E1: better in 0 tasks, worse in 12 (3 return, 3 large loss, 6 large gain), units 36–121. Winner accepted in 16–28 % of blocks. Realised loss over cross-validated loss at tuning: A +27 % / −3 % / +9 % / +29 % (return / volatility / large loss / large gain) against +23–25 % / −4 % / +6–7 % / +22–25 % for the benchmarks and E1. The penalised fitness (D − A) changes nothing: 2 better, 2 worse, 30 not significant. |
| Q3 | Colony ensemble at least as good as its best member, with less variability? | **Yes** | B − A: better in 21 tasks (2/7 return, 2/3 volatility, 7/12 large loss, 10/12 large gain), worse in 0; units 136–24. Seed spread 0.1 % of the loss against 0.3–0.5 % for A. B − E1: better in 10 tasks, worse in 1, but only −0.1 % to −0.7 % of the loss. B − group PCA: better in 1 task, worse in 0. |
| Q4 | Does the simple aggregation model (no ML layer) reach the estimator-based variants? | **On returns and tails yes, on volatility no** | C − E1: not significant in 25 of 31 return and tail tasks (worse in 6); on volatility worse at 1 and 4 weeks (+2.6 %, +3.6 % loss), 0 of 24 units won. The parity is on targets where nothing has skill. |
| Q5 | The map; expected nulls | **Nulls confirmed; volatility is where factors add information** | see section 3 |

## 3. The map, condensed

Each cell: mean skill in % against the type's reference for **B / E1 / group PCA / best
type-specific benchmark**, then B against the best benchmark of each unit (t = tie, w =
significantly worse at 95 %; never significantly better). The full map with intervals is `map.md`.

| asset class (series)      | return                             | log realised variance               | large loss                        | large gain                         |
|:--------------------------|:-----------------------------------|:------------------------------------|:----------------------------------|:-----------------------------------|
| US equity broad (3)       | -0.7 / -0.7 / -1.1 / -18.8 (3t 0w) | +10.4 / +9.8 / +10.1 / +4.8 (3t 0w) | -0.5 / -0.6 / -0.9 / -3.4 (5t 1w) | +2.6 / +2.0 / +2.8 / +10.6 (3t 3w) |
| US equity sectors (5)     | -1.3 / -1.4 / -1.3 / -14.7 (1t 2w) | +9.0 / +8.4 / +7.8 / +3.4 (3t 0w)   | -1.0 / -1.1 / -1.1 / -2.5 (6t 0w) | +0.4 / +0.1 / +1.1 / +6.9 (0t 6w)  |
| Developed ex-US equity (8)| -1.0 / -1.4 / -3.1 / -16.0 (3t 0w) | +7.6 / +7.1 / +6.6 / -11.3 (3t 0w)  | +0.5 / +0.1 / -0.3 / -2.5 (6t 0w) | +0.8 / +0.6 / +0.8 / +7.7 (2t 4w)  |
| Emerging equity (5)       | +0.4 / +0.2 / -0.4 / -10.6 (3t 0w) | +3.4 / +3.4 / +2.6 / -4.7 (3t 0w)   | -0.0 / -0.8 / -1.3 / -1.2 (6t 0w) | +1.4 / +1.2 / +1.0 / +5.0 (6t 0w)  |
| Government and IG bonds (5)| -1.3 / -1.3 / -1.4 / -7.3 (3t 0w) | +1.6 / +1.4 / +1.7 / -3.9 (3t 0w)   | -0.3 / -0.6 / -0.5 / +4.2 (6t 0w) | -1.0 / -1.1 / -0.4 / +1.2 (6t 0w)  |
| Credit and EM debt (2)    | -1.9 / -2.1 / -2.1 / -10.7 (3t 0w) | +8.7 / +8.1 / +7.1 / -17.2 (3t 0w)  | +2.1 / +1.5 / -0.4 / +0.3 (6t 0w) | -3.2 / -3.9 / +0.8 / +17.0 (2t 4w) |
| Commodities (8)           | -1.0 / -1.2 / -1.3 / -9.5 (3t 0w)  | +1.7 / +1.6 / +1.3 / -6.3 (3t 0w)   | -3.1 / -3.7 / -4.2 / -0.9 (3t 3w) | -0.5 / -0.5 / -0.4 / +1.4 (6t 0w)  |
| Real estate (1)           | -1.7 / -1.6 / -2.5 / -16.5 (3t 0w) | +4.4 / +4.1 / +3.9 / -5.1 (3t 0w)   | -0.1 / -0.2 / -0.5 / -3.7 (6t 0w) | -0.6 / -0.5 / +0.5 / +1.3 (5t 1w)  |
| Hedge-fund indices, monthly (11) | -1.7 / -1.7 / -1.4 / -62.1 (4t 0w) | — | +1.0 / +0.0 / -0.7 / -5.0 (6t 0w) | -1.2 / -0.8 / -0.8 / +7.7 (3t 3w)  |

**Returns.** Nothing beats the historical mean: SPA over the 12 IBA variants rejects in 0 of 7
tasks (median p 0.92); mean R² of every method is between −1 % and −2 %; skill is positive in 1–2
of 28 units; Diebold–Mariano finds no series where E1, B or group PCA is better at 5 %. Direction:
61.7 % correct against 63.5 % for always-long; the sign beats always-long in 12–20 % of series.
Time-series momentum is far worse than the mean. Expected null, confirmed.

**Volatility.** Where the factors work. Against HAR, pooled over the 37 weekly series:

| horizon | E1 | B | group PCA |
|---|---|---|---|
| 1 week | −6.6 % [−10.4, −3.4] | −6.9 % [−10.8, −3.8] | −7.4 % [−12.4, −3.5] |
| 4 weeks | −7.1 % [−13.8, −2.4] | −7.4 % [−14.0, −2.9] | −6.5 % [−13.4, −1.7] |
| 13 weeks | −2.2 % [−6.3, +1.5] | −2.5 % [−6.5, +1.2] | −0.9 % [−3.5, +1.4] |

SPA against HAR: p = 0.001 at 1 and 4 weeks; against group PCA: no rejection (median p 0.28).
Per series E1 and B beat HAR in 37 of 111 cells at 5 % (13 and 15 after Holm) and are never worse.
By asset class the gain is about 10 % in US equity, 7–9 % in sectors, developed ex-US equity and
credit, 3–4 % in emerging equity and real estate, under 2 % in bonds and commodities. The best
benchmark of a unit is a factor benchmark with a linear estimator in 21 of 24 units; GARCH is worse
than HAR in 19 of 24. B ranks 2.3 of 13 on average, E1 2.6, C 5.7, X 9.0.

**Large losses.** Not predictable. The base rate is the best benchmark in 26 of 54 units; SPA
against it rejects in 0 of 12 tasks. B has positive skill in 28 of 54 units, but the mean is
−0.1 %. The volatility-based benchmarks are worse than the base rate here. E1 and B are slightly
ahead of group PCA (units 38–16; significant in 1 of 12 tasks for B) while neither beats the base
rate. Expected null, confirmed.

**Large gains.** Predictable, but not by the factor methods. Logit on volatility and the GARCH
probability have positive skill in 44–46 of 54 units (5–17 % in equity and credit) and are the
best benchmark in 48 of 54; IBA and group PCA are near zero and significantly worse than the best
benchmark in 21 of 54 units. Large gains were more frequent in the evaluation years than the
training thresholds imply (14.5 % of observations against a nominal 11.7 % averaged over the three
tail sizes; large losses 12.0 %), and for the factor methods the realised log loss is 22–25 %
above the cross-validated one at tuning (6–7 % for large losses). The benchmarks that condition
on the volatility level adapt to that shift. I have not examined this further.

**Trees and exhaustive search.** With the fixed formulas the linear estimator beats trees in 154
of 160 units (137–156 for the benchmark feature sets). X is the worst configuration on every
type: worse than E1 in 31 of 34 tasks, by 6–13 % of the loss, with the largest gap between tuning
and realised loss (realised over cross-validated: +55 % return, +10 % volatility, +46 % large
loss, +80 % large gain; the low-order variant +37 %, +1 %, +24 %, +44 %).

## 4. Search comparison at equal budget (2000 distinct fitness evaluations, 96 units, 20 seeds)

| | inner gain | outer gain | optimism | accepted |
|---|---|---|---|---|
| ABC | 10.4 % | 0.6 % | 3.2 % | 23 % |
| GA | 12.4 % | 0.2 % | 3.8 % | 21 % |
| PSO | 11.2 % | 0.5 % | 3.5 % | 24 % |
| SA | 11.2 % | 0.4 % | 3.5 % | 22 % |
| ABC, winner picked on the outer fold | 3.0 % | 12.3 % | −2.8 % | 97 % |

On the inner folds ABC finds less than the others (loses to GA and SA in 96 of 96 units, to PSO in
90). Out of sample there is no difference (Friedman p = 0.63; ABC wins 50–55 of 96 against each).
Whatever the algorithm, a 10–12 % improvement of the fitness shrinks to under 1 % on data the
search did not see. The last row is the same ABC with the usual "keep what is best on validation":
it reports a 12 % gain and accepts almost every time. That gain is selection on the outer fold and
is the practice the single acceptance test replaces.

## 5. What this means for the method and the paper

1. The claim the data support: IBA with fixed formulas is an interpretable nine-aggregate
   representation at parity with group PCA, and both improve volatility forecasts over HAR by
   about 7 % at 1–4 weeks across 37 indices and eight asset classes. Not: IBA beats the benchmarks.
2. "IBA + modified ABC finds better formulas" is not supported on development data. A modified ABC
   would have to beat a null that GA, PSO and SA also fail to beat. The publishable part of the
   search work is the protocol itself: equal-budget comparison, the acceptance test, the measured
   selection effect of validation-based picking, the optimism gap. The literature pass found none
   of these applied to metaheuristic model search.
3. The colony as an ensemble is the ABC direction worth keeping: consistent, stable across
   seeds, small.
4. The prior formulas carry the method. They are still the generic ones from r8, labelled as such.
   The owner's formulas are the input most likely to move the result, and they can be tested on
   development data under a new dated spec before anything touches the confirmation series.

## 6. Limits and deviations

- **Erratum, 2026-11-14: the acceptance test was not clean.** The selection folds have overlapping
  validation windows, so 44–45 of the 78 weekly rows of the outer fold (8–9 of 18 monthly) had
  already been used by the search as validation rows of the last fitness fold. The test of A, C and
  D was therefore too lenient (on synthetic returns without signal it passes 23–27 % of winners;
  on rows the search has not used, 8–20 %), and the "outer gain" of section 4 is biased upwards.
  Expected direction: the results for A, C and D are somewhat too pessimistic (more noise winners
  replaced the prior than a clean test would allow) and the search comparison's out-of-sample
  gains somewhat too optimistic; E1, B, X and the benchmarks are not affected. Nothing here was
  re-run; SPEC-2026-11-14-abc-v2 uses clean rows and re-tests A's winner with them, which
  measures the effect (`docs/DEVIATIONS.md`).

- "Never significantly better than the best benchmark" is a strict bar: the best benchmark of a
  unit is picked on the same evaluation data, which favours the benchmark side. The pairwise tests
  in `tests.md` (against group PCA and against the reference) do not have this bias and give the
  parity result.
- The tests in `tests.md` were written after the map had been seen; the spec named them but left
  the pooling level and the list of pairs open (`docs/DEVIATIONS.md`). The map, the headline
  configurations and the search comparison were fixed before the run.
- Registry rows do not carry the deviation count the spec promised (`docs/DEVIATIONS.md`); the
  count was zero during the run. Stage 3 is logged as 15 aggregate rows (task × algorithm, 640
  runs each); the per-run diagnostics are in the artifacts.
- Four re-selection blocks per cell (2018-09 to 2026-11 weekly); hedge-fund indices have 11 series
  and monthly data; credit (2 series) and real estate (1) are thin strata.
- Generic prior formulas; one panel of 67 weekly factors; development series only.
