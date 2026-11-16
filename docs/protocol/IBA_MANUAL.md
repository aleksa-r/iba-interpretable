# IBA formula manual (version 1, 2026-11-14)

This manual is sent, unchanged, with every request for prior formulas. It defines what a formula
is and what an answer must look like. It contains no data and no results.

## 1. What a formula does

We forecast a property of an index over the next h periods (its return, its volatility, the
chance of a large loss, the chance of a large gain) from a panel of market and macroeconomic
factors. The factors are arranged in GROUPS (interest rates, credit, volatility, and so on). For
every group we want ONE logical statement about the state of that group, built from its factors.

- A **predicate** is "factor F is high". It is graded, not yes/no: the factor's trailing z-score
  (its current value against its own recent history) is mapped to a number between 0 and 1, where
  1 means "as high as it has been in the training sample" and 0 "as low as it has been".
- A **literal** is a predicate or its negation: "F is high" or "F is NOT high" (value 1 − x).
- A **formula** for a group is a conjunction of at most two literals on different factors of that
  group, for example "term spread is high AND short rate is NOT high". Its value is the product
  of the literal values (Interpolative Boolean Algebra with the product as generalized product),
  so it is close to 1 only when both statements hold strongly.
- A group may be left EMPTY if you judge that none of its factors carries information for the
  target. An empty group is simply not used.

The values of the group formulas (at most one number per group) are the only inputs of a small
linear model that produces the forecast. The model learns the sign and size of each group's
effect from data, so a formula does not have to say whether its state is good or bad for the
target: it has to describe the STATE OF THE GROUP that matters most for the target.

## 2. What makes a good formula

- It names the one or two factors of the group whose joint state is most informative for the
  target, with the polarity that makes the conjunction a recognisable economic state (for
  example "credit spreads NOT high AND high-yield returns high" = easy credit conditions).
- It rests on an economic mechanism or a well-documented empirical regularity, stated in one or
  two sentences.
- Two literals are worth it only if their combination says more than either alone. One literal
  is a perfectly good formula.
- The same factor may matter differently for different targets: the state that says most about
  next-period volatility need not be the one that says most about the return.

## 3. Targets

- **return**: the index return over the next h periods.
- **volatility**: the realised variance of the index over the next h periods, beyond what its
  own recent realised variance already predicts.
- **large_loss**: the probability that the return over the next h periods falls below the lowest
  tenth of its past distribution.
- **large_gain**: the probability that it rises above the highest tenth.

## 4. The target's own group

One group, ENDG, holds the index's own recent behaviour (for return and tail targets: its recent
return against its own history; for volatility: its recent realised variance against its own
history). Its only factor is written `__target__`.

## 5. Answer format

For each target: for each group, a list of zero, one or two literals, each a factor code of that
group with the state `high` or `not_high`, and a rationale of one or two sentences for the
group. Use only the factor codes listed for the group. Do not repeat a factor within a group.
