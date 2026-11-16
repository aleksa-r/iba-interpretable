## Search comparison at equal budget (units = cell x block, seed-averaged)

| algorithm   |   inner_gain |   outer_gain |   optimism |   accepted |   n_evals |
|:------------|-------------:|-------------:|-----------:|-----------:|----------:|
| abc         |      0.10432 |      0.00587 |    0.03167 |    0.22812 |      2000 |
| abc_gv      |      0.03001 |      0.12324 |   -0.0282  |    0.96667 |      2000 |
| ga          |      0.12394 |      0.00153 |    0.03779 |    0.20781 |      2000 |
| pso         |      0.11189 |      0.00495 |    0.03483 |    0.23542 |      2000 |
| sa          |      0.11194 |      0.00377 |    0.03517 |    0.21979 |      2000 |

- inner_gain: Friedman chi2 = 241.54, p = 0.0000 over 96 units
  - ABC vs abc_gv: wins 96, losses 0, Wilcoxon p = 0.0000, Holm p = 0.0000
  - ABC vs ga: wins 0, losses 96, Wilcoxon p = 0.0000, Holm p = 0.0000
  - ABC vs pso: wins 6, losses 90, Wilcoxon p = 0.0000, Holm p = 0.0000
  - ABC vs sa: wins 0, losses 96, Wilcoxon p = 0.0000, Holm p = 0.0000
- outer_gain: Friedman chi2 = 1.73, p = 0.6314 over 96 units
  - ABC vs abc_gv: wins 0, losses 96, Wilcoxon p = 0.0000, Holm p = 0.0000
  - ABC vs ga: wins 50, losses 46, Wilcoxon p = 0.2960, Holm p = 0.8382
  - ABC vs pso: wins 50, losses 46, Wilcoxon p = 0.5711, Holm p = 0.8382
  - ABC vs sa: wins 55, losses 41, Wilcoxon p = 0.2794, Holm p = 0.8382
