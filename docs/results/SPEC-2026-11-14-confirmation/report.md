# SPEC-2026-11-14-confirmation: the frozen final method on the confirmation series

21 series, 210 cells, test period 2018-10-05 to 2026-09-18. One run. Decisions below are made by the rules written in the spec before any of these numbers existed. Relative differences in the primary loss, a minus b (negative = a better), all series pooled on the same dates, 95 % date-block bootstrap.

## 1. The claims

### Primary

| claim   | statement                                                                                                                     | result                                                                                                                | decision   | development (weekly series; decisions were not made there)                                                            |
|:--------|:------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------|:-----------|:----------------------------------------------------------------------------------------------------------------------|
| P1      | Volatility at 1 week: interpretable reading better than HAR                                                                   | -8.3 % (-12.7 to -4.6), p = 0.000; Holm-adjusted p = 0.000                                                            | CONFIRMED  | -7.2 % (-11.6 to -3.8), p = 0.000; Holm-adjusted p = 0.000                                                            |
| P2      | Volatility at 4 weeks: interpretable reading better than HAR                                                                  | -8.8 % (-17.6 to -3.4), p = 0.024; Holm-adjusted p = 0.024                                                            | CONFIRMED  | -7.8 % (-15.7 to -2.7), p = 0.028; Holm-adjusted p = 0.028                                                            |
| P3      | Parity with group PCA: upper end of the interval below +3 % in at least 9 of 10 tasks, group PCA significantly better in none | below the margin in 10 of 10; group PCA significantly better in 0; mean difference -0.73 %; largest upper end +1.62 % | CONFIRMED  | below the margin in 10 of 10; group PCA significantly better in 0; mean difference -0.64 %; largest upper end +1.44 % |

### Secondary

| claim   | statement                                                                                                                                    | result                                                                                                                                                                                                       | decision   | development (weekly series; decisions were not made there)                                                                                                                                                    |
|:--------|:---------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| S1      | Volatility at 13 weeks against HAR (no direction claimed)                                                                                    | -3.1 % (-7.5 to -0.2), p = 0.080                                                                                                                                                                             | reported   | -2.5 % (-6.0 to -0.2), p = 0.074                                                                                                                                                                              |
| S2      | Accuracy reading better than the interpretable one in more tasks than worse                                                                  | -0.17 % (2 better, 0 worse of 10)                                                                                                                                                                            | holds      | -0.18 % (5 better, 0 worse of 10)                                                                                                                                                                             |
| S3      | On volatility the interpretable reading is better than PCA, kernel PCA and the autoencoder in at least 2 of 3 horizons each                  | PCA: -2.95 % (3 better, 0 worse of 3); kernel PCA: -5.31 % (3 better, 0 worse of 3); autoencoder: -3.53 % (3 better, 0 worse of 3)                                                                           | holds      | PCA: not available; kernel PCA: -4.66 % (3 better, 0 worse of 3); autoencoder: -3.00 % (3 better, 0 worse of 3)                                                                                               |
| S4      | Against random formulas: better on volatility in at least 2 of 3 horizons; at most 1 significant difference in the return and tail tasks     | volatility: -3.77 % (3 better, 0 worse of 3); returns and tails: +0.07 % (0 better, 0 worse of 7)                                                                                                            | holds      | volatility: -3.36 % (3 better, 0 worse of 3); returns and tails: +0.01 % (1 better, 0 worse of 7)                                                                                                             |
| S5      | No factor method is significantly better than the reference in any return or large-loss task                                                 | none                                                                                                                                                                                                         | holds      | none                                                                                                                                                                                                          |
| S6      | Elicited and generic formulas at parity: at most 1 task with a significant difference                                                        | -0.62 % (1 better, 0 worse of 10)                                                                                                                                                                            | holds      | -0.31 % (0 better, 0 worse of 10)                                                                                                                                                                             |
| S7      | Trees do not help: XGBoost and LightGBM significantly worse than the linear model in more tasks than better (IBA, raw factors, group PCA)    | Kc+xgb: 0 better, 9 worse of 10; Kc+gbt: 0 better, 8 worse of 10; raw+xgb: 0 better, 7 worse of 10; raw+gbt: 0 better, 7 worse of 10; gpca+xgb: 0 better, 10 worse of 10; gpca+gbt: 0 better, 10 worse of 10 | holds      | Kc+xgb: 0 better, 10 worse of 10; Kc+gbt: 0 better, 9 worse of 10; raw+xgb: 0 better, 8 worse of 10; raw+gbt: 0 better, 7 worse of 10; gpca+xgb: 0 better, 10 worse of 10; gpca+gbt: 0 better, 10 worse of 10 |
| S8      | Large gains: the volatility-based logit has the lower loss than the interpretable reading in every large-gain task                           | tail_gain_q10_h13: -5.1 %; tail_gain_q10_h4: -3.5 %                                                                                                                                                          | holds      | not available                                                                                                                                                                                                 |
| S9      | One-week 1 % value at risk: lower quantile loss than HAR                                                                                     | -7.9 % (better)                                                                                                                                                                                              | holds      |                                                                                                                                                                                                               |
| S10     | Long/flat rule at one week: higher Sharpe ratio than buy-and-hold in at least 15 of 21 series, and a smaller maximum drawdown in at least 15 | Sharpe 0.68 against 0.56, higher in 16; drawdown 24.6 % against 37.7 %, smaller in 17; after 10 bp per switch Sharpe 0.59 against 0.56, higher in 11                                                         | holds      |                                                                                                                                                                                                               |
| S11     | Large gains as a classifier: Matthews correlation below that of the volatility-based logit                                                   | 0.106 against 0.183                                                                                                                                                                                          | holds      |                                                                                                                                                                                                               |

## 2. Every configuration

Cell: mean relative difference; tasks where the interval excludes zero (b = a better, w = a worse).

### 2a. Against the type's reference (historical mean / HAR / base rate)

| a                                  | against   | return               | logrv                | tail_loss           | tail_gain           | all tasks               |
|:-----------------------------------|:----------|:---------------------|:---------------------|:--------------------|:--------------------|:------------------------|
| IBA interpretable (fixed formulas) | REF       | +1.52 % (0b 0w / 3)  | -6.74 % (3b 0w / 3)  | +0.43 % (0b 1w / 2) | -1.50 % (1b 0w / 2) | 4 better, 1 worse of 10 |
| IBA accuracy (ABC colony)          | REF       | +1.20 % (0b 0w / 3)  | -6.81 % (3b 0w / 3)  | +0.24 % (0b 1w / 2) | -1.58 % (1b 0w / 2) | 4 better, 1 worse of 10 |
| IBA no-search colony               | REF       | +1.33 % (0b 0w / 3)  | -6.82 % (3b 0w / 3)  | +0.34 % (0b 1w / 2) | -1.52 % (1b 0w / 2) | 4 better, 1 worse of 10 |
| IBA tested ABC winner              | REF       | +1.47 % (0b 0w / 3)  | -6.38 % (2b 0w / 3)  | +0.75 % (0b 1w / 2) | -1.53 % (1b 0w / 2) | 3 better, 1 worse of 10 |
| IBA generic formulas               | REF       | +1.57 % (0b 1w / 3)  | -5.64 % (2b 0w / 3)  | +0.30 % (0b 1w / 2) | -0.09 % (0b 0w / 2) | 2 better, 2 worse of 10 |
| random formulas (mean loss)        | REF       | +0.86 % (0b 1w / 3)  | -3.10 % (2b 0w / 3)  | +0.27 % (0b 0w / 2) | -0.61 % (0b 0w / 2) | 2 better, 1 worse of 10 |
| raw factors                        | REF       | +3.56 % (0b 2w / 3)  | -5.16 % (2b 0w / 3)  | +1.06 % (0b 1w / 2) | +0.26 % (0b 0w / 2) | 2 better, 3 worse of 10 |
| PCA                                | REF       | +1.11 % (0b 2w / 3)  | -3.92 % (2b 0w / 3)  | +0.62 % (0b 1w / 2) | -1.07 % (1b 0w / 2) | 3 better, 3 worse of 10 |
| group PCA                          | REF       | +2.05 % (0b 2w / 3)  | -5.50 % (2b 0w / 3)  | +0.83 % (0b 1w / 2) | -0.96 % (1b 0w / 2) | 3 better, 3 worse of 10 |
| LASSO                              | REF       | +2.55 % (0b 1w / 3)  | -4.28 % (2b 0w / 3)  | +0.42 % (0b 0w / 2) | -0.81 % (1b 0w / 2) | 3 better, 1 worse of 10 |
| kernel PCA                         | REF       | +0.71 % (0b 2w / 3)  | -1.53 % (2b 0w / 3)  | +0.66 % (0b 1w / 2) | -0.04 % (0b 1w / 2) | 2 better, 4 worse of 10 |
| autoencoder                        | REF       | +0.94 % (0b 2w / 3)  | -3.34 % (2b 0w / 3)  | +0.64 % (0b 1w / 2) | -1.09 % (1b 0w / 2) | 3 better, 3 worse of 10 |
| IBA K + XGBoost                    | REF       | +8.20 % (0b 3w / 3)  | -3.87 % (2b 0w / 3)  | +4.50 % (0b 2w / 2) | +2.19 % (0b 1w / 2) | 2 better, 6 worse of 10 |
| IBA K + LightGBM                   | REF       | +7.09 % (0b 1w / 3)  | -3.97 % (2b 0w / 3)  | +4.85 % (0b 2w / 2) | +2.50 % (0b 1w / 2) | 2 better, 4 worse of 10 |
| raw + XGBoost                      | REF       | +6.44 % (0b 1w / 3)  | -2.13 % (1b 0w / 3)  | +4.06 % (0b 1w / 2) | +1.98 % (0b 1w / 2) | 1 better, 3 worse of 10 |
| group PCA + XGBoost                | REF       | +10.73 % (0b 3w / 3) | -2.81 % (2b 0w / 3)  | +5.01 % (0b 2w / 2) | +2.66 % (0b 1w / 2) | 2 better, 6 worse of 10 |
| trailing momentum                  | REF       | +15.14 % (0b 3w / 3) |                      |                     |                     | 0 better, 3 worse of 3  |
| GARCH                              | REF       |                      | +12.87 % (0b 1w / 3) |                     |                     | 0 better, 1 worse of 3  |
| GJR-GARCH                          | REF       |                      | +7.73 % (0b 1w / 3)  |                     |                     | 0 better, 1 worse of 3  |
| volatility-based logit             | REF       |                      |                      | +1.60 % (0b 1w / 2) | -5.78 % (1b 0w / 2) | 1 better, 1 worse of 4  |
| GARCH-based probability            | REF       |                      |                      | +3.21 % (0b 0w / 2) | -6.38 % (1b 0w / 2) | 1 better, 0 worse of 4  |

### 2b. Against group PCA

| a                                  | against   | return               | logrv                | tail_loss           | tail_gain           | all tasks                |
|:-----------------------------------|:----------|:---------------------|:---------------------|:--------------------|:--------------------|:-------------------------|
| IBA interpretable (fixed formulas) | gpca|lin  | -0.52 % (0b 0w / 3)  | -1.29 % (2b 0w / 3)  | -0.39 % (0b 0w / 2) | -0.54 % (0b 0w / 2) | 2 better, 0 worse of 10  |
| IBA accuracy (ABC colony)          | gpca|lin  | -0.83 % (0b 0w / 3)  | -1.36 % (2b 0w / 3)  | -0.58 % (1b 0w / 2) | -0.62 % (0b 0w / 2) | 3 better, 0 worse of 10  |
| IBA no-search colony               | gpca|lin  | -0.70 % (0b 0w / 3)  | -1.37 % (2b 0w / 3)  | -0.48 % (1b 0w / 2) | -0.56 % (0b 0w / 2) | 3 better, 0 worse of 10  |
| IBA tested ABC winner              | gpca|lin  | -0.57 % (0b 0w / 3)  | -0.91 % (0b 0w / 3)  | -0.08 % (0b 0w / 2) | -0.57 % (0b 0w / 2) | 0 better, 0 worse of 10  |
| IBA generic formulas               | gpca|lin  | -0.47 % (0b 0w / 3)  | -0.12 % (0b 0w / 3)  | -0.53 % (1b 0w / 2) | +0.88 % (0b 1w / 2) | 1 better, 1 worse of 10  |
| random formulas (mean loss)        | gpca|lin  | -1.15 % (1b 0w / 3)  | +2.60 % (0b 2w / 3)  | -0.55 % (0b 0w / 2) | +0.35 % (0b 1w / 2) | 1 better, 3 worse of 10  |
| raw factors                        | gpca|lin  | +1.47 % (0b 0w / 3)  | +0.35 % (0b 0w / 3)  | +0.22 % (0b 0w / 2) | +1.23 % (0b 0w / 2) | 0 better, 0 worse of 10  |
| PCA                                | gpca|lin  | -0.92 % (2b 0w / 3)  | +1.71 % (0b 2w / 3)  | -0.21 % (0b 0w / 2) | -0.11 % (0b 0w / 2) | 2 better, 2 worse of 10  |
| LASSO                              | gpca|lin  | +0.49 % (0b 0w / 3)  | +1.28 % (0b 0w / 3)  | -0.41 % (0b 0w / 2) | +0.15 % (0b 0w / 2) | 0 better, 0 worse of 10  |
| kernel PCA                         | gpca|lin  | -1.31 % (1b 0w / 3)  | +4.28 % (0b 2w / 3)  | -0.16 % (0b 0w / 2) | +0.93 % (0b 1w / 2) | 1 better, 3 worse of 10  |
| autoencoder                        | gpca|lin  | -1.08 % (2b 0w / 3)  | +2.34 % (0b 2w / 3)  | -0.19 % (0b 0w / 2) | -0.13 % (0b 0w / 2) | 2 better, 2 worse of 10  |
| IBA K + XGBoost                    | gpca|lin  | +6.03 % (0b 2w / 3)  | +1.75 % (0b 1w / 3)  | +3.64 % (0b 2w / 2) | +3.18 % (0b 2w / 2) | 0 better, 7 worse of 10  |
| IBA K + LightGBM                   | gpca|lin  | +4.94 % (0b 1w / 3)  | +1.65 % (0b 1w / 3)  | +3.99 % (0b 2w / 2) | +3.49 % (0b 2w / 2) | 0 better, 6 worse of 10  |
| raw + XGBoost                      | gpca|lin  | +4.27 % (0b 1w / 3)  | +3.55 % (0b 2w / 3)  | +3.20 % (0b 1w / 2) | +2.96 % (0b 2w / 2) | 0 better, 6 worse of 10  |
| group PCA + XGBoost                | gpca|lin  | +8.52 % (0b 3w / 3)  | +2.84 % (0b 3w / 3)  | +4.15 % (0b 2w / 2) | +3.65 % (0b 2w / 2) | 0 better, 10 worse of 10 |
| trailing momentum                  | gpca|lin  | +12.71 % (0b 2w / 3) |                      |                     |                     | 0 better, 2 worse of 3   |
| GARCH                              | gpca|lin  |                      | +19.60 % (0b 2w / 3) |                     |                     | 0 better, 2 worse of 3   |
| GJR-GARCH                          | gpca|lin  |                      | +14.13 % (0b 2w / 3) |                     |                     | 0 better, 2 worse of 3   |
| volatility-based logit             | gpca|lin  |                      |                      | +0.77 % (0b 0w / 2) | -4.85 % (1b 0w / 2) | 1 better, 0 worse of 4   |
| GARCH-based probability            | gpca|lin  |                      |                      | +2.36 % (0b 0w / 2) | -5.47 % (1b 0w / 2) | 1 better, 0 worse of 4   |

### 2c. Against the interpretable reading

| a                           | against   | return               | logrv                | tail_loss           | tail_gain           | all tasks                |
|:----------------------------|:----------|:---------------------|:---------------------|:--------------------|:--------------------|:-------------------------|
| IBA accuracy (ABC colony)   | Kc|lin    | -0.31 % (1b 0w / 3)  | -0.07 % (0b 0w / 3)  | -0.19 % (1b 0w / 2) | -0.08 % (0b 0w / 2) | 2 better, 0 worse of 10  |
| IBA no-search colony        | Kc|lin    | -0.18 % (1b 0w / 3)  | -0.08 % (1b 0w / 3)  | -0.09 % (1b 0w / 2) | -0.02 % (0b 0w / 2) | 3 better, 0 worse of 10  |
| IBA tested ABC winner       | Kc|lin    | -0.05 % (0b 0w / 3)  | +0.39 % (0b 1w / 3)  | +0.32 % (0b 0w / 2) | -0.03 % (0b 0w / 2) | 0 better, 1 worse of 10  |
| IBA generic formulas        | Kc|lin    | +0.05 % (0b 0w / 3)  | +1.18 % (0b 0w / 3)  | -0.13 % (0b 0w / 2) | +1.43 % (0b 1w / 2) | 0 better, 1 worse of 10  |
| random formulas (mean loss) | Kc|lin    | -0.64 % (0b 0w / 3)  | +3.94 % (0b 3w / 3)  | -0.16 % (0b 0w / 2) | +0.90 % (0b 0w / 2) | 0 better, 3 worse of 10  |
| raw factors                 | Kc|lin    | +2.01 % (0b 1w / 3)  | +1.67 % (0b 1w / 3)  | +0.62 % (0b 0w / 2) | +1.78 % (0b 1w / 2) | 0 better, 3 worse of 10  |
| PCA                         | Kc|lin    | -0.40 % (0b 0w / 3)  | +3.04 % (0b 3w / 3)  | +0.19 % (0b 0w / 2) | +0.44 % (0b 0w / 2) | 0 better, 3 worse of 10  |
| group PCA                   | Kc|lin    | +0.53 % (0b 0w / 3)  | +1.32 % (0b 2w / 3)  | +0.40 % (0b 0w / 2) | +0.55 % (0b 0w / 2) | 0 better, 2 worse of 10  |
| LASSO                       | Kc|lin    | +1.02 % (0b 0w / 3)  | +2.62 % (0b 2w / 3)  | -0.01 % (0b 0w / 2) | +0.70 % (0b 0w / 2) | 0 better, 2 worse of 10  |
| kernel PCA                  | Kc|lin    | -0.80 % (0b 0w / 3)  | +5.64 % (0b 3w / 3)  | +0.23 % (0b 0w / 2) | +1.48 % (0b 0w / 2) | 0 better, 3 worse of 10  |
| autoencoder                 | Kc|lin    | -0.56 % (0b 0w / 3)  | +3.68 % (0b 3w / 3)  | +0.20 % (0b 0w / 2) | +0.42 % (0b 0w / 2) | 0 better, 3 worse of 10  |
| IBA K + XGBoost             | Kc|lin    | +6.58 % (0b 2w / 3)  | +3.09 % (0b 3w / 3)  | +4.05 % (0b 2w / 2) | +3.75 % (0b 2w / 2) | 0 better, 9 worse of 10  |
| IBA K + LightGBM            | Kc|lin    | +5.49 % (0b 1w / 3)  | +2.98 % (0b 3w / 3)  | +4.40 % (0b 2w / 2) | +4.05 % (0b 2w / 2) | 0 better, 8 worse of 10  |
| raw + XGBoost               | Kc|lin    | +4.83 % (0b 1w / 3)  | +4.92 % (0b 3w / 3)  | +3.61 % (0b 2w / 2) | +3.53 % (0b 2w / 2) | 0 better, 8 worse of 10  |
| group PCA + XGBoost         | Kc|lin    | +9.09 % (0b 3w / 3)  | +4.19 % (0b 3w / 3)  | +4.57 % (0b 2w / 2) | +4.22 % (0b 2w / 2) | 0 better, 10 worse of 10 |
| trailing momentum           | Kc|lin    | +13.34 % (0b 2w / 3) |                      |                     |                     | 0 better, 2 worse of 3   |
| GARCH                       | Kc|lin    |                      | +21.13 % (0b 2w / 3) |                     |                     | 0 better, 2 worse of 3   |
| GJR-GARCH                   | Kc|lin    |                      | +15.60 % (0b 2w / 3) |                     |                     | 0 better, 2 worse of 3   |
| volatility-based logit      | Kc|lin    |                      |                      | +1.17 % (0b 0w / 2) | -4.34 % (1b 0w / 2) | 1 better, 0 worse of 4   |
| GARCH-based probability     | Kc|lin    |                      |                      | +2.76 % (0b 0w / 2) | -4.95 % (1b 0w / 2) | 1 better, 0 worse of 4   |

## 3. By asset class (descriptive; loss relative to the reference, %, per target type)

| class                 |   series | method                             |   logrv |   return |   tail_gain |   tail_loss |
|:----------------------|---------:|:-----------------------------------|--------:|---------:|------------:|------------:|
| bonds_gov_ig          |        3 | IBA accuracy (ABC colony)          |    -0.9 |      1.9 |        -0.3 |         0.7 |
| bonds_gov_ig          |        3 | IBA interpretable (fixed formulas) |    -0.9 |      1.9 |        -0.1 |         0.8 |
| bonds_gov_ig          |        3 | group PCA                          |    -1.8 |      2.8 |        -0   |         0.3 |
| commodities           |        3 | IBA accuracy (ABC colony)          |    -5.6 |      0.8 |        -0.5 |         0.5 |
| commodities           |        3 | IBA interpretable (fixed formulas) |    -5.1 |      1.2 |        -0.6 |         0.3 |
| commodities           |        3 | group PCA                          |    -3.8 |      0.5 |         0.7 |         3.3 |
| equity_developed_exus |        6 | IBA accuracy (ABC colony)          |    -8.7 |      0.9 |        -3   |         0.4 |
| equity_developed_exus |        6 | IBA interpretable (fixed formulas) |    -8.6 |      1.3 |        -3   |         0.9 |
| equity_developed_exus |        6 | group PCA                          |    -6.9 |      3.2 |        -2   |         0.6 |
| equity_emerging       |        2 | IBA accuracy (ABC colony)          |    -4.8 |      2   |        -0.6 |         0   |
| equity_emerging       |        2 | IBA interpretable (fixed formulas) |    -4.8 |      2.4 |        -0.3 |         0.3 |
| equity_emerging       |        2 | group PCA                          |    -3.6 |      3.9 |        -0.4 |         1.7 |
| equity_us_broad       |        2 | IBA accuracy (ABC colony)          |   -11   |      1.3 |        -1.7 |         0   |
| equity_us_broad       |        2 | IBA interpretable (fixed formulas) |   -11.2 |      1.6 |        -1.5 |         0.2 |
| equity_us_broad       |        2 | group PCA                          |    -9   |      1.1 |        -1   |         0.9 |
| equity_us_sectors     |        4 | IBA accuracy (ABC colony)          |    -9.7 |      1.1 |        -2.4 |        -0.3 |
| equity_us_sectors     |        4 | IBA interpretable (fixed formulas) |   -10   |      1.3 |        -2.5 |        -0.2 |
| equity_us_sectors     |        4 | group PCA                          |    -7.5 |      1.8 |        -1.8 |         0.2 |
| real_estate           |        1 | IBA accuracy (ABC colony)          |    -5.5 |      2.3 |        -0.2 |         0.2 |
| real_estate           |        1 | IBA interpretable (fixed formulas) |    -4.8 |      2.4 |        -0   |         0   |
| real_estate           |        1 | group PCA                          |    -4.2 |      2.6 |        -1.9 |         0.5 |

## 4. Financial and classification measures

In `extra/extra_metrics.md`, with the tables behind claims S9 to S11.
