# Results of SPEC-2026-11-14-confirmation: the frozen final method on the held-out series

One run, 2026-11-15 01:18–02:22 on the Mac, from the frozen spec (version 2; fingerprint
`2bcaa0ad64aaa3ab35c5455d`, XGBoost and benchmark hashes reproduced). 21 series that had never
been downloaded or loaded, 210 cells, 7 formula sets, 1,470 cell runs, no failure; 11,340
registry rows with split `confirmation`. Download: `data/raw/yahoo_daily_conf_2026-11-15.csv`
(sha256 `97b01bb6…fe8fbe`), all 21 series passed the coverage check. Test period 5 October 2018
to 18 September 2026 (416 weeks). `report.md`, `claims.csv` and `extra/` are the pre-written
report's output, unedited; this file reads them. No deviation was recorded for this run.

## 1. The three primary claims: all confirmed

| | Claim | Confirmation | Development (37 weekly series) | Decision |
|---|---|---|---|---|
| P1 | Volatility at 1 week: lower loss than HAR | −8.3 % (−12.7 to −4.6), Holm p < 0.001 | −7.2 % (−11.6 to −3.8) | **CONFIRMED** |
| P2 | Volatility at 4 weeks: lower loss than HAR | −8.8 % (−17.6 to −3.4), Holm p = 0.024 | −7.8 % (−15.7 to −2.7) | **CONFIRMED** |
| P3 | Parity with group PCA within 3 % in at least 9 of 10 tasks, group PCA significantly better in none | within the margin in 10 of 10; largest upper end +1.6 %; mean difference −0.7 %; group PCA better in 0 | 10 of 10; +1.4 %; −0.6 % | **CONFIRMED** |

## 2. The secondary claims: all hold

- S1 (13 weeks, no direction claimed): −3.1 % against HAR (−7.5 to −0.2), bootstrap p = 0.08.
- S2: the accuracy reading (ABC colony of the development pools) is better than the
  interpretable one in 2 tasks and worse in none (−0.17 %).
- S3: on volatility the interpretable reading beats PCA (−2.9 %), kernel PCA (−5.3 %) and the
  autoencoder (−3.5 %) at all three horizons.
- S4: against random formulas, better on volatility at all three horizons (−3.8 %); no
  significant difference in any of the seven return and tail tasks.
- S5: no factor method is significantly better than the reference in any return or large-loss
  task.
- S6: elicited against generic formulas: one significant difference in ten tasks (−0.6 %).
- S7: XGBoost and LightGBM are significantly worse than the linear model in 7 to 10 of 10 tasks
  on IBA features, raw factors and group PCA, and better in none.
- S8, S11: for large gains the volatility-based logit is better than IBA in both tasks (−3.5 %,
  −5.1 %) and classifies better (Matthews correlation 0.183 against 0.106).
- S9: one-week 1 % value at risk has a 7.9 % lower quantile loss than HAR's (significant).
- S10: the long/flat rule at one week has a Sharpe ratio of 0.68 against 0.56 for buy-and-hold,
  higher in 16 of 21 series, and a drawdown of 25 % against 38 %, smaller in 17. **After 10 basis
  points per switch the Sharpe ratio is 0.59 against 0.56 and higher in only 11 of 21 series**: the
  claim holds as written (it was stated without costs) and does not survive costs.
- S12 (descriptive): against HAR the loss is −18.8 % in the COVID-19 crash, −3.3 % in 2022,
  +2.5 % in the fourth quarter of 2018, −5.3 % elsewhere; −10.7 % on dates when the index is at
  least 10 % below its peak against −4.5 % otherwise.

## 3. Reading

- The confirmation numbers repeat the development ones closely, a little stronger on volatility.
  Volatility against HAR by horizon: −8.3 / −8.8 / −3.1 % (development −7.2 / −7.8 / −2.5 %).
- The gain is not specific to IBA in size: group PCA has −8.3 / −7.3 / −1.0 % and raw factors
  −8.0 / −7.1 / −0.3 %. What IBA adds over group PCA is 1.3 % on volatility (significant at 2 of 3
  horizons), most of it at 13 weeks, and the readable form. Against kernel PCA and the
  autoencoder the margin is 3.5 to 5.3 %.
- By asset class the volatility gain is largest for equity (US broad −11 %, US sectors −10 %,
  developed markets −9 %) and smallest for bonds (−1 %).
- Returns: every method is behind the historical mean (IBA +1.5 %); tails: large losses at the
  base rate, large gains better predicted by volatility-based probabilities than by any factor
  method. As on the development series.
- GARCH and GJR-GARCH are 13 % and 8 % worse than HAR in squared error of log variance, yet
  give value-at-risk forecasts about as good as the factor methods at 1 and 4 weeks and better
  at 13 weeks.

## 4. Limits

- The confirmation series cover the same period as the development series and are correlated
  with them (the realised log variance of QQQ and SPY has a correlation of 0.91). The close
  agreement of the two sets is partly that: the same dates dominate both. The run shows that the
  results do not depend on the particular series; it does not show that they hold in another
  period.
- 21 series, all weekly; no hedge-fund index and no high-yield or emerging-market debt.
- The decision rules of the secondary claims, the crisis periods and the drawdown threshold were
  fixed by Claude Code in the frozen spec without a separate approval of their details.
- The trading rule ignores costs in its claim; with costs the advantage is not there.

## Addendum (15 Nov, after the summary was written; descriptive, no new run)

The engine stores secondary losses with every forecast (QLIKE, log score, AUC, calibration
error); the pre-written report does not tabulate them. `scripts/make_paper_tables.py` now does
(Table F5 of the paper, means over the 21 series, no test):

- **QLIKE against HAR.** Interpretable reading −12.4 % / −10.7 % / −4.3 % at 1 / 4 / 13 weeks;
  group PCA −12.6 / −9.3 / −0.6; raw factors −12.1 / −12.2 / −0.8. The picture against HAR and
  the other reductions is the same as under the primary loss.
- **GARCH under QLIKE.** −6.2 % / −13.5 % / −20.7 % against HAR: ahead of every factor method at
  4 and 13 weeks, although GARCH is 11 to 15 % behind HAR in squared log error. QLIKE scores the
  variance level, which GARCH forecasts directly; the other models forecast the logarithm. The
  development series show the same (IBA −10.9 / −10.4 / −3.9; GARCH −6.0 / −13.1 / −19.3).
- **Tail events.** Log score against the base rate: large loss +0.8 % (AUC 0.53), large gain
  −1.7 % (AUC 0.60; volatility logit −6.1 %, AUC 0.68). Calibration error 5 to 7 % for every method.

The claims were fixed for the log variance and are not affected; the paper states the QLIKE
result in Section 6.3 and among the limits.
