# SPEC-2026-11-15-confirmation-hf: the frozen final method on hedge-fund indices of a second provider

23 series, 184 cells, test period 2018-09-30 to 2026-08-31. One run. No series was dropped. Decisions below are made by the rules written in the spec before any of these numbers existed. Relative differences in the primary loss, a minus b (negative = a better), all series pooled on the same dates, 95 % date-block bootstrap.

## 1. The claims

### Primary

| claim   | statement                                                                                                                           | result                                                                                                                                                                                 | decision   | development (11 CISDM indices; decisions were not made there)                                                                                                                          |
|:--------|:------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| H1      | No factor method (the two IBA readings and the six reductions, linear model) is significantly better than the reference in any task | none                                                                                                                                                                                   | CONFIRMED  | none                                                                                                                                                                                   |
| H2      | Group PCA is significantly better than the interpretable reading in at most 1 task                                                  | group PCA significantly better in 1 of 8; interpretable reading significantly better in 0; mean difference +0.68 %; upper end of the interval below +3 % in 4 of 8 (reported, no rule) | CONFIRMED  | group PCA significantly better in 1 of 8; interpretable reading significantly better in 0; mean difference +1.10 %; upper end of the interval below +3 % in 4 of 8 (reported, no rule) |

### Secondary and reported

| claim   | statement                                                                                                                                 | result                                                                                                                                                                                               | decision   | development (11 CISDM indices; decisions were not made there)                                                                                                                                        |
|:--------|:------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| H3      | Accuracy reading better than the interpretable one in more tasks than worse                                                               | -0.52 % (1 better, 0 worse of 8)                                                                                                                                                                     | holds      | -0.47 % (2 better, 0 worse of 8)                                                                                                                                                                     |
| H4      | Elicited formulas at parity with generic and with random formulas: at most 1 task with a significant difference against each              | against generic: +0.07 % (0 better, 0 worse of 8); against random: +0.06 % (0 better, 0 worse of 8)                                                                                                  | holds      | against generic: +1.04 % (0 better, 0 worse of 8); against random: +0.29 % (0 better, 0 worse of 8)                                                                                                  |
| H5      | Trees do not help: XGBoost and LightGBM significantly worse than the linear model in more tasks than better (IBA, raw factors, group PCA) | Kc+xgb: 0 better, 6 worse of 8; Kc+gbt: 0 better, 3 worse of 8; raw+xgb: 0 better, 4 worse of 8; raw+gbt: 0 better, 4 worse of 8; gpca+xgb: 0 better, 4 worse of 8; gpca+gbt: 0 better, 6 worse of 8 | holds      | Kc+xgb: 0 better, 4 worse of 8; Kc+gbt: 0 better, 3 worse of 8; raw+xgb: 0 better, 4 worse of 8; raw+gbt: 0 better, 4 worse of 8; gpca+xgb: 0 better, 4 worse of 8; gpca+gbt: 0 better, 5 worse of 8 |
| H6      | The interpretable reading against the reference, by target (no direction claimed)                                                         | returns: +0.85 % (0 better, 0 worse of 4); large losses: +2.58 % (0 better, 1 worse of 2); large gains: +0.73 % (0 better, 0 worse of 2)                                                             | reported   | returns: +2.95 % (0 better, 1 worse of 4); large losses: +0.08 % (0 better, 0 worse of 2); large gains: +0.87 % (0 better, 1 worse of 2)                                                             |

## 2. Every configuration

Cell: mean relative difference; tasks where the interval excludes zero (b = a better, w = a worse).

### 2a. Against the type's reference (historical mean / base rate)

| a                                  | against   | return               | logrv   | tail_loss            | tail_gain           | all tasks              |
|:-----------------------------------|:----------|:---------------------|:--------|:---------------------|:--------------------|:-----------------------|
| IBA interpretable (fixed formulas) | REF       | +0.85 % (0b 0w / 4)  |         | +2.58 % (0b 1w / 2)  | +0.73 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| IBA accuracy (ABC colony)          | REF       | +0.55 % (0b 0w / 4)  |         | +1.48 % (0b 0w / 2)  | +0.27 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| IBA no-search colony               | REF       | +0.64 % (0b 0w / 4)  |         | +1.86 % (0b 1w / 2)  | +0.40 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| IBA tested ABC winner              | REF       | +1.02 % (0b 0w / 4)  |         | +3.45 % (0b 1w / 2)  | +0.68 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| IBA generic formulas               | REF       | +0.97 % (0b 0w / 4)  |         | +1.21 % (0b 0w / 2)  | +1.56 % (0b 2w / 2) | 0 better, 2 worse of 8 |
| random formulas (mean loss)        | REF       | +1.16 % (0b 0w / 4)  |         | +1.10 % (0b 1w / 2)  | +1.34 % (0b 2w / 2) | 0 better, 3 worse of 8 |
| raw factors                        | REF       | +3.97 % (0b 0w / 4)  |         | +5.50 % (0b 0w / 2)  | +2.63 % (0b 2w / 2) | 0 better, 2 worse of 8 |
| PCA                                | REF       | +1.56 % (0b 0w / 4)  |         | +0.83 % (0b 0w / 2)  | +0.50 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| group PCA                          | REF       | +0.72 % (0b 0w / 4)  |         | +0.22 % (0b 0w / 2)  | +0.61 % (0b 1w / 2) | 0 better, 1 worse of 8 |
| LASSO                              | REF       | +1.45 % (0b 0w / 4)  |         | +4.53 % (0b 1w / 2)  | +1.11 % (0b 2w / 2) | 0 better, 3 worse of 8 |
| kernel PCA                         | REF       | +0.34 % (0b 0w / 4)  |         | +2.05 % (0b 1w / 2)  | +1.50 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| autoencoder                        | REF       | +1.50 % (0b 0w / 4)  |         | +0.55 % (0b 0w / 2)  | +0.53 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| IBA K + XGBoost                    | REF       | +11.79 % (0b 3w / 4) |         | +10.71 % (0b 2w / 2) | +6.33 % (0b 1w / 2) | 0 better, 6 worse of 8 |
| IBA K + LightGBM                   | REF       | +6.46 % (0b 0w / 4)  |         | +13.44 % (0b 2w / 2) | +6.05 % (0b 1w / 2) | 0 better, 3 worse of 8 |
| raw + XGBoost                      | REF       | +15.02 % (0b 2w / 4) |         | +10.12 % (0b 2w / 2) | +8.20 % (0b 2w / 2) | 0 better, 6 worse of 8 |
| group PCA + XGBoost                | REF       | +11.82 % (0b 1w / 4) |         | +9.55 % (0b 1w / 2)  | +8.45 % (0b 2w / 2) | 0 better, 4 worse of 8 |
| trailing momentum                  | REF       | +58.60 % (0b 4w / 4) |         |                      |                     | 0 better, 4 worse of 4 |
| volatility-based logit             | REF       |                      |         | +6.42 % (0b 2w / 2)  | -3.25 % (0b 0w / 2) | 0 better, 2 worse of 4 |
| GARCH-based probability            | REF       |                      |         | +6.78 % (0b 1w / 2)  | -7.07 % (2b 0w / 2) | 2 better, 1 worse of 4 |

### 2b. Against group PCA

| a                                  | against   | return               | logrv   | tail_loss            | tail_gain           | all tasks              |
|:-----------------------------------|:----------|:---------------------|:--------|:---------------------|:--------------------|:-----------------------|
| IBA interpretable (fixed formulas) | gpca|lin  | +0.14 % (0b 0w / 4)  |         | +2.35 % (0b 1w / 2)  | +0.11 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| IBA accuracy (ABC colony)          | gpca|lin  | -0.16 % (0b 0w / 4)  |         | +1.26 % (0b 0w / 2)  | -0.34 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| IBA no-search colony               | gpca|lin  | -0.07 % (0b 0w / 4)  |         | +1.63 % (0b 1w / 2)  | -0.21 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| IBA tested ABC winner              | gpca|lin  | +0.31 % (0b 0w / 4)  |         | +3.22 % (0b 1w / 2)  | +0.07 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| IBA generic formulas               | gpca|lin  | +0.26 % (0b 0w / 4)  |         | +0.99 % (0b 0w / 2)  | +0.94 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| random formulas (mean loss)        | gpca|lin  | +0.46 % (0b 0w / 4)  |         | +0.87 % (0b 0w / 2)  | +0.73 % (0b 1w / 2) | 0 better, 1 worse of 8 |
| raw factors                        | gpca|lin  | +3.24 % (0b 0w / 4)  |         | +5.27 % (0b 0w / 2)  | +2.01 % (0b 2w / 2) | 0 better, 2 worse of 8 |
| PCA                                | gpca|lin  | +0.85 % (0b 0w / 4)  |         | +0.60 % (0b 0w / 2)  | -0.11 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| LASSO                              | gpca|lin  | +0.75 % (1b 0w / 4)  |         | +4.30 % (0b 1w / 2)  | +0.50 % (0b 0w / 2) | 1 better, 1 worse of 8 |
| kernel PCA                         | gpca|lin  | -0.36 % (0b 0w / 4)  |         | +1.82 % (0b 1w / 2)  | +0.88 % (0b 0w / 2) | 0 better, 1 worse of 8 |
| autoencoder                        | gpca|lin  | +0.80 % (0b 0w / 4)  |         | +0.32 % (0b 0w / 2)  | -0.08 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| IBA K + XGBoost                    | gpca|lin  | +10.95 % (0b 2w / 4) |         | +10.47 % (0b 2w / 2) | +5.68 % (0b 1w / 2) | 0 better, 5 worse of 8 |
| IBA K + LightGBM                   | gpca|lin  | +5.69 % (0b 0w / 4)  |         | +13.19 % (0b 2w / 2) | +5.40 % (0b 1w / 2) | 0 better, 3 worse of 8 |
| raw + XGBoost                      | gpca|lin  | +14.19 % (0b 3w / 4) |         | +9.87 % (0b 1w / 2)  | +7.54 % (0b 2w / 2) | 0 better, 6 worse of 8 |
| group PCA + XGBoost                | gpca|lin  | +10.99 % (0b 1w / 4) |         | +9.30 % (0b 1w / 2)  | +7.79 % (0b 2w / 2) | 0 better, 4 worse of 8 |
| trailing momentum                  | gpca|lin  | +57.47 % (0b 4w / 4) |         |                      |                     | 0 better, 4 worse of 4 |
| volatility-based logit             | gpca|lin  |                      |         | +6.18 % (0b 2w / 2)  | -3.84 % (0b 0w / 2) | 0 better, 2 worse of 4 |
| GARCH-based probability            | gpca|lin  |                      |         | +6.54 % (0b 1w / 2)  | -7.64 % (2b 0w / 2) | 2 better, 1 worse of 4 |

### 2c. Against the interpretable reading

| a                           | against   | return               | logrv   | tail_loss            | tail_gain           | all tasks              |
|:----------------------------|:----------|:---------------------|:--------|:---------------------|:--------------------|:-----------------------|
| IBA accuracy (ABC colony)   | Kc|lin    | -0.29 % (0b 0w / 4)  |         | -1.06 % (0b 0w / 2)  | -0.45 % (1b 0w / 2) | 1 better, 0 worse of 8 |
| IBA no-search colony        | Kc|lin    | -0.20 % (0b 0w / 4)  |         | -0.69 % (2b 0w / 2)  | -0.33 % (1b 0w / 2) | 3 better, 0 worse of 8 |
| IBA tested ABC winner       | Kc|lin    | +0.17 % (0b 0w / 4)  |         | +0.84 % (0b 0w / 2)  | -0.04 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| IBA generic formulas        | Kc|lin    | +0.13 % (0b 0w / 4)  |         | -1.32 % (0b 0w / 2)  | +0.83 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| random formulas (mean loss) | Kc|lin    | +0.33 % (0b 0w / 4)  |         | -1.42 % (0b 0w / 2)  | +0.61 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| raw factors                 | Kc|lin    | +3.10 % (0b 0w / 4)  |         | +2.81 % (0b 0w / 2)  | +1.89 % (0b 2w / 2) | 0 better, 2 worse of 8 |
| PCA                         | Kc|lin    | +0.72 % (0b 0w / 4)  |         | -1.68 % (0b 0w / 2)  | -0.23 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| group PCA                   | Kc|lin    | -0.13 % (0b 0w / 4)  |         | -2.27 % (1b 0w / 2)  | -0.11 % (0b 0w / 2) | 1 better, 0 worse of 8 |
| LASSO                       | Kc|lin    | +0.61 % (0b 0w / 4)  |         | +1.88 % (0b 0w / 2)  | +0.38 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| kernel PCA                  | Kc|lin    | -0.50 % (0b 0w / 4)  |         | -0.49 % (0b 0w / 2)  | +0.77 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| autoencoder                 | Kc|lin    | +0.67 % (0b 0w / 4)  |         | -1.96 % (0b 0w / 2)  | -0.19 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| IBA K + XGBoost             | Kc|lin    | +10.81 % (0b 3w / 4) |         | +7.93 % (0b 2w / 2)  | +5.56 % (0b 1w / 2) | 0 better, 6 worse of 8 |
| IBA K + LightGBM            | Kc|lin    | +5.56 % (0b 0w / 4)  |         | +10.58 % (0b 2w / 2) | +5.28 % (0b 1w / 2) | 0 better, 3 worse of 8 |
| raw + XGBoost               | Kc|lin    | +14.00 % (0b 2w / 4) |         | +7.40 % (0b 1w / 2)  | +7.41 % (0b 2w / 2) | 0 better, 5 worse of 8 |
| group PCA + XGBoost         | Kc|lin    | +10.84 % (0b 0w / 4) |         | +6.88 % (0b 1w / 2)  | +7.66 % (0b 2w / 2) | 0 better, 3 worse of 8 |
| trailing momentum           | Kc|lin    | +57.54 % (0b 4w / 4) |         |                      |                     | 0 better, 4 worse of 4 |
| volatility-based logit      | Kc|lin    |                      |         | +3.75 % (0b 1w / 2)  | -3.94 % (0b 0w / 2) | 0 better, 1 worse of 4 |
| GARCH-based probability     | Kc|lin    |                      |         | +4.14 % (0b 1w / 2)  | -7.75 % (2b 0w / 2) | 2 better, 1 worse of 4 |

## 3. Financial and classification measures

In `extra/extra_metrics.md` (descriptive; no claim rests on them).
