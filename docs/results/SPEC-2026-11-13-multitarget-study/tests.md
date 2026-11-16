# Tests for SPEC-2026-11-13-multitarget-study (section 8; written after the map was seen, see docs/DEVIATIONS.md)

## Paired date-block-bootstrap tests per task (all development series of the frequency pooled; 95 % interval)

Relative difference in the primary loss, a minus b (negative = a better). REF = historical mean / HAR / base rate.

| a          | b          | kind      |   tasks |   a_better |   ns |   a_worse |   mean_rel_diff |
|:-----------|:-----------|:----------|--------:|-----------:|-----:|----------:|----------------:|
| iba_e1|lin | gpca|lin   | return    |       7 |          0 |    7 |         0 |         -0.0003 |
| iba_a|lin  | iba_e1|lin | return    |       7 |          0 |    4 |         3 |          0.0042 |
| iba_d|lin  | iba_a|lin  | return    |       7 |          1 |    6 |         0 |         -0.0007 |
| iba_b      | iba_a|lin  | return    |       7 |          2 |    5 |         0 |         -0.005  |
| iba_b      | iba_e1|lin | return    |       7 |          1 |    5 |         1 |         -0.0007 |
| iba_b      | gpca|lin   | return    |       7 |          0 |    7 |         0 |         -0.0011 |
| iba_c      | iba_e1|lin | return    |       7 |          0 |    6 |         1 |          0.0019 |
| iba_x|lin  | iba_e1|lin | return    |       7 |          0 |    2 |         5 |          0.0831 |
| iba_e1|lin | REF        | return    |       7 |          0 |    7 |         0 |          0.0139 |
| iba_b      | REF        | return    |       7 |          0 |    7 |         0 |          0.0132 |
| gpca|lin   | REF        | return    |       7 |          0 |    6 |         1 |          0.0143 |
| iba_e1|lin | gpca|lin   | tail_gain |      12 |          0 |   11 |         1 |          0.0023 |
| iba_a|lin  | iba_e1|lin | tail_gain |      12 |          0 |    6 |         6 |          0.022  |
| iba_d|lin  | iba_a|lin  | tail_gain |      12 |          1 |   11 |         0 |         -0.0041 |
| iba_b      | iba_a|lin  | tail_gain |      12 |         10 |    2 |         0 |         -0.0203 |
| iba_b      | iba_e1|lin | tail_gain |      12 |          3 |    9 |         0 |          0.0009 |
| iba_b      | gpca|lin   | tail_gain |      12 |          0 |   12 |         0 |          0.0032 |
| iba_c      | iba_e1|lin | tail_gain |      12 |          0 |    9 |         3 |          0.0083 |
| iba_x|lin  | iba_e1|lin | tail_gain |      12 |          0 |    0 |        12 |          0.0972 |
| iba_e1|lin | REF        | tail_gain |      12 |          0 |    9 |         3 |          0.0034 |
| iba_b      | REF        | tail_gain |      12 |          0 |    9 |         3 |          0.0044 |
| gpca|lin   | REF        | tail_gain |      12 |          2 |    8 |         2 |          0.0011 |
| iba_e1|lin | gpca|lin   | tail_loss |      12 |          0 |   12 |         0 |         -0.0055 |
| iba_a|lin  | iba_e1|lin | tail_loss |      12 |          0 |    9 |         3 |          0.0108 |
| iba_d|lin  | iba_a|lin  | tail_loss |      12 |          0 |   10 |         2 |          0.0069 |
| iba_b      | iba_a|lin  | tail_loss |      12 |          7 |    5 |         0 |         -0.0169 |
| iba_b      | iba_e1|lin | tail_loss |      12 |          4 |    8 |         0 |         -0.0065 |
| iba_b      | gpca|lin   | tail_loss |      12 |          1 |   11 |         0 |         -0.0121 |
| iba_c      | iba_e1|lin | tail_loss |      12 |          0 |   10 |         2 |          0.0074 |
| iba_x|lin  | iba_e1|lin | tail_loss |      12 |          0 |    1 |        11 |          0.1265 |
| iba_e1|lin | REF        | tail_loss |      12 |          0 |   10 |         2 |          0.0044 |
| iba_b      | REF        | tail_loss |      12 |          0 |   11 |         1 |         -0.0023 |
| gpca|lin   | REF        | tail_loss |      12 |          0 |    6 |         6 |          0.0099 |
| iba_e1|lin | gpca|lin   | logrv     |       3 |          0 |    3 |         0 |         -0.0036 |
| iba_a|lin  | iba_e1|lin | logrv     |       3 |          0 |    3 |         0 |          0.002  |
| iba_d|lin  | iba_a|lin  | logrv     |       3 |          0 |    3 |         0 |          0.0005 |
| iba_b      | iba_a|lin  | logrv     |       3 |          2 |    1 |         0 |         -0.0055 |
| iba_b      | iba_e1|lin | logrv     |       3 |          2 |    1 |         0 |         -0.0035 |
| iba_b      | gpca|lin   | logrv     |       3 |          0 |    3 |         0 |         -0.0071 |
| iba_c      | iba_e1|lin | logrv     |       3 |          0 |    1 |         2 |          0.0243 |
| iba_x|lin  | iba_e1|lin | logrv     |       3 |          0 |    0 |         3 |          0.0615 |
| iba_e1|lin | REF        | logrv     |       3 |          2 |    1 |         0 |         -0.0529 |
| iba_b      | REF        | logrv     |       3 |          2 |    1 |         0 |         -0.0562 |
| gpca|lin   | REF        | logrv     |       3 |          2 |    1 |         0 |         -0.0492 |

## SPA: does any of the 12 IBA variants beat the benchmark? (consistent p-value; tasks with p < 0.05)

| benchmark   | kind      |   tasks |   significant |   median_p |
|:------------|:----------|--------:|--------------:|-----------:|
| REF         | logrv     |       3 |             2 |     0.001  |
| REF         | return    |       7 |             0 |     0.9215 |
| REF         | tail_gain |      12 |             0 |     0.7275 |
| REF         | tail_loss |      12 |             0 |     0.569  |
| gpca|lin    | logrv     |       3 |             0 |     0.2765 |
| gpca|lin    | return    |       7 |             0 |     0.6965 |
| gpca|lin    | tail_gain |      12 |             0 |     0.8128 |
| gpca|lin    | tail_loss |      12 |             0 |     0.301  |

Variant with the lowest pooled loss per task:

| kind      |   iba_a|lin |   iba_b |   iba_c |   iba_d|lin |   iba_e1|lin |   iba_xlo|lin |
|:----------|------------:|--------:|--------:|------------:|-------------:|--------------:|
| logrv     |           0 |       3 |       0 |           0 |            0 |             0 |
| return    |           0 |       2 |       3 |           1 |            1 |             0 |
| tail_gain |           0 |       4 |       4 |           0 |            3 |             1 |
| tail_loss |           1 |       8 |       2 |           0 |            1 |             0 |

## Diebold–Mariano per series (descriptive; HAC lag h − 1, HLN; Holm inside target type and comparison)

| a          | b        | kind      |   cells |   a_better_5pct |   a_worse_5pct |   a_better_holm |   a_worse_holm |
|:-----------|:---------|:----------|--------:|----------------:|---------------:|----------------:|---------------:|
| iba_e1|lin | REF      | return    |     155 |               0 |              5 |               0 |              0 |
| iba_b      | REF      | return    |     155 |               0 |              3 |               0 |              0 |
| gpca|lin   | REF      | return    |     155 |               0 |              5 |               0 |              1 |
| iba_e1|lin | gpca|lin | return    |     155 |               0 |              2 |               0 |              0 |
| iba_b      | gpca|lin | return    |     155 |               1 |              2 |               0 |              1 |
| iba_e1|lin | REF      | tail_gain |     288 |               6 |              7 |               0 |              0 |
| iba_b      | REF      | tail_gain |     288 |               4 |              6 |               0 |              0 |
| gpca|lin   | REF      | tail_gain |     288 |              11 |              8 |               0 |              0 |
| iba_e1|lin | gpca|lin | tail_gain |     288 |               2 |             17 |               0 |              0 |
| iba_b      | gpca|lin | tail_gain |     288 |               2 |             10 |               0 |              0 |
| iba_e1|lin | REF      | tail_loss |     288 |               1 |              3 |               0 |              0 |
| iba_b      | REF      | tail_loss |     288 |               2 |              4 |               0 |              0 |
| gpca|lin   | REF      | tail_loss |     288 |               1 |              5 |               0 |              0 |
| iba_e1|lin | gpca|lin | tail_loss |     288 |              10 |              2 |               0 |              0 |
| iba_b      | gpca|lin | tail_loss |     288 |              15 |              3 |               0 |              0 |
| iba_e1|lin | REF      | logrv     |     111 |              37 |              0 |              13 |              0 |
| iba_b      | REF      | logrv     |     111 |              37 |              0 |              15 |              0 |
| gpca|lin   | REF      | logrv     |     111 |              30 |              0 |              12 |              0 |
| iba_e1|lin | gpca|lin | logrv     |     111 |               1 |              0 |               0 |              0 |
| iba_b      | gpca|lin | logrv     |     111 |               6 |              0 |               0 |              0 |

## Clark–West against the historical mean, return cells (descriptive, one-sided; seeded methods: first seed)

| model      |   cells |   p_below_5pct |   holm_below_5pct |   median_p |
|:-----------|--------:|---------------:|------------------:|-----------:|
| gpca|lin   |     155 |              2 |                 0 |      0.67  |
| iba_e1|lin |     155 |              2 |                 0 |      0.519 |
| iba_a|lin  |     155 |              5 |                 0 |      0.432 |
| iba_b      |     155 |              5 |                 0 |      0.482 |
| iba_c      |     155 |             12 |                 0 |      0.535 |

## Walk-throughs: per target type the unit where iba_e1|lin is most and least favourable against the best benchmark

### return, most favourable: weekly return_h13, equity_emerging (5 series)

Best benchmark gpca|lin, skill against the reference +0.0122.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin |  0.019  | 1/10   |             -0.0069 | [-0.0387, +0.0203] | -0.067  +0.006  +0.003  +0.029            |                   |
| iba_a|lin  |  0.0121 | 2/10   |              0.0001 | [-0.0274, +0.0255] | -0.041  +0.007  +0.021  +0.020            | 28%               |
| iba_b      |  0.0212 | 1/10   |             -0.0091 | [-0.0407, +0.0208] | -0.073  -0.001  +0.004  +0.031            |                   |
| iba_c      | -0.0047 | 4/10   |              0.0172 | [-0.0477, +0.0865] | -0.058  -0.008  +0.027  +0.089            | 12%               |

### return, least favourable: weekly return_h4, equity_us_sectors (5 series)

Best benchmark bench|mean, skill against the reference +0.0000.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin | -0.0122 | 3/10   |              0.0122 | [+0.0050, +0.0204] | +0.015  -0.001  +0.012  +0.027            |                   |
| iba_a|lin  | -0.0095 | 3/10   |              0.0095 | [-0.0069, +0.0245] | +0.004  -0.004  +0.032  +0.027            | 22%               |
| iba_b      | -0.0115 | 3/10   |              0.0115 | [+0.0041, +0.0201] | +0.013  -0.000  +0.009  +0.030            |                   |
| iba_c      | -0.0033 | 2/10   |              0.0033 | [-0.0013, +0.0078] | +0.003  +0.001  +0.008  +0.003            | 12%               |

### logrv, most favourable: weekly logrv_h4, credit_em_debt (2 series)

Best benchmark gpca|lin, skill against the reference +0.0841.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin |  0.0997 | 1/12   |             -0.0171 | [-0.0443, +0.0094] | -0.008  -0.031  -0.003  -0.028            |                   |
| iba_a|lin  |  0.0935 | 1/12   |             -0.0103 | [-0.0375, +0.0161] | +0.007  -0.031  -0.003  -0.028            | 4%                |
| iba_b      |  0.1058 | 1/12   |             -0.0237 | [-0.0501, +0.0023] | -0.017  -0.042  -0.008  -0.028            |                   |
| iba_c      |  0.0512 | 6/12   |              0.0359 | [-0.0059, +0.0813] | +0.031  +0.011  +0.068  +0.052            | 29%               |

### logrv, least favourable: weekly logrv_h1, equity_us_broad (3 series)

Best benchmark lasso|lin, skill against the reference +0.1680.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin |  0.1437 | 7/12   |              0.0292 | [-0.0085, +0.0670] | +0.022  +0.050  +0.015  +0.031            |                   |
| iba_a|lin  |  0.146  | 6/12   |              0.0265 | [-0.0077, +0.0602] | +0.016  +0.047  +0.015  +0.031            | 25%               |
| iba_b      |  0.1521 | 4/12   |              0.0191 | [-0.0158, +0.0542] | +0.020  +0.041  -0.000  +0.015            |                   |
| iba_c      |  0.0963 | 9/12   |              0.0862 | [+0.0389, +0.1323] | +0.100  +0.095  +0.056  +0.089            | 36%               |

### tail_loss, most favourable: weekly tail_loss_q05_h13, real_estate (1 series)

Best benchmark bench|base, skill against the reference +0.0000.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin |  0.0032 | 1/11   |             -0.0032 | [-0.0090, +0.0024] | +0.002  -0.005  -0.003  -0.159            |                   |
| iba_a|lin  |  0.0032 | 1/11   |             -0.0032 | [-0.0090, +0.0024] | +0.002  -0.005  -0.003  -0.159            | 0%                |
| iba_b      |  0.0029 | 1/11   |             -0.0029 | [-0.0086, +0.0028] | +0.002  -0.005  -0.003  -0.122            |                   |
| iba_c      |  0.0005 | 1/11   |             -0.0005 | [-0.0465, +0.0458] | +0.039  -0.057  -0.004  -0.058            | 42%               |

### tail_loss, least favourable: weekly tail_loss_q05_h13, commodities (8 series)

Best benchmark bench|base, skill against the reference +0.0000.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin | -0.094  | 6/11   |              0.094  | [+0.0302, +0.1752] | +0.116  +0.025  +0.164  +0.007            |                   |
| iba_a|lin  | -0.1027 | 6/11   |              0.1027 | [+0.0369, +0.1874] | +0.116  +0.033  +0.189  +0.020            | 17%               |
| iba_b      | -0.0803 | 5/11   |              0.0803 | [+0.0243, +0.1528] | +0.105  +0.023  +0.126  +0.004            |                   |
| iba_c      | -0.0724 | 4/11   |              0.0724 | [+0.0210, +0.1403] | +0.124  +0.063  +0.007  +0.009            | 21%               |

### tail_gain, most favourable: weekly tail_gain_q05_h13, real_estate (1 series)

Best benchmark bench|base, skill against the reference +0.0000.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin |  0.0004 | 1/11   |             -0.0004 | [-0.0016, +0.0007] | -0.001  +0.002  -0.001  +0.011            |                   |
| iba_a|lin  | -0.0221 | 7/11   |              0.0221 | [+0.0023, +0.0476] | -0.001  +0.170  -0.001  +0.011            | 17%               |
| iba_b      | -0.0002 | 2/11   |              0.0002 | [-0.0096, +0.0094] | -0.003  +0.004  -0.005  +0.194            |                   |
| iba_c      |  0.0036 | 1/11   |             -0.0036 | [-0.0284, +0.0188] | -0.031  +0.060  -0.014  +0.317            | 25%               |

### tail_gain, least favourable: weekly tail_gain_q20_h4, equity_us_sectors (5 series)

Best benchmark bench|garch_prob, skill against the reference +0.0540.

| config     |   skill | rank   |   rel. diff to best | 95 % interval      | per block (rel. loss vs best benchmark)   | search accepted   |
|:-----------|--------:|:-------|--------------------:|:-------------------|:------------------------------------------|:------------------|
| iba_e1|lin |  0.0044 | 9/11   |              0.0524 | [+0.0211, +0.0904] | +0.119  +0.047  +0.006  +0.035            |                   |
| iba_a|lin  |  0.008  | 8/11   |              0.0486 | [+0.0197, +0.0817] | +0.100  +0.047  +0.006  +0.038            | 18%               |
| iba_b      |  0.0082 | 8/11   |              0.0483 | [+0.0196, +0.0832] | +0.109  +0.047  +0.005  +0.030            |                   |
| iba_c      |  0.0154 | 6/11   |              0.0408 | [+0.0124, +0.0769] | +0.112  +0.040  -0.007  +0.014            | 20%               |

## Registry

27757 rows for this spec in `registry/trials.jsonl`:

|   stage | split       | fingerprint              |   rows |
|--------:|:------------|:-------------------------|-------:|
|       1 | development | 2bcaa0ad64aaa3ab35c5455d |  14270 |
|       2 | development | 2bcaa0ad64aaa3ab35c5455d |  13472 |
|       3 | development | 2bcaa0ad64aaa3ab35c5455d |     15 |
