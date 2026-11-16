# Results of SPEC-2026-11-15-ablations: component contribution analysis (development series only)

Run 2026-11-15 02:23, 458 cells, no failure; in every cell the unchanged variant reproduced the
stored forecast of the wrap-up run; 5,466 registry rows. `report.md` is the pre-written
analysis after one recorded correction (`docs/DEVIATIONS.md`, 2026-11-15: a series whose asset
class has no formula in a group now counts as unchanged when that group is removed; the first
version is kept as `report_first_version.md`). Differences are variant minus unchanged method,
positive = the component contributes.

- **Groups, weekly volatility.** Removing the index's own behaviour costs 1.9 % (significant at
  all 3 horizons), credit 1.0 % (2 of 3), volatility 0.9 % and equity factors 0.4 % (not
  significant). Removing macro-financial conditions lowers the loss by 0.4 % (significant at 2
  of 3 horizons): that group's formula hurts. The other groups are within ±0.2 %.
- **Groups, other targets.** For returns and tails on the weekly series no group matters much:
  of 63 comparisons the removal is significantly worse in 3 and better in 1, and no difference
  exceeds 1.0 %. On the monthly hedge-fund indices no removal is significantly worse (80
  comparisons; 2 significantly better).
- **HAR stage.** Without it the volatility loss is 27.5 % higher (significant at 2 of 3 horizons).
- **One literal per group.** +0.4 % on volatility, not significant; nothing elsewhere.
- **Predicate scaling.** Empirical-distribution scaling is 1.3 % worse on volatility, not
  significant; nothing elsewhere.

As expected in the spec, except that the removal of the volatility group was expected to hurt as
much as the removal of the own-behaviour group and does not reach significance.
