# SPEC-2026-11-14-abc-v3: pooled fitness, noise-aware replacement, ensembles (development series)

Arms: S = fitness on one series, C = on the asset class, F = on every series of the frequency; greedy or noise-aware replacement; colony anchored at the prior or spread over the whole space. `S greedy anchored` and `S greedy spread` are the earlier specs' ABC (clean test) and W. Readings: tested = the winner if it passed the acceptance test on clean rows, else the prior; untested = the winner; ensemble = the final colony. E1 = fixed prior formulas; B = the first ensemble.

## 1. What the searches do

Cell: gain of the winner over the prior on the fitness folds / on the clean outer rows (before the test) / share of winners that pass the test / literals of the winner. Units = (cell, block), seeds averaged; pooled arms count once per member series.

| arm                    | return                     | logrv                     | tail_loss                   | tail_gain                   |
|:-----------------------|:---------------------------|:--------------------------|:----------------------------|:----------------------------|
| S greedy anchored      | +15.0 / -4.8 / 12 % / 16.8 | +8.3 / -3.5 / 9 % / 16.2  | +16.7 / -8.0 / 14 % / 16.8  | +16.2 / -11.9 / 8 % / 16.9  |
| S greedy spread        | +22.0 / -6.0 / 8 % / 12.2  | +11.6 / -7.4 / 9 % / 12.5 | +23.8 / -10.6 / 11 % / 12.9 | +23.8 / -10.1 / 10 % / 12.8 |
| S noise-aware anchored | +14.0 / -3.8 / 11 % / 16.7 | +7.6 / -2.9 / 11 % / 16.2 | +15.8 / -5.5 / 12 % / 16.7  | +15.3 / -12.1 / 8 % / 16.8  |
| S noise-aware spread   | +18.2 / -3.2 / 9 % / 9.3   | +8.6 / -6.9 / 9 % / 10.2  | +19.1 / -9.3 / 12 % / 10.0  | +19.5 / -6.2 / 12 % / 9.9   |
| C greedy anchored      | +11.1 / -2.5 / 10 % / 16.7 | +6.5 / -2.1 / 9 % / 16.4  | +10.1 / -0.5 / 10 % / 16.6  | +9.8 / -8.3 / 8 % / 16.9    |
| C greedy spread        | +16.8 / -1.2 / 8 % / 10.8  | +8.9 / -5.3 / 7 % / 12.3  | +14.7 / -1.7 / 14 % / 11.6  | +15.5 / -6.6 / 6 % / 10.5   |
| C noise-aware anchored | +10.5 / -2.2 / 10 % / 16.6 | +5.9 / -2.1 / 13 % / 16.3 | +9.6 / -1.6 / 12 % / 16.6   | +9.4 / -7.1 / 7 % / 16.6    |
| C noise-aware spread   | +14.3 / +1.0 / 10 % / 8.2  | +6.3 / -5.0 / 7 % / 10.4  | +12.4 / +0.5 / 15 % / 8.9   | +13.2 / -2.0 / 10 % / 8.7   |
| F greedy anchored      | +9.2 / -1.1 / 18 % / 16.5  | +4.6 / -1.4 / 17 % / 16.2 | +7.6 / -0.5 / 13 % / 16.6   | +7.2 / -5.1 / 1 % / 16.6    |
| F greedy spread        | +14.0 / -0.6 / 11 % / 9.3  | +6.1 / -3.9 / 14 % / 11.8 | +11.6 / -2.1 / 17 % / 10.2  | +11.9 / +1.3 / 7 % / 9.7    |
| F noise-aware anchored | +8.8 / -0.6 / 17 % / 16.1  | +4.3 / -1.9 / 8 % / 16.0  | +7.1 / -1.7 / 16 % / 16.4   | +7.2 / -3.6 / 4 % / 16.2    |
| F noise-aware spread   | +12.1 / +2.6 / 13 % / 7.2  | +4.2 / -3.6 / 14 % / 9.5  | +10.0 / +1.6 / 19 % / 7.7   | +10.6 / +2.1 / 15 % / 7.5   |

## 2a. Tested winner against E1

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                      | against    | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:-----------------------|:-----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| S greedy anchored      | iba_e1|lin | +0.26 % (0b 1w / 7) | +0.17 % (0b 0w / 3) | +0.38 % (0b 1w / 4) | +0.59 % (0b 1w / 4) | 0 better, 3 worse of 18 |
| S greedy spread        | iba_e1|lin | +0.40 % (0b 4w / 7) | +0.34 % (0b 1w / 3) | +0.45 % (0b 2w / 4) | +0.93 % (0b 2w / 4) | 0 better, 9 worse of 18 |
| S noise-aware anchored | iba_e1|lin | +0.22 % (0b 1w / 7) | +0.15 % (0b 0w / 3) | +0.43 % (0b 2w / 4) | +0.40 % (0b 1w / 4) | 0 better, 4 worse of 18 |
| S noise-aware spread   | iba_e1|lin | +0.31 % (0b 0w / 7) | +0.34 % (0b 1w / 3) | +0.41 % (0b 2w / 4) | +1.13 % (0b 4w / 4) | 0 better, 7 worse of 18 |
| C greedy anchored      | iba_e1|lin | +0.06 % (1b 1w / 7) | +0.27 % (0b 0w / 3) | +0.10 % (0b 0w / 4) | +0.32 % (0b 1w / 4) | 1 better, 2 worse of 18 |
| C greedy spread        | iba_e1|lin | -0.09 % (0b 0w / 7) | +0.16 % (0b 0w / 3) | +0.21 % (0b 1w / 4) | +0.13 % (0b 1w / 4) | 0 better, 2 worse of 18 |
| C noise-aware anchored | iba_e1|lin | +0.14 % (1b 2w / 7) | +0.17 % (0b 0w / 3) | +0.15 % (0b 1w / 4) | +0.12 % (0b 0w / 4) | 1 better, 3 worse of 18 |
| C noise-aware spread   | iba_e1|lin | -0.26 % (0b 0w / 7) | +0.11 % (0b 1w / 3) | +0.56 % (0b 2w / 4) | +0.23 % (0b 0w / 4) | 0 better, 3 worse of 18 |
| F greedy anchored      | iba_e1|lin | +0.12 % (1b 1w / 7) | +0.01 % (0b 0w / 3) | +0.12 % (0b 0w / 4) | +0.29 % (0b 1w / 4) | 1 better, 2 worse of 18 |
| F greedy spread        | iba_e1|lin | +0.10 % (0b 0w / 7) | +0.28 % (0b 0w / 3) | +0.17 % (0b 0w / 4) | +0.11 % (0b 1w / 4) | 0 better, 1 worse of 18 |
| F noise-aware anchored | iba_e1|lin | +0.21 % (1b 2w / 7) | +0.05 % (0b 0w / 3) | +0.09 % (0b 0w / 4) | +0.09 % (0b 0w / 4) | 1 better, 2 worse of 18 |
| F noise-aware spread   | iba_e1|lin | -0.26 % (0b 0w / 7) | +0.33 % (0b 0w / 3) | +0.47 % (0b 1w / 4) | +0.19 % (0b 0w / 4) | 0 better, 1 worse of 18 |

## 2b. Winner WITHOUT the test against E1

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                      | against    | return              | logrv               | tail_loss           | tail_gain           | all tasks                |
|:-----------------------|:-----------|:--------------------|:--------------------|:--------------------|:--------------------|:-------------------------|
| S greedy anchored      | iba_e1|lin | +3.38 % (0b 4w / 7) | +1.34 % (0b 1w / 3) | +4.71 % (0b 2w / 4) | +4.09 % (0b 2w / 4) | 0 better, 9 worse of 18  |
| S greedy spread        | iba_e1|lin | +4.91 % (0b 7w / 7) | +3.08 % (0b 3w / 3) | +9.70 % (0b 4w / 4) | +6.67 % (0b 4w / 4) | 0 better, 18 worse of 18 |
| S noise-aware anchored | iba_e1|lin | +2.93 % (0b 5w / 7) | +1.26 % (0b 2w / 3) | +4.77 % (0b 2w / 4) | +3.95 % (0b 3w / 4) | 0 better, 12 worse of 18 |
| S noise-aware spread   | iba_e1|lin | +3.89 % (0b 5w / 7) | +2.84 % (0b 3w / 3) | +5.83 % (0b 3w / 4) | +4.39 % (0b 3w / 4) | 0 better, 14 worse of 18 |
| C greedy anchored      | iba_e1|lin | +1.38 % (0b 2w / 7) | +1.19 % (0b 1w / 3) | +1.21 % (0b 0w / 4) | +2.05 % (0b 3w / 4) | 0 better, 6 worse of 18  |
| C greedy spread        | iba_e1|lin | +2.34 % (0b 2w / 7) | +2.20 % (0b 3w / 3) | +3.64 % (0b 2w / 4) | +5.05 % (0b 2w / 4) | 0 better, 9 worse of 18  |
| C noise-aware anchored | iba_e1|lin | +2.23 % (0b 3w / 7) | +1.08 % (0b 0w / 3) | +2.27 % (0b 1w / 4) | +1.89 % (0b 2w / 4) | 0 better, 6 worse of 18  |
| C noise-aware spread   | iba_e1|lin | +2.21 % (0b 3w / 7) | +2.35 % (0b 2w / 3) | +3.35 % (0b 2w / 4) | +2.51 % (0b 2w / 4) | 0 better, 9 worse of 18  |
| F greedy anchored      | iba_e1|lin | +1.34 % (0b 2w / 7) | +0.39 % (0b 0w / 3) | +0.81 % (0b 0w / 4) | +1.51 % (0b 2w / 4) | 0 better, 4 worse of 18  |
| F greedy spread        | iba_e1|lin | +2.57 % (0b 3w / 7) | +1.33 % (0b 0w / 3) | +2.94 % (0b 1w / 4) | +4.49 % (0b 2w / 4) | 0 better, 6 worse of 18  |
| F noise-aware anchored | iba_e1|lin | +2.04 % (0b 3w / 7) | +0.54 % (0b 0w / 3) | +1.89 % (0b 1w / 4) | +1.47 % (0b 1w / 4) | 0 better, 5 worse of 18  |
| F noise-aware spread   | iba_e1|lin | +1.99 % (0b 2w / 7) | +2.21 % (0b 2w / 3) | +2.43 % (1b 1w / 4) | +1.93 % (0b 1w / 4) | 1 better, 6 worse of 18  |

## 2c. Colony ensemble against E1

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                           | against    | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:----------------------------|:-----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| S greedy anchored           | iba_e1|lin | -0.07 % (1b 1w / 7) | -0.35 % (2b 0w / 3) | -0.67 % (1b 0w / 4) | +0.07 % (1b 0w / 4) | 5 better, 1 worse of 18 |
| S greedy spread             | iba_e1|lin | -0.31 % (0b 0w / 7) | +0.22 % (0b 0w / 3) | -0.37 % (1b 0w / 4) | -0.30 % (1b 0w / 4) | 2 better, 0 worse of 18 |
| S noise-aware anchored      | iba_e1|lin | -0.13 % (1b 1w / 7) | -0.25 % (1b 0w / 3) | -0.52 % (1b 0w / 4) | -0.10 % (1b 0w / 4) | 4 better, 1 worse of 18 |
| S noise-aware spread        | iba_e1|lin | -0.82 % (0b 0w / 7) | +1.37 % (0b 0w / 3) | -0.21 % (0b 0w / 4) | -0.41 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| C greedy anchored           | iba_e1|lin | -0.15 % (1b 0w / 7) | -0.33 % (1b 0w / 3) | -0.52 % (1b 0w / 4) | -0.20 % (2b 0w / 4) | 5 better, 0 worse of 18 |
| C greedy spread             | iba_e1|lin | -0.60 % (1b 0w / 7) | +0.16 % (0b 0w / 3) | -0.17 % (1b 0w / 4) | -0.57 % (1b 0w / 4) | 3 better, 0 worse of 18 |
| C noise-aware anchored      | iba_e1|lin | -0.19 % (1b 0w / 7) | -0.25 % (1b 0w / 3) | -0.57 % (2b 0w / 4) | -0.17 % (1b 0w / 4) | 5 better, 0 worse of 18 |
| C noise-aware spread        | iba_e1|lin | -0.95 % (1b 0w / 7) | +1.30 % (0b 0w / 3) | +0.07 % (1b 0w / 4) | -0.57 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| F greedy anchored           | iba_e1|lin | -0.19 % (2b 0w / 7) | -0.33 % (1b 0w / 3) | -0.53 % (2b 0w / 4) | -0.22 % (3b 0w / 4) | 8 better, 0 worse of 18 |
| F greedy spread             | iba_e1|lin | -0.58 % (0b 0w / 7) | +0.21 % (0b 0w / 3) | -0.26 % (1b 0w / 4) | -0.57 % (1b 0w / 4) | 2 better, 0 worse of 18 |
| F noise-aware anchored      | iba_e1|lin | -0.21 % (2b 0w / 7) | -0.25 % (1b 0w / 3) | -0.54 % (2b 0w / 4) | -0.18 % (1b 0w / 4) | 6 better, 0 worse of 18 |
| F noise-aware spread        | iba_e1|lin | -0.98 % (1b 0w / 7) | +1.27 % (0b 0w / 3) | +0.05 % (1b 0w / 4) | -0.56 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| control: starting colony, a | iba_e1|lin | -0.14 % (3b 0w / 7) | -0.12 % (1b 0w / 3) | -0.18 % (1b 0w / 4) | -0.14 % (3b 0w / 4) | 8 better, 0 worse of 18 |
| control: starting colony, w | iba_e1|lin | -1.08 % (0b 0w / 7) | +2.01 % (0b 2w / 3) | -0.35 % (1b 0w / 4) | -0.44 % (1b 0w / 4) | 2 better, 2 worse of 18 |

## 2d. Colony ensemble against the first ensemble (B)

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                           | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:----------------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| S greedy spread             | iba_b     | -0.24 % (0b 0w / 7) | +0.57 % (0b 0w / 3) | +0.30 % (0b 0w / 4) | -0.37 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| S noise-aware anchored      | iba_b     | -0.06 % (0b 0w / 7) | +0.10 % (0b 0w / 3) | +0.15 % (0b 0w / 4) | -0.17 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| S noise-aware spread        | iba_b     | -0.74 % (0b 0w / 7) | +1.73 % (0b 2w / 3) | +0.46 % (0b 0w / 4) | -0.48 % (0b 0w / 4) | 0 better, 2 worse of 18 |
| C greedy anchored           | iba_b     | -0.08 % (1b 0w / 7) | +0.02 % (0b 0w / 3) | +0.15 % (0b 0w / 4) | -0.27 % (2b 0w / 4) | 3 better, 0 worse of 18 |
| C greedy spread             | iba_b     | -0.53 % (0b 0w / 7) | +0.51 % (0b 0w / 3) | +0.51 % (0b 0w / 4) | -0.64 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| C noise-aware anchored      | iba_b     | -0.11 % (2b 1w / 7) | +0.10 % (0b 0w / 3) | +0.10 % (0b 0w / 4) | -0.23 % (1b 0w / 4) | 3 better, 1 worse of 18 |
| C noise-aware spread        | iba_b     | -0.88 % (0b 0w / 7) | +1.66 % (0b 2w / 3) | +0.74 % (0b 0w / 4) | -0.64 % (2b 0w / 4) | 2 better, 2 worse of 18 |
| F greedy anchored           | iba_b     | -0.11 % (2b 0w / 7) | +0.02 % (0b 0w / 3) | +0.14 % (0b 0w / 4) | -0.29 % (2b 0w / 4) | 4 better, 0 worse of 18 |
| F greedy spread             | iba_b     | -0.51 % (0b 0w / 7) | +0.56 % (0b 0w / 3) | +0.42 % (0b 0w / 4) | -0.64 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| F noise-aware anchored      | iba_b     | -0.14 % (2b 1w / 7) | +0.10 % (0b 0w / 3) | +0.13 % (0b 0w / 4) | -0.25 % (2b 0w / 4) | 4 better, 1 worse of 18 |
| F noise-aware spread        | iba_b     | -0.91 % (0b 0w / 7) | +1.62 % (0b 1w / 3) | +0.73 % (0b 0w / 4) | -0.63 % (2b 0w / 4) | 2 better, 1 worse of 18 |
| control: starting colony, a | iba_b     | -0.06 % (2b 0w / 7) | +0.23 % (0b 2w / 3) | +0.49 % (0b 1w / 4) | -0.21 % (1b 0w / 4) | 3 better, 3 worse of 18 |
| control: starting colony, w | iba_b     | -1.00 % (0b 0w / 7) | +2.37 % (0b 2w / 3) | +0.32 % (0b 0w / 4) | -0.51 % (1b 0w / 4) | 1 better, 2 worse of 18 |

## 2e. Colony ensemble against group PCA

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                           | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:----------------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| S greedy anchored           | gpca|lin  | -0.11 % (0b 0w / 7) | -0.71 % (0b 0w / 3) | -1.30 % (1b 0w / 4) | +0.35 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| S greedy spread             | gpca|lin  | -0.35 % (1b 0w / 7) | -0.14 % (1b 0w / 3) | -1.01 % (2b 0w / 4) | -0.02 % (0b 0w / 4) | 4 better, 0 worse of 18 |
| S noise-aware anchored      | gpca|lin  | -0.17 % (0b 0w / 7) | -0.61 % (0b 0w / 3) | -1.16 % (1b 0w / 4) | +0.18 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| S noise-aware spread        | gpca|lin  | -0.85 % (1b 0w / 7) | +1.01 % (0b 0w / 3) | -0.85 % (2b 0w / 4) | -0.13 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| C greedy anchored           | gpca|lin  | -0.19 % (0b 0w / 7) | -0.69 % (0b 0w / 3) | -1.15 % (1b 0w / 4) | +0.08 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| C greedy spread             | gpca|lin  | -0.64 % (1b 0w / 7) | -0.20 % (1b 0w / 3) | -0.80 % (2b 0w / 4) | -0.29 % (1b 0w / 4) | 5 better, 0 worse of 18 |
| C noise-aware anchored      | gpca|lin  | -0.22 % (0b 0w / 7) | -0.60 % (0b 0w / 3) | -1.21 % (1b 0w / 4) | +0.11 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| C noise-aware spread        | gpca|lin  | -0.99 % (1b 0w / 7) | +0.94 % (0b 0w / 3) | -0.57 % (2b 0w / 4) | -0.30 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| F greedy anchored           | gpca|lin  | -0.22 % (0b 0w / 7) | -0.69 % (0b 0w / 3) | -1.17 % (1b 0w / 4) | +0.06 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| F greedy spread             | gpca|lin  | -0.62 % (1b 0w / 7) | -0.15 % (1b 0w / 3) | -0.89 % (2b 0w / 4) | -0.29 % (1b 0w / 4) | 5 better, 0 worse of 18 |
| F noise-aware anchored      | gpca|lin  | -0.25 % (0b 0w / 7) | -0.61 % (0b 0w / 3) | -1.17 % (1b 0w / 4) | +0.10 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| F noise-aware spread        | gpca|lin  | -1.02 % (1b 0w / 7) | +0.91 % (0b 1w / 3) | -0.59 % (2b 0w / 4) | -0.29 % (1b 0w / 4) | 4 better, 1 worse of 18 |
| control: starting colony, a | gpca|lin  | -0.17 % (0b 0w / 7) | -0.48 % (0b 0w / 3) | -0.81 % (1b 0w / 4) | +0.14 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| control: starting colony, w | gpca|lin  | -1.11 % (2b 0w / 7) | +1.65 % (0b 1w / 3) | -0.98 % (2b 0w / 4) | -0.16 % (0b 0w / 4) | 4 better, 1 worse of 18 |

## 2f. Ensembles averaged over the three seeds, against E1 and against group PCA

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                         | against    | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:--------------------------|:-----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| S greedy anchored @3      | iba_e1|lin | -0.09 % (1b 1w / 7) | -0.38 % (2b 0w / 3) | -0.71 % (1b 0w / 4) | +0.05 % (1b 0w / 4) | 5 better, 1 worse of 18 |
| S greedy spread @3        | iba_e1|lin | -0.36 % (0b 0w / 7) | +0.14 % (0b 0w / 3) | -0.47 % (1b 0w / 4) | -0.36 % (1b 0w / 4) | 2 better, 0 worse of 18 |
| S noise-aware anchored @3 | iba_e1|lin | -0.14 % (1b 1w / 7) | -0.27 % (1b 0w / 3) | -0.55 % (2b 0w / 4) | -0.12 % (1b 0w / 4) | 5 better, 1 worse of 18 |
| S noise-aware spread @3   | iba_e1|lin | -0.84 % (0b 0w / 7) | +1.31 % (0b 0w / 3) | -0.27 % (0b 0w / 4) | -0.44 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| C greedy anchored @3      | iba_e1|lin | -0.17 % (2b 0w / 7) | -0.36 % (1b 0w / 3) | -0.55 % (1b 0w / 4) | -0.21 % (2b 0w / 4) | 6 better, 0 worse of 18 |
| C greedy spread @3        | iba_e1|lin | -0.64 % (1b 0w / 7) | +0.09 % (0b 0w / 3) | -0.22 % (1b 0w / 4) | -0.61 % (1b 0w / 4) | 3 better, 0 worse of 18 |
| C noise-aware anchored @3 | iba_e1|lin | -0.20 % (2b 0w / 7) | -0.27 % (1b 0w / 3) | -0.60 % (2b 0w / 4) | -0.18 % (1b 0w / 4) | 6 better, 0 worse of 18 |
| C noise-aware spread @3   | iba_e1|lin | -0.98 % (1b 0w / 7) | +1.24 % (0b 0w / 3) | +0.03 % (1b 0w / 4) | -0.60 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| F greedy anchored @3      | iba_e1|lin | -0.20 % (3b 0w / 7) | -0.35 % (1b 0w / 3) | -0.57 % (2b 0w / 4) | -0.24 % (3b 0w / 4) | 9 better, 0 worse of 18 |
| F greedy spread @3        | iba_e1|lin | -0.61 % (0b 0w / 7) | +0.15 % (0b 0w / 3) | -0.31 % (1b 0w / 4) | -0.61 % (1b 0w / 4) | 2 better, 0 worse of 18 |
| F noise-aware anchored @3 | iba_e1|lin | -0.23 % (2b 0w / 7) | -0.27 % (1b 0w / 3) | -0.57 % (2b 0w / 4) | -0.20 % (1b 0w / 4) | 6 better, 0 worse of 18 |
| F noise-aware spread @3   | iba_e1|lin | -1.00 % (1b 0w / 7) | +1.21 % (0b 0w / 3) | +0.01 % (1b 0w / 4) | -0.59 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| control a @3              | iba_e1|lin | -0.14 % (3b 0w / 7) | -0.13 % (1b 0w / 3) | -0.19 % (1b 0w / 4) | -0.14 % (3b 0w / 4) | 8 better, 0 worse of 18 |
| control w @3              | iba_e1|lin | -1.10 % (0b 0w / 7) | +1.96 % (0b 2w / 3) | -0.38 % (1b 0w / 4) | -0.46 % (1b 0w / 4) | 2 better, 2 worse of 18 |
| S greedy anchored @3      | gpca|lin   | -0.13 % (0b 0w / 7) | -0.73 % (0b 0w / 3) | -1.34 % (1b 0w / 4) | +0.33 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| S greedy spread @3        | gpca|lin   | -0.40 % (1b 0w / 7) | -0.22 % (1b 0w / 3) | -1.10 % (2b 0w / 4) | -0.08 % (0b 0w / 4) | 4 better, 0 worse of 18 |
| S noise-aware anchored @3 | gpca|lin   | -0.18 % (0b 0w / 7) | -0.63 % (0b 0w / 3) | -1.18 % (1b 0w / 4) | +0.16 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| S noise-aware spread @3   | gpca|lin   | -0.88 % (1b 0w / 7) | +0.94 % (0b 0w / 3) | -0.90 % (2b 0w / 4) | -0.17 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| C greedy anchored @3      | gpca|lin   | -0.21 % (0b 0w / 7) | -0.72 % (0b 0w / 3) | -1.18 % (1b 0w / 4) | +0.06 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| C greedy spread @3        | gpca|lin   | -0.68 % (1b 0w / 7) | -0.27 % (1b 0w / 3) | -0.86 % (2b 0w / 4) | -0.34 % (1b 0w / 4) | 5 better, 0 worse of 18 |
| C noise-aware anchored @3 | gpca|lin   | -0.24 % (0b 0w / 7) | -0.63 % (0b 0w / 3) | -1.24 % (1b 0w / 4) | +0.10 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| C noise-aware spread @3   | gpca|lin   | -1.02 % (1b 0w / 7) | +0.87 % (0b 0w / 3) | -0.61 % (2b 0w / 4) | -0.32 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| F greedy anchored @3      | gpca|lin   | -0.24 % (0b 0w / 7) | -0.71 % (0b 0w / 3) | -1.20 % (1b 0w / 4) | +0.04 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| F greedy spread @3        | gpca|lin   | -0.65 % (1b 0w / 7) | -0.21 % (1b 0w / 3) | -0.94 % (2b 0w / 4) | -0.33 % (1b 0w / 4) | 5 better, 0 worse of 18 |
| F noise-aware anchored @3 | gpca|lin   | -0.26 % (0b 0w / 7) | -0.63 % (0b 0w / 3) | -1.20 % (1b 0w / 4) | +0.08 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| F noise-aware spread @3   | gpca|lin   | -1.04 % (1b 0w / 7) | +0.85 % (0b 0w / 3) | -0.62 % (2b 0w / 4) | -0.31 % (1b 0w / 4) | 4 better, 0 worse of 18 |
| control a @3              | gpca|lin   | -0.17 % (0b 0w / 7) | -0.49 % (0b 0w / 3) | -0.82 % (1b 0w / 4) | +0.14 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| control w @3              | gpca|lin   | -1.13 % (2b 0w / 7) | +1.59 % (0b 1w / 3) | -1.02 % (2b 0w / 4) | -0.18 % (0b 0w / 4) | 4 better, 1 worse of 18 |

## 2g. Against the type's reference (historical mean / HAR / base rate)

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                                | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:---------------------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| E1                               | REF       | +1.39 % (0b 0w / 7) | -5.29 % (2b 0w / 3) | -0.29 % (0b 1w / 4) | +0.17 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| B                                | REF       | +1.32 % (0b 0w / 7) | -5.62 % (2b 0w / 3) | -0.95 % (0b 0w / 4) | +0.24 % (0b 1w / 4) | 2 better, 1 worse of 18 |
| group PCA                        | REF       | +1.43 % (0b 1w / 7) | -4.92 % (2b 0w / 3) | +0.35 % (0b 1w / 4) | -0.11 % (1b 0w / 4) | 3 better, 2 worse of 18 |
| S greedy anchored, tested        | REF       | +1.66 % (0b 1w / 7) | -5.13 % (2b 0w / 3) | +0.09 % (0b 1w / 4) | +0.76 % (0b 2w / 4) | 2 better, 4 worse of 18 |
| S greedy spread, tested          | REF       | +1.80 % (0b 0w / 7) | -4.97 % (2b 0w / 3) | +0.16 % (0b 1w / 4) | +1.10 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| S noise-aware anchored, tested   | REF       | +1.62 % (0b 1w / 7) | -5.15 % (2b 0w / 3) | +0.14 % (0b 1w / 4) | +0.57 % (0b 2w / 4) | 2 better, 4 worse of 18 |
| S noise-aware spread, tested     | REF       | +1.70 % (0b 0w / 7) | -4.97 % (2b 0w / 3) | +0.12 % (0b 1w / 4) | +1.30 % (0b 2w / 4) | 2 better, 3 worse of 18 |
| C greedy anchored, tested        | REF       | +1.46 % (0b 0w / 7) | -5.03 % (2b 0w / 3) | -0.18 % (0b 1w / 4) | +0.49 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| C greedy spread, tested          | REF       | +1.30 % (0b 0w / 7) | -5.14 % (2b 0w / 3) | -0.08 % (0b 1w / 4) | +0.30 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| C noise-aware anchored, tested   | REF       | +1.53 % (0b 1w / 7) | -5.13 % (2b 0w / 3) | -0.14 % (0b 1w / 4) | +0.28 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| C noise-aware spread, tested     | REF       | +1.13 % (0b 0w / 7) | -5.19 % (2b 0w / 3) | +0.27 % (0b 1w / 4) | +0.39 % (0b 1w / 4) | 2 better, 2 worse of 18 |
| F greedy anchored, tested        | REF       | +1.52 % (0b 1w / 7) | -5.28 % (2b 0w / 3) | -0.17 % (0b 1w / 4) | +0.46 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| F greedy spread, tested          | REF       | +1.49 % (0b 1w / 7) | -5.03 % (2b 0w / 3) | -0.12 % (0b 1w / 4) | +0.28 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| F noise-aware anchored, tested   | REF       | +1.60 % (0b 1w / 7) | -5.24 % (2b 0w / 3) | -0.20 % (0b 1w / 4) | +0.26 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| F noise-aware spread, tested     | REF       | +1.13 % (0b 1w / 7) | -4.97 % (2b 0w / 3) | +0.18 % (0b 1w / 4) | +0.36 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| S greedy anchored, ensemble      | REF       | +1.32 % (0b 0w / 7) | -5.62 % (2b 0w / 3) | -0.95 % (0b 0w / 4) | +0.24 % (0b 1w / 4) | 2 better, 1 worse of 18 |
| S greedy spread, ensemble        | REF       | +1.08 % (0b 1w / 7) | -5.08 % (2b 0w / 3) | -0.66 % (0b 0w / 4) | -0.13 % (1b 0w / 4) | 3 better, 1 worse of 18 |
| S noise-aware anchored, ensemble | REF       | +1.26 % (0b 0w / 7) | -5.53 % (2b 0w / 3) | -0.81 % (0b 0w / 4) | +0.06 % (0b 1w / 4) | 2 better, 1 worse of 18 |
| S noise-aware spread, ensemble   | REF       | +0.56 % (0b 1w / 7) | -3.99 % (2b 0w / 3) | -0.51 % (0b 1w / 4) | -0.24 % (1b 0w / 4) | 3 better, 2 worse of 18 |
| C greedy anchored, ensemble      | REF       | +1.24 % (0b 0w / 7) | -5.60 % (2b 0w / 3) | -0.80 % (0b 0w / 4) | -0.03 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| C greedy spread, ensemble        | REF       | +0.78 % (0b 1w / 7) | -5.14 % (2b 0w / 3) | -0.46 % (0b 0w / 4) | -0.40 % (1b 0w / 4) | 3 better, 1 worse of 18 |
| C noise-aware anchored, ensemble | REF       | +1.20 % (0b 0w / 7) | -5.52 % (2b 0w / 3) | -0.86 % (0b 0w / 4) | +0.00 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| C noise-aware spread, ensemble   | REF       | +0.42 % (0b 1w / 7) | -4.06 % (2b 0w / 3) | -0.23 % (0b 1w / 4) | -0.41 % (1b 0w / 4) | 3 better, 2 worse of 18 |
| F greedy anchored, ensemble      | REF       | +1.20 % (0b 0w / 7) | -5.60 % (2b 0w / 3) | -0.82 % (0b 0w / 4) | -0.06 % (1b 0w / 4) | 3 better, 0 worse of 18 |
| F greedy spread, ensemble        | REF       | +0.80 % (0b 1w / 7) | -5.09 % (3b 0w / 3) | -0.55 % (0b 0w / 4) | -0.40 % (1b 0w / 4) | 4 better, 1 worse of 18 |
| F noise-aware anchored, ensemble | REF       | +1.18 % (0b 0w / 7) | -5.53 % (2b 0w / 3) | -0.83 % (0b 0w / 4) | -0.02 % (1b 0w / 4) | 3 better, 0 worse of 18 |
| F noise-aware spread, ensemble   | REF       | +0.40 % (0b 1w / 7) | -4.09 % (3b 0w / 3) | -0.25 % (0b 0w / 4) | -0.40 % (1b 0w / 4) | 4 better, 1 worse of 18 |

## 2h. The controls: starting colonies as ensembles (no search)

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a                  | against    | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:-------------------|:-----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| starting colony, a | iba_e1|lin | -0.14 % (3b 0w / 7) | -0.12 % (1b 0w / 3) | -0.18 % (1b 0w / 4) | -0.14 % (3b 0w / 4) | 8 better, 0 worse of 18 |
| starting colony, a | iba_b      | -0.06 % (2b 0w / 7) | +0.23 % (0b 2w / 3) | +0.49 % (0b 1w / 4) | -0.21 % (1b 0w / 4) | 3 better, 3 worse of 18 |
| starting colony, a | iba_wb     | +0.18 % (0b 0w / 7) | -0.34 % (0b 0w / 3) | +0.20 % (0b 1w / 4) | +0.16 % (0b 1w / 4) | 0 better, 2 worse of 18 |
| starting colony, a | gpca|lin   | -0.17 % (0b 0w / 7) | -0.48 % (0b 0w / 3) | -0.81 % (1b 0w / 4) | +0.14 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| starting colony, a | REF        | +1.26 % (0b 0w / 7) | -5.40 % (2b 0w / 3) | -0.47 % (0b 1w / 4) | +0.03 % (0b 0w / 4) | 2 better, 1 worse of 18 |
| starting colony, w | iba_e1|lin | -1.08 % (0b 0w / 7) | +2.01 % (0b 2w / 3) | -0.35 % (1b 0w / 4) | -0.44 % (1b 0w / 4) | 2 better, 2 worse of 18 |
| starting colony, w | iba_b      | -1.00 % (0b 0w / 7) | +2.37 % (0b 2w / 3) | +0.32 % (0b 0w / 4) | -0.51 % (1b 0w / 4) | 1 better, 2 worse of 18 |
| starting colony, w | iba_wb     | -0.77 % (2b 0w / 7) | +1.79 % (0b 2w / 3) | +0.02 % (0b 0w / 4) | -0.14 % (0b 1w / 4) | 2 better, 3 worse of 18 |
| starting colony, w | gpca|lin   | -1.11 % (2b 0w / 7) | +1.65 % (0b 1w / 3) | -0.98 % (2b 0w / 4) | -0.16 % (0b 0w / 4) | 4 better, 1 worse of 18 |
| starting colony, w | REF        | +0.30 % (0b 0w / 7) | -3.41 % (3b 0w / 3) | -0.65 % (0b 0w / 4) | -0.28 % (1b 0w / 4) | 4 better, 0 worse of 18 |

## 3. The three factors (a against b at fixed levels of the other two)

Cell: mean relative difference in the primary loss, a minus b (negative = a better); tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

### tested

| contrast                                | against     | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:----------------------------------------|:------------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| C against S: iba_ca|lin                 | iba_ac|lin  | -0.20 % (1b 0w / 7) | +0.10 % (0b 0w / 3) | -0.27 % (0b 0w / 4) | -0.27 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| F against S: iba_fa|lin                 | iba_ac|lin  | -0.14 % (0b 0w / 7) | -0.16 % (0b 0w / 3) | -0.26 % (1b 0w / 4) | -0.30 % (0b 0w / 4) | 1 better, 0 worse of 18 |
| C against S: iba_cw|lin                 | iba_w|lin   | -0.48 % (3b 0w / 7) | -0.18 % (1b 0w / 3) | -0.23 % (1b 0w / 4) | -0.78 % (1b 0w / 4) | 6 better, 0 worse of 18 |
| F against S: iba_fw|lin                 | iba_w|lin   | -0.30 % (4b 0w / 7) | -0.06 % (0b 0w / 3) | -0.27 % (1b 0w / 4) | -0.80 % (1b 0w / 4) | 6 better, 0 worse of 18 |
| C against S: iba_cna|lin                | iba_sna|lin | -0.08 % (0b 1w / 7) | +0.02 % (0b 0w / 3) | -0.28 % (1b 0w / 4) | -0.28 % (0b 0w / 4) | 1 better, 1 worse of 18 |
| F against S: iba_fna|lin                | iba_sna|lin | -0.01 % (1b 1w / 7) | -0.09 % (0b 0w / 3) | -0.34 % (2b 0w / 4) | -0.31 % (0b 0w / 4) | 3 better, 1 worse of 18 |
| C against S: iba_cnw|lin                | iba_snw|lin | -0.56 % (1b 0w / 7) | -0.24 % (1b 0w / 3) | +0.15 % (1b 1w / 4) | -0.89 % (2b 0w / 4) | 5 better, 1 worse of 18 |
| F against S: iba_fnw|lin                | iba_snw|lin | -0.56 % (1b 0w / 7) | -0.01 % (0b 0w / 3) | +0.06 % (1b 1w / 4) | -0.92 % (2b 0w / 4) | 4 better, 1 worse of 18 |
| noise-aware against greedy: iba_sna|lin | iba_ac|lin  | -0.04 % (0b 0w / 7) | -0.02 % (0b 0w / 3) | +0.05 % (0b 0w / 4) | -0.19 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| noise-aware against greedy: iba_snw|lin | iba_w|lin   | -0.09 % (1b 0w / 7) | +0.00 % (0b 0w / 3) | -0.04 % (1b 0w / 4) | +0.20 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| spread against anchored: iba_w|lin      | iba_ac|lin  | +0.13 % (0b 1w / 7) | +0.17 % (0b 1w / 3) | +0.07 % (0b 0w / 4) | +0.34 % (1b 2w / 4) | 1 better, 4 worse of 18 |
| spread against anchored: iba_snw|lin    | iba_sna|lin | +0.09 % (1b 0w / 7) | +0.20 % (0b 0w / 3) | -0.02 % (0b 0w / 4) | +0.72 % (0b 2w / 4) | 1 better, 2 worse of 18 |
| noise-aware against greedy: iba_cna|lin | iba_ca|lin  | +0.08 % (0b 1w / 7) | -0.10 % (0b 0w / 3) | +0.05 % (0b 0w / 4) | -0.20 % (1b 0w / 4) | 1 better, 1 worse of 18 |
| noise-aware against greedy: iba_cnw|lin | iba_cw|lin  | -0.17 % (0b 0w / 7) | -0.05 % (0b 0w / 3) | +0.35 % (0b 1w / 4) | +0.09 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| spread against anchored: iba_cw|lin     | iba_ca|lin  | -0.15 % (1b 0w / 7) | -0.11 % (0b 0w / 3) | +0.11 % (0b 0w / 4) | -0.18 % (1b 0w / 4) | 2 better, 0 worse of 18 |
| spread against anchored: iba_cnw|lin    | iba_cna|lin | -0.40 % (2b 0w / 7) | -0.06 % (1b 0w / 3) | +0.41 % (0b 1w / 4) | +0.11 % (0b 0w / 4) | 3 better, 1 worse of 18 |
| noise-aware against greedy: iba_fna|lin | iba_fa|lin  | +0.08 % (0b 1w / 7) | +0.04 % (0b 0w / 3) | -0.03 % (0b 0w / 4) | -0.20 % (1b 0w / 4) | 1 better, 1 worse of 18 |
| noise-aware against greedy: iba_fnw|lin | iba_fw|lin  | -0.35 % (0b 0w / 7) | +0.05 % (0b 0w / 3) | +0.29 % (0b 1w / 4) | +0.08 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| spread against anchored: iba_fw|lin     | iba_fa|lin  | -0.03 % (0b 0w / 7) | +0.27 % (0b 0w / 3) | +0.06 % (0b 0w / 4) | -0.18 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| spread against anchored: iba_fnw|lin    | iba_fna|lin | -0.46 % (1b 0w / 7) | +0.28 % (0b 0w / 3) | +0.38 % (0b 1w / 4) | +0.10 % (0b 0w / 4) | 1 better, 1 worse of 18 |

Averaged over the contrasts of each factor:

| factor                     | return   | logrv   | tail_loss   | tail_gain   | tasks better / worse   |
|:---------------------------|:---------|:--------|:------------|:------------|:-----------------------|
| C against S                | -0.33 %  | -0.07 % | -0.16 %     | -0.55 %     | 13 / 2 of 72           |
| F against S                | -0.25 %  | -0.08 % | -0.20 %     | -0.58 %     | 14 / 2 of 72           |
| noise-aware against greedy | -0.08 %  | -0.01 % | +0.11 %     | -0.04 %     | 4 / 4 of 108           |
| spread against anchored    | -0.14 %  | +0.13 % | +0.17 %     | +0.15 %     | 9 / 8 of 108           |

### untested

| contrast                                  | against       | return              | logrv               | tail_loss           | tail_gain           | all tasks                |
|:------------------------------------------|:--------------|:--------------------|:--------------------|:--------------------|:--------------------|:-------------------------|
| C against S: iba_ca_r|lin                 | iba_ar|lin    | -1.91 % (4b 0w / 7) | -0.15 % (0b 0w / 3) | -3.26 % (2b 0w / 4) | -1.94 % (1b 0w / 4) | 7 better, 0 worse of 18  |
| F against S: iba_fa_r|lin                 | iba_ar|lin    | -1.96 % (3b 0w / 7) | -0.94 % (2b 0w / 3) | -3.65 % (2b 0w / 4) | -2.46 % (1b 0w / 4) | 8 better, 0 worse of 18  |
| C against S: iba_cw_r|lin                 | iba_wr|lin    | -2.42 % (3b 0w / 7) | -0.85 % (2b 0w / 3) | -5.24 % (3b 0w / 4) | -1.52 % (2b 0w / 4) | 10 better, 0 worse of 18 |
| F against S: iba_fw_r|lin                 | iba_wr|lin    | -2.20 % (1b 0w / 7) | -1.70 % (3b 0w / 3) | -5.93 % (3b 0w / 4) | -2.07 % (3b 0w / 4) | 10 better, 0 worse of 18 |
| C against S: iba_cna_r|lin                | iba_sna_r|lin | -0.66 % (1b 0w / 7) | -0.17 % (0b 0w / 3) | -2.34 % (1b 0w / 4) | -1.96 % (1b 0w / 4) | 3 better, 0 worse of 18  |
| F against S: iba_fna_r|lin                | iba_sna_r|lin | -0.85 % (2b 0w / 7) | -0.71 % (1b 0w / 3) | -2.72 % (2b 0w / 4) | -2.37 % (2b 0w / 4) | 7 better, 0 worse of 18  |
| C against S: iba_cnw_r|lin                | iba_snw_r|lin | -1.60 % (4b 0w / 7) | -0.47 % (1b 0w / 3) | -2.25 % (1b 0w / 4) | -1.78 % (3b 0w / 4) | 9 better, 0 worse of 18  |
| F against S: iba_fnw_r|lin                | iba_snw_r|lin | -1.81 % (4b 0w / 7) | -0.61 % (1b 0w / 3) | -3.16 % (2b 0w / 4) | -2.34 % (3b 0w / 4) | 10 better, 0 worse of 18 |
| noise-aware against greedy: iba_sna_r|lin | iba_ar|lin    | -0.44 % (0b 0w / 7) | -0.08 % (0b 0w / 3) | +0.07 % (0b 0w / 4) | -0.13 % (0b 0w / 4) | 0 better, 0 worse of 18  |
| noise-aware against greedy: iba_snw_r|lin | iba_wr|lin    | -0.97 % (1b 0w / 7) | -0.24 % (1b 0w / 3) | -3.34 % (3b 0w / 4) | -2.09 % (3b 0w / 4) | 8 better, 0 worse of 18  |
| spread against anchored: iba_wr|lin       | iba_ar|lin    | +1.47 % (0b 1w / 7) | +1.71 % (0b 3w / 3) | +4.64 % (0b 2w / 4) | +2.44 % (0b 2w / 4) | 0 better, 8 worse of 18  |
| spread against anchored: iba_snw_r|lin    | iba_sna_r|lin | +0.93 % (0b 1w / 7) | +1.56 % (0b 2w / 3) | +0.98 % (0b 1w / 4) | +0.42 % (0b 0w / 4) | 0 better, 4 worse of 18  |
| noise-aware against greedy: iba_cna_r|lin | iba_ca_r|lin  | +0.84 % (0b 1w / 7) | -0.10 % (0b 0w / 3) | +1.06 % (0b 0w / 4) | -0.16 % (1b 0w / 4) | 1 better, 1 worse of 18  |
| noise-aware against greedy: iba_cnw_r|lin | iba_cw_r|lin  | -0.12 % (0b 0w / 7) | +0.15 % (0b 0w / 3) | -0.25 % (0b 0w / 4) | -2.25 % (2b 0w / 4) | 2 better, 0 worse of 18  |
| spread against anchored: iba_cw_r|lin     | iba_ca_r|lin  | +0.95 % (0b 2w / 7) | +1.00 % (0b 1w / 3) | +2.39 % (0b 0w / 4) | +2.92 % (0b 2w / 4) | 0 better, 5 worse of 18  |
| spread against anchored: iba_cnw_r|lin    | iba_cna_r|lin | -0.01 % (0b 1w / 7) | +1.26 % (0b 1w / 3) | +1.05 % (0b 1w / 4) | +0.61 % (0b 0w / 4) | 0 better, 3 worse of 18  |
| noise-aware against greedy: iba_fna_r|lin | iba_fa_r|lin  | +0.69 % (1b 1w / 7) | +0.15 % (0b 0w / 3) | +1.07 % (0b 0w / 4) | -0.04 % (0b 0w / 4) | 1 better, 1 worse of 18  |
| noise-aware against greedy: iba_fnw_r|lin | iba_fw_r|lin  | -0.56 % (2b 0w / 7) | +0.87 % (0b 0w / 3) | -0.48 % (0b 0w / 4) | -2.28 % (2b 0w / 4) | 4 better, 0 worse of 18  |
| spread against anchored: iba_fw_r|lin     | iba_fa_r|lin  | +1.22 % (0b 2w / 7) | +0.94 % (0b 0w / 3) | +2.08 % (0b 0w / 4) | +2.90 % (0b 1w / 4) | 0 better, 3 worse of 18  |
| spread against anchored: iba_fnw_r|lin    | iba_fna_r|lin | -0.04 % (0b 1w / 7) | +1.67 % (0b 1w / 3) | +0.51 % (0b 0w / 4) | +0.45 % (0b 0w / 4) | 0 better, 2 worse of 18  |

Averaged over the contrasts of each factor:

| factor                     | return   | logrv   | tail_loss   | tail_gain   | tasks better / worse   |
|:---------------------------|:---------|:--------|:------------|:------------|:-----------------------|
| C against S                | -1.65 %  | -0.41 % | -3.27 %     | -1.80 %     | 29 / 0 of 72           |
| F against S                | -1.71 %  | -0.99 % | -3.87 %     | -2.31 %     | 35 / 0 of 72           |
| noise-aware against greedy | -0.09 %  | +0.12 % | -0.31 %     | -1.16 %     | 16 / 2 of 108          |
| spread against anchored    | +0.75 %  | +1.36 % | +1.94 %     | +1.62 %     | 0 / 25 of 108          |

### ensemble

| contrast                              | against   | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:--------------------------------------|:----------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| C against S: iba_ca_b                 | iba_b     | -0.08 % (1b 0w / 7) | +0.02 % (0b 0w / 3) | +0.15 % (0b 0w / 4) | -0.27 % (2b 0w / 4) | 3 better, 0 worse of 18 |
| F against S: iba_fa_b                 | iba_b     | -0.11 % (2b 0w / 7) | +0.02 % (0b 0w / 3) | +0.14 % (0b 0w / 4) | -0.29 % (2b 0w / 4) | 4 better, 0 worse of 18 |
| C against S: iba_cw_b                 | iba_wb    | -0.29 % (1b 0w / 7) | -0.06 % (1b 0w / 3) | +0.20 % (0b 0w / 4) | -0.27 % (0b 0w / 4) | 2 better, 0 worse of 18 |
| F against S: iba_fw_b                 | iba_wb    | -0.27 % (1b 0w / 7) | -0.00 % (0b 0w / 3) | +0.12 % (0b 0w / 4) | -0.27 % (1b 0w / 4) | 2 better, 0 worse of 18 |
| C against S: iba_cna_b                | iba_sna_b | -0.06 % (1b 1w / 7) | +0.01 % (0b 0w / 3) | -0.05 % (0b 0w / 4) | -0.06 % (0b 0w / 4) | 1 better, 1 worse of 18 |
| F against S: iba_fna_b                | iba_sna_b | -0.08 % (1b 1w / 7) | -0.00 % (0b 0w / 3) | -0.02 % (0b 0w / 4) | -0.08 % (0b 0w / 4) | 1 better, 1 worse of 18 |
| C against S: iba_cnw_b                | iba_snw_b | -0.14 % (1b 0w / 7) | -0.07 % (0b 0w / 3) | +0.28 % (1b 0w / 4) | -0.16 % (2b 0w / 4) | 4 better, 0 worse of 18 |
| F against S: iba_fnw_b                | iba_snw_b | -0.17 % (1b 0w / 7) | -0.10 % (1b 0w / 3) | +0.26 % (1b 0w / 4) | -0.16 % (2b 0w / 4) | 5 better, 0 worse of 18 |
| noise-aware against greedy: iba_sna_b | iba_b     | -0.06 % (0b 0w / 7) | +0.10 % (0b 0w / 3) | +0.15 % (0b 0w / 4) | -0.17 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| noise-aware against greedy: iba_snw_b | iba_wb    | -0.50 % (2b 0w / 7) | +1.15 % (0b 2w / 3) | +0.16 % (0b 0w / 4) | -0.11 % (0b 0w / 4) | 2 better, 2 worse of 18 |
| spread against anchored: iba_wb       | iba_b     | -0.24 % (0b 0w / 7) | +0.57 % (0b 0w / 3) | +0.30 % (0b 0w / 4) | -0.37 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| spread against anchored: iba_snw_b    | iba_sna_b | -0.69 % (0b 0w / 7) | +1.63 % (0b 1w / 3) | +0.31 % (0b 0w / 4) | -0.31 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| noise-aware against greedy: iba_cna_b | iba_ca_b  | -0.03 % (0b 0w / 7) | +0.09 % (0b 0w / 3) | -0.06 % (0b 0w / 4) | +0.03 % (0b 0w / 4) | 0 better, 0 worse of 18 |
| noise-aware against greedy: iba_cnw_b | iba_cw_b  | -0.35 % (1b 0w / 7) | +1.14 % (0b 2w / 3) | +0.23 % (0b 0w / 4) | -0.00 % (1b 0w / 4) | 2 better, 2 worse of 18 |
| spread against anchored: iba_cw_b     | iba_ca_b  | -0.45 % (0b 0w / 7) | +0.49 % (0b 0w / 3) | +0.35 % (0b 0w / 4) | -0.37 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| spread against anchored: iba_cnw_b    | iba_cna_b | -0.77 % (0b 0w / 7) | +1.55 % (0b 1w / 3) | +0.65 % (0b 0w / 4) | -0.41 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| noise-aware against greedy: iba_fna_b | iba_fa_b  | -0.02 % (0b 0w / 7) | +0.08 % (0b 0w / 3) | -0.01 % (0b 1w / 4) | +0.04 % (0b 0w / 4) | 0 better, 1 worse of 18 |
| noise-aware against greedy: iba_fnw_b | iba_fw_b  | -0.40 % (1b 0w / 7) | +1.05 % (0b 2w / 3) | +0.30 % (0b 0w / 4) | +0.01 % (1b 0w / 4) | 2 better, 2 worse of 18 |
| spread against anchored: iba_fw_b     | iba_fa_b  | -0.39 % (0b 0w / 7) | +0.54 % (0b 0w / 3) | +0.28 % (0b 0w / 4) | -0.35 % (1b 0w / 4) | 1 better, 0 worse of 18 |
| spread against anchored: iba_fnw_b    | iba_fna_b | -0.77 % (0b 0w / 7) | +1.53 % (0b 1w / 3) | +0.60 % (0b 0w / 4) | -0.38 % (0b 0w / 4) | 0 better, 1 worse of 18 |

Averaged over the contrasts of each factor:

| factor                     | return   | logrv   | tail_loss   | tail_gain   | tasks better / worse   |
|:---------------------------|:---------|:--------|:------------|:------------|:-----------------------|
| C against S                | -0.14 %  | -0.03 % | +0.15 %     | -0.19 %     | 10 / 1 of 72           |
| F against S                | -0.16 %  | -0.02 % | +0.12 %     | -0.20 %     | 12 / 1 of 72           |
| noise-aware against greedy | -0.23 %  | +0.60 % | +0.13 %     | -0.03 %     | 7 / 7 of 108           |
| spread against anchored    | -0.55 %  | +1.05 % | +0.41 %     | -0.36 %     | 3 / 3 of 108           |

## 4. SPA: does any of the 32 new configurations beat the benchmark? (consistent p-value; tasks with p < 0.05)

| benchmark   | kind      |   tasks |   significant |   median_p |
|:------------|:----------|--------:|--------------:|-----------:|
| REF         | logrv     |       3 |             2 |     0      |
| REF         | return    |       7 |             0 |     0.9245 |
| REF         | tail_gain |       4 |             1 |     0.5237 |
| REF         | tail_loss |       4 |             0 |     0.4235 |
| gpca|lin    | logrv     |       3 |             0 |     0.541  |
| gpca|lin    | return    |       7 |             0 |     0.347  |
| gpca|lin    | tail_gain |       4 |             1 |     0.456  |
| gpca|lin    | tail_loss |       4 |             1 |     0.1737 |
| iba_b       | logrv     |       3 |             0 |     0.904  |
| iba_b       | return    |       7 |             0 |     0.4515 |
| iba_b       | tail_gain |       4 |             0 |     0.1848 |
| iba_b       | tail_loss |       4 |             0 |     0.8375 |
| iba_e1|lin  | logrv     |       3 |             1 |     0.566  |
| iba_e1|lin  | return    |       7 |             0 |     0.248  |
| iba_e1|lin  | tail_gain |       4 |             1 |     0.3808 |
| iba_e1|lin  | tail_loss |       4 |             0 |     0.4162 |
| iba_wb      | logrv     |       3 |             0 |     0.5115 |
| iba_wb      | return    |       7 |             1 |     0.5135 |
| iba_wb      | tail_gain |       4 |             0 |     0.3355 |
| iba_wb      | tail_loss |       4 |             0 |     0.6255 |

New configuration with the lowest pooled loss per task:

| kind      |   iba_ca_b |   iba_cna_b |   iba_cnw_b |   iba_cw_b |   iba_fa_b |   iba_fnw_b |   iba_fnw_r|lin |   iba_fw_b |   iba_rndw |   iba_snw|lin |
|:----------|-----------:|------------:|------------:|-----------:|-----------:|------------:|----------------:|-----------:|-----------:|--------------:|
| logrv     |          1 |           0 |           0 |          1 |          1 |           0 |               0 |          0 |          0 |             0 |
| return    |          0 |           0 |           2 |          0 |          0 |           1 |               0 |          0 |          4 |             0 |
| tail_gain |          0 |           0 |           1 |          2 |          0 |           0 |               0 |          1 |          0 |             0 |
| tail_loss |          0 |           1 |           0 |          0 |          0 |           0 |               1 |          1 |          0 |             1 |

Seed spread of the ensembles (standard deviation over the three seeds of the pooled loss, relative to the loss):

| config    |   logrv |   return |   tail_gain |   tail_loss |
|:----------|--------:|---------:|------------:|------------:|
| iba_b     |  0.0004 |   0.0008 |      0.0008 |      0.0014 |
| iba_ca_b  |  0.0009 |   0.0009 |      0.0007 |      0.0026 |
| iba_cna_b |  0.0002 |   0.0008 |      0.0008 |      0.0017 |
| iba_cnw_b |  0.0015 |   0.0017 |      0.0008 |      0.0017 |
| iba_cw_b  |  0.0008 |   0.002  |      0.0018 |      0.0018 |
| iba_fa_b  |  0.0011 |   0.0011 |      0.0007 |      0.0028 |
| iba_fna_b |  0.001  |   0.0008 |      0.0008 |      0.0017 |
| iba_fnw_b |  0.002  |   0.0016 |      0.0009 |      0.002  |
| iba_fw_b  |  0.0018 |   0.002  |      0.0019 |      0.0019 |
| iba_rnda  |  0.0007 |   0.0005 |      0.0003 |      0.0012 |
| iba_rndw  |  0.0036 |   0.0011 |      0.0008 |      0.0015 |
| iba_sna_b |  0.0003 |   0.0007 |      0.0005 |      0.0009 |
| iba_snw_b |  0.0008 |   0.0014 |      0.0008 |      0.0012 |
| iba_wb    |  0.0004 |   0.0015 |      0.001  |      0.0017 |

## 5. Decision rule (spec section 6)

A candidate qualifies if it is significantly better than its incumbent in more tasks than it is significantly worse AND its mean loss is lower in at least 3 of the 4 target types.

| candidate                        | config      | incumbent   |   tasks better |   tasks worse | types with lower mean loss   |   mean rel. diff % (types equally weighted) | qualifies   |
|:---------------------------------|:------------|:------------|---------------:|--------------:|:-----------------------------|--------------------------------------------:|:------------|
| S noise-aware anchored, tested   | iba_sna|lin | iba_e1|lin  |              0 |             4 | 0/4                          |                                       0.3   | False       |
| S noise-aware spread, tested     | iba_snw|lin | iba_e1|lin  |              0 |             7 | 0/4                          |                                       0.547 | False       |
| C greedy anchored, tested        | iba_ca|lin  | iba_e1|lin  |              1 |             2 | 0/4                          |                                       0.188 | False       |
| C greedy spread, tested          | iba_cw|lin  | iba_e1|lin  |              0 |             2 | 1/4                          |                                       0.104 | False       |
| C noise-aware anchored, tested   | iba_cna|lin | iba_e1|lin  |              1 |             3 | 0/4                          |                                       0.145 | False       |
| C noise-aware spread, tested     | iba_cnw|lin | iba_e1|lin  |              0 |             3 | 1/4                          |                                       0.158 | False       |
| F greedy anchored, tested        | iba_fa|lin  | iba_e1|lin  |              1 |             2 | 0/4                          |                                       0.135 | False       |
| F greedy spread, tested          | iba_fw|lin  | iba_e1|lin  |              0 |             1 | 0/4                          |                                       0.167 | False       |
| F noise-aware anchored, tested   | iba_fna|lin | iba_e1|lin  |              1 |             2 | 0/4                          |                                       0.11  | False       |
| F noise-aware spread, tested     | iba_fnw|lin | iba_e1|lin  |              0 |             1 | 1/4                          |                                       0.184 | False       |
| S noise-aware anchored, ensemble | iba_sna_b   | iba_b       |              1 |             0 | 2/4                          |                                       0.004 | False       |
| S noise-aware spread, ensemble   | iba_snw_b   | iba_b       |              0 |             2 | 2/4                          |                                       0.243 | False       |
| C greedy anchored, ensemble      | iba_ca_b    | iba_b       |              3 |             0 | 2/4                          |                                      -0.044 | False       |
| C greedy spread, ensemble        | iba_cw_b    | iba_b       |              1 |             0 | 2/4                          |                                      -0.037 | False       |
| C noise-aware anchored, ensemble | iba_cna_b   | iba_b       |              3 |             1 | 2/4                          |                                      -0.037 | False       |
| C noise-aware spread, ensemble   | iba_cnw_b   | iba_b       |              2 |             2 | 2/4                          |                                       0.22  | False       |
| F greedy anchored, ensemble      | iba_fa_b    | iba_b       |              4 |             0 | 2/4                          |                                      -0.062 | False       |
| F greedy spread, ensemble        | iba_fw_b    | iba_b       |              1 |             0 | 2/4                          |                                      -0.041 | False       |
| F noise-aware anchored, ensemble | iba_fna_b   | iba_b       |              4 |             1 | 2/4                          |                                      -0.041 | False       |
| F noise-aware spread, ensemble   | iba_fnw_b   | iba_b       |              2 |             1 | 2/4                          |                                       0.203 | False       |
| control a, ensemble              | iba_rnda    | iba_b       |              3 |             3 | 2/4                          |                                       0.114 | False       |
| control w, ensemble              | iba_rndw    | iba_b       |              1 |             2 | 2/4                          |                                       0.295 | False       |

Qualifying: none; E1 and the ensembles of the earlier specs stay.
