# SPEC-2026-11-14-benchmarks-kpca-ae: kernel PCA and an autoencoder as benchmarks (development series)

`kpca` = RBF kernel PCA, 6 components; `ae` = autoencoder with a 6-unit bottleneck; both fitted on admissible rows only, as every reducer. IBA readings are those of the wrap-up's final method: interpretable `Kc|lin`, accuracy `iba_ca_b` (formula set Kc); G = generic formulas.

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

### 1. The two benchmarks, linear model, against the reference and the other benchmarks

| a           | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| kernel PCA  | REF       | +1.14 % (0b 3w / 7) | -1.26 % (1b 0w / 3) | +0.86 % (0b 1w / 4) | +0.90 % (1b 0w / 4) | 2 better, 4 worse of 18 |
| kernel PCA  | pca|lin   | -0.16 % (1b 0w / 7) | +2.29 % (0b 2w / 3) | -0.15 % (0b 0w / 4) | +0.80 % (0b 0w / 4) | 1 better, 2 worse of 18 |
| kernel PCA  | gpca|lin  | -0.29 % (1b 0w / 7) | +3.91 % (0b 2w / 3) | +0.52 % (0b 0w / 4) | +1.01 % (0b 0w / 4) | 1 better, 2 worse of 18 |
| kernel PCA  | raw|lin   | -2.65 % (1b 0w / 7) | +3.65 % (0b 1w / 3) | -1.41 % (1b 0w / 4) | -0.41 % (0b 0w / 4) | 2 better, 1 worse of 18 |
| kernel PCA  | lasso|lin | -0.87 % (0b 0w / 7) | +2.80 % (0b 2w / 3) | -0.42 % (0b 0w / 4) | +0.58 % (0b 0w / 4) | 0 better, 2 worse of 18 |
| autoencoder | REF       | +1.23 % (0b 5w / 7) | -2.95 % (2b 0w / 3) | +0.78 % (0b 1w / 4) | -0.07 % (1b 0w / 4) | 3 better, 6 worse of 18 |
| autoencoder | pca|lin   | -0.07 % (0b 0w / 7) | +0.52 % (0b 0w / 3) | -0.23 % (0b 0w / 4) | -0.17 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| autoencoder | gpca|lin  | -0.19 % (0b 0w / 7) | +2.11 % (0b 2w / 3) | +0.45 % (0b 1w / 4) | +0.04 % (0b 0w / 4) | 0 better, 3 worse of 18 |
| autoencoder | raw|lin   | -2.55 % (0b 0w / 7) | +1.84 % (0b 1w / 3) | -1.51 % (0b 0w / 4) | -1.36 % (2b 0w / 4) | 2 better, 1 worse of 18 |
| autoencoder | lasso|lin | -0.78 % (0b 0w / 7) | +1.01 % (0b 2w / 3) | -0.50 % (0b 0w / 4) | -0.39 % (0b 0w / 4) | 0 better, 2 worse of 18 |
| autoencoder | kpca|lin  | +0.10 % (0b 1w / 7) | -1.72 % (1b 0w / 3) | -0.07 % (0b 0w / 4) | -0.96 % (2b 0w / 4) | 3 better, 1 worse of 18 |

### 2. With trees

| a                 | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks                |
|:------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:-------------------------|
| kernel PCA + xgb  | kpca|lin  | +2.94 % (0b 4w / 7) | +1.47 % (0b 1w / 3) | +3.91 % (0b 4w / 4) | +2.85 % (0b 3w / 4) | 0 better, 12 worse of 18 |
| kernel PCA + gbt  | kpca|lin  | +2.98 % (0b 4w / 7) | +1.44 % (0b 1w / 3) | +3.55 % (0b 3w / 4) | +3.20 % (0b 3w / 4) | 0 better, 11 worse of 18 |
| autoencoder + xgb | ae|lin    | +6.83 % (0b 5w / 7) | +3.09 % (0b 3w / 3) | +3.67 % (0b 3w / 4) | +5.16 % (0b 4w / 4) | 0 better, 15 worse of 18 |
| autoencoder + gbt | ae|lin    | +6.93 % (0b 5w / 7) | +2.78 % (0b 3w / 3) | +3.68 % (0b 2w / 4) | +5.68 % (0b 4w / 4) | 0 better, 14 worse of 18 |
| kernel PCA + xgb  | raw|xgb   | -4.68 % (0b 0w / 7) | +1.26 % (0b 1w / 3) | -0.21 % (0b 0w / 4) | -2.03 % (0b 0w / 4) | 0 better, 1 worse of 18  |
| kernel PCA + xgb  | pca|xgb   | -2.37 % (0b 0w / 7) | +1.87 % (0b 0w / 3) | -0.68 % (0b 0w / 4) | -2.43 % (2b 0w / 4) | 2 better, 0 worse of 18  |
| kernel PCA + xgb  | REF       | +4.10 % (0b 4w / 7) | +0.20 % (1b 1w / 3) | +4.79 % (0b 3w / 4) | +3.78 % (0b 2w / 4) | 1 better, 10 worse of 18 |
| autoencoder + xgb | raw|xgb   | -1.03 % (0b 0w / 7) | +1.12 % (0b 1w / 3) | -0.51 % (0b 0w / 4) | -0.83 % (1b 0w / 4) | 1 better, 1 worse of 18  |
| autoencoder + xgb | pca|xgb   | +1.40 % (0b 0w / 7) | +1.71 % (0b 1w / 3) | -0.97 % (0b 0w / 4) | -1.24 % (1b 0w / 4) | 1 better, 1 worse of 18  |
| autoencoder + xgb | REF       | +8.16 % (0b 6w / 7) | +0.04 % (0b 0w / 3) | +4.48 % (0b 3w / 4) | +5.10 % (0b 3w / 4) | 0 better, 12 worse of 18 |

### 3. IBA against the two benchmarks

| a                    | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:---------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| IBA interpretable    | kpca|lin  | +0.97 % (0b 0w / 7) | -4.66 % (3b 0w / 3) | -0.40 % (0b 0w / 4) | -0.98 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| IBA accuracy         | kpca|lin  | +0.50 % (0b 0w / 7) | -4.83 % (3b 0w / 3) | -0.73 % (0b 0w / 4) | -1.12 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| IBA generic formulas | kpca|lin  | +0.25 % (0b 0w / 7) | -4.08 % (2b 0w / 3) | -1.13 % (1b 0w / 4) | -0.72 % (0b 0w / 4) | 3 better, 0 worse of 18 |
| IBA interpretable    | ae|lin    | +0.88 % (0b 0w / 7) | -3.00 % (3b 0w / 3) | -0.35 % (0b 0w / 4) | -0.02 % (0b 0w / 4) | 3 better, 0 worse of 18 |
| IBA accuracy         | ae|lin    | +0.41 % (0b 0w / 7) | -3.17 % (3b 0w / 3) | -0.66 % (0b 0w / 4) | -0.16 % (0b 0w / 4) | 3 better, 0 worse of 18 |
| IBA generic formulas | ae|lin    | +0.16 % (0b 0w / 7) | -2.41 % (2b 0w / 3) | -1.06 % (0b 0w / 4) | +0.24 % (0b 1w / 4) | 2 better, 1 worse of 18 |
| IBA Kc + xgb         | kpca|xgb  | +6.67 % (0b 2w / 7) | -3.39 % (2b 0w / 3) | -0.15 % (0b 0w / 4) | +1.70 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| IBA Kc + gbt         | kpca|gbt  | +2.88 % (0b 0w / 7) | -3.52 % (2b 0w / 3) | +0.95 % (0b 0w / 4) | +0.56 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| IBA Kc + xgb         | ae|xgb    | +2.59 % (0b 0w / 7) | -3.25 % (2b 0w / 3) | +0.16 % (0b 0w / 4) | +0.44 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| IBA Kc + gbt         | ae|gbt    | -0.91 % (1b 0w / 7) | -3.11 % (2b 0w / 3) | +0.91 % (0b 0w / 4) | -0.81 % (0b 0w / 4) | 3 better, 0 worse of 18 |
