---
spec_id: SPEC-2026-11-14-benchmarks-kpca-ae
status: frozen     # frozen by Claude Code on 2026-11-14 on the owner's request (section 0), before any forecast of SPEC-2026-11-14-wrapup was read
version: 1 (2026-11-14; requested by the owner and the owner's supervisor, details by Claude Code)
fingerprint: 2bcaa0ad64aaa3ab35c5455d
xgb_hash: c6e501978f15890d889f6075
bench_hash: 6e8fef997182e116c313a365
authors: Aleksa Radosavčević; drafted by Claude Code
depends_on: specs/SPEC-2026-11-14-wrapup.md
scope: DEVELOPMENT series only. Two more benchmarks on the cells of the wrap-up spec; no method decision depends on them.
---

# Kernel PCA and an autoencoder as benchmarks

## 0. Why

The benchmarks of the study are linear (PCA, group PCA, LASSO) or no reduction at all. The
owner's supervisor asked for kernel PCA, and the owner for an autoencoder as a benchmark from the
deep-learning domain ("we would need to have kernel pca (maybe instead of plain pca or as an
addition)"; "Autoencoders, would be great to have something from deep learning domain as a
benchmark", 2026-11-14). Both were benchmarks of the r6 study on the monthly hedge-fund indices,
where kernel PCA with XGBoost was among the best models; they were never run in this repository.
SPEC-2026-11-14-wrapup was already frozen and running when the request came, so this is a spec of
its own. It was frozen while stage 7 of the wrap-up was still running: no forecast and no report
of that run had been read.

## 1. Question and expectation (written before any result)

Do two non-linear reductions of the same factor panel forecast better than the linear ones, than
the references, and than the IBA readings of the wrap-up's final method?

Expected: parity with PCA and group PCA on every target type, like every other factor
representation so far; nothing ahead of the reference on returns and tails; volatility a few
per cent below HAR at short horizons if they carry the same information as the others. The r6
advantage of kernel PCA came with XGBoost under column sampling on eleven monthly series and may
not appear here. A result in either direction is reported as it is.

## 2. Data and cells

The 458 development cells and 18 tasks of SPEC-2026-11-14-wrapup; protocol, labels, folds,
estimators and references unchanged. Stage 10 (`ibanext.protocol.study.STAGES[10]`).

## 3. The two reducers (`ibanext.models.reducers`), both exactly as in the r6 study

Added to plain PCA, not instead of it. Both are fitted like every reducer: once per block on the
rows admissible at the block origin, and per fold on that fold's training rows for tuning; both
are unsupervised.
- **Kernel PCA (`kpca`).** Standardised features, RBF kernel with γ = 1 / number of features,
  6 components (as many as plain PCA). Dense eigen-solver, so there is no random start.
- **Autoencoder (`ae`).** Standardised features, fully connected p → 16 → 6 → 16 → p with tanh,
  squared reconstruction error, Adam, L2 penalty 10⁻³, at most 400 epochs, seed 0; the six
  bottleneck activations are the features. It is a small network on purpose: a block has 538 to
  850 weekly rows or 163 to 235 monthly rows, on 67 or 75 features.

Nothing is tuned: the numbers of components, the kernel width, the architecture and the training
settings are the r6 ones and stay fixed. Each reducer is read with the linear model, LightGBM and
XGBoost (`kpca|lin`, `kpca|gbt`, `kpca|xgb`, `ae|lin`, `ae|gbt`, `ae|xgb`): 6 new
configurations.

Neither is covered by the engine fingerprint (iterative training and a kernel eigen-problem can
differ in the last digits between machines), so they have their own hash of the fingerprint cell
(`bench_hash` above, measured on the Mac); the runner stops if the machine does not reproduce it.
The limit to state in the paper: one seed for the autoencoder.

## 4. Compute

458 cells, 2.3 core-hours measured on real cells (seconds only, nothing evaluated): about 20
minutes on 8 workers. `scripts/run_kpca_ae.sh` starts when the wrap-up run has finished.

## 5. Statistics and reporting (`scripts/make_kpca_ae_report.py`, written before the run and tested on synthetic cells)

Per (frequency, task), all development series of the frequency pooled on the same dates, paired
date-block-bootstrap 95 % intervals (2 000 draws, block ≥ h) of the relative difference in the
primary loss:
1. each new benchmark with the linear model against the type's reference, PCA, group PCA, raw
   factors and LASSO; the autoencoder against kernel PCA;
2. with trees: XGBoost and LightGBM against the linear model on each; with XGBoost against raw
   factors and PCA with XGBoost and against the reference;
3. IBA against each: the interpretable and the accuracy reading of the wrap-up's final method and
   the generic formulas with the linear model; the chosen formula set with XGBoost and with
   LightGBM against the benchmark with the same estimator.

No decision rule: the final method of the wrap-up spec does not change with this report. Every
configuration is in the registry.

## 6. Freeze

Frozen by Claude Code on the owner's request quoted in section 0. Details decided here: both as
additions, the r6 settings unchanged, one seed, three estimators, the comparisons of section 5.

## 7. Deviations

Appended to `docs/DEVIATIONS.md` before the deviating run; the count for this spec is written
into every registry row of the run.
