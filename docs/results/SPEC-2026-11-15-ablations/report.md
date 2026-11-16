# SPEC-2026-11-15-ablations: component contribution analysis (development series)

Each row changes one component of the interpretable reading (consensus formulas, linear model) and compares it with the unchanged method. Cell: mean relative difference in the primary loss, variant minus unchanged (positive = the change hurts, so the component contributes); tasks where the 95 % date-block-bootstrap interval excludes zero (b = variant better, w = variant worse).

### weekly: removing one group's formula

| a                                         | against      | return              | logrv               | tail_loss           | tail_gain           | all tasks               |
|:------------------------------------------|:-------------|:--------------------|:--------------------|:--------------------|:--------------------|:------------------------|
| without group: equity factors             | abl_base|lin | +0.11 % (0b 1w / 3) | +0.37 % (0b 0w / 3) | +0.03 % (0b 0w / 2) | -0.09 % (0b 0w / 2) | 0 better, 1 worse of 10 |
| without group: credit                     | abl_base|lin | +0.05 % (0b 0w / 3) | +0.97 % (0b 2w / 3) | -0.01 % (0b 0w / 2) | -0.08 % (0b 0w / 2) | 0 better, 2 worse of 10 |
| without group: commodities                | abl_base|lin | +0.03 % (0b 0w / 3) | -0.10 % (0b 0w / 3) | +0.04 % (0b 0w / 2) | -0.06 % (0b 0w / 2) | 0 better, 0 worse of 10 |
| without group: own behaviour              | abl_base|lin | +0.05 % (0b 1w / 3) | +1.89 % (0b 3w / 3) | +0.02 % (0b 0w / 2) | -0.00 % (0b 0w / 2) | 0 better, 4 worse of 10 |
| without group: currencies                 | abl_base|lin | +0.01 % (0b 0w / 3) | -0.15 % (0b 0w / 3) | -0.09 % (0b 0w / 2) | -0.03 % (0b 0w / 2) | 0 better, 0 worse of 10 |
| without group: interest rates             | abl_base|lin | -0.03 % (0b 0w / 3) | -0.10 % (0b 0w / 3) | -0.08 % (0b 0w / 2) | -0.10 % (0b 0w / 2) | 0 better, 0 worse of 10 |
| without group: macro-financial conditions | abl_base|lin | -0.49 % (0b 0w / 3) | -0.37 % (2b 0w / 3) | -0.16 % (0b 0w / 2) | -0.04 % (1b 0w / 2) | 3 better, 0 worse of 10 |
| without group: styles                     | abl_base|lin | -0.08 % (0b 0w / 3) | +0.11 % (0b 0w / 3) | +0.04 % (0b 0w / 2) | -0.07 % (0b 0w / 2) | 0 better, 0 worse of 10 |
| without group: volatility                 | abl_base|lin | -0.08 % (0b 0w / 3) | +0.91 % (0b 0w / 3) | -0.10 % (0b 0w / 2) | +0.78 % (0b 1w / 2) | 0 better, 1 worse of 10 |

### weekly: formula order, predicate scaling, HAR stage

| a                                            | against      | return              | logrv                | tail_loss           | tail_gain           | all tasks               |
|:---------------------------------------------|:-------------|:--------------------|:---------------------|:--------------------|:--------------------|:------------------------|
| empirical-distribution scaling of predicates | abl_base|lin | -0.27 % (0b 0w / 3) | +1.30 % (0b 0w / 3)  | +0.07 % (0b 0w / 2) | +0.05 % (0b 0w / 2) | 0 better, 0 worse of 10 |
| no HAR first stage (volatility)              | abl_base|lin |                     | +27.52 % (0b 2w / 3) |                     |                     | 0 better, 2 worse of 3  |
| one literal per group                        | abl_base|lin | +0.02 % (0b 0w / 3) | +0.38 % (0b 0w / 3)  | +0.07 % (0b 0w / 2) | +0.15 % (0b 0w / 2) | 0 better, 0 worse of 10 |
| unchanged method against the reference       | REF          | +1.03 % (0b 0w / 3) | -5.85 % (3b 0w / 3)  | +0.80 % (0b 1w / 2) | -1.07 % (0b 0w / 2) | 3 better, 1 worse of 10 |

### monthly: removing one group's formula

| a                                         | against      | return              | logrv   | tail_loss           | tail_gain           | all tasks              |
|:------------------------------------------|:-------------|:--------------------|:--------|:--------------------|:--------------------|:-----------------------|
| without group: equity factors             | abl_base|lin | +0.15 % (0b 0w / 4) |         | +0.42 % (0b 0w / 2) | -0.05 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| without group: credit                     | abl_base|lin | -0.09 % (0b 0w / 4) |         | +0.26 % (0b 0w / 2) | +0.06 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| without group: commodities                | abl_base|lin | -0.03 % (0b 0w / 4) |         | -0.28 % (1b 0w / 2) | -0.16 % (0b 0w / 2) | 1 better, 0 worse of 8 |
| without group: own behaviour              | abl_base|lin | -0.22 % (0b 0w / 4) |         | -0.24 % (0b 0w / 2) | +0.19 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| without group: currencies                 | abl_base|lin | -0.15 % (1b 0w / 4) |         | +0.35 % (0b 0w / 2) | -0.12 % (0b 0w / 2) | 1 better, 0 worse of 8 |
| without group: interest rates             | abl_base|lin | -0.48 % (0b 0w / 4) |         | +1.45 % (0b 0w / 2) | -0.06 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| without group: macro-financial conditions | abl_base|lin | -1.15 % (0b 0w / 4) |         | +0.91 % (0b 0w / 2) | -0.11 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| without group: styles                     | abl_base|lin | -0.23 % (0b 0w / 4) |         | +0.39 % (0b 0w / 2) | +0.18 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| without group: trend-following            | abl_base|lin | +0.02 % (0b 0w / 4) |         | +0.70 % (0b 0w / 2) | +0.06 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| without group: volatility                 | abl_base|lin | -0.79 % (0b 0w / 4) |         | -0.10 % (0b 0w / 2) | +0.04 % (0b 0w / 2) | 0 better, 0 worse of 8 |

### monthly: formula order, predicate scaling, HAR stage

| a                                            | against      | return              | logrv   | tail_loss           | tail_gain           | all tasks              |
|:---------------------------------------------|:-------------|:--------------------|:--------|:--------------------|:--------------------|:-----------------------|
| empirical-distribution scaling of predicates | abl_base|lin | -0.42 % (0b 0w / 4) |         | +1.40 % (0b 0w / 2) | +0.70 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| one literal per group                        | abl_base|lin | +0.20 % (0b 0w / 4) |         | -0.73 % (0b 0w / 2) | +0.50 % (0b 0w / 2) | 0 better, 0 worse of 8 |
| unchanged method against the reference       | REF          | +2.95 % (0b 1w / 4) |         | +0.08 % (0b 0w / 2) | +0.87 % (0b 1w / 2) | 0 better, 2 worse of 8 |
