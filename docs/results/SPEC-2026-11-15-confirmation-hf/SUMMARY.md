# Results of SPEC-2026-11-15-confirmation-hf: the frozen method on BarclayHedge hedge-fund indices

Run 2026-11-15 12:45–13:21 on the Mac from the frozen spec (fingerprint `2bcaa0ad64aaa3ab35c5455d`;
the freeze commit is of 12:45, the spec text says 12:47). 23 monthly hedge-fund indices of a second
provider, 8 tasks, 184 cells × 7 formula sets = 1,288 cell runs, no failed cell, no series
dropped, no deviation. `report.md` is the pre-written analysis, unedited; this file reads it.

## 1. The claims

| Claim | Result | Development (11 CISDM indices) | Decision |
|---|---|---|---|
| H1. No factor method significantly better than the reference in any of the 8 tasks | none | none | **CONFIRMED** |
| H2. Group PCA significantly better than the interpretable reading in at most 1 task | 1 of 8 (large loss at 6 months, +4.0 %, 0.5 to 8.4); mean difference +0.7 %; upper end below +3 % in 4 of 8 | 1 of 8; +1.1 %; 4 of 8 | **CONFIRMED** |
| H3. Accuracy reading significantly better than the interpretable one in more tasks than worse | −0.5 %; 1 better, 0 worse | −0.5 %; 2 better, 0 worse | holds |
| H4. Elicited formulas at parity with generic and random ones (at most 1 significant difference each) | generic +0.1 %, 0 of 8; random +0.1 %, 0 of 8 | +1.0 %, 0; +0.3 %, 0 | holds |
| H5. Trees significantly worse than the linear model in more tasks than better, in each of six comparisons | worse in 3 to 6 of 8, better in none | worse in 3 to 5, better in none | holds |
| H6. Interpretable reading against the reference, by target | returns +0.85 %; large losses +2.6 % (significantly worse in 1 of 2); large gains +0.7 % | +2.9 %; +0.1 %; +0.9 % | reported |

## 2. What it says

- **The development picture repeats on another provider's indices.** No reduction of the factor
  panel forecasts hedge-fund returns or tail events better than the historical mean or the base
  rate. The interpretable reading is 0.85 % behind the historical mean on returns (development
  2.9 %), not significantly in any task.
- **The same weak spot as on the development indices:** large losses at 6 months, where the
  interpretable reading is 4.0 % behind the base rate and behind group PCA, significantly. The
  accuracy reading is not significantly behind in any task (large losses +1.5 %).
- **Against group PCA the method is level**, not within the 3 % margin of the weekly claims: the
  intervals are wide (upper ends up to +10 % at 6 months), as on the development indices. This
  was not claimed and is not shown.
- **Content of the formulas does not matter here:** elicited, generic and random formulas are
  within 0.1 % of each other. Consistent with the weekly result that content matters only where
  there is signal.
- **Not about factor methods, but worth stating:** the GARCH-based probability is significantly
  better than the base rate for large gains in both tasks (−7.1 %), and the volatility-based
  logit is 3.3 % better (not significant). For large losses both are worse. As on the weekly
  series, recent volatility says more about a large gain than the factor states do.
- **Financial readings (descriptive; the indices are not investable).** One-month long/flat
  rule on the IBA forecasts: Sharpe ratio 1.04 against 0.97, higher in 12 of 23 series; maximum
  drawdown 13.3 % against 16.1 %, smaller in 12 of 23. About half the series either way: no
  evidence of an advantage. As a classifier of large gains the IBA forecasts have a Matthews
  correlation of 0.09 (volatility logit 0.20); of large losses 0.05.

## 3. Limits

A BarclayHedge index and the CISDM index of the same strategy average many of the same funds, and
both sets cover the same years: the run shows robustness to the provider and to the construction
of the index and adds sector and regional indices; it is not independent evidence. The September
2026 value of every index is the provider's estimate (one test label in 96). The claims were of
absence and were expected to be confirmed.
