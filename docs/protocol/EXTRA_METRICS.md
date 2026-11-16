# A second view of the forecasts: financial and classification measures (version 1, 2026-11-14)

Asked for by the owner on 2026-11-14 as another perspective on the same forecasts. Everything here is
computed from stored forecasts and labels (`iba.eval.finmetrics`, `scripts/make_extra_metrics.py`);
nothing is refitted. The definitions below were written before any of these numbers was computed.

**Status.** On the development series these tables are DESCRIPTIVE: the specs whose forecasts they read
were frozen without them, so they decide nothing and are not added to those specs' reports. The same
definitions, unchanged, are to be declared in the confirmation spec before the held-out series are
touched; only there do they count as evidence.

## 1. Value at risk and expected shortfall from the volatility forecasts (weekly series, 1, 4 and 13 weeks)

A volatility forecast is a forecast of the variance of the return over the next h weeks. With a
zero-mean normal return it gives the 5 % and 1 % quantile of the h-week log return (VaR) and the
expected return below it (expected shortfall). Every method uses the same distributional
assumption, so differences between methods come from the variance forecasts only; the assumption
itself (no fat tails, no mean) is a limit of the absolute numbers.
- Violation rate: share of forecast dates on which the realised return is below the quantile
  (target 5 % or 1 %), all series pooled.
- Quantile (tick) loss of the VaR forecast, a proper score for a quantile; relative difference to
  HAR with the same paired date-block bootstrap as the reports.
- Fissler-Ziegel loss (FZ0), a proper joint score of VaR and expected shortfall; mean difference to
  HAR with the same bootstrap.
- Shortfall ratio: mean realised return on violation dates over the mean forecast expected
  shortfall on those dates (1 = shortfall as forecast; above 1 = losses deeper than forecast).
- At 1 week only (longer horizons overlap): per series the Kupiec test of the violation rate and
  the Christoffersen test of the independence of violations; reported as the share of series that
  reject at 5 %.

## 2. Risk of the long/flat rule on the return forecasts (weekly 1, 4, 13 weeks; monthly 1, 3, 6, 12 months)

The engine's rule: long the index for the next h periods when the forecast return is not negative,
otherwise flat; one decision every h periods, every starting phase, averaged over phases. For the
rule and for buy-and-hold, per series: annualised return, Sharpe ratio, historical 5 % VaR and CVaR
of the h-period returns, maximum drawdown, share of time invested, switches per year. Averaged over
series; also the number of series on which the rule has the higher Sharpe ratio and the smaller
drawdown than buy-and-hold. No transaction costs: with costs every rule that trades looks worse.

## 3. The tail probabilities as a classifier (large loss, large gain; 10 % events)

- A signal is raised when the forecast probability is above the historical frequency of the event
  known at the forecast date (the base-rate forecast), and a strong signal when it is above twice
  that. The thresholds are fixed here, not tuned. All series of a task pooled: the confusion matrix
  and from it signal rate, precision, recall, specificity, F1, balanced accuracy and the Matthews
  correlation. The base-rate forecast itself never signals.
- Murphy's decomposition of the Brier score on ten quantile bins of the forecast: reliability
  (calibration error, lower is better), resolution (how far the observed frequency moves with the
  forecast, higher is better), uncertainty; and sharpness, the standard deviation of the forecasts.
- A reliability table for the method and for the best benchmark: mean forecast and observed
  frequency by fifth of the forecast.

## 5. Crisis and drawdown periods (added 2026-11-15 at the owner's request, before any of it was computed)

The primary loss of each method relative to the reference, restricted to forecasts MADE in a
period (by forecast date; the label may be realised after the period ends), all series pooled.
- **Named periods**, fixed here: the sell-off of the fourth quarter of 2018 (1 October to
  31 December 2018); the COVID-19 crash (17 February to 30 April 2020); 2022, the invasion of
  Ukraine and the rate shock (21 February to 31 October 2022); and all other forecast dates.
- **Drawdown state**, per series: forecast dates on which the index stands 10 % or more below
  its running peak since the start of its sample (known at the forecast date), against all other
  dates.
A period enters a task's table only with at least 20 pooled forecasts and a positive reference
loss; the entry for a target type is the mean over its tasks. These subsamples are short (the
COVID-19 period is eleven weekly dates), so the table is descriptive in every data set,
confirmation included: no test is attached and no direction is claimed.

## 4. Methods shown

The IBA readings of the final method (fixed formulas; averaged formulas), the generic formulas,
group PCA, PCA, LASSO, raw factors, kernel PCA and the autoencoder (when their run exists), all with
the linear model, and each target's references (historical mean and trailing momentum; HAR, GARCH
and GJR-GARCH; base rate, the volatility-based logit and the GARCH-based probability). GARCH
forecasts are those of the first study on the same cells and dates.
