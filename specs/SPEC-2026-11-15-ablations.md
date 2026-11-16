---
spec_id: SPEC-2026-11-15-ablations
status: frozen     # frozen by Claude Code on 2026-11-15 on the owner's word ("run what needs to be run"); written while the confirmation run was in progress, before any of its results was read
version: 1 (2026-11-15; the four missing rows of the component contribution table, details by Claude Code)
fingerprint: 2bcaa0ad64aaa3ab35c5455d
authors: Aleksa Radosavčević; drafted by Claude Code
depends_on: specs/SPEC-2026-11-14-wrapup.md
scope: DEVELOPMENT series only. Descriptive ablations of the final method's interpretable reading; no method decision depends on them.
---

# Component contribution analysis: the four rows that needed a run

## 0. Why

The paper's appendix has a table that changes one component of the method at a time. Nine rows
come from runs that exist (reduction, logical form, formula content, the two elicitation
procedures, consensus, averaging, search, estimator, each group's share of the forecast). Four
need forecasts that were never made. The final method is fixed and the confirmation run is in
progress; nothing here can change either.

## 1. Variants (`ibanext.explain.ablate`), each against the unchanged interpretable reading

The unchanged method is the consensus formula set Kc with the linear model (`Kc|lin`), recomputed
here; a cell where the recomputation differs from the stored forecast of the wrap-up run by more
than 1e-9 is a failure.
1. **Leave one group out.** The formula of one group is removed, for every group in turn,
   including the group of the index's own behaviour. A positive difference in loss means the group
   contributes.
2. **No HAR stage** (volatility only). The linear model on the group values forecasts log
   variance directly.
3. **One literal per group.** Of a two-literal formula only the literal whose factor comes first
   in the group is kept.
4. **Predicate scaling.** The empirical distribution of the training rows instead of the min–max
   range.

Everything else is unchanged: the 458 development cells, the protocol, the tuning of the penalty,
the information rule. Nothing is tuned.

## 2. Expectations (written before the run)

Removing the own-behaviour group or the volatility group should hurt the volatility forecasts
most; removing most other groups should change little, with intervals that include zero. Without
the HAR stage volatility should be far worse, since the formulas were asked only for what HAR
does not explain. One literal against two should differ little. The scaling should matter little
for the linear model. For returns and tails, where the method has no advantage over the
reference, removing a group may even lower the loss.

## 3. Statistics and reporting (`scripts/make_ablation_report.py`, written before the run)

Per (frequency, task), all development series of the frequency pooled on the same dates, the
paired date-block bootstrap of the other reports (2 000 draws, block ≥ h, 95 % interval): each
variant against the unchanged method. Reported per target type as the mean relative difference
and the number of tasks in which the interval excludes zero. Descriptive: development data, no
decision rule. Every variant of every cell is a registry row.

## 4. Compute

Linear models only: about one second per cell, 458 cells, a few minutes. Started after the
confirmation run has finished, so that the two runs do not write the registry at the same time.

## 5. Deviations

Appended to `docs/DEVIATIONS.md` before the deviating run.
