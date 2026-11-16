# Results of SPEC-2026-11-14-benchmarks-kpca-ae: kernel PCA and an autoencoder as benchmarks (development series only)

Run 2026-11-14 21:55–22:12 on the Mac from the frozen spec (fingerprint `2bcaa0ad64aaa3ab35c5455d`,
benchmark hash `6e8fef997182e116c313a365`): 458 cells of stage 10, no failure, 3,664 registry
rows. `report.md` is the pre-written analysis, unedited; this file reads it. Both reducers are
the r6 ones, unchanged and untuned; linear model unless said. IBA readings: the final method of
the wrap-up spec (interpretable `Kc|lin`, accuracy `iba_ca_b`).

## 1. Outcome

Neither non-linear reduction improves on the linear ones, and IBA is better than both on
volatility at every horizon and never significantly worse on anything.

| | return | volatility | large loss | large gain | tasks better / worse |
|---|---|---|---|---|---|
| kernel PCA against the reference | +1.1 % | −1.3 % | +0.9 % | +0.9 % | 2 / 4 |
| autoencoder against the reference | +1.2 % | −3.0 % | +0.8 % | −0.1 % | 3 / 6 |
| kernel PCA against PCA | −0.2 % | +2.3 % | −0.2 % | +0.8 % | 1 / 2 |
| autoencoder against PCA | −0.1 % | +0.5 % | −0.2 % | −0.2 % | 0 / 0 |
| kernel PCA against group PCA | −0.3 % | +3.9 % | +0.5 % | +1.0 % | 1 / 2 |
| autoencoder against group PCA | −0.2 % | +2.1 % | +0.5 % | 0.0 % | 0 / 3 |
| IBA interpretable against kernel PCA | +1.0 % | −4.7 % | −0.4 % | −1.0 % | 4 / 0 |
| IBA accuracy against kernel PCA | +0.5 % | −4.8 % | −0.7 % | −1.1 % | 4 / 0 |
| IBA interpretable against the autoencoder | +0.9 % | −3.0 % | −0.4 % | 0.0 % | 3 / 0 |
| IBA accuracy against the autoencoder | +0.4 % | −3.2 % | −0.7 % | −0.2 % | 3 / 0 |

- Kernel PCA keeps the least of the volatility signal: 1.3 % below HAR against 3.5 % for plain
  PCA and about 6 % for IBA; significantly worse than PCA and group PCA at 2 of 3 horizons.
- The autoencoder is level with plain PCA everywhere and behind group PCA on volatility.
- With trees both get worse, like every other representation: 11–15 of 18 tasks significantly
  worse than their own linear model.
- The r6 result (kernel PCA with XGBoost among the best models on eleven monthly series) does not
  appear: with XGBoost kernel PCA is worse than the reference in 10 of 18 tasks.

## 2. Limits

One seed for the autoencoder; a small network by design (blocks of 163–850 rows); the settings of
the r6 study, not tuned here, so a tuned kernel width or architecture could do better and would
need its own spec. Development evidence only.
