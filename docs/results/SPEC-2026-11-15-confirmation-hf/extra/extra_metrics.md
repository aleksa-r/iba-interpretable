# Financial and classification measures (hedge-fund confirmation series)

CONFIRMATION series (23 monthly hedge-fund indices), measures declared in the spec before the run (`docs/protocol/EXTRA_METRICS.md`). All factor methods with the linear model. The averaged reading is the ABC colony of the development run, applied unchanged. The indices are not investable: the long/flat rule is a reading of the forecasts, not a strategy.

## 1. Value at risk and expected shortfall from the volatility forecasts (weekly series, zero-mean normal returns)

No volatility target in this run.

## 2. The long/flat rule on the return forecasts (no transaction costs)

Long for the next h periods when the forecast return is not negative, else flat. Means over series; VaR and CVaR are of the h-period returns.

### monthly, 1 month

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 23) |   series with smaller drawdown (of 23) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 6.5 %           |     1.04 |                            1.01 | 2.9 %     | 4.1 %      | 13.3 %         | 91 %            |               1.5 |                                                    12 |                                     12 |
| IBA, K formulas (averaged) | 6.6 %           |     1.01 |                            0.99 | 2.9 %     | 4.1 %      | 13.4 %         | 92 %            |               1.4 |                                                    11 |                                     13 |
| IBA, generic formulas      | 6.4 %           |     0.96 |                            0.94 | 3.0 %     | 4.5 %      | 13.4 %         | 94 %            |               1.3 |                                                     9 |                                      9 |
| group PCA                  | 6.7 %           |     1.01 |                            0.99 | 3.0 %     | 4.3 %      | 13.4 %         | 94 %            |               1.1 |                                                    12 |                                     11 |
| PCA                        | 6.6 %           |     1    |                            0.98 | 3.0 %     | 4.5 %      | 14.5 %         | 96 %            |               0.8 |                                                     9 |                                      9 |
| kernel PCA                 | 6.2 %           |     0.97 |                            0.94 | 3.0 %     | 4.4 %      | 14.1 %         | 92 %            |               1.6 |                                                     6 |                                     10 |
| autoencoder                | 6.6 %           |     0.99 |                            0.98 | 3.0 %     | 4.6 %      | 14.7 %         | 97 %            |               0.7 |                                                     7 |                                      7 |
| LASSO                      | 6.4 %           |     0.99 |                            0.97 | 2.9 %     | 4.5 %      | 14.8 %         | 93 %            |               1.2 |                                                     7 |                                     11 |
| raw factors                | 6.4 %           |     1.04 |                            0.99 | 2.9 %     | 4.1 %      | 11.4 %         | 87 %            |               2.2 |                                                    15 |                                     16 |
| historical mean            | 7.0 %           |     0.97 |                            0.97 | 3.2 %     | 5.3 %      | 16.1 %         | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 5.2 %           |     0.89 |                            0.87 | 2.5 %     | 4.6 %      | 13.1 %         | 75 %            |               1   |                                                     5 |                                     10 |
| buy-and-hold               | 7.0 %           |     0.97 |                            0.97 | 3.2 %     | 5.3 %      | 16.1 %         | 100 %           |               0   |                                                       |                                        |

### monthly, 3 months

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 23) |   series with smaller drawdown (of 23) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 6.8 %           |     0.94 |                            0.94 | 5.0 %     | 7.4 %      | 13.4 %         | 98 %            |               0.1 |                                                     3 |                                      0 |
| IBA, K formulas (averaged) | 6.7 %           |     0.94 |                            0.93 | 5.0 %     | 7.4 %      | 13.5 %         | 98 %            |               0.1 |                                                     1 |                                      0 |
| IBA, generic formulas      | 6.5 %           |     0.92 |                            0.91 | 5.0 %     | 7.3 %      | 13.1 %         | 98 %            |               0.2 |                                                     2 |                                      2 |
| group PCA                  | 6.6 %           |     0.93 |                            0.93 | 5.0 %     | 7.4 %      | 13.4 %         | 99 %            |               0.1 |                                                     0 |                                      1 |
| PCA                        | 6.9 %           |     0.95 |                            0.94 | 5.0 %     | 7.4 %      | 13.4 %         | 100 %           |               0   |                                                     0 |                                      0 |
| kernel PCA                 | 6.8 %           |     0.94 |                            0.94 | 4.9 %     | 7.3 %      | 13.3 %         | 99 %            |               0.1 |                                                     2 |                                      1 |
| autoencoder                | 7.0 %           |     0.95 |                            0.95 | 5.0 %     | 7.4 %      | 13.4 %         | 100 %           |               0   |                                                     0 |                                      0 |
| LASSO                      | 6.6 %           |     0.93 |                            0.93 | 5.0 %     | 7.4 %      | 13.4 %         | 98 %            |               0.1 |                                                     0 |                                      2 |
| raw factors                | 6.3 %           |     0.91 |                            0.9  | 4.7 %     | 7.0 %      | 12.2 %         | 93 %            |               0.5 |                                                     4 |                                     10 |
| historical mean            | 7.0 %           |     0.96 |                            0.95 | 5.0 %     | 7.4 %      | 13.4 %         | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 4.9 %           |     0.8  |                            0.79 | 4.5 %     | 7.0 %      | 11.9 %         | 75 %            |               0.7 |                                                     2 |                                     11 |
| buy-and-hold               | 7.0 %           |     0.96 |                            0.95 | 5.0 %     | 7.4 %      | 13.4 %         | 100 %           |               0   |                                                       |                                        |

### monthly, 6 months

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 23) |   series with smaller drawdown (of 23) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 6.9 %           |     0.91 |                            0.9  | 6.0 %     | 8.6 %      | 11.2 %         | 99 %            |               0   |                                                     2 |                                      1 |
| IBA, K formulas (averaged) | 6.9 %           |     0.91 |                            0.9  | 6.0 %     | 8.6 %      | 11.2 %         | 99 %            |               0   |                                                     1 |                                      1 |
| IBA, generic formulas      | 6.8 %           |     0.9  |                            0.9  | 6.0 %     | 8.6 %      | 11.2 %         | 99 %            |               0   |                                                     0 |                                      1 |
| group PCA                  | 6.8 %           |     0.91 |                            0.91 | 5.9 %     | 8.5 %      | 10.8 %         | 99 %            |               0.1 |                                                     3 |                                      4 |
| PCA                        | 6.8 %           |     0.91 |                            0.91 | 5.9 %     | 8.5 %      | 10.9 %         | 99 %            |               0   |                                                     2 |                                      4 |
| kernel PCA                 | 6.7 %           |     0.9  |                            0.9  | 5.8 %     | 8.2 %      | 10.6 %         | 97 %            |               0.1 |                                                     5 |                                      5 |
| autoencoder                | 6.8 %           |     0.91 |                            0.9  | 6.0 %     | 8.5 %      | 10.9 %         | 99 %            |               0   |                                                     0 |                                      4 |
| LASSO                      | 6.8 %           |     0.9  |                            0.9  | 6.0 %     | 8.6 %      | 11.2 %         | 99 %            |               0   |                                                     1 |                                      3 |
| raw factors                | 6.6 %           |     0.9  |                            0.89 | 5.6 %     | 8.2 %      | 10.1 %         | 95 %            |               0.2 |                                                     5 |                                     11 |
| historical mean            | 6.9 %           |     0.91 |                            0.91 | 6.0 %     | 8.6 %      | 11.3 %         | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 5.1 %           |     0.76 |                            0.75 | 5.2 %     | 8.1 %      | 9.8 %          | 75 %            |               0.5 |                                                     1 |                                     15 |
| buy-and-hold               | 6.9 %           |     0.91 |                            0.91 | 6.0 %     | 8.6 %      | 11.3 %         | 100 %           |               0   |                                                       |                                        |

### monthly, 12 months

| method                     | annual return   |   Sharpe |   Sharpe after 10 bp per switch | 5 % VaR   | 5 % CVaR   | max drawdown   | time invested   |   switches / year |   series with higher Sharpe than buy-and-hold (of 23) |   series with smaller drawdown (of 23) |
|:---------------------------|:----------------|---------:|--------------------------------:|:----------|:-----------|:---------------|:----------------|------------------:|------------------------------------------------------:|---------------------------------------:|
| IBA, K formulas (fixed)    | 6.5 %           |     0.82 |                            0.82 | 6.2 %     | 8.3 %      | 9.1 %          | 99 %            |               0   |                                                     1 |                                      1 |
| IBA, K formulas (averaged) | 6.4 %           |     0.82 |                            0.81 | 6.2 %     | 8.3 %      | 9.1 %          | 100 %           |               0   |                                                     0 |                                      0 |
| IBA, generic formulas      | 6.4 %           |     0.82 |                            0.81 | 6.2 %     | 8.3 %      | 9.2 %          | 99 %            |               0   |                                                     0 |                                      0 |
| group PCA                  | 6.5 %           |     0.82 |                            0.82 | 6.1 %     | 8.3 %      | 9.0 %          | 100 %           |               0   |                                                     0 |                                      1 |
| PCA                        | 6.5 %           |     0.82 |                            0.82 | 6.1 %     | 8.3 %      | 9.1 %          | 100 %           |               0   |                                                     0 |                                      1 |
| kernel PCA                 | 6.5 %           |     0.82 |                            0.82 | 6.1 %     | 8.2 %      | 8.9 %          | 99 %            |               0   |                                                     1 |                                      2 |
| autoencoder                | 6.5 %           |     0.82 |                            0.82 | 6.2 %     | 8.3 %      | 9.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| LASSO                      | 6.5 %           |     0.82 |                            0.82 | 6.2 %     | 8.3 %      | 9.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| raw factors                | 6.3 %           |     0.81 |                            0.81 | 5.9 %     | 8.0 %      | 8.9 %          | 97 %            |               0   |                                                     3 |                                      4 |
| historical mean            | 6.5 %           |     0.82 |                            0.82 | 6.2 %     | 8.3 %      | 9.0 %          | 100 %           |               0   |                                                     0 |                                      0 |
| trailing momentum          | 4.4 %           |     0.64 |                            0.64 | 5.8 %     | 7.8 %      | 8.6 %          | 75 %            |               0.4 |                                                     0 |                                     16 |
| buy-and-hold               | 6.5 %           |     0.82 |                            0.82 | 6.2 %     | 8.3 %      | 9.0 %          | 100 %           |               0   |                                                       |                                        |

## 3. The tail probabilities as a classifier (10 % events; all tasks of the type, counts summed)

Signal: forecast probability above the base-rate forecast of the date; strong signal: above twice that.

### Large loss (event rate 8.1 %)

| method                     | signal rate   | precision     | recall   | specificity   |    MCC | strong: signal rate   | strong: precision   | strong: recall   |   reliability x1000 |   resolution x1000 |   sharpness |
|:---------------------------|:--------------|:--------------|:---------|:--------------|-------:|:----------------------|:--------------------|:-----------------|--------------------:|-------------------:|------------:|
| IBA, K formulas (fixed)    | 39.7 %        | 9.9 %         | 48.2 %   | 61.1 %        |  0.052 | 2.9 %                 | 7.0 %               | 2.5 %            |                1.85 |               0.55 |       0.052 |
| IBA, K formulas (averaged) | 38.8 %        | 10.5 %        | 50.0 %   | 62.2 %        |  0.068 | 3.3 %                 | 8.4 %               | 3.4 %            |                1.8  |               0.73 |       0.046 |
| IBA, generic formulas      | 40.1 %        | 11.3 %        | 55.7 %   | 61.2 %        |  0.094 | 3.5 %                 | 11.7 %              | 5.0 %            |                2.09 |               1.28 |       0.054 |
| group PCA                  | 41.9 %        | 9.7 %         | 50.1 %   | 58.8 %        |  0.05  | 2.0 %                 | 16.1 %              | 3.9 %            |                1.27 |               1.16 |       0.038 |
| PCA                        | 45.4 %        | 8.9 %         | 49.9 %   | 55.0 %        |  0.027 | 1.5 %                 | 10.4 %              | 1.9 %            |                1.63 |               0.95 |       0.032 |
| kernel PCA                 | 45.7 %        | 9.3 %         | 52.4 %   | 54.8 %        |  0.04  | 2.0 %                 | 8.0 %               | 1.9 %            |                2.43 |               1.03 |       0.039 |
| autoencoder                | 48.1 %        | 9.7 %         | 57.7 %   | 52.7 %        |  0.057 | 1.7 %                 | 9.6 %               | 1.9 %            |                1.33 |               0.74 |       0.031 |
| LASSO                      | 42.7 %        | 9.3 %         | 49.0 %   | 57.9 %        |  0.038 | 3.1 %                 | 7.2 %               | 2.8 %            |                3.2  |               0.83 |       0.052 |
| raw factors                | 39.7 %        | 10.3 %        | 50.1 %   | 61.3 %        |  0.064 | 4.1 %                 | 14.8 %              | 7.5 %            |                3.43 |               1.08 |       0.075 |
| base rate                  | 0.0 %         | never signals | 0.0 %    | 100.0 %       |  0     | 0.0 %                 | never               | 0.0 %            |                1.45 |               1    |       0.002 |
| volatility-based logit     | 44.2 %        | 7.0 %         | 38.2 %   | 55.2 %        | -0.036 | 5.7 %                 | 5.6 %               | 3.9 %            |                5.67 |               0.86 |       0.055 |
| GARCH-based probability    | 31.2 %        | 5.4 %         | 20.9 %   | 67.8 %        | -0.066 | 3.9 %                 | 2.3 %               | 1.1 %            |                6.56 |               1.59 |       0.055 |

Reliability by fifth of the forecast (lowest to highest), tasks pooled:

| method                  |   fifth | mean forecast   | observed   |
|:------------------------|--------:|:----------------|:-----------|
| IBA, K formulas (fixed) |       1 | 5.9 %           | 6.1 %      |
| IBA, K formulas (fixed) |       2 | 9.6 %           | 7.4 %      |
| IBA, K formulas (fixed) |       3 | 10.1 %          | 7.9 %      |
| IBA, K formulas (fixed) |       4 | 10.4 %          | 10.1 %     |
| IBA, K formulas (fixed) |       5 | 15.8 %          | 9.2 %      |
| volatility-based logit  |       1 | 4.1 %           | 11.4 %     |
| volatility-based logit  |       2 | 7.4 %           | 8.3 %      |
| volatility-based logit  |       3 | 9.6 %           | 6.9 %      |
| volatility-based logit  |       4 | 12.0 %          | 6.6 %      |
| volatility-based logit  |       5 | 18.8 %          | 7.5 %      |

### Large gain (event rate 15.2 %)

| method                     | signal rate   | precision     | recall   | specificity   |    MCC | strong: signal rate   | strong: precision   | strong: recall   |   reliability x1000 |   resolution x1000 |   sharpness |
|:---------------------------|:--------------|:--------------|:---------|:--------------|-------:|:----------------------|:--------------------|:-----------------|--------------------:|-------------------:|------------:|
| IBA, K formulas (fixed)    | 43.5 %        | 18.9 %        | 54.1 %   | 58.3 %        |  0.09  | 2.4 %                 | 18.3 %              | 2.8 %            |                4.13 |               1.67 |       0.043 |
| IBA, K formulas (averaged) | 41.1 %        | 18.5 %        | 50.0 %   | 60.5 %        |  0.077 | 2.3 %                 | 19.5 %              | 2.9 %            |                4.13 |               1.59 |       0.037 |
| IBA, generic formulas      | 48.6 %        | 16.4 %        | 52.5 %   | 52.0 %        |  0.032 | 1.0 %                 | 4.7 %               | 0.3 %            |                6.15 |               2.83 |       0.036 |
| group PCA                  | 49.3 %        | 15.8 %        | 51.0 %   | 51.1 %        |  0.015 | 0.6 %                 | 14.3 %              | 0.6 %            |                4.52 |               1.34 |       0.021 |
| PCA                        | 48.5 %        | 14.6 %        | 46.5 %   | 51.1 %        | -0.017 | 0.5 %                 | 13.6 %              | 0.4 %            |                3.83 |               0.84 |       0.019 |
| kernel PCA                 | 40.3 %        | 16.6 %        | 44.0 %   | 60.3 %        |  0.032 | 3.9 %                 | 17.2 %              | 4.5 %            |                5.27 |               0.9  |       0.052 |
| autoencoder                | 46.6 %        | 14.9 %        | 45.5 %   | 53.2 %        | -0.01  | 0.8 %                 | 22.2 %              | 1.2 %            |                4.3  |               1.09 |       0.023 |
| LASSO                      | 49.4 %        | 16.5 %        | 53.3 %   | 51.3 %        |  0.034 | 1.3 %                 | 19.3 %              | 1.6 %            |                4.38 |               0.97 |       0.037 |
| raw factors                | 45.6 %        | 15.2 %        | 45.5 %   | 54.4 %        | -0.001 | 1.8 %                 | 12.3 %              | 1.5 %            |                5.69 |               1.21 |       0.051 |
| base rate                  | 0.0 %         | never signals | 0.0 %    | 100.0 %       |  0     | 0.0 %                 | never               | 0.0 %            |                7.42 |               4.78 |       0.002 |
| volatility-based logit     | 35.3 %        | 25.0 %        | 57.9 %   | 68.7 %        |  0.201 | 14.8 %                | 32.1 %              | 31.2 %           |                5.29 |               8.02 |       0.153 |
| GARCH-based probability    | 41.7 %        | 23.0 %        | 63.0 %   | 62.2 %        |  0.183 | 8.4 %                 | 42.8 %              | 23.5 %           |                5.13 |              10.59 |       0.061 |

Reliability by fifth of the forecast (lowest to highest), tasks pooled:

| method                  |   fifth | mean forecast   | observed   |
|:------------------------|--------:|:----------------|:-----------|
| IBA, K formulas (fixed) |       1 | 6.2 %           | 12.8 %     |
| IBA, K formulas (fixed) |       2 | 9.8 %           | 12.4 %     |
| IBA, K formulas (fixed) |       3 | 10.1 %          | 15.5 %     |
| IBA, K formulas (fixed) |       4 | 10.4 %          | 17.8 %     |
| IBA, K formulas (fixed) |       5 | 14.4 %          | 17.8 %     |
| volatility-based logit  |       1 | 1.0 %           | 7.4 %      |
| volatility-based logit  |       2 | 3.5 %           | 7.4 %      |
| volatility-based logit  |       3 | 6.9 %           | 13.0 %     |
| volatility-based logit  |       4 | 12.1 %          | 19.2 %     |
| volatility-based logit  |       5 | 34.8 %          | 29.3 %     |

## 4. Crisis and drawdown periods (descriptive: short subsamples, no test)

Primary loss relative to the reference (negative = better) on forecasts made in the period, all series pooled; mean over the tasks of the type. In brackets: pooled forecasts per task, smallest to largest.

### monthly: Q4 2018 sell-off (69 to 69 forecasts)

| method                     | return   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:------------|:------------|
| IBA, K formulas (fixed)    | +16.2 %  | +24.2 %     | -0.4 %      |
| IBA, K formulas (averaged) | +14.6 %  | +22.8 %     | +0.0 %      |
| IBA, generic formulas      | +24.3 %  | +44.8 %     | +2.4 %      |
| group PCA                  | +15.0 %  | +22.5 %     | -0.6 %      |
| PCA                        | +5.2 %   | +19.4 %     | +1.1 %      |
| kernel PCA                 | +9.9 %   | +41.5 %     | -1.6 %      |
| autoencoder                | +5.6 %   | +6.9 %      | +2.2 %      |
| LASSO                      | +14.1 %  | +91.7 %     | -0.5 %      |
| raw factors                | +8.1 %   | +14.1 %     | +1.7 %      |
| trailing momentum          | +308.8 % |             |             |
| volatility-based logit     |          | +12.0 %     | -6.6 %      |
| GARCH-based probability    |          | +1.7 %      | -6.9 %      |

### monthly: COVID-19 crash (69 to 69 forecasts)

| method                     | return   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:------------|:------------|
| IBA, K formulas (fixed)    | +4.9 %   | +32.4 %     | +1.1 %      |
| IBA, K formulas (averaged) | +5.2 %   | +39.9 %     | -0.6 %      |
| IBA, generic formulas      | +11.9 %  | +20.6 %     | +0.7 %      |
| group PCA                  | +12.7 %  | +30.3 %     | +1.5 %      |
| PCA                        | +8.8 %   | +18.0 %     | +0.3 %      |
| kernel PCA                 | +1.9 %   | +17.8 %     | +4.3 %      |
| autoencoder                | +4.2 %   | +11.4 %     | -0.9 %      |
| LASSO                      | +11.8 %  | +143.2 %    | +2.2 %      |
| raw factors                | +18.3 %  | +241.4 %    | +4.2 %      |
| trailing momentum          | +70.1 %  |             |             |
| volatility-based logit     |          | +14.2 %     | -16.4 %     |
| GARCH-based probability    |          | +84.1 %     | -25.4 %     |

### monthly: 2022: invasion of Ukraine and rate shock (207 to 207 forecasts)

| method                     | return   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:------------|:------------|
| IBA, K formulas (fixed)    | -4.2 %   | +10.0 %     | +2.5 %      |
| IBA, K formulas (averaged) | -3.5 %   | +4.1 %      | +2.8 %      |
| IBA, generic formulas      | -5.9 %   | +7.2 %      | +2.3 %      |
| group PCA                  | -5.0 %   | +6.0 %      | +1.8 %      |
| PCA                        | -1.4 %   | +3.0 %      | +2.1 %      |
| kernel PCA                 | -3.3 %   | +0.5 %      | -2.8 %      |
| autoencoder                | -1.4 %   | +0.5 %      | +1.9 %      |
| LASSO                      | -2.6 %   | +1.9 %      | +5.3 %      |
| raw factors                | -5.2 %   | -0.5 %      | +4.5 %      |
| trailing momentum          | +120.5 % |             |             |
| volatility-based logit     |          | +1.5 %      | +1.2 %      |
| GARCH-based probability    |          | +2.5 %      | +14.9 %     |

### monthly: other periods (1863 to 1863 forecasts)

| method                     | return   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:------------|:------------|
| IBA, K formulas (fixed)    | +0.7 %   | +0.7 %      | +0.7 %      |
| IBA, K formulas (averaged) | +0.2 %   | +0.3 %      | +0.4 %      |
| IBA, generic formulas      | +0.3 %   | -0.6 %      | +1.6 %      |
| group PCA                  | -0.2 %   | -1.4 %      | +0.5 %      |
| PCA                        | +0.9 %   | -0.0 %      | +0.4 %      |
| kernel PCA                 | +0.6 %   | +1.9 %      | +1.2 %      |
| autoencoder                | +1.4 %   | +0.4 %      | +0.7 %      |
| LASSO                      | +0.5 %   | +2.6 %      | +0.9 %      |
| raw factors                | +2.9 %   | +4.0 %      | +2.4 %      |
| trailing momentum          | +53.1 %  |             |             |
| volatility-based logit     |          | +7.2 %      | -1.7 %      |
| GARCH-based probability    |          | +6.3 %      | -5.5 %      |

### monthly: in drawdown (at least 10 % below the peak) (311 to 328 forecasts)

| method                     | return   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:------------|:------------|
| IBA, K formulas (fixed)    | +1.8 %   | -0.4 %      | +1.2 %      |
| IBA, K formulas (averaged) | +2.3 %   | -2.4 %      | +0.1 %      |
| IBA, generic formulas      | +3.3 %   | +2.6 %      | +4.6 %      |
| group PCA                  | +4.3 %   | +5.0 %      | +1.1 %      |
| PCA                        | +4.3 %   | +3.6 %      | +0.5 %      |
| kernel PCA                 | +3.8 %   | +3.8 %      | +1.2 %      |
| autoencoder                | +2.9 %   | +1.8 %      | +0.1 %      |
| LASSO                      | +4.7 %   | +10.6 %     | +0.7 %      |
| raw factors                | +7.8 %   | +18.5 %     | +4.2 %      |
| trailing momentum          | +83.8 %  |             |             |
| volatility-based logit     |          | +5.6 %      | -2.8 %      |
| GARCH-based probability    |          | +5.2 %      | -14.9 %     |

### monthly: not in drawdown (1880 to 1897 forecasts)

| method                     | return   | tail_loss   | tail_gain   |
|:---------------------------|:---------|:------------|:------------|
| IBA, K formulas (fixed)    | +0.4 %   | +3.0 %      | +0.7 %      |
| IBA, K formulas (averaged) | -0.2 %   | +2.0 %      | +0.3 %      |
| IBA, generic formulas      | -0.0 %   | +0.9 %      | +1.0 %      |
| group PCA                  | -0.7 %   | -0.4 %      | +0.5 %      |
| PCA                        | +0.4 %   | +0.4 %      | +0.5 %      |
| kernel PCA                 | -0.9 %   | +1.8 %      | +1.6 %      |
| autoencoder                | +0.8 %   | +0.3 %      | +0.6 %      |
| LASSO                      | -0.0 %   | +3.7 %      | +1.2 %      |
| raw factors                | +2.4 %   | +3.7 %      | +2.3 %      |
| trailing momentum          | +49.3 %  |             |             |
| volatility-based logit     |          | +6.5 %      | -3.3 %      |
| GARCH-based probability    |          | +7.0 %      | -5.4 %      |
