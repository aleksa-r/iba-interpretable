# SPEC-2026-11-14-abc-v2: ABC over the whole space, development series

Configurations: `iba_<s>|lin` the winner of search s if it passed the acceptance test, else the prior; `iba_<s>r|lin` the winner without the test; `iba_<s>b` the final colony as an ensemble. Searches: W  discrete moves, whole space, spread start; V  vector moves, crisp formulas; G  vector moves, graded formulas, spread start; Z  graded formulas, zero start. A, B, E1, group PCA and the references are the first study's forecasts for the same cells.

## 1. What the searches do (units = cell x block, seeds averaged; gains relative to the prior)

inner_gain: fitness folds. outer_gain: the WHOLE outer fold (as in the first study; most of its rows are also validation rows of the last fitness fold). clean_gain: the outer rows the search has not used, the basis of this spec's acceptance test. All for the winner before the test. ac = the first study's ABC (same search); accepted_whole_fold = its acceptance rate under the first study's test.

| kind      | search   |   inner_gain |   outer_gain |   clean_gain |   accepted |   accepted_whole_fold |   literals |   groups |    empty |   colony_distinct |   colony_literals |   clean_rows |   n_evals |
|:----------|:---------|-------------:|-------------:|-------------:|-----------:|----------------------:|-----------:|---------:|---------:|------------------:|------------------:|-------------:|----------:|
| return    | ac       |       0.1496 |       0.009  |      -0.0482 |     0.1188 |                0.243  |    16.8419 | nan      | nan      |          nan      |          nan      |      26.8161 |      2000 |
| return    | w        |       0.2202 |       0.0131 |      -0.0603 |     0.0758 |              nan      |    12.1935 |   6.3747 |   0      |           19.9995 |            9.0538 |      26.8161 |      2000 |
| return    | v        |       0.2614 |       0.0032 |      -0.0995 |     0.0624 |              nan      |    19.4817 |   8.3204 |   0      |           19.0328 |           19.0602 |      26.8161 |      2000 |
| return    | g        |       0.359  |       0.0117 |      -0.1497 |     0.0677 |              nan      |    27.6864 |   9.2457 |   0      |           20      |           28.4299 |      26.8161 |      2000 |
| return    | z        |       0.3076 |       0.0087 |      -0.1087 |     0.0661 |              nan      |    13.2697 |   8.9161 |   0.0011 |           20      |           12.6813 |      26.8161 |      2000 |
| logrv     | ac       |       0.0826 |      -0.013  |      -0.035  |     0.0863 |                0.1629 |    16.247  | nan      | nan      |          nan      |          nan      |      34.75   |      2000 |
| logrv     | w        |       0.1157 |      -0.029  |      -0.0739 |     0.0863 |              nan      |    12.5353 |   6.8378 |   0      |           20      |            9.9592 |      34.75   |      2000 |
| logrv     | v        |       0.1375 |      -0.0331 |      -0.0907 |     0.0713 |              nan      |    17.8131 |   8.211  |   0      |           18.6141 |           18.0523 |      34.75   |      2000 |
| logrv     | g        |       0.1918 |      -0.0252 |      -0.1002 |     0.0608 |              nan      |    21.4721 |   8.9722 |   0      |           20      |           22.4433 |      34.75   |      2000 |
| logrv     | z        |       0.1894 |      -0.0324 |      -0.1058 |     0.0533 |              nan      |    14.668  |   8.9234 |   0      |           20      |           14.4538 |      34.75   |      2000 |
| tail_loss | ac       |       0.1666 |      -0.0288 |      -0.0801 |     0.138  |                0.197  |    16.8351 | nan      | nan      |          nan      |          nan      |      26.224  |      2000 |
| tail_loss | w        |       0.2385 |      -0.0362 |      -0.1058 |     0.1128 |              nan      |    12.8698 |   6.6832 |   0      |           20      |            9.4393 |      26.224  |      2000 |
| tail_loss | v        |       0.2995 |      -0.065  |      -0.1776 |     0.0955 |              nan      |    20.2214 |   8.4401 |   0      |           18.6467 |           19.7859 |      26.224  |      2000 |
| tail_loss | g        |       0.4115 |      -0.0636 |      -0.2287 |     0.099  |              nan      |    28.8781 |   9.2057 |   0      |           20      |           29.5093 |      26.224  |      2000 |
| tail_loss | z        |       0.3542 |      -0.0466 |      -0.1538 |     0.1198 |              nan      |    13.7757 |   8.9974 |   0      |           20      |           13.3147 |      26.224  |      2000 |
| tail_gain | ac       |       0.1623 |       0.014  |      -0.1189 |     0.079  |                0.2743 |    16.9219 | nan      | nan      |          nan      |          nan      |      26.224  |      2000 |
| tail_gain | w        |       0.2383 |       0.0272 |      -0.1005 |     0.099  |              nan      |    12.8116 |   6.6528 |   0      |           20      |            9.3704 |      26.224  |      2000 |
| tail_gain | v        |       0.3082 |       0.0404 |      -0.0935 |     0.1337 |              nan      |    20.5512 |   8.4983 |   0      |           18.6224 |           20.1557 |      26.224  |      2000 |
| tail_gain | g        |       0.4373 |       0.0484 |      -0.1615 |     0.1458 |              nan      |    29.7899 |   9.2161 |   0      |           20      |           30.3779 |      26.224  |      2000 |
| tail_gain | z        |       0.3736 |       0.0341 |      -0.1713 |     0.1276 |              nan      |    14.6104 |   9.026  |   0      |           20      |           14.2573 |      26.224  |      2000 |

## 2a. Winner with the acceptance test against the fixed prior formulas (E1); iba_a = first study's test, all others = clean rows

Cell: mean relative difference in the primary loss, a minus b (negative = a better), and the tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a          | b          | return              | logrv               | tail_loss           | tail_gain           | all tasks                |
|:-----------|:-----------|:--------------------|:--------------------|:--------------------|:--------------------|:-------------------------|
| iba_a|lin  | iba_e1|lin | +0.42 % (0b 3w / 7) | +0.20 % (0b 0w / 3) | +1.15 % (0b 0w / 4) | +2.03 % (0b 2w / 4) | 0 better, 5 worse of 18  |
| iba_ac|lin | iba_e1|lin | +0.26 % (0b 1w / 7) | +0.17 % (0b 0w / 3) | +0.38 % (0b 1w / 4) | +0.59 % (0b 1w / 4) | 0 better, 3 worse of 18  |
| iba_w|lin  | iba_e1|lin | +0.40 % (0b 4w / 7) | +0.34 % (0b 1w / 3) | +0.45 % (0b 2w / 4) | +0.93 % (0b 2w / 4) | 0 better, 9 worse of 18  |
| iba_v|lin  | iba_e1|lin | +0.29 % (0b 2w / 7) | +0.44 % (0b 2w / 3) | +0.77 % (0b 2w / 4) | +2.35 % (0b 3w / 4) | 0 better, 9 worse of 18  |
| iba_g|lin  | iba_e1|lin | +0.19 % (0b 2w / 7) | +0.34 % (0b 2w / 3) | +1.47 % (0b 4w / 4) | +4.12 % (0b 3w / 4) | 0 better, 11 worse of 18 |
| iba_z|lin  | iba_e1|lin | +0.31 % (0b 2w / 7) | +0.33 % (0b 2w / 3) | +1.38 % (0b 3w / 4) | +2.97 % (0b 3w / 4) | 0 better, 10 worse of 18 |

## 2b. Winner WITHOUT the acceptance test against E1 (diagnostic: what the search alone does)

Cell: mean relative difference in the primary loss, a minus b (negative = a better), and the tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a          | b          | return               | logrv               | tail_loss            | tail_gain            | all tasks                |
|:-----------|:-----------|:---------------------|:--------------------|:---------------------|:---------------------|:-------------------------|
| iba_ar|lin | iba_e1|lin | +3.38 % (0b 4w / 7)  | +1.34 % (0b 1w / 3) | +4.71 % (0b 2w / 4)  | +4.09 % (0b 2w / 4)  | 0 better, 9 worse of 18  |
| iba_wr|lin | iba_e1|lin | +4.91 % (0b 7w / 7)  | +3.08 % (0b 3w / 3) | +9.70 % (0b 4w / 4)  | +6.67 % (0b 4w / 4)  | 0 better, 18 worse of 18 |
| iba_vr|lin | iba_e1|lin | +7.74 % (0b 7w / 7)  | +3.82 % (0b 3w / 3) | +13.78 % (0b 4w / 4) | +9.28 % (0b 4w / 4)  | 0 better, 18 worse of 18 |
| iba_gr|lin | iba_e1|lin | +10.39 % (0b 7w / 7) | +4.39 % (0b 3w / 3) | +19.81 % (0b 4w / 4) | +13.61 % (0b 4w / 4) | 0 better, 18 worse of 18 |
| iba_zr|lin | iba_e1|lin | +9.70 % (0b 6w / 7)  | +4.22 % (0b 3w / 3) | +15.69 % (0b 4w / 4) | +12.12 % (0b 4w / 4) | 0 better, 17 worse of 18 |

## 2c. Colony ensemble against E1

Cell: mean relative difference in the primary loss, a minus b (negative = a better), and the tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a      | b          | return              | logrv               | tail_loss            | tail_gain            | all tasks                |
|:-------|:-----------|:--------------------|:--------------------|:---------------------|:---------------------|:-------------------------|
| iba_b  | iba_e1|lin | -0.07 % (1b 1w / 7) | -0.35 % (2b 0w / 3) | -0.67 % (1b 0w / 4)  | +0.07 % (1b 0w / 4)  | 5 better, 1 worse of 18  |
| iba_wb | iba_e1|lin | -0.31 % (0b 0w / 7) | +0.22 % (0b 0w / 3) | -0.37 % (1b 0w / 4)  | -0.30 % (1b 0w / 4)  | 2 better, 0 worse of 18  |
| iba_vb | iba_e1|lin | +3.33 % (0b 4w / 7) | +1.93 % (0b 2w / 3) | +6.22 % (0b 3w / 4)  | +3.96 % (0b 3w / 4)  | 0 better, 12 worse of 18 |
| iba_gb | iba_e1|lin | +9.13 % (0b 6w / 7) | +3.59 % (0b 3w / 3) | +17.61 % (0b 4w / 4) | +12.17 % (0b 4w / 4) | 0 better, 17 worse of 18 |
| iba_zb | iba_e1|lin | +6.97 % (0b 6w / 7) | +3.12 % (0b 3w / 3) | +11.29 % (0b 4w / 4) | +8.16 % (0b 4w / 4)  | 0 better, 17 worse of 18 |

## 2d. Colony ensemble against the first study's ensemble (B)

Cell: mean relative difference in the primary loss, a minus b (negative = a better), and the tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a      | b     | return              | logrv               | tail_loss            | tail_gain            | all tasks                |
|:-------|:------|:--------------------|:--------------------|:---------------------|:---------------------|:-------------------------|
| iba_wb | iba_b | -0.24 % (0b 0w / 7) | +0.57 % (0b 0w / 3) | +0.30 % (0b 0w / 4)  | -0.37 % (1b 0w / 4)  | 1 better, 0 worse of 18  |
| iba_vb | iba_b | +3.41 % (0b 5w / 7) | +2.28 % (0b 3w / 3) | +6.94 % (0b 3w / 4)  | +3.88 % (0b 3w / 4)  | 0 better, 14 worse of 18 |
| iba_gb | iba_b | +9.20 % (0b 7w / 7) | +3.95 % (0b 3w / 3) | +18.45 % (0b 4w / 4) | +12.08 % (0b 4w / 4) | 0 better, 18 worse of 18 |
| iba_zb | iba_b | +7.04 % (0b 6w / 7) | +3.48 % (0b 3w / 3) | +12.07 % (0b 4w / 4) | +8.08 % (0b 4w / 4)  | 0 better, 17 worse of 18 |

## 2e. Colony ensemble against group PCA

Cell: mean relative difference in the primary loss, a minus b (negative = a better), and the tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a      | b        | return              | logrv               | tail_loss            | tail_gain            | all tasks                |
|:-------|:---------|:--------------------|:--------------------|:---------------------|:---------------------|:-------------------------|
| iba_wb | gpca|lin | -0.35 % (1b 0w / 7) | -0.14 % (1b 0w / 3) | -1.01 % (2b 0w / 4)  | -0.02 % (0b 0w / 4)  | 4 better, 0 worse of 18  |
| iba_vb | gpca|lin | +3.30 % (0b 5w / 7) | +1.56 % (0b 1w / 3) | +5.54 % (0b 2w / 4)  | +4.25 % (0b 3w / 4)  | 0 better, 11 worse of 18 |
| iba_gb | gpca|lin | +9.10 % (0b 6w / 7) | +3.21 % (0b 2w / 3) | +16.89 % (0b 4w / 4) | +12.48 % (0b 4w / 4) | 0 better, 16 worse of 18 |
| iba_zb | gpca|lin | +6.94 % (0b 6w / 7) | +2.75 % (0b 2w / 3) | +10.60 % (0b 3w / 4) | +8.46 % (0b 4w / 4)  | 0 better, 15 worse of 18 |

## 2f. Against the type's reference (historical mean / HAR / base rate)

Cell: mean relative difference in the primary loss, a minus b (negative = a better), and the tasks where the 95 % date-block-bootstrap interval excludes zero (b = a better, w = a worse).

| a          | b   | return               | logrv               | tail_loss            | tail_gain            | all tasks                |
|:-----------|:----|:---------------------|:--------------------|:---------------------|:---------------------|:-------------------------|
| iba_e1|lin | REF | +1.39 % (0b 0w / 7)  | -5.29 % (2b 0w / 3) | -0.29 % (0b 1w / 4)  | +0.17 % (0b 1w / 4)  | 2 better, 2 worse of 18  |
| iba_b      | REF | +1.32 % (0b 0w / 7)  | -5.62 % (2b 0w / 3) | -0.95 % (0b 0w / 4)  | +0.24 % (0b 1w / 4)  | 2 better, 1 worse of 18  |
| gpca|lin   | REF | +1.43 % (0b 1w / 7)  | -4.92 % (2b 0w / 3) | +0.35 % (0b 1w / 4)  | -0.11 % (1b 0w / 4)  | 3 better, 2 worse of 18  |
| iba_w|lin  | REF | +1.80 % (0b 0w / 7)  | -4.97 % (2b 0w / 3) | +0.16 % (0b 1w / 4)  | +1.10 % (0b 1w / 4)  | 2 better, 2 worse of 18  |
| iba_v|lin  | REF | +1.69 % (0b 1w / 7)  | -4.88 % (2b 0w / 3) | +0.48 % (0b 1w / 4)  | +2.52 % (0b 2w / 4)  | 2 better, 4 worse of 18  |
| iba_g|lin  | REF | +1.59 % (0b 1w / 7)  | -4.97 % (2b 0w / 3) | +1.17 % (0b 1w / 4)  | +4.30 % (0b 2w / 4)  | 2 better, 4 worse of 18  |
| iba_z|lin  | REF | +1.71 % (0b 1w / 7)  | -4.98 % (2b 0w / 3) | +1.08 % (0b 1w / 4)  | +3.16 % (0b 2w / 4)  | 2 better, 4 worse of 18  |
| iba_wb     | REF | +1.08 % (0b 1w / 7)  | -5.08 % (2b 0w / 3) | -0.66 % (0b 0w / 4)  | -0.13 % (1b 0w / 4)  | 3 better, 1 worse of 18  |
| iba_vb     | REF | +4.78 % (0b 5w / 7)  | -3.46 % (2b 0w / 3) | +5.85 % (0b 2w / 4)  | +4.14 % (0b 2w / 4)  | 2 better, 9 worse of 18  |
| iba_gb     | REF | +10.66 % (0b 7w / 7) | -1.88 % (1b 0w / 3) | +17.14 % (0b 4w / 4) | +12.39 % (0b 4w / 4) | 1 better, 15 worse of 18 |
| iba_zb     | REF | +8.46 % (0b 6w / 7)  | -2.32 % (1b 0w / 3) | +10.88 % (0b 4w / 4) | +8.36 % (0b 3w / 4)  | 1 better, 13 worse of 18 |

## 3. SPA: does any of the 12 new configurations beat the benchmark? (consistent p-value; tasks with p < 0.05)

| benchmark   | kind      |   tasks |   significant |   median_p |
|:------------|:----------|--------:|--------------:|-----------:|
| REF         | logrv     |       3 |             2 |     0      |
| REF         | return    |       7 |             0 |     0.8865 |
| REF         | tail_gain |       4 |             1 |     0.5202 |
| REF         | tail_loss |       4 |             0 |     0.4162 |
| gpca|lin    | logrv     |       3 |             0 |     0.79   |
| gpca|lin    | return    |       7 |             0 |     0.6405 |
| gpca|lin    | tail_gain |       4 |             0 |     0.4388 |
| gpca|lin    | tail_loss |       4 |             1 |     0.1598 |
| iba_b       | logrv     |       3 |             0 |     0.9535 |
| iba_b       | return    |       7 |             0 |     0.251  |
| iba_b       | tail_gain |       4 |             1 |     0.4035 |
| iba_b       | tail_loss |       4 |             0 |     0.6535 |
| iba_e1|lin  | logrv     |       3 |             0 |     0.8055 |
| iba_e1|lin  | return    |       7 |             0 |     0.3225 |
| iba_e1|lin  | tail_gain |       4 |             1 |     0.4725 |
| iba_e1|lin  | tail_loss |       4 |             0 |     0.3675 |

New configuration with the lowest pooled loss per task:

| kind      |   iba_g|lin |   iba_wb |   iba_w|lin |   iba_z|lin |
|:----------|------------:|---------:|------------:|------------:|
| logrv     |           0 |        2 |           0 |           1 |
| return    |           2 |        5 |           0 |           0 |
| tail_gain |           0 |        4 |           0 |           0 |
| tail_loss |           0 |        3 |           1 |           0 |

## 4. Units (task x asset class) where a has the lower loss - where b has

| a          | b          | return   | logrv   | tail_loss   | tail_gain   | all   |
|:-----------|:-----------|:---------|:--------|:------------|:------------|:------|
| iba_ac|lin | iba_e1|lin | 4-19     | 6-17    | 1-15        | 7-7         | 18-58 |
| iba_w|lin  | iba_e1|lin | 7-17     | 2-20    | 0-17        | 2-12        | 11-66 |
| iba_v|lin  | iba_e1|lin | 6-16     | 2-20    | 2-14        | 0-13        | 10-63 |
| iba_g|lin  | iba_e1|lin | 4-17     | 2-17    | 2-16        | 1-14        | 9-64  |
| iba_z|lin  | iba_e1|lin | 6-15     | 2-17    | 1-15        | 3-13        | 12-60 |
| iba_wb     | iba_b      | 24-4     | 5-19    | 8-10        | 16-2        | 53-35 |
| iba_vb     | iba_b      | 2-26     | 1-23    | 2-16        | 1-17        | 6-82  |
| iba_gb     | iba_b      | 0-28     | 0-24    | 0-18        | 0-18        | 0-88  |
| iba_zb     | iba_b      | 2-26     | 2-22    | 1-17        | 0-18        | 5-83  |
| iba_wb     | gpca|lin   | 23-5     | 12-12   | 17-1        | 12-6        | 64-24 |
| iba_vb     | gpca|lin   | 3-25     | 0-24    | 8-10        | 0-18        | 11-77 |
| iba_gb     | gpca|lin   | 2-26     | 1-23    | 1-17        | 0-18        | 4-84  |
| iba_zb     | gpca|lin   | 2-26     | 2-22    | 3-15        | 0-18        | 7-81  |

Seed spread (standard deviation over the three seeds of the pooled loss, relative to the loss):

| config     |   logrv |   return |   tail_gain |   tail_loss |
|:-----------|--------:|---------:|------------:|------------:|
| iba_ac|lin |  0.0012 |   0.0015 |      0.0016 |      0.003  |
| iba_a|lin  |  0.0009 |   0.0022 |      0.0071 |      0.0064 |
| iba_b      |  0.0004 |   0.0008 |      0.0008 |      0.0014 |
| iba_gb     |  0.0031 |   0.0094 |      0.0148 |      0.0095 |
| iba_gr|lin |  0.0035 |   0.0096 |      0.0155 |      0.0096 |
| iba_g|lin  |  0.0013 |   0.0018 |      0.0089 |      0.005  |
| iba_vb     |  0.0031 |   0.0049 |      0.0097 |      0.0038 |
| iba_vr|lin |  0.0041 |   0.0077 |      0.0145 |      0.007  |
| iba_v|lin  |  0.0011 |   0.0023 |      0.0127 |      0.0052 |
| iba_wb     |  0.0004 |   0.0015 |      0.001  |      0.0017 |
| iba_wr|lin |  0.0028 |   0.0068 |      0.0091 |      0.0172 |
| iba_w|lin  |  0.0011 |   0.0017 |      0.0045 |      0.0016 |
| iba_zb     |  0.0037 |   0.0094 |      0.0068 |      0.0086 |
| iba_zr|lin |  0.0038 |   0.0103 |      0.0091 |      0.0099 |
| iba_z|lin  |  0.0011 |   0.0023 |      0.0065 |      0.0084 |

## 5. Decision rule (spec section 6)

A candidate qualifies if it is significantly better than its incumbent in more tasks than it is significantly worse AND its mean loss is lower in at least 3 of the 4 target types.

| candidate   | incumbent   |   tasks better |   tasks worse | types with lower mean loss   |   mean rel. diff (types equally weighted) | qualifies   |
|:------------|:------------|---------------:|--------------:|:-----------------------------|------------------------------------------:|:------------|
| iba_ac|lin  | iba_e1|lin  |              0 |             3 | 0/4                          |                                     0.35  | False       |
| iba_w|lin   | iba_e1|lin  |              0 |             9 | 0/4                          |                                     0.53  | False       |
| iba_v|lin   | iba_e1|lin  |              0 |             9 | 0/4                          |                                     0.962 | False       |
| iba_g|lin   | iba_e1|lin  |              0 |            11 | 0/4                          |                                     1.532 | False       |
| iba_z|lin   | iba_e1|lin  |              0 |            10 | 0/4                          |                                     1.248 | False       |
| iba_wb      | iba_b       |              1 |             0 | 2/4                          |                                     0.066 | False       |
| iba_vb      | iba_b       |              0 |            14 | 0/4                          |                                     4.129 | False       |
| iba_gb      | iba_b       |              0 |            18 | 0/4                          |                                    10.92  | False       |
| iba_zb      | iba_b       |              0 |            17 | 0/4                          |                                     7.669 | False       |

Qualifying: none; the first study's implementation stays.
