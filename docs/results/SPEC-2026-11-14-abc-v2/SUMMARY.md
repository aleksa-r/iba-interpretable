# Results of SPEC-2026-11-14-abc-v2: ABC over the whole space (development series only)

Run 2026-11-14 04:06–06:35 on the Mac from the frozen spec (fingerprint `2bcaa0ad64aaa3ab35c5455d`):
458 cells (48 development series; returns, volatility, tails at q = 10 %), 18 tasks, 3 seeds,
no failed cell, 20,152 registry rows (deviation count 0). No confirmation series was loaded.
`report.md` is the pre-written analysis, unedited; this file reads it.

Names: **E1** fixed generic prior formulas; **A** / **B** the first study's ABC winner / colony
ensemble; **W** discrete moves, colony started at the prior and at random formulas, no distance
limit; **V** whole-vector moves on crisp formulas; **G** whole-vector moves on graded formulas
(each number is the degree to which a literal is in the conjunction, zero = not used); **Z** = G
started from zero. Every search is read three ways: its winner after the acceptance test, its
winner without the test, its final colony as an ensemble.

## 1. Outcome

No candidate qualifies under the rule fixed in the spec; the first study's implementation stays.
The more freedom a search has, the better it fits the selection folds and the worse it forecasts.
One thing holds up: the colony of the spread-start search W, used as an ensemble, is level with B
and is significantly better than group PCA in 4 of the 18 tasks and worse in none.

## 2. The three ideas

Gain = relative reduction of the loss against the prior formulas. "Unused rows" are the rows of
the outer fold the search has not seen (section 3). Loss differences are against E1, pooled per
task over all series, 95 % date-block bootstrap; ranges are over the four target types.

| | first ABC (A) | W: different starting positions | V: whole vector, crisp | G: whole vector, graded | Z: graded, from zero |
|---|---|---|---|---|---|
| Gain on the selection folds | 14 % | 20 % | 25 % | 35 % | 30 % |
| Gain of the winner on unused rows | −6.7 % | −8.2 % | −11.3 % | −15.7 % | −13.1 % |
| Winner passes the test | 11 % | 9 % | 9 % | 9 % | 9 % |
| Winner without the test vs E1 | +1.3 to +4.7 %; worse in 9 of 18 tasks | +3.1 to +9.7 %; 18 of 18 | +3.8 to +13.8 %; 18 of 18 | +4.4 to +19.8 %; 18 of 18 | +4.2 to +15.7 %; 17 of 18 |
| Winner with the test vs E1 | +0.2 to +0.6 %; worse in 3, better in 0 | +0.3 to +0.9 %; 9, 0 | +0.3 to +2.4 %; 9, 0 | +0.2 to +4.1 %; 11, 0 | +0.3 to +3.0 %; 10, 0 |
| Colony ensemble vs B | — | −0.4 to +0.6 %; better in 1, worse in 0 | +2.3 to +6.9 %; worse in 14 | +4.0 to +18.5 %; worse in 18 | +3.5 to +12.1 %; worse in 17 |

- **Different starting positions.** As a search for one formula it is worse than staying near the
  prior. As a source of an ensemble it is as good as the first one (section 4).
- **Whole vector at once.** It is the stronger optimiser (25–35 % on the selection folds against
  14 %) and the weaker forecaster, crisp or graded, winner or ensemble.
- **Zero allowed, start from zero.** The searches do not end sparse. Winners use 8–9 of the 9
  groups (W: 6.6) with 13–27 literals or units of inclusion against 17 in the weekly prior; the
  empty formula won in 0.04 % of Z's searches and never elsewhere. From zero the colony fills up
  within the budget: adding literals lowers the selection loss.

## 3. The acceptance test, now measured on real data

The first study tested the winner on an outer fold of which 44–45 of 78 weekly rows had already
served the search (erratum in the first summary). On these 458 cells:

| winner of the first ABC | first study's test (whole fold) | this spec's test (unused rows) |
|---|---|---|
| gain measured by the test | −2.9 % to +1.4 % by type | −3.5 % to −11.9 % |
| passed | 22 % | 11 % |
| loss against E1 after the test | +0.2 / +0.4 / +1.2 / +2.0 % (volatility / return / large loss / large gain); worse in 5 of 18 tasks | +0.2 / +0.3 / +0.4 / +0.6 %; worse in 3 of 18 |

So part of what the first study reported as "the ABC refinement hurts" came from the lenient
test. With a clean test the refinement costs about a third of a percent instead of one percent.
It is still better than E1 in no task, and the winner loses on unused rows in every target type.
A clean test passes fewer than the one in six a neutral candidate would get.

## 4. The ensembles

| | W ensemble vs B | vs E1 | vs group PCA | vs reference |
|---|---|---|---|---|
| return (7 tasks) | −0.24 % | −0.31 % | −0.35 %, better in 1 | +1.08 %, worse in 1 |
| volatility (3) | +0.57 % | +0.22 % | −0.14 %, better in 1 | −5.08 %, better in 2 |
| large loss (4) | +0.30 % | −0.37 %, better in 1 | −1.01 %, better in 2 | −0.66 % |
| large gain (4) | −0.37 %, better in 1 | −0.30 %, better in 1 | −0.02 % | −0.13 %, better in 1 |

- Against group PCA the W ensemble is significantly better in weekly volatility at 13 weeks
  (−1.1 %), returns at 4 weeks (−1.4 %) and large losses at 4 and 13 weeks (−1.0 %, −1.5 %), and
  has the lower loss in 64 of 88 units (task × asset class). On the same 18 tasks B is better
  than group PCA in 1 and E1 in none. On returns "better than group PCA" still means less far
  behind the historical mean.
- Read with care: twelve new configurations were compared with several benchmarks. The SPA over
  the twelve rejects against group PCA in 1 of 18 tasks, against E1 and against B in 1 each.
- Against HAR the W ensemble is at −6.8 % (1 week), −6.5 % (4 weeks), −2.0 % (13 weeks); B at
  −6.9 %, −7.4 %, −2.5 %.
- Seed spread of the W ensemble is 0.04–0.17 % of the loss, as stable as B. The V and G colonies
  end in dense formulas (18–30 literals), Z's in about 14 units of inclusion spread over all
  groups; their ensembles are as poor as their winners.

## 5. Reading

The limit is not the optimiser or the search space, it is what is optimised. The fitness is a
validation loss on four overlapping 78-week windows of one series. Selection among 2 000
candidates lowers it by 14–35 %, the same on synthetic panels with and without signal, and on
rows the search has not used the winner is worse than the prior for every search and every
target type. A stronger ABC on this fitness is a weaker forecaster.

What could change that (none of it run; each needs its own dated spec):
1. Pooled fitness: one formula per asset class, the fitness being the mean loss over all its
   series (5–8 times the data behind every evaluation). This is the change that addresses the
   noise directly.
2. Noise-aware replacement: a food source is replaced only if the candidate is better by more
   than the standard error across folds.
3. ABC as an ensemble generator only, with the spread start: what works today.

The prior formulas are still the generic r8 ones.

## 6. Limits

- Tails at q = 10 % only. Monthly 12-month returns have no unused outer rows, so the tested
  winner equals E1 there by construction.
- Threshold 0.5, "not used" below 0.1 and the move constants were not tuned; the move rate was
  chosen on synthetic data by inner fit, which is the quantity that turned out not to matter.
- The graded formulas are a different model class (a logical aggregation), not only another way
  of searching.
- The spec was frozen by Claude Code on the owner's instruction, without a separate approval.
