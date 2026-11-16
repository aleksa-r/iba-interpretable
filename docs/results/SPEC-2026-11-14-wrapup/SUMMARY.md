# Results of SPEC-2026-11-14-wrapup: elicited priors, XGBoost, five search algorithms, the final method (development series only)

Run 2026-11-14 17:24–21:55 on the Mac from the frozen spec (fingerprint `2bcaa0ad64aaa3ab35c5455d`,
XGBoost hash `c6e501978f15890d889f6075`): 8,244 cell runs of stage 7 (18 formula sets × 458
cells), 352 pool-blocks of stage 8, 458 cells of stage 9; no failure; 61,156 registry rows. No
confirmation series was loaded. `report.md` is the pre-written analysis, unedited
(`report_part_A.md` is its first part, written after stage 7 to choose the formula set); this
file reads it. Differences are relative losses, pooled per task over all series, 95 % date-block
bootstrap; 18 tasks. G = the generic formulas, K / S = knowledge-only / statistics-informed
elicitation, Kc / Sc their consensus, R = random formulas.

Check: G's linear forecasts made here are identical to the first study's (largest difference 0
over 458 cells).

## 1. Outcome

- **Formula set of the method: Kc** (the default; S does not qualify against K).
- **Interpretable reading: the fixed formula, `Kc|lin`.** The tested ABC winner does not qualify.
- **Accuracy reading: the ABC colony ensemble on the class-pooled fitness, `iba_ca_b`.** It
  qualifies against the no-search colony by the rule of the spec: better in 3 of 18 tasks, worse
  in none, lower mean loss in all 4 target types. The margin is 0.09 % of the loss.
- **Search algorithm: ABC** (the default; no algorithm differs from it on unused rows).
- Against the references nothing moved: volatility about 6 % below HAR, returns behind the
  historical mean, tails at the base rate.

## 2. Prior formulas

| | return | volatility | large loss | large gain | tasks better / worse |
|---|---|---|---|---|---|
| Kc against G | +0.72 % | −0.60 % | +0.74 % | −0.27 % | 0 / 0 |
| Sc against G | −0.46 % | −0.50 % | −0.18 % | +0.27 % | 1 / 0 |
| Sc against Kc | −1.16 % | +0.10 % | −0.90 % | +0.53 % | 0 / 0 |
| Kc against random (mean loss of R1–R5) | +0.86 % | −3.36 % | −0.42 % | −0.50 % | 4 / 0 |
| Sc against random | −0.33 % | −3.26 % | −1.32 % | +0.03 % | 3 / 0 |
| G against random | +0.14 % | −2.78 % | −1.14 % | −0.23 % | 3 / 0 |

- The elicited formulas are at parity with the generic ones, as expected. They are really
  different formulas (the consensus keeps about a fifth of the generic literals and reverses a
  third), so the parity is a statement about the representation, not about one lucky formula.
- Knowledge matters where there is signal: on volatility every informed set is about 3 % better
  than random formulas (significant in 2–3 of 3 horizons); on returns and tails informed and
  random formulas cannot be told apart, and random sets have the lowest loss in 5 of 7 return
  tasks.
- S against K: numerically better on returns and large losses, significant in no task, lower
  mean loss in 2 of 4 types. It does not qualify; K, which uses no data, stays.
- Draws: the standard deviation across the five draws of a procedure is 0.15–1.2 % of the loss,
  as large as the difference between the procedures. Averaging the five draws' forecasts beats
  the consensus formula (K: 5 tasks better, 0 worse; S: 4 / 0) and beats group PCA (K: 4 / 0;
  S: 3 / 0). The consensus formula is the interpretable object; it is not the most accurate way
  to use five draws.
- The no-search colony beats its own fixed formula for every set (G 8 / 0, Kc 9 / 0, Sc 7 / 0 of
  18), by 0.1–0.3 %.

## 3. Estimators

XGBoost without sampling is not better than LightGBM (on Kc: 1 task better, 4 worse; +3.7 % on
returns). Both are clearly worse than the linear model on every representation (IBA, raw
factors, group PCA): 3–9 % higher loss, worse in 11–15 of 18 tasks, better in none.

## 4. Search

Five algorithms, class-pooled fitness, anchored space, 2 000 formulas per search, 3 seeds, 352
pool-blocks:

| | ABC | GA | PSO | SA | DE | Friedman p |
|---|---|---|---|---|---|---|
| gain on the fitness folds | 9.0 % | 11.0 % | 9.8 % | 9.7 % | 10.5 % | < 0.001 |
| gain on clean unused rows | −1.4 % | −2.0 % | −2.0 % | −1.5 % | −1.4 % | 0.60 |
| winners passing the test | 12.3 % | 11.9 % | 12.4 % | 11.6 % | 12.6 % | 0.69 |

- The algorithms differ in how hard they fit the selection folds (GA most, ABC least) and not at
  all in what survives on unused rows: every winner loses there on average, and passes the test
  about one time in eight, below the one in six of a neutral candidate. No algorithm is better
  than ABC (sign tests, Holm p = 1 for all four). DE, the algorithm of the published IBA hybrids,
  is indistinguishable from ABC.
- Forecasts from the pooled ABC with Kc as the prior: the tested winner is +0.2 % behind the
  fixed formula (0 tasks better, 2 worse); the winner without the test is worse in 12 of 18
  tasks (+1.5 to +2.9 %). The colony ensemble is better than the fixed formula in 7 tasks and
  worse in none (−0.14 to −0.46 %), better than the no-search colony in 3 and worse in none,
  better than group PCA in 4 and worse in none.

## 5. Best-of-many test over the 63 new configurations

Against the reference: rejects in 2 of 3 volatility tasks and in no other task. Against G: in 1
of 18 tasks. Against group PCA: in 2 of 18 (both large-loss tasks).

## 6. Reading

The fourth study on these series changes one thing and confirms the rest. What changed: with the
elicited prior the ABC colony, used as an ensemble, passes the pre-set rule against averaging
without search. The margin (0.09 %) is far below anything of practical size, the rule was passed
once in four studies, and in SPEC-2026-11-14-abc-v3 the no-search colony was level with the
searched ensembles on the generic prior; the honest description is "search as an ensemble generator is not worse than
averaging near-prior formulas and may be marginally better". What is confirmed: a single searched
formula never beats the prior; the choice of algorithm does not matter out of sample; the
representation is at parity with group PCA and carries its value on volatility; trees do not
help; and the content of the formulas matters only for volatility.

## 7. Limits

- Fourth spec on the same cells and series: development evidence only. Tails at q = 10 %.
- The knowledge cut-off of the elicitation cannot be enforced; the model was trained on later
  data. That Kc does not beat G or random formulas on returns argues against large hindsight
  effects, but does not exclude them.
- The sign tests of section 4 treat units that share dates as independent.
- Table 1e of the report repeats one row (G colony against G); nothing else is affected.
- Code was committed while stage 7 was running (the kernel-PCA / autoencoder spec and the
  explanation step): the behaviour of stages 7–9 and the fingerprint are unchanged, but registry
  rows of this run carry more than one git commit.
- Frozen by Claude Code on the owner's agreement to the proposal, without a separate approval of
  version 1's details.
