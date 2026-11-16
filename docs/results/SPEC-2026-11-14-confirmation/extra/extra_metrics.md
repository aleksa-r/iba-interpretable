# Financial and classification measures (confirmation series)

CONFIRMATION series (21), measures declared in the spec before the run (`docs/protocol/EXTRA_METRICS.md`). All factor methods with the linear model. The averaged reading is the ABC colony of the development run, applied unchanged.

## 1. Value at risk and expected shortfall from the volatility forecasts (weekly series, zero-mean normal returns)

### 5 % level, 1 week (21 series)

| method                     | violations (target 5 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio | series rejecting coverage (Kupiec)   | series rejecting independence (Christoffersen)   |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|:-------------------------------------|:-------------------------------------------------|
| IBA, K formulas (fixed)    | 5.12 %                    | -3.56 % better         | -0.0533 better              |              1.14 | 0 %                                  | 0 %                                              |
| IBA, K formulas (averaged) | 5.08 %                    | -3.59 % better         | -0.0532 better              |              1.14 | 0 %                                  | 0 %                                              |
| IBA, generic formulas      | 5.07 %                    | -3.33 % better         | -0.0448 better              |              1.14 | 5 %                                  | 0 %                                              |
| group PCA                  | 5.08 %                    | -3.49 % n.s.           | -0.0482 n.s.                |              1.14 | 0 %                                  | 0 %                                              |
| PCA                        | 5.01 %                    | -2.43 % n.s.           | -0.0262 n.s.                |              1.16 | 5 %                                  | 0 %                                              |
| kernel PCA                 | 5.19 %                    | -0.25 % n.s.           | -0.0049 n.s.                |              1.16 | 0 %                                  | 5 %                                              |
| autoencoder                | 4.97 %                    | -1.99 % n.s.           | -0.0200 n.s.                |              1.16 | 0 %                                  | 0 %                                              |
| LASSO                      | 5.14 %                    | -3.08 % n.s.           | -0.0460 better              |              1.15 | 5 %                                  | 0 %                                              |
| raw factors                | 5.15 %                    | -3.48 % n.s.           | -0.0472 better              |              1.15 | 10 %                                 | 0 %                                              |
| HAR                        | 4.99 %                    | +0.00 %                | +0.0000                     |              1.17 | 10 %                                 | 5 %                                              |
| GARCH                      | 5.20 %                    | -2.40 % n.s.           | -0.0318 n.s.                |              1.15 | 5 %                                  | 5 %                                              |
| GJR-GARCH                  | 5.45 %                    | -3.05 % n.s.           | -0.0418 n.s.                |              1.13 | 0 %                                  | 0 %                                              |

### 5 % level, 4 weeks (21 series)

| method                     | violations (target 5 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 5.04 %                    | -2.17 % n.s.           | -0.0331 n.s.                |              1.32 |
| IBA, K formulas (averaged) | 5.01 %                    | -2.08 % n.s.           | -0.0334 n.s.                |              1.32 |
| IBA, generic formulas      | 5.08 %                    | -2.02 % better         | -0.0378 n.s.                |              1.33 |
| group PCA                  | 4.99 %                    | -1.80 % n.s.           | -0.0327 n.s.                |              1.32 |
| PCA                        | 4.98 %                    | -1.08 % n.s.           | -0.0148 n.s.                |              1.34 |
| kernel PCA                 | 4.83 %                    | -0.21 % n.s.           | +0.0025 n.s.                |              1.38 |
| autoencoder                | 4.95 %                    | -1.06 % n.s.           | -0.0134 n.s.                |              1.35 |
| LASSO                      | 4.95 %                    | -1.68 % better         | -0.0333 n.s.                |              1.35 |
| raw factors                | 5.20 %                    | -2.43 % n.s.           | -0.0463 n.s.                |              1.32 |
| HAR                        | 4.83 %                    | +0.00 %                | +0.0000                     |              1.38 |
| GARCH                      | 4.96 %                    | -1.47 % n.s.           | -0.0615 n.s.                |              1.33 |
| GJR-GARCH                  | 5.33 %                    | -2.10 % n.s.           | -0.0730 n.s.                |              1.29 |

### 5 % level, 13 weeks (21 series)

| method                     | violations (target 5 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 4.28 %                    | -0.21 % n.s.           | -0.0082 n.s.                |              1.65 |
| IBA, K formulas (averaged) | 4.26 %                    | -0.16 % n.s.           | -0.0052 n.s.                |              1.65 |
| IBA, generic formulas      | 4.24 %                    | -0.38 % n.s.           | -0.0103 n.s.                |              1.66 |
| group PCA                  | 4.19 %                    | +0.40 % n.s.           | +0.0174 n.s.                |              1.69 |
| PCA                        | 4.29 %                    | +0.15 % n.s.           | +0.0068 n.s.                |              1.65 |
| kernel PCA                 | 4.24 %                    | +0.19 % n.s.           | +0.0082 n.s.                |              1.66 |
| autoencoder                | 4.24 %                    | +0.04 % n.s.           | +0.0043 n.s.                |              1.67 |
| LASSO                      | 4.14 %                    | +0.34 % n.s.           | +0.0203 n.s.                |              1.7  |
| raw factors                | 4.30 %                    | -0.16 % n.s.           | +0.0095 n.s.                |              1.67 |
| HAR                        | 4.14 %                    | +0.00 %                | +0.0000                     |              1.67 |
| GARCH                      | 3.77 %                    | -0.61 % n.s.           | -0.0927 n.s.                |              1.58 |
| GJR-GARCH                  | 3.88 %                    | -1.25 % n.s.           | -0.0898 n.s.                |              1.59 |

### 1 % level, 1 week (21 series)

| method                     | violations (target 1 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio | series rejecting coverage (Kupiec)   | series rejecting independence (Christoffersen)   |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|:-------------------------------------|:-------------------------------------------------|
| IBA, K formulas (fixed)    | 1.73 %                    | -7.93 % better         | -0.1541 better              |              1.19 | 19 %                                 | 5 %                                              |
| IBA, K formulas (averaged) | 1.74 %                    | -8.04 % better         | -0.1562 better              |              1.19 | 24 %                                 | 5 %                                              |
| IBA, generic formulas      | 1.79 %                    | -7.38 % better         | -0.1287 better              |              1.19 | 33 %                                 | 0 %                                              |
| group PCA                  | 1.80 %                    | -8.73 % better         | -0.1551 better              |              1.17 | 33 %                                 | 5 %                                              |
| PCA                        | 1.83 %                    | -5.47 % n.s.           | -0.0807 n.s.                |              1.2  | 48 %                                 | 0 %                                              |
| kernel PCA                 | 1.87 %                    | -1.47 % n.s.           | -0.0205 n.s.                |              1.22 | 43 %                                 | 0 %                                              |
| autoencoder                | 1.82 %                    | -4.60 % n.s.           | -0.0624 n.s.                |              1.21 | 33 %                                 | 0 %                                              |
| LASSO                      | 1.83 %                    | -6.75 % better         | -0.1396 better              |              1.18 | 43 %                                 | 5 %                                              |
| raw factors                | 1.87 %                    | -7.97 % better         | -0.1454 better              |              1.18 | 38 %                                 | 0 %                                              |
| HAR                        | 1.80 %                    | +0.00 %                | +0.0000                     |              1.24 | 38 %                                 | 5 %                                              |
| GARCH                      | 1.88 %                    | -6.35 % n.s.           | -0.1125 n.s.                |              1.18 | 43 %                                 | 0 %                                              |
| GJR-GARCH                  | 1.91 %                    | -8.27 % n.s.           | -0.1389 better              |              1.17 | 38 %                                 | 0 %                                              |

### 1 % level, 4 weeks (21 series)

| method                     | violations (target 1 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 1.85 %                    | -5.52 % n.s.           | -0.0956 n.s.                |              1.54 |
| IBA, K formulas (averaged) | 1.83 %                    | -5.20 % n.s.           | -0.0943 n.s.                |              1.56 |
| IBA, generic formulas      | 1.93 %                    | -4.34 % n.s.           | -0.1080 n.s.                |              1.51 |
| group PCA                  | 1.84 %                    | -5.18 % n.s.           | -0.1001 n.s.                |              1.53 |
| PCA                        | 1.85 %                    | -3.83 % n.s.           | -0.0471 n.s.                |              1.57 |
| kernel PCA                 | 1.88 %                    | -0.34 % n.s.           | +0.0163 n.s.                |              1.61 |
| autoencoder                | 1.87 %                    | -3.34 % n.s.           | -0.0392 n.s.                |              1.57 |
| LASSO                      | 1.95 %                    | -3.77 % n.s.           | -0.0926 n.s.                |              1.54 |
| raw factors                | 1.97 %                    | -5.42 % n.s.           | -0.1320 n.s.                |              1.51 |
| HAR                        | 1.96 %                    | +0.00 %                | +0.0000                     |              1.59 |
| GARCH                      | 1.77 %                    | -5.37 % better         | -0.2466 better              |              1.53 |
| GJR-GARCH                  | 1.82 %                    | -6.86 % n.s.           | -0.2718 better              |              1.48 |

### 1 % level, 13 weeks (21 series)

| method                     | violations (target 1 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 2.47 %                    | -0.48 % n.s.           | -0.0311 n.s.                |              1.7  |
| IBA, K formulas (averaged) | 2.48 %                    | -0.39 % n.s.           | -0.0204 n.s.                |              1.7  |
| IBA, generic formulas      | 2.47 %                    | -0.66 % n.s.           | -0.0399 n.s.                |              1.7  |
| group PCA                  | 2.55 %                    | +1.20 % n.s.           | +0.0615 n.s.                |              1.72 |
| PCA                        | 2.45 %                    | +0.14 % n.s.           | +0.0209 n.s.                |              1.72 |
| kernel PCA                 | 2.46 %                    | +0.23 % n.s.           | +0.0226 n.s.                |              1.72 |
| autoencoder                | 2.45 %                    | +0.03 % n.s.           | +0.0125 n.s.                |              1.72 |
| LASSO                      | 2.55 %                    | +1.04 % n.s.           | +0.0768 n.s.                |              1.71 |
| raw factors                | 2.54 %                    | +0.21 % n.s.           | +0.0509 n.s.                |              1.7  |
| HAR                        | 2.46 %                    | +0.00 %                | +0.0000                     |              1.71 |
| GARCH                      | 2.20 %                    | -5.81 % n.s.           | -0.4017 n.s.                |              1.6  |
| GJR-GARCH                  | 2.26 %                    | -5.31 % n.s.           | -0.3458 better              |              1.61 |

## 2. The long/flat rule on the return forecasts (no transaction costs)

Long for the next h periods when the forecast return is not negative, else flat. Means over series; VaR and CVaR are of the h-period returns.

### weekly, 1 week

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 21) |   series with smaller drawdown (of 21) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 9.4 %           |     0.68 |                            0.59 | 3.1 %     | 4.9 %      | 24.6 %         | 76 %            |              12.1 |                                                    16 |                                     17 |
| IBA, K formulas (averaged) | 8.8 %           |     0.64 |                            0.56 | 3.2 %     | 5.0 %      | 25.8 %         | 77 %            |              11.3 |                                                    16 |                                     15 |
| IBA, generic formulas      | 7.8 %           |     0.56 |                            0.48 | 3.3 %     | 5.1 %      | 29.0 %         | 76 %            |              12.6 |                                                    10 |                                     14 |
| group PCA                  | 8.7 %           |     0.63 |                            0.55 | 3.2 %     | 5.0 %      | 26.0 %         | 77 %            |              10.8 |                                                    14 |                                     19 |
| PCA                        | 6.3 %           |     0.48 |                            0.41 | 3.4 %     | 5.3 %      | 31.1 %         | 80 %            |              10.3 |                                                     6 |                                      9 |
| kernel PCA                 | 6.9 %           |     0.49 |                            0.45 | 3.5 %     | 5.6 %      | 32.7 %         | 85 %            |               6.2 |                                                     2 |                                      5 |
| autoencoder                | 6.6 %           |     0.5  |                            0.44 | 3.4 %     | 5.4 %      | 32.3 %         | 82 %            |               8.8 |                                                     6 |                                      9 |
| LASSO                      | 7.4 %           |     0.56 |                            0.44 | 3.2 %     | 4.7 %      | 24.2 %         | 71 %            |              14.4 |                                                    12 |                                     17 |
| raw factors                | 10.2 %          |     0.75 |                            0.58 | 3.0 %     | 4.5 %      | 25.0 %         | 66 %            |              19.1 |                                                    18 |                                     18 |
| historical mean            | 7.9 %           |     0.51 |                            0.51 | 3.6 %     | 5.7 %      | 33.8 %         | 92 %            |               0.1 |                                                     0 |                                      3 |
| trailing momentum          | 4.6 %           |     0.43 |                            0.4  | 3.2 %     | 4.9 %      | 29.4 %         | 69 %            |               3.1 |                                                     2 |                                     18 |
| buy-and-hold               | 8.9 %           |     0.56 |                            0.56 | 4.1 %     | 6.5 %      | 37.7 %         | 100 %           |               0   |                                                       |                                        |

### weekly, 4 weeks

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 21) |   series with smaller drawdown (of 21) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 7.5 %           |     0.55 |                            0.54 | 6.3 %     | 9.8 %      | 28.3 %         | 85 %            |               1.7 |                                                     5 |                                     12 |
| IBA, K formulas (averaged) | 8.1 %           |     0.57 |                            0.56 | 6.3 %     | 9.7 %      | 27.6 %         | 86 %            |               1.5 |                                                     8 |                                     13 |
| IBA, generic formulas      | 7.4 %           |     0.53 |                            0.52 | 6.4 %     | 9.8 %      | 29.0 %         | 85 %            |               1.8 |                                                     3 |                                     15 |
| group PCA                  | 6.9 %           |     0.52 |                            0.51 | 6.4 %     | 10.0 %     | 29.4 %         | 86 %            |               1.5 |                                                     3 |                                     13 |
| PCA                        | 7.3 %           |     0.53 |                            0.52 | 6.5 %     | 10.2 %     | 30.4 %         | 89 %            |               1.1 |                                                     1 |                                      7 |
| kernel PCA                 | 7.6 %           |     0.53 |                            0.52 | 6.5 %     | 10.1 %     | 29.8 %         | 88 %            |               1   |                                                     0 |                                      5 |
| autoencoder                | 7.3 %           |     0.52 |                            0.52 | 6.5 %     | 10.2 %     | 30.3 %         | 89 %            |               1.1 |                                                     1 |                                      7 |
| LASSO                      | 7.0 %           |     0.55 |                            0.53 | 5.8 %     | 9.0 %      | 25.5 %         | 78 %            |               2.2 |                                                     6 |                                     16 |
| raw factors                | 7.2 %           |     0.55 |                            0.53 | 5.8 %     | 9.4 %      | 26.9 %         | 73 %            |               3.5 |                                                     5 |                                     18 |
| historical mean            | 8.3 %           |     0.55 |                            0.55 | 6.7 %     | 10.3 %     | 29.4 %         | 93 %            |               0.1 |                                                     0 |                                      3 |
| trailing momentum          | 4.2 %           |     0.43 |                            0.41 | 6.1 %     | 9.6 %      | 28.8 %         | 69 %            |               1.5 |                                                     2 |                                     14 |
| buy-and-hold               | 9.0 %           |     0.58 |                            0.58 | 7.5 %     | 11.8 %     | 33.8 %         | 100 %           |               0   |                                                       |                                        |

### weekly, 13 weeks

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 21) |   series with smaller drawdown (of 21) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 8.0 %           |     0.58 |                            0.58 | 9.6 %     | 14.8 %     | 24.2 %         | 88 %            |               0.4 |                                                     2 |                                     11 |
| IBA, K formulas (averaged) | 8.1 %           |     0.58 |                            0.58 | 9.7 %     | 15.0 %     | 24.4 %         | 90 %            |               0.4 |                                                     1 |                                      6 |
| IBA, generic formulas      | 8.2 %           |     0.59 |                            0.58 | 9.6 %     | 14.9 %     | 24.3 %         | 88 %            |               0.5 |                                                     4 |                                     11 |
| group PCA                  | 8.0 %           |     0.58 |                            0.58 | 9.7 %     | 15.0 %     | 24.4 %         | 89 %            |               0.4 |                                                     0 |                                      8 |
| PCA                        | 8.0 %           |     0.58 |                            0.57 | 9.8 %     | 15.1 %     | 24.7 %         | 91 %            |               0.2 |                                                     0 |                                      3 |
| kernel PCA                 | 8.3 %           |     0.59 |                            0.58 | 9.8 %     | 15.1 %     | 24.6 %         | 92 %            |               0.2 |                                                     2 |                                      4 |
| autoencoder                | 8.2 %           |     0.59 |                            0.58 | 9.8 %     | 15.1 %     | 24.7 %         | 91 %            |               0.2 |                                                     0 |                                      3 |
| LASSO                      | 7.3 %           |     0.54 |                            0.54 | 9.6 %     | 15.4 %     | 25.8 %         | 87 %            |               0.6 |                                                     1 |                                      5 |
| raw factors                | 7.1 %           |     0.54 |                            0.53 | 9.6 %     | 15.5 %     | 25.6 %         | 83 %            |               0.9 |                                                     0 |                                      7 |
| historical mean            | 8.8 %           |     0.61 |                            0.61 | 9.9 %     | 15.1 %     | 23.9 %         | 94 %            |               0   |                                                     0 |                                      2 |
| trailing momentum          | 3.5 %           |     0.42 |                            0.41 | 9.6 %     | 16.0 %     | 27.4 %         | 68 %            |               0.9 |                                                     3 |                                     10 |
| buy-and-hold               | 8.9 %           |     0.63 |                            0.63 | 11.2 %    | 17.8 %     | 28.1 %         | 100 %           |               0   |                                                       |                                        |

## 3. The tail probabilities as a classifier (10 % events; all tasks of the type, counts summed)

Signal: forecast probability above the base-rate forecast of the date; strong signal: above twice that.

### Large loss (event rate 10.2 %)

| method                     | signal rate   | precision     | recall   | specificity   |   MCC | strong: signal rate   | strong: precision   | strong: recall   |   reliability x1000 |   resolution x1000 |   sharpness |
|:---------------------------|:--------------|:--------------|:---------|:--------------|------:|:----------------------|:--------------------|:-----------------|--------------------:|-------------------:|------------:|
| IBA, K formulas (fixed)    | 39.9 %        | 11.9 %        | 46.2 %   | 60.8 %        | 0.044 | 1.2 %                 | 15.2 %              | 1.7 %            |                0.56 |               0.49 |       0.036 |
| IBA, K formulas (averaged) | 39.0 %        | 12.2 %        | 46.5 %   | 61.8 %        | 0.052 | 1.0 %                 | 15.5 %              | 1.5 %            |                0.55 |               0.53 |       0.033 |
| IBA, generic formulas      | 40.3 %        | 13.1 %        | 51.5 %   | 61.0 %        | 0.078 | 2.2 %                 | 17.7 %              | 3.7 %            |                0.95 |               0.86 |       0.042 |
| group PCA                  | 42.6 %        | 11.0 %        | 45.8 %   | 57.8 %        | 0.022 | 1.2 %                 | 13.0 %              | 1.6 %            |                0.64 |               0.23 |       0.035 |
| PCA                        | 46.1 %        | 10.7 %        | 48.2 %   | 54.2 %        | 0.015 | 1.1 %                 | 14.6 %              | 1.6 %            |                0.62 |               0.36 |       0.031 |
| kernel PCA                 | 51.4 %        | 10.7 %        | 53.9 %   | 48.9 %        | 0.017 | 0.8 %                 | 8.5 %               | 0.7 %            |                0.86 |               0.42 |       0.025 |
| autoencoder                | 45.0 %        | 10.9 %        | 47.8 %   | 55.3 %        | 0.019 | 1.3 %                 | 12.8 %              | 1.6 %            |                0.61 |               0.32 |       0.026 |
| LASSO                      | 40.7 %        | 11.8 %        | 47.0 %   | 60.0 %        | 0.043 | 1.9 %                 | 18.2 %              | 3.4 %            |                0.71 |               0.54 |       0.045 |
| raw factors                | 41.7 %        | 11.6 %        | 47.4 %   | 59.0 %        | 0.039 | 1.6 %                 | 12.9 %              | 2.1 %            |                0.59 |               0.3  |       0.044 |
| base rate                  | 0.0 %         | never signals | 0.0 %    | 100.0 %       | 0     | 0.0 %                 | never               | 0.0 %            |                2.04 |               2.06 |       0     |
| volatility-based logit     | 42.7 %        | 10.5 %        | 43.7 %   | 57.4 %        | 0.007 | 2.9 %                 | 12.0 %              | 3.4 %            |                1.49 |               0.36 |       0.045 |
| GARCH-based probability    | 65.7 %        | 11.1 %        | 71.1 %   | 34.9 %        | 0.038 | 12.6 %                | 14.5 %              | 17.8 %           |                3.12 |               0.6  |       0.064 |

Reliability by fifth of the forecast (lowest to highest), tasks pooled:

| method                  |   fifth | mean forecast   | observed   |
|:------------------------|--------:|:----------------|:-----------|
| IBA, K formulas (fixed) |       1 | 7.2 %           | 9.0 %      |
| IBA, K formulas (fixed) |       2 | 9.4 %           | 8.8 %      |
| IBA, K formulas (fixed) |       3 | 9.9 %           | 9.3 %      |
| IBA, K formulas (fixed) |       4 | 10.2 %          | 11.3 %     |
| IBA, K formulas (fixed) |       5 | 13.4 %          | 12.8 %     |
| volatility-based logit  |       1 | 5.9 %           | 10.5 %     |
| volatility-based logit  |       2 | 8.2 %           | 9.5 %      |
| volatility-based logit  |       3 | 9.5 %           | 10.0 %     |
| volatility-based logit  |       4 | 11.0 %          | 10.0 %     |
| volatility-based logit  |       5 | 16.4 %          | 11.2 %     |

### Large gain (event rate 12.6 %)

| method                     | signal rate   | precision     | recall   | specificity   |   MCC | strong: signal rate   | strong: precision   | strong: recall   |   reliability x1000 |   resolution x1000 |   sharpness |
|:---------------------------|:--------------|:--------------|:---------|:--------------|------:|:----------------------|:--------------------|:-----------------|--------------------:|-------------------:|------------:|
| IBA, K formulas (fixed)    | 39.0 %        | 17.0 %        | 52.7 %   | 62.9 %        | 0.106 | 2.6 %                 | 27.1 %              | 5.7 %            |                1.19 |               1.83 |       0.042 |
| IBA, K formulas (averaged) | 39.0 %        | 16.6 %        | 51.6 %   | 62.8 %        | 0.098 | 2.3 %                 | 29.0 %              | 5.4 %            |                1.19 |               1.95 |       0.039 |
| IBA, generic formulas      | 42.3 %        | 16.0 %        | 54.0 %   | 59.4 %        | 0.09  | 3.1 %                 | 17.3 %              | 4.2 %            |                1.27 |               1.26 |       0.042 |
| group PCA                  | 42.3 %        | 15.8 %        | 53.1 %   | 59.3 %        | 0.083 | 1.8 %                 | 30.5 %              | 4.3 %            |                1.08 |               1.43 |       0.035 |
| PCA                        | 42.6 %        | 15.5 %        | 52.5 %   | 58.9 %        | 0.076 | 1.8 %                 | 30.9 %              | 4.4 %            |                0.98 |               1.28 |       0.036 |
| kernel PCA                 | 50.4 %        | 13.8 %        | 55.3 %   | 50.3 %        | 0.037 | 0.6 %                 | 15.4 %              | 0.7 %            |                1.14 |               0.52 |       0.026 |
| autoencoder                | 42.6 %        | 15.1 %        | 51.2 %   | 58.6 %        | 0.065 | 1.8 %                 | 31.2 %              | 4.5 %            |                0.9  |               1.19 |       0.033 |
| LASSO                      | 40.7 %        | 15.5 %        | 50.2 %   | 60.6 %        | 0.073 | 2.6 %                 | 23.2 %              | 4.8 %            |                1.16 |               1.37 |       0.042 |
| raw factors                | 40.6 %        | 15.7 %        | 50.7 %   | 60.8 %        | 0.077 | 3.7 %                 | 22.3 %              | 6.7 %            |                1.48 |               1.36 |       0.057 |
| base rate                  | 0.0 %         | never signals | 0.0 %    | 100.0 %       | 0     | 0.0 %                 | never               | 0.0 %            |                1.62 |               0.97 |       0     |
| volatility-based logit     | 29.7 %        | 21.9 %        | 51.8 %   | 73.5 %        | 0.183 | 8.2 %                 | 31.8 %              | 20.8 %           |                1.26 |               5.81 |       0.094 |
| GARCH-based probability    | 73.4 %        | 14.9 %        | 87.0 %   | 28.6 %        | 0.116 | 16.3 %                | 28.7 %              | 37.3 %           |                1.22 |               6.8  |       0.065 |

Reliability by fifth of the forecast (lowest to highest), tasks pooled:

| method                  |   fifth | mean forecast   | observed   |
|:------------------------|--------:|:----------------|:-----------|
| IBA, K formulas (fixed) |       1 | 6.4 %           | 7.8 %      |
| IBA, K formulas (fixed) |       2 | 8.6 %           | 10.3 %     |
| IBA, K formulas (fixed) |       3 | 9.8 %           | 11.3 %     |
| IBA, K formulas (fixed) |       4 | 10.3 %          | 15.4 %     |
| IBA, K formulas (fixed) |       5 | 15.5 %          | 18.0 %     |
| volatility-based logit  |       1 | 3.0 %           | 4.6 %      |
| volatility-based logit  |       2 | 5.2 %           | 7.6 %      |
| volatility-based logit  |       3 | 7.3 %           | 11.1 %     |
| volatility-based logit  |       4 | 10.1 %          | 14.7 %     |
| volatility-based logit  |       5 | 23.3 %          | 24.9 %     |

## 4. Crisis and drawdown periods (descriptive: short subsamples, no test)

Primary loss relative to the reference (negative = better) on forecasts made in the period, all series pooled; mean over the tasks of the type. In brackets: pooled forecasts per task, smallest to largest.

### weekly: Q4 2018 sell-off (273 to 273 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +10.0 %  | +2.5 %  | +6.3 %      | -3.0 %      |
| IBA, K formulas (averaged) | +8.4 %   | -0.4 %  | +6.3 %      | -3.8 %      |
| IBA, generic formulas      | +10.9 %  | -0.4 %  | +9.7 %      | -0.7 %      |
| group PCA                  | +8.5 %   | +1.1 %  | +7.4 %      | -4.2 %      |
| PCA                        | +3.9 %   | -5.3 %  | +4.3 %      | -5.1 %      |
| kernel PCA                 | +1.5 %   | -6.3 %  | +1.8 %      | -0.4 %      |
| autoencoder                | +3.9 %   | -4.3 %  | +3.2 %      | -4.9 %      |
| LASSO                      | +10.8 %  | -2.5 %  | +14.2 %     | -5.0 %      |
| raw factors                | +10.4 %  | -3.9 %  | +16.9 %     | -6.5 %      |
| trailing momentum          | +28.0 %  |         |             |             |
| GARCH                      |          | +0.9 %  |             |             |
| GJR-GARCH                  |          | -0.6 %  |             |             |
| volatility-based logit     |          |         | +3.9 %      | -1.8 %      |
| GARCH-based probability    |          |         | +10.8 %     | -6.5 %      |

### weekly: COVID-19 crash (210 to 210 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | -0.1 %   | -18.8 % | -0.0 %      | -12.5 %     |
| IBA, K formulas (averaged) | -0.4 %   | -18.3 % | -3.6 %      | -11.8 %     |
| IBA, generic formulas      | -1.2 %   | -16.3 % | -7.0 %      | -6.1 %      |
| group PCA                  | +5.2 %   | -19.4 % | -0.5 %      | -4.3 %      |
| PCA                        | +2.2 %   | -14.2 % | -2.2 %      | -4.3 %      |
| kernel PCA                 | +0.2 %   | -2.7 %  | -1.9 %      | -1.5 %      |
| autoencoder                | +0.9 %   | -11.8 % | -3.9 %      | -4.4 %      |
| LASSO                      | +0.1 %   | -16.3 % | -4.2 %      | -6.6 %      |
| raw factors                | +1.3 %   | -22.4 % | -0.2 %      | -8.0 %      |
| trailing momentum          | +13.7 %  |         |             |             |
| GARCH                      |          | -11.3 % |             |             |
| GJR-GARCH                  |          | -14.9 % |             |             |
| volatility-based logit     |          |         | +5.4 %      | -37.9 %     |
| GARCH-based probability    |          |         | +30.7 %     | -31.7 %     |

### weekly: 2022: invasion of Ukraine and rate shock (756 to 756 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | -0.2 %   | -3.3 %  | -0.3 %      | +0.9 %      |
| IBA, K formulas (averaged) | -0.2 %   | -4.3 %  | -0.3 %      | +0.7 %      |
| IBA, generic formulas      | +0.6 %   | -10.5 % | -0.9 %      | +2.1 %      |
| group PCA                  | +1.1 %   | -6.2 %  | +0.1 %      | -0.6 %      |
| PCA                        | +1.4 %   | -4.4 %  | +0.3 %      | -0.6 %      |
| kernel PCA                 | +0.1 %   | -1.8 %  | -0.5 %      | -0.1 %      |
| autoencoder                | +1.3 %   | -2.6 %  | +0.0 %      | -0.4 %      |
| LASSO                      | +3.2 %   | -8.6 %  | -1.1 %      | -0.2 %      |
| raw factors                | +3.4 %   | -11.6 % | -0.8 %      | +12.6 %     |
| trailing momentum          | +17.3 %  |         |             |             |
| GARCH                      |          | -11.8 % |             |             |
| GJR-GARCH                  |          | -6.4 %  |             |             |
| volatility-based logit     |          |         | -0.7 %      | +7.8 %      |
| GARCH-based probability    |          |         | -9.1 %      | +4.6 %      |

### weekly: other periods (7497 to 7497 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +2.1 %   | -5.3 %  | +0.8 %      | -0.7 %      |
| IBA, K formulas (averaged) | +1.8 %   | -5.3 %  | +0.7 %      | -0.8 %      |
| IBA, generic formulas      | +2.2 %   | -3.8 %  | +1.1 %      | +0.2 %      |
| group PCA                  | +1.6 %   | -3.4 %  | +1.2 %      | -0.6 %      |
| PCA                        | +0.9 %   | -2.2 %  | +1.0 %      | -0.7 %      |
| kernel PCA                 | +0.9 %   | -1.2 %  | +1.4 %      | +0.1 %      |
| autoencoder                | +0.9 %   | -2.0 %  | +1.2 %      | -0.7 %      |
| LASSO                      | +3.3 %   | -2.2 %  | +1.1 %      | -0.2 %      |
| raw factors                | +4.3 %   | -2.0 %  | +1.6 %      | +0.1 %      |
| trailing momentum          | +15.4 %  |         |             |             |
| GARCH                      |          | +19.0 % |             |             |
| GJR-GARCH                  |          | +12.9 % |             |             |
| volatility-based logit     |          |         | +2.0 %      | -4.5 %      |
| GARCH-based probability    |          |         | +5.7 %      | -5.2 %      |

### weekly: in drawdown (at least 10 % below the peak) (3788 to 3823 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +1.5 %   | -10.7 % | +0.5 %      | -1.8 %      |
| IBA, K formulas (averaged) | +1.2 %   | -10.7 % | +0.2 %      | -1.9 %      |
| IBA, generic formulas      | +1.5 %   | -8.2 %  | +1.4 %      | -0.9 %      |
| group PCA                  | +2.3 %   | -8.6 %  | +1.8 %      | -1.1 %      |
| PCA                        | +1.3 %   | -6.3 %  | +1.2 %      | -1.4 %      |
| kernel PCA                 | +0.8 %   | -2.0 %  | +1.2 %      | -0.3 %      |
| autoencoder                | +1.1 %   | -5.2 %  | +1.0 %      | -1.3 %      |
| LASSO                      | +2.6 %   | -7.0 %  | +1.5 %      | -1.5 %      |
| raw factors                | +3.2 %   | -9.4 %  | +1.7 %      | -0.2 %      |
| trailing momentum          | +15.9 %  |         |             |             |
| GARCH                      |          | +15.5 % |             |             |
| GJR-GARCH                  |          | +10.3 % |             |             |
| volatility-based logit     |          |         | +2.9 %      | -6.7 %      |
| GARCH-based probability    |          |         | +7.8 %      | -9.7 %      |

### weekly: not in drawdown (4913 to 4948 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +1.4 %   | -4.5 %  | +0.5 %      | -1.1 %      |
| IBA, K formulas (averaged) | +1.1 %   | -4.5 %  | +0.4 %      | -1.1 %      |
| IBA, generic formulas      | +1.7 %   | -4.1 %  | -0.2 %      | +0.9 %      |
| group PCA                  | +1.5 %   | -3.7 %  | +0.3 %      | -0.7 %      |
| PCA                        | +0.6 %   | -2.5 %  | +0.3 %      | -0.7 %      |
| kernel PCA                 | +0.5 %   | -1.3 %  | +0.4 %      | +0.3 %      |
| autoencoder                | +0.6 %   | -2.2 %  | +0.5 %      | -0.8 %      |
| LASSO                      | +2.4 %   | -2.7 %  | -0.0 %      | +0.1 %      |
| raw factors                | +4.2 %   | -2.7 %  | +0.8 %      | +0.8 %      |
| trailing momentum          | +13.4 %  |         |             |             |
| GARCH                      |          | +12.4 % |             |             |
| GJR-GARCH                  |          | +7.0 %  |             |             |
| volatility-based logit     |          |         | +0.8 %      | -4.6 %      |
| GARCH-based probability    |          |         | +0.8 %      | -2.0 %      |
