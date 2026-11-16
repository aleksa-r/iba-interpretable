# The explanation step (version 1, 2026-11-14)

The last step of the method: a language model writes a short text about what the fitted model
does, from exact numbers, and the text is accepted only if every number in it is in those
numbers. It is a description of the final method, not an experiment: it changes no forecast and
no result. Agreed with the owner on 2026-11-14: the list of inputs, and two levels (a summary per
asset class, and single forecasts, of which a few worked examples are written first).

## What is explained

The interpretable reading of the final method of SPEC-2026-11-14-wrapup: one fixed formula per
group for each asset class and target, a linear model on the group values. The formula set and
the readings are read from that run's `final_method.json`; if the interpretable reading were not
the fixed formula, the script stops. The accuracy reading (the no-search colony, or the ABC colony
if it qualified) enters only as a line of the track record. Development series only.

## Where the numbers come from (`iba.explain.trace`)

Every forecast is repeated with the engine's own pieces and must equal the stored forecast of the
run (linear model to 1e-9, XGBoost to 1e-5); otherwise nothing is explained. The repetition keeps
what the engine does not store: the value of every group formula at every forecast date, the
linear model's coefficient and contribution per group, and the exact tree attribution per group
(XGBoost's own, no approximation). Contributions are in the forecast's units for returns, in
log-variance units on top of the HAR part for volatility, and in log-odds for the two tail
probabilities.

## Inputs

**A single forecast** (series, target, horizon, forecast date):
1. the formula of every group in words, and the rationale recorded when it was elicited (for a
   consensus formula: of the lowest-numbered draw with exactly that formula for the group, or of
   the draw sharing most of it, said so);
2. on the forecast date, for every factor in a formula: its z-score, the degree of truth of
   "the factor is high", the value of the literal, and the value of the group's formula;
3. the linear model: starting level, and per group the value today, its training average, the
   coefficient and today's contribution;
4. XGBoost on the same group values: its forecast, starting level and exact attribution per group;
5. the reference forecast (historical mean, HAR, base rate) and the track record on the test
   period: for the series, and for all series of the frequency with the bootstrap interval.

**An asset class and target** (all its series, horizons and forecast dates of the test period):
1. the formulas and rationales, as above;
2. per group: the average value of the formula and its 10th to 90th percentile; its share of the
   absolute contributions in the linear model; the share of forecasts made with a positive
   coefficient; its share of the tree model's attributions;
3. per horizon: the relative loss against the reference for the class (fixed formulas, and the
   averaged formulas of the accuracy reading) and for all series of the frequency with the
   bootstrap interval and verdict.

Nothing dated after a forecast date enters the numbers of that forecast, except the track record,
which is the test period's and is labelled as such.

## The request and the check (`iba.explain.narrate`)

Model `claude-opus-5-5`, one request per case, a fixed system prompt (use only the material; quote
numbers digit for digit and compute none; the rationale is an assumption, say where the fitted
model agrees or not; state the track record plainly; plain prose). The answer has a headline, an
explanation and the limits. Every number written in the answer must be written in the material
(compared by magnitude; whole numbers up to 12, and 95 and 100, are free). If one is not, the
request is repeated with the offending numbers named, at most twice; after that the case is
recorded as failed. No fallback model. Every record (material, its hash, response ids, usage,
rejected drafts, accepted text) is kept under `explanations/raw/<formula set>/`.

Limits to state where these texts are used: the check covers numbers, not wording, so a text can
still describe a relation more strongly than the numbers support; the rationale was written by
the same family of model that writes the explanation; and a text is only as informative as the
forecast it explains, which for returns and tails has shown no advantage over the reference.

## The worked examples (fixed before any text was written)

The last forecast date of the alphabetically first development series of the class, middle
horizon: broad US equity at 4 weeks for all four targets; monthly hedge-fund indices at 3 months
for the return and the large loss. Six in all. Summaries: every asset class with development
series and every target (35).
