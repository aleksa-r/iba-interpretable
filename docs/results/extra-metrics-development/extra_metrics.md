# Financial and classification measures of the stored forecasts (development series)

DESCRIPTIVE. Definitions in `docs/protocol/EXTRA_METRICS.md`, written before these numbers were computed; the specs whose forecasts are read were frozen without these measures, so nothing here decides anything. All factor methods with the linear model. Formula set of the final method: Kc; its averaged reading: `iba_ca_b`. GARCH forecasts from the first study (458 cells); kernel PCA and autoencoder from their own run (458 cells).

## 1. Value at risk and expected shortfall from the volatility forecasts (weekly series, zero-mean normal returns)

### 5 % level, 1 week (37 series)

| method                     | violations (target 5 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio | series rejecting coverage (Kupiec)   | series rejecting independence (Christoffersen)   |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|:-------------------------------------|:-------------------------------------------------|
| IBA, K formulas (fixed)    | 5.26 %                    | -2.19 % n.s.           | -0.0418 better              |              1.12 | 3 %                                  | 3 %                                              |
| IBA, K formulas (averaged) | 5.26 %                    | -2.28 % better         | -0.0451 better              |              1.11 | 3 %                                  | 3 %                                              |
| IBA, generic formulas      | 5.17 %                    | -2.19 % better         | -0.0401 better              |              1.13 | 3 %                                  | 3 %                                              |
| group PCA                  | 5.24 %                    | -2.19 % n.s.           | -0.0433 better              |              1.12 | 3 %                                  | 3 %                                              |
| PCA                        | 5.05 %                    | -1.43 % n.s.           | -0.0225 n.s.                |              1.14 | 0 %                                  | 3 %                                              |
| kernel PCA                 | 5.21 %                    | -0.03 % n.s.           | -0.0022 n.s.                |              1.14 | 5 %                                  | 3 %                                              |
| autoencoder                | 5.04 %                    | -1.36 % n.s.           | -0.0191 n.s.                |              1.14 | 0 %                                  | 3 %                                              |
| LASSO                      | 5.28 %                    | -1.82 % n.s.           | -0.0331 n.s.                |              1.13 | 3 %                                  | 3 %                                              |
| raw factors                | 5.29 %                    | -2.20 % n.s.           | -0.0418 better              |              1.13 | 3 %                                  | 3 %                                              |
| HAR                        | 5.09 %                    | +0.00 %                | +0.0000                     |              1.14 | 0 %                                  | 3 %                                              |
| GARCH                      | 5.20 %                    | -1.47 % n.s.           | -0.0251 n.s.                |              1.14 | 3 %                                  | 0 %                                              |
| GJR-GARCH                  | 5.37 %                    | -1.80 % n.s.           | -0.0294 n.s.                |              1.13 | 3 %                                  | 5 %                                              |

### 5 % level, 4 weeks (37 series)

| method                     | violations (target 5 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 4.94 %                    | -1.96 % n.s.           | -0.0307 n.s.                |              1.2  |
| IBA, K formulas (averaged) | 4.91 %                    | -1.84 % n.s.           | -0.0294 n.s.                |              1.21 |
| IBA, generic formulas      | 4.86 %                    | -2.02 % better         | -0.0371 better              |              1.21 |
| group PCA                  | 4.95 %                    | -1.49 % n.s.           | -0.0282 n.s.                |              1.2  |
| PCA                        | 4.96 %                    | -0.88 % n.s.           | -0.0116 n.s.                |              1.22 |
| kernel PCA                 | 4.92 %                    | -0.01 % n.s.           | +0.0034 n.s.                |              1.24 |
| autoencoder                | 4.90 %                    | -0.68 % n.s.           | -0.0096 n.s.                |              1.23 |
| LASSO                      | 4.94 %                    | -1.15 % n.s.           | -0.0257 n.s.                |              1.22 |
| raw factors                | 5.07 %                    | -1.98 % n.s.           | -0.0415 n.s.                |              1.21 |
| HAR                        | 4.87 %                    | +0.00 %                | +0.0000                     |              1.24 |
| GARCH                      | 4.85 %                    | -0.88 % n.s.           | -0.0567 n.s.                |              1.2  |
| GJR-GARCH                  | 4.91 %                    | -1.63 % n.s.           | -0.0666 better              |              1.2  |

### 5 % level, 13 weeks (37 series)

| method                     | violations (target 5 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 4.09 %                    | +0.02 % n.s.           | -0.0037 n.s.                |              1.37 |
| IBA, K formulas (averaged) | 4.09 %                    | +0.01 % n.s.           | -0.0031 n.s.                |              1.37 |
| IBA, generic formulas      | 4.05 %                    | -0.31 % n.s.           | -0.0109 n.s.                |              1.38 |
| group PCA                  | 4.08 %                    | +0.28 % n.s.           | +0.0071 n.s.                |              1.38 |
| PCA                        | 4.07 %                    | +0.24 % n.s.           | +0.0062 n.s.                |              1.37 |
| kernel PCA                 | 4.06 %                    | +0.11 % n.s.           | +0.0051 n.s.                |              1.37 |
| autoencoder                | 4.08 %                    | +0.11 % n.s.           | +0.0029 n.s.                |              1.37 |
| LASSO                      | 4.08 %                    | +0.27 % n.s.           | +0.0074 n.s.                |              1.37 |
| raw factors                | 4.15 %                    | +0.01 % n.s.           | +0.0022 n.s.                |              1.38 |
| HAR                        | 4.02 %                    | +0.00 %                | +0.0000                     |              1.37 |
| GARCH                      | 3.75 %                    | -0.97 % n.s.           | -0.0821 n.s.                |              1.28 |
| GJR-GARCH                  | 3.85 %                    | -1.53 % n.s.           | -0.0822 n.s.                |              1.29 |

### 1 % level, 1 week (37 series)

| method                     | violations (target 1 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio | series rejecting coverage (Kupiec)   | series rejecting independence (Christoffersen)   |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|:-------------------------------------|:-------------------------------------------------|
| IBA, K formulas (fixed)    | 1.77 %                    | -5.91 % better         | -0.1274 better              |              1.17 | 22 %                                 | 0 %                                              |
| IBA, K formulas (averaged) | 1.76 %                    | -6.33 % better         | -0.1386 better              |              1.17 | 21 %                                 | 0 %                                              |
| IBA, generic formulas      | 1.81 %                    | -5.40 % better         | -0.1263 better              |              1.17 | 19 %                                 | 0 %                                              |
| group PCA                  | 1.78 %                    | -6.26 % better         | -0.1413 better              |              1.16 | 19 %                                 | 0 %                                              |
| PCA                        | 1.83 %                    | -3.88 % n.s.           | -0.0700 n.s.                |              1.18 | 30 %                                 | 0 %                                              |
| kernel PCA                 | 1.89 %                    | -1.07 % n.s.           | -0.0197 n.s.                |              1.19 | 43 %                                 | 0 %                                              |
| autoencoder                | 1.84 %                    | -3.34 % n.s.           | -0.0567 n.s.                |              1.19 | 35 %                                 | 0 %                                              |
| LASSO                      | 1.82 %                    | -4.50 % better         | -0.1044 better              |              1.18 | 32 %                                 | 0 %                                              |
| raw factors                | 1.83 %                    | -6.24 % better         | -0.1369 better              |              1.16 | 22 %                                 | 0 %                                              |
| HAR                        | 1.83 %                    | +0.00 %                | +0.0000                     |              1.21 | 32 %                                 | 0 %                                              |
| GARCH                      | 1.81 %                    | -4.12 % n.s.           | -0.0889 n.s.                |              1.18 | 32 %                                 | 0 %                                              |
| GJR-GARCH                  | 1.83 %                    | -4.97 % n.s.           | -0.0968 n.s.                |              1.18 | 38 %                                 | 0 %                                              |

### 1 % level, 4 weeks (37 series)

| method                     | violations (target 1 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 1.57 %                    | -4.42 % n.s.           | -0.0758 n.s.                |              1.45 |
| IBA, K formulas (averaged) | 1.60 %                    | -4.28 % n.s.           | -0.0724 n.s.                |              1.45 |
| IBA, generic formulas      | 1.54 %                    | -3.82 % better         | -0.0863 n.s.                |              1.48 |
| group PCA                  | 1.57 %                    | -4.02 % n.s.           | -0.0760 n.s.                |              1.45 |
| PCA                        | 1.60 %                    | -2.81 % n.s.           | -0.0263 n.s.                |              1.45 |
| kernel PCA                 | 1.71 %                    | -0.23 % n.s.           | +0.0157 n.s.                |              1.44 |
| autoencoder                | 1.61 %                    | -2.02 % n.s.           | -0.0193 n.s.                |              1.45 |
| LASSO                      | 1.70 %                    | -2.88 % n.s.           | -0.0706 n.s.                |              1.41 |
| raw factors                | 1.72 %                    | -3.95 % n.s.           | -0.1032 n.s.                |              1.42 |
| HAR                        | 1.73 %                    | +0.00 %                | +0.0000                     |              1.43 |
| GARCH                      | 1.49 %                    | -4.63 % n.s.           | -0.2093 better              |              1.42 |
| GJR-GARCH                  | 1.55 %                    | -5.86 % n.s.           | -0.2249 better              |              1.39 |

### 1 % level, 13 weeks (37 series)

| method                     | violations (target 1 %)   | quantile loss vs HAR   | VaR-ES score (FZ0) vs HAR   |   shortfall ratio |
|:---------------------------|:--------------------------|:-----------------------|:----------------------------|------------------:|
| IBA, K formulas (fixed)    | 2.23 %                    | -0.32 % n.s.           | -0.0177 n.s.                |              1.42 |
| IBA, K formulas (averaged) | 2.23 %                    | -0.27 % n.s.           | -0.0146 n.s.                |              1.42 |
| IBA, generic formulas      | 2.24 %                    | -0.67 % n.s.           | -0.0329 n.s.                |              1.42 |
| group PCA                  | 2.26 %                    | +0.65 % n.s.           | +0.0238 n.s.                |              1.43 |
| PCA                        | 2.23 %                    | +0.17 % n.s.           | +0.0187 n.s.                |              1.42 |
| kernel PCA                 | 2.22 %                    | +0.22 % n.s.           | +0.0167 n.s.                |              1.43 |
| autoencoder                | 2.23 %                    | -0.03 % n.s.           | +0.0083 n.s.                |              1.41 |
| LASSO                      | 2.22 %                    | +0.68 % n.s.           | +0.0386 n.s.                |              1.45 |
| raw factors                | 2.31 %                    | +0.24 % n.s.           | +0.0254 n.s.                |              1.41 |
| HAR                        | 2.20 %                    | +0.00 %                | +0.0000                     |              1.44 |
| GARCH                      | 1.85 %                    | -7.85 % n.s.           | -0.3460 n.s.                |              1.34 |
| GJR-GARCH                  | 1.89 %                    | -7.44 % n.s.           | -0.3110 better              |              1.35 |

## 2. The long/flat rule on the return forecasts (no transaction costs)

Long for the next h periods when the forecast return is not negative, else flat. Means over series; VaR and CVaR are of the h-period returns.

### weekly, 1 week

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 37) |   series with smaller drawdown (of 37) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 8.6 %           |     0.61 |                            0.52 | 3.1 %     | 4.7 %      | 26.0 %         | 72 %            |              12.1 |                                                    24 |                                     33 |
| IBA, K formulas (averaged) | 8.5 %           |     0.6  |                            0.51 | 3.1 %     | 4.7 %      | 25.7 %         | 73 %            |              11.3 |                                                    25 |                                     32 |
| IBA, generic formulas      | 7.6 %           |     0.55 |                            0.45 | 3.2 %     | 4.7 %      | 28.3 %         | 73 %            |              12.8 |                                                    20 |                                     31 |
| group PCA                  | 7.5 %           |     0.52 |                            0.43 | 3.2 %     | 4.8 %      | 28.4 %         | 74 %            |              11.3 |                                                    22 |                                     27 |
| PCA                        | 5.6 %           |     0.42 |                            0.35 | 3.3 %     | 5.1 %      | 32.0 %         | 77 %            |              10.3 |                                                     7 |                                     18 |
| kernel PCA                 | 6.3 %           |     0.42 |                            0.37 | 3.3 %     | 5.4 %      | 34.6 %         | 81 %            |               6.8 |                                                     4 |                                     11 |
| autoencoder                | 5.8 %           |     0.42 |                            0.36 | 3.3 %     | 5.2 %      | 31.4 %         | 78 %            |               8.7 |                                                     6 |                                     20 |
| LASSO                      | 6.9 %           |     0.53 |                            0.41 | 3.1 %     | 4.5 %      | 25.4 %         | 69 %            |              14.4 |                                                    18 |                                     32 |
| raw factors                | 8.8 %           |     0.62 |                            0.45 | 3.1 %     | 4.6 %      | 26.7 %         | 63 %            |              19.7 |                                                    26 |                                     31 |
| historical mean            | 7.2 %           |     0.45 |                            0.44 | 3.2 %     | 5.2 %      | 32.9 %         | 86 %            |               0.1 |                                                     1 |                                      5 |
| trailing momentum          | 5.3 %           |     0.45 |                            0.43 | 3.2 %     | 5.1 %      | 28.6 %         | 66 %            |               2.7 |                                                    11 |                                     31 |
| buy-and-hold               | 8.1 %           |     0.51 |                            0.51 | 4.1 %     | 6.3 %      | 38.3 %         | 100 %           |               0   |                                                       |                                        |

### weekly, 4 weeks

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 37) |   series with smaller drawdown (of 37) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 7.1 %           |     0.5  |                            0.48 | 5.9 %     | 8.9 %      | 27.0 %         | 80 %            |               1.7 |                                                    11 |                                     20 |
| IBA, K formulas (averaged) | 7.3 %           |     0.5  |                            0.49 | 5.9 %     | 9.0 %      | 27.0 %         | 80 %            |               1.6 |                                                    12 |                                     20 |
| IBA, generic formulas      | 6.9 %           |     0.48 |                            0.47 | 6.0 %     | 9.1 %      | 28.4 %         | 82 %            |               1.6 |                                                     9 |                                     22 |
| group PCA                  | 6.6 %           |     0.47 |                            0.46 | 6.1 %     | 9.2 %      | 28.6 %         | 82 %            |               1.4 |                                                     6 |                                     20 |
| PCA                        | 6.3 %           |     0.44 |                            0.43 | 6.1 %     | 9.3 %      | 29.7 %         | 84 %            |               1   |                                                     3 |                                     13 |
| kernel PCA                 | 6.6 %           |     0.45 |                            0.44 | 6.0 %     | 9.1 %      | 28.8 %         | 82 %            |               1.2 |                                                     2 |                                     15 |
| autoencoder                | 6.6 %           |     0.46 |                            0.45 | 6.1 %     | 9.3 %      | 28.9 %         | 84 %            |               1   |                                                     3 |                                     15 |
| LASSO                      | 6.5 %           |     0.5  |                            0.49 | 5.5 %     | 8.5 %      | 26.0 %         | 74 %            |               2.3 |                                                    13 |                                     31 |
| raw factors                | 6.9 %           |     0.5  |                            0.47 | 5.5 %     | 8.8 %      | 27.1 %         | 71 %            |               3.4 |                                                    16 |                                     29 |
| historical mean            | 7.4 %           |     0.47 |                            0.47 | 6.0 %     | 9.1 %      | 28.7 %         | 86 %            |               0.1 |                                                     1 |                                      5 |
| trailing momentum          | 4.7 %           |     0.42 |                            0.41 | 5.9 %     | 9.3 %      | 27.9 %         | 66 %            |               1.4 |                                                     7 |                                     26 |
| buy-and-hold               | 8.0 %           |     0.52 |                            0.52 | 7.7 %     | 11.2 %     | 34.8 %         | 100 %           |               0   |                                                       |                                        |

### weekly, 13 weeks

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 37) |   series with smaller drawdown (of 37) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 7.1 %           |     0.51 |                            0.51 | 9.2 %     | 13.2 %     | 24.5 %         | 84 %            |               0.4 |                                                     6 |                                     15 |
| IBA, K formulas (averaged) | 7.1 %           |     0.51 |                            0.51 | 9.2 %     | 13.3 %     | 24.6 %         | 84 %            |               0.4 |                                                     7 |                                     13 |
| IBA, generic formulas      | 7.2 %           |     0.52 |                            0.51 | 9.1 %     | 13.2 %     | 24.4 %         | 83 %            |               0.4 |                                                     8 |                                     19 |
| group PCA                  | 6.9 %           |     0.5  |                            0.5  | 9.2 %     | 13.3 %     | 24.6 %         | 84 %            |               0.4 |                                                     6 |                                     16 |
| PCA                        | 7.2 %           |     0.5  |                            0.5  | 9.4 %     | 13.6 %     | 24.9 %         | 86 %            |               0.2 |                                                     2 |                                      9 |
| kernel PCA                 | 7.1 %           |     0.49 |                            0.49 | 9.4 %     | 13.6 %     | 25.0 %         | 86 %            |               0.2 |                                                     1 |                                      9 |
| autoencoder                | 7.1 %           |     0.5  |                            0.49 | 9.4 %     | 13.7 %     | 25.2 %         | 86 %            |               0.3 |                                                     1 |                                      9 |
| LASSO                      | 6.5 %           |     0.49 |                            0.49 | 9.1 %     | 13.5 %     | 24.8 %         | 82 %            |               0.5 |                                                     5 |                                     20 |
| raw factors                | 6.5 %           |     0.49 |                            0.48 | 9.0 %     | 13.4 %     | 24.3 %         | 79 %            |               0.8 |                                                     3 |                                     23 |
| historical mean            | 7.4 %           |     0.51 |                            0.51 | 9.4 %     | 13.6 %     | 25.0 %         | 87 %            |               0.1 |                                                     1 |                                      7 |
| trailing momentum          | 4.5 %           |     0.45 |                            0.44 | 9.3 %     | 14.5 %     | 25.2 %         | 65 %            |               0.8 |                                                     9 |                                     27 |
| buy-and-hold               | 7.9 %           |     0.56 |                            0.55 | 11.5 %    | 16.7 %     | 30.2 %         | 100 %           |               0   |                                                       |                                        |

### monthly, 1 month

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 11) |   series with smaller drawdown (of 11) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 5.6 %           |     1.05 |                            1.03 | 2.1 %     | 3.6 %      | 9.5 %          | 94 %            |               1.1 |                                                     4 |                                      2 |
| IBA, K formulas (averaged) | 5.7 %           |     1.05 |                            1.03 | 2.1 %     | 3.6 %      | 9.5 %          | 94 %            |               1.1 |                                                     4 |                                      2 |
| IBA, generic formulas      | 5.4 %           |     0.96 |                            0.94 | 2.3 %     | 3.9 %      | 9.6 %          | 95 %            |               1   |                                                     0 |                                      1 |
| group PCA                  | 5.9 %           |     1.09 |                            1.07 | 2.2 %     | 3.6 %      | 8.6 %          | 97 %            |               0.6 |                                                     2 |                                      2 |
| PCA                        | 6.1 %           |     1.13 |                            1.12 | 2.2 %     | 3.4 %      | 8.6 %          | 96 %            |               0.7 |                                                     4 |                                      2 |
| kernel PCA                 | 5.9 %           |     1.11 |                            1.08 | 2.1 %     | 3.4 %      | 8.7 %          | 94 %            |               1.1 |                                                     4 |                                      3 |
| autoencoder                | 6.0 %           |     1.05 |                            1.03 | 2.2 %     | 3.9 %      | 9.4 %          | 96 %            |               0.7 |                                                     2 |                                      1 |
| LASSO                      | 5.7 %           |     1.11 |                            1.08 | 2.1 %     | 3.5 %      | 8.5 %          | 94 %            |               1.2 |                                                     3 |                                      3 |
| raw factors                | 5.8 %           |     1.17 |                            1.13 | 2.0 %     | 3.1 %      | 8.7 %          | 91 %            |               1.7 |                                                     5 |                                      6 |
| historical mean            | 6.3 %           |     1.07 |                            1.07 | 2.3 %     | 3.9 %      | 9.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 4.9 %           |     0.97 |                            0.95 | 1.9 %     | 3.5 %      | 8.5 %          | 82 %            |               0.8 |                                                     2 |                                      6 |
| buy-and-hold               | 6.3 %           |     1.07 |                            1.07 | 2.3 %     | 3.9 %      | 9.5 %          | 100 %           |               0   |                                                       |                                        |

### monthly, 3 months

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 11) |   series with smaller drawdown (of 11) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 6.2 %           |     1.05 |                            1.04 | 3.5 %     | 4.9 %      | 8.1 %          | 99 %            |               0.1 |                                                     0 |                                      0 |
| IBA, K formulas (averaged) | 6.2 %           |     1.05 |                            1.05 | 3.5 %     | 4.9 %      | 8.1 %          | 99 %            |               0.1 |                                                     0 |                                      0 |
| IBA, generic formulas      | 6.1 %           |     1.04 |                            1.04 | 3.5 %     | 4.9 %      | 8.0 %          | 99 %            |               0.1 |                                                     0 |                                      0 |
| group PCA                  | 6.2 %           |     1.06 |                            1.05 | 3.5 %     | 4.9 %      | 8.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| PCA                        | 6.3 %           |     1.06 |                            1.06 | 3.5 %     | 4.9 %      | 8.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| kernel PCA                 | 6.3 %           |     1.06 |                            1.06 | 3.5 %     | 4.9 %      | 8.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| autoencoder                | 6.3 %           |     1.07 |                            1.07 | 3.5 %     | 4.9 %      | 8.0 %          | 100 %           |               0   |                                                     1 |                                      1 |
| LASSO                      | 6.2 %           |     1.05 |                            1.05 | 3.5 %     | 4.9 %      | 8.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| raw factors                | 5.9 %           |     1.04 |                            1.03 | 3.2 %     | 4.6 %      | 7.8 %          | 95 %            |               0.3 |                                                     1 |                                      4 |
| historical mean            | 6.3 %           |     1.07 |                            1.06 | 3.5 %     | 4.9 %      | 8.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 4.8 %           |     0.91 |                            0.89 | 3.0 %     | 4.6 %      | 7.5 %          | 82 %            |               0.6 |                                                     1 |                                      5 |
| buy-and-hold               | 6.3 %           |     1.07 |                            1.06 | 3.5 %     | 4.9 %      | 8.0 %          | 100 %           |               0   |                                                       |                                        |

### monthly, 6 months

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 11) |   series with smaller drawdown (of 11) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 6.3 %           |     1.03 |                            1.03 | 3.4 %     | 5.4 %      | 6.5 %          | 99 %            |               0   |                                                     0 |                                      0 |
| IBA, K formulas (averaged) | 6.4 %           |     1.04 |                            1.04 | 3.4 %     | 5.4 %      | 6.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| IBA, generic formulas      | 6.2 %           |     1.03 |                            1.03 | 3.4 %     | 5.4 %      | 6.5 %          | 99 %            |               0   |                                                     0 |                                      0 |
| group PCA                  | 6.3 %           |     1.03 |                            1.03 | 3.4 %     | 5.4 %      | 6.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| PCA                        | 6.3 %           |     1.04 |                            1.03 | 3.4 %     | 5.4 %      | 6.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| kernel PCA                 | 6.3 %           |     1.03 |                            1.03 | 3.4 %     | 5.4 %      | 6.5 %          | 99 %            |               0   |                                                     0 |                                      0 |
| autoencoder                | 6.4 %           |     1.04 |                            1.04 | 3.4 %     | 5.4 %      | 6.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| LASSO                      | 6.3 %           |     1.04 |                            1.03 | 3.4 %     | 5.4 %      | 6.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| raw factors                | 6.2 %           |     1.02 |                            1.02 | 3.4 %     | 5.4 %      | 6.4 %          | 98 %            |               0.1 |                                                     0 |                                      2 |
| historical mean            | 6.4 %           |     1.04 |                            1.04 | 3.4 %     | 5.4 %      | 6.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 4.9 %           |     0.87 |                            0.86 | 3.1 %     | 5.4 %      | 6.5 %          | 82 %            |               0.4 |                                                     0 |                                      6 |
| buy-and-hold               | 6.4 %           |     1.04 |                            1.04 | 3.4 %     | 5.4 %      | 6.5 %          | 100 %           |               0   |                                                       |                                        |

### monthly, 12 months

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 11) |   series with smaller drawdown (of 11) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 6.2 %           |     1.01 |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| IBA, K formulas (averaged) | 6.2 %           |     1.01 |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| IBA, generic formulas      | 6.2 %           |     1.01 |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     1 |                                      0 |
| group PCA                  | 6.2 %           |     1.01 |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| PCA                        | 6.2 %           |     1.01 |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| kernel PCA                 | 6.2 %           |     1    |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| autoencoder                | 6.2 %           |     1    |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| LASSO                      | 6.2 %           |     1    |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| raw factors                | 6.1 %           |     0.99 |                            0.99 | 2.8 %     | 4.4 %      | 4.5 %          | 99 %            |               0   |                                                     0 |                                      0 |
| historical mean            | 6.2 %           |     1.01 |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 4.7 %           |     0.81 |                            0.8  | 3.1 %     | 4.4 %      | 4.8 %          | 82 %            |               0.3 |                                                     0 |                                      4 |
| buy-and-hold               | 6.2 %           |     1.01 |                            1    | 2.7 %     | 4.4 %      | 4.5 %          | 100 %           |               0   |                                                       |                                        |

## 3. The tail probabilities as a classifier (10 % events; all tasks of the type, counts summed)

Signal: forecast probability above the base-rate forecast of the date; strong signal: above twice that.

### Large loss (event rate 10.6 %)

| method                     | signal rate   | precision     | recall   | specificity   |   MCC | strong: signal rate   | strong: precision   | strong: recall   |   reliability x1000 |   resolution x1000 |   sharpness |
|:---------------------------|:--------------|:--------------|:---------|:--------------|------:|:----------------------|:--------------------|:-----------------|--------------------:|-------------------:|------------:|
| IBA, K formulas (fixed)    | 40.6 %        | 11.9 %        | 46.9 %   | 60.1 %        | 0.044 | 1.2 %                 | 13.7 %              | 1.6 %            |                1.86 |               1.23 |       0.05  |
| IBA, K formulas (averaged) | 39.7 %        | 11.9 %        | 45.8 %   | 61.0 %        | 0.042 | 1.1 %                 | 14.4 %              | 1.5 %            |                1.14 |               1    |       0.046 |
| IBA, generic formulas      | 41.0 %        | 13.2 %        | 52.4 %   | 60.3 %        | 0.079 | 2.1 %                 | 14.3 %              | 2.9 %            |                1.02 |               1.74 |       0.046 |
| group PCA                  | 41.8 %        | 11.4 %        | 46.0 %   | 58.7 %        | 0.029 | 1.3 %                 | 10.9 %              | 1.4 %            |                1.08 |               1.19 |       0.039 |
| PCA                        | 46.0 %        | 10.8 %        | 48.1 %   | 54.2 %        | 0.014 | 1.2 %                 | 8.2 %               | 0.9 %            |                1.15 |               0.84 |       0.034 |
| kernel PCA                 | 51.2 %        | 11.0 %        | 54.4 %   | 49.2 %        | 0.022 | 0.8 %                 | 4.4 %               | 0.4 %            |                1.62 |               1.32 |       0.034 |
| autoencoder                | 45.8 %        | 10.7 %        | 47.5 %   | 54.4 %        | 0.012 | 1.4 %                 | 8.5 %               | 1.1 %            |                1.08 |               0.86 |       0.034 |
| LASSO                      | 41.4 %        | 12.0 %        | 48.2 %   | 59.4 %        | 0.047 | 1.8 %                 | 11.7 %              | 2.0 %            |                1.04 |               0.9  |       0.045 |
| raw factors                | 41.6 %        | 11.6 %        | 46.6 %   | 59.0 %        | 0.034 | 2.1 %                 | 10.8 %              | 2.2 %            |                1.54 |               1.1  |       0.056 |
| base rate                  | 0.0 %         | never signals | 0.0 %    | 100.0 %       | 0     | 0.0 %                 | never               | 0.0 %            |                1.5  |               1.47 |       0.001 |
| volatility-based logit     | 40.7 %        | 11.4 %        | 45.0 %   | 59.7 %        | 0.029 | 3.3 %                 | 12.9 %              | 4.1 %            |                4.69 |               1.4  |       0.064 |
| GARCH-based probability    | 61.9 %        | 11.7 %        | 70.3 %   | 39.1 %        | 0.059 | 11.2 %                | 16.1 %              | 17.4 %           |                3.66 |               1.29 |       0.064 |

Reliability by fifth of the forecast (lowest to highest), tasks pooled:

| method                  |   fifth | mean forecast   | observed   |
|:------------------------|--------:|:----------------|:-----------|
| IBA, K formulas (fixed) |       1 | 7.2 %           | 10.1 %     |
| IBA, K formulas (fixed) |       2 | 9.5 %           | 8.0 %      |
| IBA, K formulas (fixed) |       3 | 9.9 %           | 9.2 %      |
| IBA, K formulas (fixed) |       4 | 10.2 %          | 10.8 %     |
| IBA, K formulas (fixed) |       5 | 13.3 %          | 13.4 %     |
| volatility-based logit  |       1 | 5.6 %           | 12.1 %     |
| volatility-based logit  |       2 | 8.0 %           | 7.5 %      |
| volatility-based logit  |       3 | 9.4 %           | 9.1 %      |
| volatility-based logit  |       4 | 11.0 %          | 10.7 %     |
| volatility-based logit  |       5 | 16.8 %          | 12.2 %     |

### Large gain (event rate 14.2 %)

| method                     | signal rate   | precision     | recall   | specificity   |   MCC | strong: signal rate   | strong: precision   | strong: recall   |   reliability x1000 |   resolution x1000 |   sharpness |
|:---------------------------|:--------------|:--------------|:---------|:--------------|------:|:----------------------|:--------------------|:-----------------|--------------------:|-------------------:|------------:|
| IBA, K formulas (fixed)    | 40.0 %        | 16.0 %        | 51.7 %   | 61.6 %        | 0.09  | 2.0 %                 | 25.3 %              | 4.1 %            |                3.15 |               1.19 |       0.038 |
| IBA, K formulas (averaged) | 39.5 %        | 15.9 %        | 50.7 %   | 62.1 %        | 0.086 | 2.0 %                 | 25.2 %              | 4.1 %            |                3.19 |               1.47 |       0.037 |
| IBA, generic formulas      | 43.3 %        | 15.0 %        | 52.4 %   | 58.0 %        | 0.07  | 2.5 %                 | 18.9 %              | 3.8 %            |                4.31 |               1.91 |       0.039 |
| group PCA                  | 43.5 %        | 14.4 %        | 50.5 %   | 57.5 %        | 0.053 | 1.8 %                 | 23.5 %              | 3.3 %            |                3.72 |               1.51 |       0.031 |
| PCA                        | 43.4 %        | 14.4 %        | 50.7 %   | 57.6 %        | 0.055 | 1.5 %                 | 26.2 %              | 3.1 %            |                4.5  |               2.01 |       0.029 |
| kernel PCA                 | 48.3 %        | 13.5 %        | 52.9 %   | 52.3 %        | 0.034 | 1.0 %                 | 14.8 %              | 1.2 %            |                4.48 |               1.64 |       0.041 |
| autoencoder                | 43.8 %        | 14.5 %        | 51.3 %   | 57.2 %        | 0.056 | 1.5 %                 | 24.5 %              | 3.0 %            |                3.72 |               1.47 |       0.03  |
| LASSO                      | 42.2 %        | 14.8 %        | 50.5 %   | 58.9 %        | 0.063 | 2.3 %                 | 23.4 %              | 4.4 %            |                3.78 |               1.19 |       0.046 |
| raw factors                | 42.6 %        | 14.2 %        | 49.0 %   | 58.3 %        | 0.048 | 2.2 %                 | 22.6 %              | 4.1 %            |                4.47 |               1.49 |       0.052 |
| base rate                  | 0.0 %         | never signals | 0.0 %    | 100.0 %       | 0     | 0.0 %                 | never               | 0.0 %            |                4.22 |               2.1  |       0.001 |
| volatility-based logit     | 32.5 %        | 20.4 %        | 53.7 %   | 70.4 %        | 0.17  | 7.3 %                 | 33.7 %              | 19.9 %           |                3.56 |               9.72 |       0.13  |
| GARCH-based probability    | 69.8 %        | 14.4 %        | 81.2 %   | 31.9 %        | 0.094 | 14.5 %                | 27.0 %              | 31.6 %           |                2.75 |               7.6  |       0.07  |

Reliability by fifth of the forecast (lowest to highest), tasks pooled:

| method                  |   fifth | mean forecast   | observed   |
|:------------------------|--------:|:----------------|:-----------|
| IBA, K formulas (fixed) |       1 | 6.8 %           | 8.0 %      |
| IBA, K formulas (fixed) |       2 | 9.0 %           | 9.9 %      |
| IBA, K formulas (fixed) |       3 | 9.9 %           | 12.1 %     |
| IBA, K formulas (fixed) |       4 | 10.3 %          | 14.7 %     |
| IBA, K formulas (fixed) |       5 | 14.6 %          | 17.1 %     |
| volatility-based logit  |       1 | 3.2 %           | 4.9 %      |
| volatility-based logit  |       2 | 5.5 %           | 7.8 %      |
| volatility-based logit  |       3 | 7.7 %           | 11.4 %     |
| volatility-based logit  |       4 | 10.7 %          | 13.9 %     |
| volatility-based logit  |       5 | 21.7 %          | 23.7 %     |

## 4. Crisis and drawdown periods (descriptive: short subsamples, no test)

Primary loss relative to the reference (negative = better) on forecasts made in the period, all series pooled; mean over the tasks of the type. In brackets: pooled forecasts per task, smallest to largest.

### weekly: Q4 2018 sell-off (481 to 481 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +5.5 %   | +3.9 %  | +5.2 %      | -4.6 %      |
| IBA, K formulas (averaged) | +3.6 %   | +2.1 %  | +4.9 %      | -5.1 %      |
| IBA, generic formulas      | +4.2 %   | +4.1 %  | +8.7 %      | -0.4 %      |
| group PCA                  | +5.5 %   | +4.5 %  | +5.6 %      | -2.2 %      |
| PCA                        | +2.0 %   | -3.1 %  | +3.1 %      | -3.6 %      |
| kernel PCA                 | +0.6 %   | -4.8 %  | +1.4 %      | +0.5 %      |
| autoencoder                | +2.4 %   | -2.2 %  | +2.9 %      | -3.2 %      |
| LASSO                      | +5.7 %   | -1.6 %  | +12.3 %     | -3.6 %      |
| raw factors                | +5.6 %   | -0.0 %  | +14.0 %     | -4.3 %      |
| trailing momentum          | +40.5 %  |         |             |             |
| GARCH                      |          | +7.1 %  |             |             |
| GJR-GARCH                  |          | +5.8 %  |             |             |
| volatility-based logit     |          |         | -0.9 %      | -2.4 %      |
| GARCH-based probability    |          |         | +5.8 %      | -1.5 %      |

### weekly: COVID-19 crash (370 to 370 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +2.1 %   | -18.1 % | +11.8 %     | -4.3 %      |
| IBA, K formulas (averaged) | +1.9 %   | -17.9 % | +10.3 %     | -4.9 %      |
| IBA, generic formulas      | +1.2 %   | -16.9 % | +3.0 %      | -2.8 %      |
| group PCA                  | +8.6 %   | -18.8 % | +17.9 %     | -2.1 %      |
| PCA                        | +3.5 %   | -13.0 % | +13.5 %     | -1.7 %      |
| kernel PCA                 | +0.1 %   | -2.2 %  | +0.8 %      | -2.1 %      |
| autoencoder                | +1.7 %   | -10.8 % | +3.2 %      | -3.6 %      |
| LASSO                      | +3.3 %   | -15.9 % | +12.2 %     | -3.6 %      |
| raw factors                | +4.9 %   | -21.1 % | +16.1 %     | -4.2 %      |
| trailing momentum          | +20.3 %  |         |             |             |
| GARCH                      |          | -5.8 %  |             |             |
| GJR-GARCH                  |          | -7.5 %  |             |             |
| volatility-based logit     |          |         | +15.7 %     | -32.3 %     |
| GARCH-based probability    |          |         | +41.1 %     | -29.6 %     |

### weekly: 2022: invasion of Ukraine and rate shock (1332 to 1332 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +0.5 %   | -6.0 %  | -0.3 %      | +0.6 %      |
| IBA, K formulas (averaged) | +0.3 %   | -6.3 %  | -0.5 %      | +0.5 %      |
| IBA, generic formulas      | +1.2 %   | -13.1 % | -1.4 %      | +1.4 %      |
| group PCA                  | +1.8 %   | -9.1 %  | +0.0 %      | -0.0 %      |
| PCA                        | +1.5 %   | -6.2 %  | +0.5 %      | +0.1 %      |
| kernel PCA                 | +0.4 %   | -3.4 %  | -0.6 %      | -0.1 %      |
| autoencoder                | +1.5 %   | -4.8 %  | +0.3 %      | -0.2 %      |
| LASSO                      | +2.7 %   | -10.4 % | -1.1 %      | +0.8 %      |
| raw factors                | +5.0 %   | -14.0 % | -0.8 %      | +6.3 %      |
| trailing momentum          | +14.1 %  |         |             |             |
| GARCH                      |          | -14.7 % |             |             |
| GJR-GARCH                  |          | -14.1 % |             |             |
| volatility-based logit     |          |         | -0.7 %      | +1.6 %      |
| GARCH-based probability    |          |         | -9.2 %      | +0.8 %      |

### weekly: other periods (13209 to 13209 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +1.0 %   | -4.3 %  | +0.7 %      | -0.9 %      |
| IBA, K formulas (averaged) | +0.8 %   | -4.5 %  | +0.6 %      | -0.9 %      |
| IBA, generic formulas      | +1.0 %   | -3.2 %  | +1.4 %      | -0.4 %      |
| group PCA                  | +0.6 %   | -2.9 %  | +1.2 %      | -0.5 %      |
| PCA                        | +0.6 %   | -1.8 %  | +0.8 %      | -0.4 %      |
| kernel PCA                 | +0.7 %   | -0.8 %  | +1.3 %      | -0.0 %      |
| autoencoder                | +0.7 %   | -1.8 %  | +1.1 %      | -0.6 %      |
| LASSO                      | +1.8 %   | -1.8 %  | +1.3 %      | -0.6 %      |
| raw factors                | +2.4 %   | -1.6 %  | +1.6 %      | -0.3 %      |
| trailing momentum          | +11.0 %  |         |             |             |
| GARCH                      |          | +15.3 % |             |             |
| GJR-GARCH                  |          | +9.4 %  |             |             |
| volatility-based logit     |          |         | +1.9 %      | -4.0 %      |
| GARCH-based probability    |          |         | +3.5 %      | -3.2 %      |

### weekly: in drawdown (at least 10 % below the peak) (8219 to 8273 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +1.2 %   | -6.5 %  | +1.4 %      | -1.4 %      |
| IBA, K formulas (averaged) | +1.0 %   | -6.6 %  | +1.1 %      | -1.6 %      |
| IBA, generic formulas      | +1.2 %   | -5.8 %  | +1.4 %      | -0.9 %      |
| group PCA                  | +2.0 %   | -5.2 %  | +2.5 %      | -0.8 %      |
| PCA                        | +1.2 %   | -4.0 %  | +1.9 %      | -0.6 %      |
| kernel PCA                 | +0.7 %   | -1.1 %  | +1.1 %      | -0.2 %      |
| autoencoder                | +1.0 %   | -3.2 %  | +1.3 %      | -0.9 %      |
| LASSO                      | +2.2 %   | -4.3 %  | +2.1 %      | -1.2 %      |
| raw factors                | +3.0 %   | -5.5 %  | +2.4 %      | -0.4 %      |
| trailing momentum          | +11.5 %  |         |             |             |
| GARCH                      |          | +13.0 % |             |             |
| GJR-GARCH                  |          | +8.5 %  |             |             |
| volatility-based logit     |          |         | +1.6 %      | -6.8 %      |
| GARCH-based probability    |          |         | +3.7 %      | -7.7 %      |

### weekly: not in drawdown (7119 to 7173 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +0.5 %   | -5.4 %  | +0.2 %      | -0.4 %      |
| IBA, K formulas (averaged) | +0.3 %   | -5.6 %  | +0.1 %      | -0.5 %      |
| IBA, generic formulas      | +0.6 %   | -4.9 %  | +0.1 %      | +0.8 %      |
| group PCA                  | +0.1 %   | -4.7 %  | +0.3 %      | -0.3 %      |
| PCA                        | +0.4 %   | -3.0 %  | +0.3 %      | -0.4 %      |
| kernel PCA                 | +0.5 %   | -1.4 %  | +0.4 %      | +0.0 %      |
| autoencoder                | +0.5 %   | -2.8 %  | +0.5 %      | -0.7 %      |
| LASSO                      | +0.9 %   | -3.6 %  | +0.0 %      | +0.1 %      |
| raw factors                | +2.3 %   | -4.0 %  | +0.8 %      | +0.6 %      |
| trailing momentum          | +13.6 %  |         |             |             |
| GARCH                      |          | +9.2 %  |             |             |
| GJR-GARCH                  |          | +3.7 %  |             |             |
| volatility-based logit     |          |         | +1.8 %      | -2.4 %      |
| GARCH-based probability    |          |         | -0.4 %      | +1.7 %      |

### monthly: Q4 2018 sell-off (33 to 33 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +13.3 %  |         | +61.2 %     | -0.2 %      |
| IBA, K formulas (averaged) | +11.1 %  |         | +53.3 %     | -1.7 %      |
| IBA, generic formulas      | +12.6 %  |         | +92.4 %     | -1.4 %      |
| group PCA                  | +3.5 %   |         | +78.8 %     | -3.6 %      |
| PCA                        | +2.0 %   |         | +61.4 %     | -4.3 %      |
| kernel PCA                 | +4.1 %   |         | +91.6 %     | +2.3 %      |
| autoencoder                | -0.9 %   |         | +20.0 %     | -5.6 %      |
| LASSO                      | +4.9 %   |         | +129.0 %    | +0.4 %      |
| raw factors                | -4.5 %   |         | +23.7 %     | -2.9 %      |
| trailing momentum          | +183.2 % |         |             |             |
| volatility-based logit     |          |         | +1.1 %      | +3.5 %      |
| GARCH-based probability    |          |         | +9.2 %      | -7.0 %      |

### monthly: COVID-19 crash (33 to 33 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +2.4 %   |         | +26.3 %     | -0.6 %      |
| IBA, K formulas (averaged) | +2.1 %   |         | +26.7 %     | -0.6 %      |
| IBA, generic formulas      | +7.8 %   |         | +10.0 %     | -2.0 %      |
| group PCA                  | +7.8 %   |         | +23.6 %     | -0.7 %      |
| PCA                        | +4.0 %   |         | +16.4 %     | -1.7 %      |
| kernel PCA                 | +0.6 %   |         | +2.1 %      | +3.4 %      |
| autoencoder                | +2.2 %   |         | +13.3 %     | +0.6 %      |
| LASSO                      | +9.0 %   |         | +75.1 %     | -1.2 %      |
| raw factors                | +10.9 %  |         | +93.2 %     | +4.8 %      |
| trailing momentum          | +56.7 %  |         |             |             |
| volatility-based logit     |          |         | +25.6 %     | -32.1 %     |
| GARCH-based probability    |          |         | +78.4 %     | -31.8 %     |

### monthly: 2022: invasion of Ukraine and rate shock (99 to 99 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | -3.2 %   |         | -4.8 %      | -1.1 %      |
| IBA, K formulas (averaged) | -3.2 %   |         | -6.2 %      | -2.0 %      |
| IBA, generic formulas      | -4.6 %   |         | -5.6 %      | +0.9 %      |
| group PCA                  | -1.8 %   |         | -1.1 %      | -1.4 %      |
| PCA                        | -0.9 %   |         | +0.2 %      | +0.7 %      |
| kernel PCA                 | -1.5 %   |         | -3.0 %      | -0.1 %      |
| autoencoder                | -0.2 %   |         | -2.5 %      | +0.2 %      |
| LASSO                      | -2.0 %   |         | -1.3 %      | +2.6 %      |
| raw factors                | -5.1 %   |         | -2.2 %      | +2.5 %      |
| trailing momentum          | +79.3 %  |         |             |             |
| volatility-based logit     |          |         | +0.7 %      | +12.4 %     |
| GARCH-based probability    |          |         | -4.1 %      | -3.1 %      |

### monthly: other periods (891 to 891 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +3.6 %   |         | +1.5 %      | +1.3 %      |
| IBA, K formulas (averaged) | +2.9 %   |         | +1.4 %      | +1.2 %      |
| IBA, generic formulas      | +1.5 %   |         | -0.2 %      | +1.1 %      |
| group PCA                  | +0.9 %   |         | -1.3 %      | +0.8 %      |
| PCA                        | +1.4 %   |         | +0.8 %      | +1.3 %      |
| kernel PCA                 | +2.2 %   |         | +2.3 %      | +1.9 %      |
| autoencoder                | +1.7 %   |         | +1.7 %      | +0.9 %      |
| LASSO                      | +1.6 %   |         | +0.8 %      | +1.8 %      |
| raw factors                | +5.0 %   |         | +3.8 %      | +2.5 %      |
| trailing momentum          | +64.1 %  |         |             |             |
| volatility-based logit     |          |         | +7.9 %      | -5.9 %      |
| GARCH-based probability    |          |         | +7.3 %      | -5.5 %      |

### monthly: in drawdown (at least 10 % below the peak) (25 to 25 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +12.8 %  |         | +173.1 %    | +1.2 %      |
| IBA, K formulas (averaged) | +11.0 %  |         | +202.5 %    | +1.4 %      |
| IBA, generic formulas      | +14.6 %  |         | +122.7 %    | +1.4 %      |
| group PCA                  | +15.6 %  |         | +109.0 %    | +1.8 %      |
| PCA                        | +11.3 %  |         | +37.4 %     | +1.1 %      |
| kernel PCA                 | +9.3 %   |         | +43.1 %     | +3.7 %      |
| autoencoder                | +6.8 %   |         | +45.0 %     | +1.7 %      |
| LASSO                      | +18.2 %  |         | +172.7 %    | -7.5 %      |
| raw factors                | +25.1 %  |         | +81.4 %     | +5.2 %      |
| trailing momentum          | +188.4 % |         |             |             |
| volatility-based logit     |          |         | +34.4 %     | -37.0 %     |
| GARCH-based probability    |          |         | +328.8 %    | -28.9 %     |

### monthly: not in drawdown (1031 to 1031 forecasts)

| method                     | return   | logrv   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:--------|:------------|:------------|
| IBA, K formulas (fixed)    | +2.4 %   |         | -0.3 %      | +0.9 %      |
| IBA, K formulas (averaged) | +1.8 %   |         | -0.9 %      | +0.7 %      |
| IBA, generic formulas      | +1.0 %   |         | -1.7 %      | +0.7 %      |
| group PCA                  | +0.6 %   |         | -1.0 %      | +0.3 %      |
| PCA                        | +1.0 %   |         | +0.8 %      | +0.7 %      |
| kernel PCA                 | +1.1 %   |         | +0.9 %      | +1.9 %      |
| autoencoder                | +1.2 %   |         | +0.5 %      | +0.6 %      |
| LASSO                      | +1.3 %   |         | +1.1 %      | +1.8 %      |
| raw factors                | +3.6 %   |         | +3.0 %      | +2.6 %      |
| trailing momentum          | +55.5 %  |         |             |             |
| volatility-based logit     |          |         | +5.7 %      | -6.3 %      |
| GARCH-based probability    |          |         | +4.5 %      | -7.2 %      |
