# Results of SPEC-2026-11-14-abc-v3: pooled fitness, noise-aware replacement, ensembles (development series only)

Run 2026-11-14 07:45–11:43 on the Mac from the frozen spec (fingerprint `2bcaa0ad64aaa3ab35c5455d`):
424 pool-blocks of pooled searches (stage 5) and 458 cells of forecasts (stage 6), 18 tasks, 3 seeds, no failure. No
confirmation series was loaded. `report.md` is the pre-written analysis, unedited; this file
reads it.

Arms: fitness on one series (S), on the asset class (C), on every series of the frequency (F) ×
greedy or noise-aware replacement × colony anchored at the prior or spread over the whole space.
Each arm is read as its tested winner, its untested winner and its colony ensemble. E1 = fixed
generic prior formulas; B = the first ensemble. Differences are relative losses, pooled per task
over all series, 95 % date-block bootstrap; 18 tasks.

## 1. Outcome

No candidate qualifies under the rule fixed in the spec. Pooling does what it was meant to do to
the search, and it is still not enough: no searched formula beats the fixed prior. The ensembles
are better than E1 by a small, consistent margin, and a colony that was never searched does
about as well.

## 2. Pooled fitness

Anchored greedy search, returns / volatility / large loss / large gain:

| fitness on | gain on the fitness folds | gain of the winner on unused rows | untested winner vs E1 | tested winner vs E1 (tasks better / worse) |
|---|---|---|---|---|
| one series | 15 / 8 / 17 / 16 % | −4.8 / −3.5 / −8.0 / −11.9 % | +3.4 / +1.3 / +4.7 / +4.1 % | 0 / 3 |
| asset class | 11 / 7 / 10 / 10 % | −2.5 / −2.1 / −0.5 / −8.3 % | +1.4 / +1.2 / +1.2 / +2.1 % | 1 / 2 |
| whole frequency | 9 / 5 / 8 / 7 % | −1.1 / −1.4 / −0.5 / −5.1 % | +1.3 / +0.4 / +0.8 / +1.5 % | 1 / 2 |

- The fit to the selection folds falls and the loss on unused rows shrinks as more series stand
  behind the fitness. Across all contrasts the untested pooled winner is better than the
  single-series one in 29 (class) and 35 (frequency) of 72 task comparisons and worse in none.
- It still does not cross zero. Untested pooled winners are worse than E1 in 4–9 of 18 tasks and
  better in none (one arm: 1). Tested winners differ from E1 by +0.1 to +0.2 % on average, are
  better in at most 1 task and worse in 1–3. Winners pass the test in 1–19 % of the blocks, around
  the one in six a neutral candidate gets.
- The one arm with a positive gain on unused rows is the sparsest (whole frequency, noise-aware,
  spread: 7 literals; +2.6 % returns, +1.6 % large losses, +2.1 % large gains). As expected from
  the synthetic check this is sparsity, and it does not survive into the forecasts, where the
  estimator's regularisation is tuned: its untested winner is +2 % behind E1.

## 3. Noise-aware replacement

No measurable effect on tested winners (better in 4, worse in 4 of 108 comparisons with greedy)
or on ensembles (7 and 7). Untested winners improve a little (16 better, 2 worse of 108; about
−1 % on large gains, 0.3 % or less elsewhere).

## 4. Ensembles and the no-search control

| ensemble | vs E1: tasks better / worse | mean difference to E1 (return / volatility / large loss / large gain) | vs B |
|---|---|---|---|
| B (one series, anchored) | 5 / 1 | −0.07 / −0.35 / −0.67 / +0.07 % | — |
| asset class, anchored | 5 / 0 | −0.15 / −0.33 / −0.52 / −0.20 % | 3 / 0 |
| whole frequency, anchored | 8 / 0 | −0.19 / −0.33 / −0.53 / −0.22 % | 4 / 0 |
| **control: anchored starting colony, no search** | 8 / 0 | −0.14 / −0.12 / −0.18 / −0.14 % | 3 / 3 |
| one series, spread (`iba_wb`) | 2 / 0 | −0.31 / +0.22 / −0.37 / −0.30 % | 1 / 0 |
| whole frequency, spread | 2 / 0 | −0.58 / +0.21 / −0.26 / −0.57 % | 1 / 0 |
| **control: spread starting colony, no search** | 2 / 2 | −1.08 / +2.01 / −0.35 / −0.44 % | 1 / 2 |

- Every anchored ensemble beats E1 in 4–8 of 18 tasks and loses in at most 1. The best is the
  whole-frequency one (8 / 0; 9 / 0 averaged over seeds; better than B in 4 tasks, worse in none).
  It fails the rule because its mean loss is lower than B's in only 2 of the 4 target types, and
  the margin to B is 0.06 %.
- The prior and nineteen random one- or two-move neighbours, averaged without any search, also
  beat E1 in 8 tasks and lose in none. Against B that control is better in 3 tasks (returns, large
  gains) and worse in 3 (volatility at two horizons, one large-loss task). So most of the ensemble
  gain is averaging over small perturbations of the prior; the search adds about 0.2 % on
  volatility and 0.5 % on large losses and nothing elsewhere.
- Spread ensembles trade volatility for returns. Random formulas without search do the same more
  strongly: closer to the historical mean on returns (still +0.3 % behind it), 2 % worse than E1
  on volatility.
- Against group PCA: spread ensembles are better in 4–5 tasks and worse in 0–1, anchored ones in 1
  and 0. Seed averaging changes losses by under 0.1 %.
- Best-of-many test over the 32 new configurations: rejects against E1 in 2 of 18 tasks, against
  group PCA in 2, against B in none.

## 5. Against the references, nothing moves

Volatility: every tested winner and ensemble is 4 to 5.6 % below HAR, significant in at least 2
of the 3 horizons, as before. Returns: every one is behind the historical mean (+0.4 to +1.8 %).
Large losses and large gains: within about 1 % of the base rate.

## 6. Reading across the three studies

More than twenty search designs have now been run on these development series: four algorithms, the
neighbourhood of the prior and the whole space, crisp and graded formulas, greedy and noise-aware
replacement, fitness on one series, an asset class and the whole frequency. None produced a
formula that forecasts better than the fixed prior. Pooling was the right diagnosis (it removes
most of the over-fit) and shows where the floor is: with the generic prior, about nine features
per series and these sample sizes there is no structure for a search to find beyond what the
prior and plain averaging give. What holds up is the representation itself (parity with group
PCA, about 5 % over HAR on volatility) and averaging near-prior formulas (up to 0.7 %).

Open levers, none started: the owner's own prior formulas; the equal-budget comparison of ABC,
GA, PSO, annealing and DE on the pooled fitness with the clean test (for the paper's protocol
claim; expected to show no difference); the confirmation run of the final method.

## 7. Limits

- Third spec on the same cells and series; all of it is development evidence. Tails at q = 10 %.
- The decision rule compares ensembles with B, not with E1; against E1 several ensembles would
  pass it. Margins are below 1 % of the loss either way.
- Pool sizes are uneven (1 to 8 series per class); the class and frequency levels gave the same
  picture.
- The spec was frozen by Claude Code on the owner's agreement to the three directions, without a
  separate approval of its details.
