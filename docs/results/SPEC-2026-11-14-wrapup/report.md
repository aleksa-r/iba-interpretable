# SPEC-2026-11-14-wrapup: elicited priors, XGBoost, five search algorithms, the final method (development series)

Formula sets: G generic; K1-K5 knowledge-only draws; S1-S5 statistics-informed draws; Kc, Sc consensus; R1-R5 random. `|lin`, `|gbt`, `|xgb` = fixed formula with the linear model, LightGBM, XGBoost; `_nb` = the formula and 19 near neighbours averaged (no search); `K@5`, `S@5` = the five draws' linear forecasts averaged; `Rm` = mean loss of the five random sets.

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

Check: the linear fixed-formula forecasts of G made here differ from the first study's by at most 0.00e+00 over 458 cells.

## 1. Prior formulas

### 1a. Every formula set, linear model, against the generic formulas (G)

| a                      | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:-----------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| K1                     | G|lin     | +0.35 % (0b 0w / 7) | -0.48 % (0b 0w / 3) | +2.19 % (0b 1w / 4) | -0.24 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| K2                     | G|lin     | +0.02 % (0b 0w / 7) | -0.38 % (0b 0w / 3) | +1.33 % (0b 1w / 4) | +0.43 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| K3                     | G|lin     | +0.41 % (0b 0w / 7) | -0.06 % (0b 0w / 3) | +1.11 % (0b 1w / 4) | +0.76 % (1b 0w / 4) | 1 better, 1 worse of 18 |
| K4                     | G|lin     | +0.48 % (0b 0w / 7) | -0.49 % (0b 0w / 3) | +1.14 % (0b 1w / 4) | -0.47 % (1b 0w / 4) | 1 better, 1 worse of 18 |
| K5                     | G|lin     | +0.34 % (0b 0w / 7) | -0.54 % (0b 0w / 3) | +0.97 % (0b 0w / 4) | -0.07 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| S1                     | G|lin     | -0.43 % (0b 0w / 7) | -0.29 % (1b 0w / 3) | -0.22 % (0b 0w / 4) | +0.17 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| S2                     | G|lin     | -0.46 % (0b 0w / 7) | -0.30 % (0b 0w / 3) | +0.69 % (0b 0w / 4) | +0.03 % (0b 1w / 4) | 0 better, 1 worse of 18 |
| S3                     | G|lin     | -0.51 % (0b 0w / 7) | -0.52 % (1b 0w / 3) | +0.17 % (0b 0w / 4) | +0.09 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| S4                     | G|lin     | -0.65 % (1b 0w / 7) | -0.20 % (1b 0w / 3) | +0.85 % (0b 0w / 4) | +0.04 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| S5                     | G|lin     | -0.05 % (0b 0w / 7) | -0.46 % (1b 0w / 3) | -0.22 % (1b 0w / 4) | +0.09 % (0b 1w / 4) | 2 better, 1 worse of 18 |
| K consensus            | G|lin     | +0.72 % (0b 0w / 7) | -0.60 % (0b 0w / 3) | +0.74 % (0b 0w / 4) | -0.27 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| S consensus            | G|lin     | -0.46 % (0b 0w / 7) | -0.50 % (1b 0w / 3) | -0.18 % (0b 0w / 4) | +0.27 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| R1                     | G|lin     | +0.04 % (0b 0w / 7) | +2.94 % (0b 2w / 3) | +1.05 % (0b 0w / 4) | -0.09 % (0b 0w / 4) | 0 better, 2 worse of 18 |
| R2                     | G|lin     | +0.02 % (0b 0w / 7) | +3.17 % (0b 2w / 3) | +1.14 % (0b 0w / 4) | +0.96 % (0b 1w / 4) | 0 better, 3 worse of 18 |
| R3                     | G|lin     | -0.06 % (0b 0w / 7) | +2.10 % (0b 2w / 3) | +0.28 % (0b 0w / 4) | +0.31 % (0b 0w / 4) | 0 better, 2 worse of 18 |
| R4                     | G|lin     | -0.41 % (0b 0w / 7) | +3.46 % (0b 2w / 3) | +1.50 % (0b 2w / 4) | -0.18 % (0b 0w / 4) | 0 better, 4 worse of 18 |
| R5                     | G|lin     | -0.27 % (0b 0w / 7) | +2.67 % (0b 2w / 3) | +1.91 % (0b 0w / 4) | +0.18 % (0b 0w / 4) | 0 better, 2 worse of 18 |
| K, five draws averaged | G|lin     | -0.13 % (0b 0w / 7) | -0.78 % (0b 0w / 3) | +0.41 % (0b 0w / 4) | -0.25 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| S, five draws averaged | G|lin     | -0.55 % (0b 0w / 7) | -0.55 % (1b 0w / 3) | +0.01 % (0b 0w / 4) | -0.20 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| random (mean loss)     | G|lin     | -0.14 % (0b 0w / 7) | +2.87 % (0b 2w / 3) | +1.18 % (0b 1w / 4) | +0.23 % (0b 0w / 4) | 0 better, 3 worse of 18 |

### 1b. Against the type's reference (historical mean / HAR / base rate)

| a                      | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:-----------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| G                      | REF       | +1.39 % (0b 0w / 7) | -5.29 % (2b 0w / 3) | -0.29 % (0b 1w / 4) | +0.17 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| K1                     | REF       | +1.75 % (0b 1w / 7) | -5.74 % (3b 0w / 3) | +1.87 % (0b 2w / 4) | -0.07 % (0b 1w / 4) | 3 better, 4 worse of 18 |
| K2                     | REF       | +1.41 % (0b 1w / 7) | -5.64 % (2b 0w / 3) | +1.02 % (0b 1w / 4) | +0.61 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| K3                     | REF       | +1.81 % (0b 0w / 7) | -5.35 % (3b 0w / 3) | +0.81 % (0b 2w / 4) | +0.94 % (1b 2w / 4) | 4 better, 4 worse of 18 |
| K4                     | REF       | +1.88 % (0b 1w / 7) | -5.76 % (3b 0w / 3) | +0.83 % (0b 2w / 4) | -0.31 % (0b 0w / 4) | 3 better, 3 worse of 18 |
| K5                     | REF       | +1.74 % (0b 1w / 7) | -5.80 % (3b 0w / 3) | +0.67 % (0b 1w / 4) | +0.10 % (0b 1w / 4) | 3 better, 3 worse of 18 |
| S1                     | REF       | +0.95 % (0b 0w / 7) | -5.56 % (2b 0w / 3) | -0.51 % (0b 1w / 4) | +0.34 % (1b 0w / 4) | 3 better, 1 worse of 18 |
| S2                     | REF       | +0.92 % (0b 0w / 7) | -5.56 % (2b 0w / 3) | +0.39 % (0b 2w / 4) | +0.20 % (1b 2w / 4) | 3 better, 4 worse of 18 |
| S3                     | REF       | +0.88 % (0b 0w / 7) | -5.77 % (2b 0w / 3) | -0.12 % (0b 1w / 4) | +0.26 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| S4                     | REF       | +0.74 % (0b 1w / 7) | -5.47 % (2b 0w / 3) | +0.55 % (0b 2w / 4) | +0.21 % (1b 2w / 4) | 3 better, 5 worse of 18 |
| S5                     | REF       | +1.34 % (0b 0w / 7) | -5.71 % (2b 0w / 3) | -0.51 % (0b 0w / 4) | +0.26 % (1b 2w / 4) | 3 better, 2 worse of 18 |
| K consensus            | REF       | +2.13 % (0b 1w / 7) | -5.85 % (3b 0w / 3) | +0.44 % (0b 1w / 4) | -0.10 % (0b 1w / 4) | 3 better, 3 worse of 18 |
| S consensus            | REF       | +0.92 % (0b 0w / 7) | -5.75 % (2b 0w / 3) | -0.47 % (0b 1w / 4) | +0.44 % (1b 0w / 4) | 3 better, 1 worse of 18 |
| R1                     | REF       | +1.43 % (0b 1w / 7) | -2.53 % (2b 0w / 3) | +0.74 % (0b 2w / 4) | +0.07 % (0b 1w / 4) | 2 better, 4 worse of 18 |
| R2                     | REF       | +1.41 % (0b 2w / 7) | -2.32 % (2b 0w / 3) | +0.83 % (0b 0w / 4) | +1.13 % (0b 2w / 4) | 2 better, 4 worse of 18 |
| R3                     | REF       | +1.33 % (0b 2w / 7) | -3.31 % (2b 0w / 3) | -0.02 % (0b 0w / 4) | +0.47 % (0b 0w / 4) | 2 better, 2 worse of 18 |
| R4                     | REF       | +0.98 % (0b 3w / 7) | -2.04 % (1b 0w / 3) | +1.19 % (0b 1w / 4) | -0.01 % (1b 2w / 4) | 2 better, 6 worse of 18 |
| R5                     | REF       | +1.11 % (0b 1w / 7) | -2.78 % (2b 0w / 3) | +1.60 % (0b 1w / 4) | +0.34 % (0b 2w / 4) | 2 better, 4 worse of 18 |
| K, five draws averaged | REF       | +1.26 % (0b 0w / 7) | -6.03 % (3b 0w / 3) | +0.11 % (0b 1w / 4) | -0.08 % (1b 1w / 4) | 4 better, 2 worse of 18 |
| S, five draws averaged | REF       | +0.83 % (0b 0w / 7) | -5.80 % (2b 0w / 3) | -0.29 % (0b 1w / 4) | -0.03 % (1b 2w / 4) | 3 better, 3 worse of 18 |
| group PCA              | REF       | +1.43 % (0b 1w / 7) | -4.92 % (2b 0w / 3) | +0.35 % (0b 1w / 4) | -0.11 % (1b 0w / 4) | 3 better, 2 worse of 18 |

### 1c. Against group PCA

| a                      | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:-----------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| G                      | gpca|lin  | -0.03 % (0b 0w / 7) | -0.36 % (0b 0w / 3) | -0.63 % (0b 0w / 4) | +0.28 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| K1                     | gpca|lin  | +0.32 % (0b 0w / 7) | -0.84 % (1b 0w / 3) | +1.56 % (1b 1w / 4) | +0.04 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| K2                     | gpca|lin  | -0.02 % (0b 0w / 7) | -0.74 % (0b 0w / 3) | +0.70 % (2b 0w / 4) | +0.71 % (0b 1w / 4) | 2 better, 1 worse of 18 |
| K3                     | gpca|lin  | +0.37 % (0b 0w / 7) | -0.41 % (1b 0w / 3) | +0.46 % (0b 0w / 4) | +1.04 % (1b 1w / 4) | 2 better, 1 worse of 18 |
| K4                     | gpca|lin  | +0.44 % (0b 0w / 7) | -0.85 % (1b 0w / 3) | +0.52 % (1b 1w / 4) | -0.20 % (1b 0w / 4) | 3 better, 1 worse of 18 |
| K5                     | gpca|lin  | +0.30 % (0b 0w / 7) | -0.90 % (1b 0w / 3) | +0.34 % (0b 1w / 4) | +0.21 % (0b 1w / 4) | 1 better, 2 worse of 18 |
| S1                     | gpca|lin  | -0.47 % (0b 0w / 7) | -0.66 % (0b 0w / 3) | -0.84 % (2b 0w / 4) | +0.45 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| S2                     | gpca|lin  | -0.50 % (0b 0w / 7) | -0.66 % (0b 0w / 3) | +0.07 % (1b 0w / 4) | +0.30 % (0b 1w / 4) | 1 better, 1 worse of 18 |
| S3                     | gpca|lin  | -0.54 % (0b 0w / 7) | -0.89 % (0b 0w / 3) | -0.45 % (1b 0w / 4) | +0.37 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| S4                     | gpca|lin  | -0.68 % (0b 0w / 7) | -0.57 % (0b 0w / 3) | +0.23 % (1b 1w / 4) | +0.32 % (0b 0w / 4) | 1 better, 1 worse of 18 |
| S5                     | gpca|lin  | -0.08 % (0b 0w / 7) | -0.82 % (0b 0w / 3) | -0.84 % (2b 0w / 4) | +0.37 % (0b 1w / 4) | 2 better, 1 worse of 18 |
| K consensus            | gpca|lin  | +0.69 % (0b 0w / 7) | -0.96 % (1b 0w / 3) | +0.11 % (0b 1w / 4) | +0.01 % (1b 0w / 4) | 2 better, 1 worse of 18 |
| S consensus            | gpca|lin  | -0.50 % (0b 0w / 7) | -0.86 % (0b 0w / 3) | -0.80 % (1b 0w / 4) | +0.55 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| R1                     | gpca|lin  | +0.00 % (0b 0w / 7) | +2.57 % (0b 2w / 3) | +0.40 % (0b 0w / 4) | +0.19 % (0b 1w / 4) | 0 better, 3 worse of 18 |
| R2                     | gpca|lin  | -0.01 % (0b 0w / 7) | +2.80 % (0b 2w / 3) | +0.50 % (1b 0w / 4) | +1.24 % (0b 2w / 4) | 1 better, 4 worse of 18 |
| R3                     | gpca|lin  | -0.10 % (1b 0w / 7) | +1.74 % (0b 1w / 3) | -0.36 % (0b 0w / 4) | +0.59 % (0b 0w / 4) | 1 better, 1 worse of 18 |
| R4                     | gpca|lin  | -0.45 % (0b 1w / 7) | +3.09 % (0b 2w / 3) | +0.86 % (1b 1w / 4) | +0.10 % (0b 0w / 4) | 1 better, 4 worse of 18 |
| R5                     | gpca|lin  | -0.31 % (0b 0w / 7) | +2.30 % (0b 2w / 3) | +1.27 % (0b 0w / 4) | +0.46 % (0b 1w / 4) | 0 better, 3 worse of 18 |
| K, five draws averaged | gpca|lin  | -0.17 % (0b 0w / 7) | -1.14 % (2b 0w / 3) | -0.22 % (2b 0w / 4) | +0.03 % (0b 0w / 4) | 4 better, 0 worse of 18 |
| S, five draws averaged | gpca|lin  | -0.59 % (0b 0w / 7) | -0.92 % (0b 0w / 3) | -0.61 % (3b 0w / 4) | +0.08 % (0b 0w / 4) | 3 better, 0 worse of 18 |

### 1d. Procedures against each other, consensus against the draws' average, elicited against random

| a                      | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:-----------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| S consensus            | Kc|lin    | -1.16 % (0b 0w / 7) | +0.10 % (0b 0w / 3) | -0.90 % (0b 0w / 4) | +0.53 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| K, five draws averaged | Kc|lin    | -0.83 % (2b 0w / 7) | -0.18 % (1b 0w / 3) | -0.32 % (1b 0w / 4) | +0.02 % (1b 0w / 4) | 5 better, 0 worse of 18 |
| S, five draws averaged | Sc|lin    | -0.09 % (2b 0w / 7) | -0.05 % (0b 0w / 3) | +0.18 % (2b 0w / 4) | -0.46 % (0b 0w / 4) | 4 better, 0 worse of 18 |
| S, five draws averaged | K@5       | -0.43 % (0b 0w / 7) | +0.23 % (0b 0w / 3) | -0.40 % (0b 0w / 4) | +0.05 % (0b 1w / 4) | 0 better, 1 worse of 18 |
| K consensus            | Rm        | +0.86 % (0b 0w / 7) | -3.36 % (3b 0w / 3) | -0.42 % (0b 0w / 4) | -0.50 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| S consensus            | Rm        | -0.33 % (0b 0w / 7) | -3.26 % (2b 0w / 3) | -1.32 % (1b 0w / 4) | +0.03 % (0b 0w / 4) | 3 better, 0 worse of 18 |
| generic                | Rm        | +0.14 % (0b 0w / 7) | -2.78 % (2b 0w / 3) | -1.14 % (1b 0w / 4) | -0.23 % (0b 0w / 4) | 3 better, 0 worse of 18 |

### 1e. The no-search colony of a set

| a         | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:----------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| G colony  | G|lin     | -0.14 % (3b 0w / 7) | -0.12 % (1b 0w / 3) | -0.18 % (1b 0w / 4) | -0.14 % (3b 0w / 4) | 8 better, 0 worse of 18 |
| G colony  | G|lin     | -0.14 % (3b 0w / 7) | -0.12 % (1b 0w / 3) | -0.18 % (1b 0w / 4) | -0.14 % (3b 0w / 4) | 8 better, 0 worse of 18 |
| G colony  | REF       | +1.26 % (0b 0w / 7) | -5.40 % (2b 0w / 3) | -0.47 % (0b 1w / 4) | +0.03 % (0b 0w / 4) | 2 better, 1 worse of 18 |
| G colony  | gpca|lin  | -0.17 % (0b 0w / 7) | -0.48 % (0b 0w / 3) | -0.81 % (1b 0w / 4) | +0.14 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| Kc colony | Kc|lin    | -0.28 % (4b 0w / 7) | -0.12 % (1b 0w / 3) | -0.27 % (3b 0w / 4) | -0.07 % (1b 0w / 4) | 9 better, 0 worse of 18 |
| Kc colony | G|lin     | +0.43 % (0b 0w / 7) | -0.72 % (0b 0w / 3) | +0.46 % (0b 0w / 4) | -0.34 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| Kc colony | REF       | +1.83 % (0b 1w / 7) | -5.96 % (3b 0w / 3) | +0.17 % (0b 1w / 4) | -0.17 % (1b 1w / 4) | 4 better, 3 worse of 18 |
| Kc colony | gpca|lin  | +0.40 % (0b 0w / 7) | -1.08 % (2b 0w / 3) | -0.16 % (0b 0w / 4) | -0.06 % (1b 0w / 4) | 3 better, 0 worse of 18 |
| Sc colony | Sc|lin    | -0.08 % (2b 0w / 7) | -0.11 % (1b 0w / 3) | -0.13 % (2b 0w / 4) | -0.32 % (2b 0w / 4) | 7 better, 0 worse of 18 |
| Sc colony | G|lin     | -0.55 % (0b 0w / 7) | -0.62 % (1b 0w / 3) | -0.31 % (1b 0w / 4) | -0.06 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| Sc colony | REF       | +0.84 % (0b 0w / 7) | -5.86 % (2b 0w / 3) | -0.60 % (0b 1w / 4) | +0.11 % (1b 0w / 4) | 3 better, 1 worse of 18 |
| Sc colony | gpca|lin  | -0.58 % (0b 0w / 7) | -0.98 % (0b 0w / 3) | -0.93 % (2b 0w / 4) | +0.22 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| Kc colony | G_nb      | +0.57 % (0b 0w / 7) | -0.60 % (0b 0w / 3) | +0.65 % (0b 0w / 4) | -0.20 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| Sc colony | G_nb      | -0.41 % (0b 0w / 7) | -0.49 % (1b 0w / 3) | -0.13 % (1b 0w / 4) | +0.08 % (0b 0w / 4) | 2 better, 0 worse of 18 |

### 1f. Spread between draws and difference between procedures

Per task, relative to the loss of G: standard deviation across the five draws of a procedure; differences of the procedures' mean losses. Averaged over the tasks of a type, in %.

| kind      |   sd K draws |   sd S draws |   sd R draws |   mean S - mean K |   mean K - G |   mean S - G |   mean R - G |
|:----------|-------------:|-------------:|-------------:|------------------:|-------------:|-------------:|-------------:|
| return    |        0.383 |        0.38  |        0.671 |            -0.737 |        0.318 |       -0.419 |       -0.137 |
| logrv     |        0.354 |        0.15  |        0.602 |             0.036 |       -0.392 |       -0.355 |        2.866 |
| tail_loss |        1.199 |        0.57  |        0.748 |            -1.092 |        1.349 |        0.257 |        1.176 |
| tail_gain |        0.614 |        0.183 |        0.566 |             0     |        0.083 |        0.083 |        0.234 |

## 2. The formula set of the method (spec 7.2)

K is the default. Sc replaces Kc only if it is significantly better than Kc in more tasks than worse AND its mean loss is lower in at least 3 of the 4 target types.

| candidate   | incumbent   |   tasks |   tasks better |   tasks worse | types with lower mean loss   |   mean rel. diff % (types equally weighted) | qualifies   |
|:------------|:------------|--------:|---------------:|--------------:|:-----------------------------|--------------------------------------------:|:------------|
| Sc|lin      | Kc|lin      |      18 |              0 |             0 | 2/4                          |                                      -0.356 | False       |
| Kc|lin      | G|lin       |      18 |              0 |             0 | 2/4                          |                                       0.148 | False       |

**Chosen: Kc** (S does not qualify; the default stays). Against the generic formulas the chosen set is not worse in more tasks than better.

## 3. Estimators

### 3a. XGBoost against LightGBM

| a                     | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:----------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| K consensus + XGBoost | Kc|gbt    | +3.72 % (0b 3w / 7) | +0.16 % (0b 0w / 3) | -0.74 % (1b 0w / 4) | +0.78 % (0b 1w / 4) | 1 better, 4 worse of 18 |
| G + XGBoost           | G|gbt     | +3.10 % (0b 1w / 7) | +0.26 % (0b 0w / 3) | +0.35 % (0b 0w / 4) | +0.17 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| raw + XGBoost         | raw|gbt   | +1.47 % (0b 2w / 7) | +0.66 % (0b 2w / 3) | -0.54 % (1b 0w / 4) | -0.08 % (0b 0w / 4) | 1 better, 4 worse of 18 |
| gpca + XGBoost        | gpca|gbt  | +1.51 % (1b 0w / 7) | -0.27 % (1b 0w / 3) | -0.32 % (0b 0w / 4) | +0.64 % (0b 1w / 4) | 2 better, 1 worse of 18 |

### 3b. Trees against the linear model

| a                 | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks                |
|:------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:-------------------------|
| K consensus + xgb | Kc|lin    | +8.68 % (0b 5w / 7) | +2.82 % (0b 3w / 3) | +4.16 % (0b 3w / 4) | +5.68 % (0b 3w / 4) | 0 better, 14 worse of 18 |
| K consensus + gbt | Kc|lin    | +4.88 % (0b 4w / 7) | +2.65 % (0b 2w / 3) | +4.95 % (0b 3w / 4) | +4.83 % (0b 3w / 4) | 0 better, 12 worse of 18 |
| G + xgb           | G|lin     | +8.79 % (0b 5w / 7) | +3.36 % (0b 3w / 3) | +5.06 % (0b 3w / 4) | +3.90 % (0b 3w / 4) | 0 better, 14 worse of 18 |
| G + gbt           | G|lin     | +5.47 % (0b 5w / 7) | +3.10 % (0b 3w / 3) | +4.68 % (0b 3w / 4) | +3.72 % (0b 2w / 4) | 0 better, 13 worse of 18 |
| raw + xgb         | raw|lin   | +5.25 % (0b 2w / 7) | +3.84 % (0b 3w / 3) | +2.68 % (0b 3w / 4) | +4.59 % (0b 4w / 4) | 0 better, 12 worse of 18 |
| raw + gbt         | raw|lin   | +3.76 % (0b 2w / 7) | +3.16 % (0b 2w / 3) | +3.21 % (0b 3w / 4) | +4.68 % (0b 4w / 4) | 0 better, 11 worse of 18 |
| gpca + xgb        | gpca|lin  | +8.49 % (0b 4w / 7) | +3.21 % (0b 3w / 3) | +5.24 % (0b 3w / 4) | +6.36 % (0b 4w / 4) | 0 better, 14 worse of 18 |
| gpca + gbt        | gpca|lin  | +6.85 % (0b 5w / 7) | +3.50 % (0b 3w / 3) | +5.56 % (0b 3w / 4) | +5.67 % (0b 4w / 4) | 0 better, 15 worse of 18 |

## 4. Search with the chosen formula set (Kc) as the prior

### 4a. Five algorithms on the pooled fitness of the asset-class pools, equal budget

Cell: gain of the winner over the prior on the fitness folds / on the clean outer rows / share of winners that pass the test / literals. Units = (task, pool, block), seeds averaged.

| algorithm   | return                     | logrv                     | tail_loss                  | tail_gain                  |
|:------------|:---------------------------|:--------------------------|:---------------------------|:---------------------------|
| ABC         | +11.2 / +1.4 / 16 % / 10.3 | +6.3 / -3.2 / 10 % / 9.8  | +9.4 / +2.2 / 17 % / 10.5  | +8.7 / -7.1 / 5 % / 10.0   |
| GA          | +13.2 / +1.3 / 13 % / 11.6 | +7.6 / -4.4 / 8 % / 10.5  | +11.0 / +2.0 / 20 % / 11.6 | +12.0 / -7.5 / 7 % / 11.5  |
| PSO         | +12.0 / +1.0 / 12 % / 10.9 | +6.9 / -3.3 / 8 % / 10.1  | +10.2 / +2.1 / 21 % / 11.0 | +9.9 / -8.8 / 9 % / 10.6   |
| SA          | +11.9 / +0.8 / 12 % / 10.5 | +6.8 / -3.4 / 9 % / 10.0  | +10.0 / +1.6 / 17 % / 10.8 | +9.8 / -5.7 / 8 % / 10.4   |
| DE          | +12.7 / +1.1 / 13 % / 11.1 | +7.3 / -3.8 / 10 % / 10.2 | +10.7 / +2.3 / 18 % / 11.3 | +11.0 / -5.6 / 10 % / 10.9 |

Friedman test across the five algorithms (means in the columns):

| metric     |   units |      ABC |       GA |      PSO |       SA |       DE |   friedman_p |
|:-----------|--------:|---------:|---------:|---------:|---------:|---------:|-------------:|
| clean_gain |     348 | -0.01447 | -0.0196  | -0.0199  | -0.01513 | -0.01393 |      0.60406 |
| passes     |     352 |  0.12311 |  0.11932 |  0.12405 |  0.11648 |  0.12595 |      0.69149 |
| inner_gain |     352 |  0.08974 |  0.10978 |  0.09798 |  0.09669 |  0.10481 |      0       |

Each algorithm against ABC on the clean-row gain (sign test over units, Holm over the four comparisons). Units share dates and are not independent; the test is the one fixed in the spec.

| algorithm   |   units |   better than ABC |   worse than ABC |   mean difference |   sign_p |   holm_p | replaces ABC   |
|:------------|--------:|------------------:|-----------------:|------------------:|---------:|---------:|:---------------|
| GA          |     348 |               163 |              184 |          -0.00513 |  0.28296 |        1 | False          |
| PSO         |     348 |               168 |              180 |          -0.00543 |  0.55548 |        1 | False          |
| SA          |     348 |               173 |              174 |          -0.00066 |  1       |        1 | False          |
| DE          |     348 |               176 |              171 |           0.00054 |  0.83002 |        1 | False          |

**Algorithm of the method: ABC** (the default; no algorithm is better than ABC at Holm p < 0.05).

### 4b. Forecasts from the pooled ABC (class pools, anchored, greedy)

| a                       | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks                |
|:------------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:-------------------------|
| tested winner           | Kc|lin    | +0.09 % (0b 1w / 7) | +0.30 % (0b 1w / 3) | +0.44 % (0b 0w / 4) | -0.00 % (0b 0w / 4) | 0 better, 2 worse of 18  |
| winner without the test | Kc|lin    | +2.40 % (0b 4w / 7) | +1.46 % (0b 2w / 3) | +2.86 % (0b 3w / 4) | +2.69 % (0b 3w / 4) | 0 better, 12 worse of 18 |
| colony ensemble         | Kc|lin    | -0.46 % (3b 0w / 7) | -0.18 % (1b 0w / 3) | -0.32 % (2b 0w / 4) | -0.14 % (1b 0w / 4) | 7 better, 0 worse of 18  |
| colony ensemble         | Kc_nb     | -0.18 % (2b 0w / 7) | -0.06 % (1b 0w / 3) | -0.04 % (0b 0w / 4) | -0.07 % (0b 0w / 4) | 3 better, 0 worse of 18  |
| tested winner           | REF       | +2.22 % (0b 1w / 7) | -5.57 % (2b 0w / 3) | +0.89 % (0b 2w / 4) | -0.10 % (0b 1w / 4) | 2 better, 4 worse of 18  |
| colony ensemble         | REF       | +1.65 % (0b 1w / 7) | -6.02 % (3b 0w / 3) | +0.12 % (0b 1w / 4) | -0.24 % (1b 1w / 4) | 4 better, 3 worse of 18  |
| colony ensemble         | gpca|lin  | +0.22 % (0b 0w / 7) | -1.14 % (2b 0w / 3) | -0.21 % (1b 0w / 4) | -0.13 % (1b 0w / 4) | 4 better, 0 worse of 18  |
| tested winner           | G|lin     | +0.81 % (0b 0w / 7) | -0.30 % (0b 0w / 3) | +1.20 % (0b 1w / 4) | -0.27 % (0b 0w / 4) | 0 better, 1 worse of 18  |
| colony ensemble         | G|lin     | +0.25 % (0b 0w / 7) | -0.78 % (1b 0w / 3) | +0.41 % (0b 0w / 4) | -0.40 % (1b 0w / 4) | 2 better, 0 worse of 18  |

## 5. The final method (spec 7.5)

| candidate   | incumbent   |   tasks |   tasks better |   tasks worse | types with lower mean loss   |   mean rel. diff % (types equally weighted) | qualifies   |
|:------------|:------------|--------:|---------------:|--------------:|:-----------------------------|--------------------------------------------:|:------------|
| iba_ca|lin  | Kc|lin      |      18 |              0 |             2 | 1/4                          |                                       0.208 | False       |
| iba_ca_b    | Kc_nb       |      18 |              3 |             0 | 4/4                          |                                      -0.089 | True        |

- **Interpretable reading: `Kc|lin`** (the fixed formula; the tested ABC winner does not qualify).
- **Accuracy reading: `iba_ca_b`** (the ABC colony qualifies against the no-search colony).
- Formula set: Kc. Search algorithm of the method: ABC.

## 6. Best-of-many test: does any of the 63 new configurations beat the benchmark? (consistent p-value; tasks with p < 0.05)

| benchmark   | kind      |   tasks |   significant |   median_p |
|:------------|:----------|--------:|--------------:|-----------:|
| G|lin       | logrv     |       3 |             1 |     0.4715 |
| G|lin       | return    |       7 |             0 |     0.6595 |
| G|lin       | tail_gain |       4 |             0 |     0.5505 |
| G|lin       | tail_loss |       4 |             0 |     0.5765 |
| REF         | logrv     |       3 |             2 |     0.0005 |
| REF         | return    |       7 |             0 |     0.953  |
| REF         | tail_gain |       4 |             0 |     0.6018 |
| REF         | tail_loss |       4 |             0 |     0.7018 |
| gpca|lin    | logrv     |       3 |             0 |     0.203  |
| gpca|lin    | return    |       7 |             0 |     0.749  |
| gpca|lin    | tail_gain |       4 |             0 |     0.7623 |
| gpca|lin    | tail_loss |       4 |             2 |     0.3213 |

New configuration with the lowest pooled loss per task:

| kind      | best_variant   |   tasks |
|:----------|:---------------|--------:|
| logrv     | K@5            |       1 |
| logrv     | Kc_nb          |       1 |
| logrv     | Sc_nb          |       1 |
| return    | R2|lin         |       2 |
| return    | R3|lin         |       1 |
| return    | R4|lin         |       1 |
| return    | R5|lin         |       1 |
| return    | S4|lin         |       1 |
| return    | iba_ca_b       |       1 |
| tail_gain | R1|lin         |       1 |
| tail_gain | S@5            |       1 |
| tail_gain | Sc_nb          |       1 |
| tail_gain | iba_ca_r|lin   |       1 |
| tail_loss | K1|lin         |       1 |
| tail_loss | R3|lin         |       1 |
| tail_loss | R4|lin         |       1 |
| tail_loss | S5|lin         |       1 |
