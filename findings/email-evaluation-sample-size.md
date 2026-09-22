# Sample size for the personal email model evaluation

## Question

Are 100 hand-labelled emails enough to compare Kev 0.8B, Kev 4B, and Laya for personal email triage, or should the evaluation include more messages?

## Proposed operationalisation

Treat the evaluation as a paired, descriptive study of the user's own email population. Every selected email is scored by every model. Judge a sample size by the uncertainty around overall and per-class error rates, pairwise differences, probability scores, and selective risk at useful coverage. The study may describe this inbox but cannot establish general performance for other people or future distribution shifts.

## In-scope claims

- The precision that 100, 200, and 300 emails provide for plausible accuracy and error rates.
- How class imbalance and multiple decisions per email reduce the effective evidence for rare outcomes.
- Which conclusions are defensible with 100 emails and which require a larger sample.
- Whether a pre-labelled pilot can be expanded without tuning the tested models or decision rules on test outcomes.

## Unknowns

- The prevalence of each hand-labelled class in the user's target inbox population.
- The smallest performance difference the user wants the study to distinguish.
- The acceptable uncertainty around destructive or high-cost errors.

## Evidence method

The user confirmed the question, personal-case-study scope, natural inbox population, and predeclared expansion rule on 21 September 2026. The inquiry then calculated Wilson 95% intervals for single proportions and illustrative paired-difference half-widths for 100, 200, and 300 emails in [`email-evaluation-sample-size.ipynb`](email-evaluation-sample-size.ipynb). It also inspected primary calibration research from PMLR.

## Findings

### One hundred emails supports an exploratory estimate, not a precise rate

**Claim.** At plausible model performance, 100 emails leaves enough sampling uncertainty that modest differences between models will be unresolved.

**Operationalisation.** Use the width of a 95% Wilson interval around an observed accuracy of 80% as an illustrative single-model precision check.

**Evidence.** The first executable cell in the [sample-size notebook](email-evaluation-sample-size.ipynb) gives an interval of 71.1% to 86.7% for 80 correct decisions out of 100, a half-width of 7.8 percentage points. At 200 emails the half-width is 5.5 points; at 300 it is 4.5 points.

**Not searched or run.** No model outputs were inspected. No formal power calculation was attempted because the paired disagreement rate and class prevalences are not yet known.

**Uncertainty and failure modes.** The interval assumes the sampled email units are independent. Repeated messages from one thread, campaign, or sender reduce the effective diversity and can make these figures optimistic.

**Verdict.** Settled: 100 emails can reveal large differences and common failure patterns, but it cannot support a precise ranking when models are close.

### Rare outcomes are the binding sample-size constraint

**Claim.** A natural 100-email sample gives too few examples for dependable class-specific claims when an important outcome occurs in only 5–10% of messages.

**Operationalisation.** Count the expected examples of outcomes with 5%, 10%, and 20% prevalence in samples of 100, 200, and 300 emails.

**Evidence.** The second executable cell in the [sample-size notebook](email-evaluation-sample-size.ipynb) shows that 100 emails contain only about five observations of a 5% outcome and ten of a 10% outcome. Even 300 emails contain only about fifteen observations of a 5% outcome. The corresponding prevalence intervals remain wide.

**Not searched or run.** The user's actual label distribution has not been counted because the label schema and frozen retrieval window have not yet been agreed.

**Uncertainty and failure modes.** Random variation may yield fewer examples than the prevalence estimate suggests. A deliberately balanced set would answer a different question from performance on the natural inbox mix.

**Verdict.** Settled: inspect label counts before inference, expand the natural sample under a predeclared rule, and report very rare outcomes as case analysis when the cap still yields too few examples.

### Paired evaluation helps, but does not rescue a very small sample

**Claim.** Scoring every email with every model is more informative than evaluating separate samples, but uncertainty in a model difference still depends on how often the models disagree.

**Operationalisation.** Use the same emails for all models and illustrate the 95% half-width of a paired accuracy difference when 10%, 20%, or 50% of results are discordant and the observed difference is near zero.

**Evidence.** The third executable cell in the [sample-size notebook](email-evaluation-sample-size.ipynb) gives illustrative half-widths at 20% discordance of 8.8 points for 100 emails, 6.2 for 200, and 5.1 for 300.

**Not searched or run.** Actual discordance is unknown until the frozen evaluation is run. The calculation is an approximation for planning, not the final interval method.

**Uncertainty and failure modes.** Multiple decisions made on the same email are correlated and must not be counted as independent emails. Final paired bootstrap intervals should resample the email, or the thread if related messages remain in the sample, as the unit.

**Verdict.** Settled: use paired comparisons and paired uncertainty intervals, but do not interpret a small point difference from 100 emails as a stable winner.

### One hundred emails is too small for a strong calibration claim

**Claim.** Calibration plots and conventional binned expected calibration error are unstable at this sample size and should be secondary diagnostics.

**Operationalisation.** Separate probability quality, which can be scored per prediction, from a claim that confidence bins match long-run frequencies.

**Evidence.** [Roelofs et al. (2022)](https://proceedings.mlr.press/v151/roelofs22a.html) show that common binned ECE estimators are biased and that equal-mass bins reduce bias; their worked examples still use larger samples than many per-class slices in this study. [Guo et al. (2017)](https://proceedings.mlr.press/v70/guo17a.html) define reliability diagrams and temperature scaling, but do not make a 100-item target-domain calibration guarantee. The model evidence already shows that shipped temperatures were fitted on unrelated data.

**Not searched or run.** No target-domain calibration model was fitted, and none should be fitted on the final test emails.

**Uncertainty and failure modes.** Pooling multiple question types to inflate the count would mix distinct events. Fine bins can appear authoritative while containing only a handful of observations.

**Verdict.** Settled: report Brier score and log loss as probability-quality measures, show a coarse equal-mass reliability view descriptively, and avoid a strong target-domain calibration conclusion.

## Shared reading

One hundred emails is a useful pilot and can support a transparent personal case study when model differences are large. It is too small for precise model ranking, rare-class efficacy, or strong calibration claims. Two hundred emails is a better default target; three hundred materially improves precision but still does not solve a 5% rare-outcome problem. The eventual expansion rule must use hand-label counts and duplication structure only, before any model predictions are viewed.

## Remaining bounded unknowns

- The label schema determines which class counts are material.
- The recent-window prevalence of each primary outcome is unknown until the pilot is labelled.
- The paired model-disagreement rate is unknown until the final frozen set is scored.
- The acceptable labelling workload and maximum sample size remain user decisions.

## Inquiry status

Confirmed by the user on 21 September 2026. One hundred emails will be treated as a pilot, the evaluation will expand to 200 by default, and the predeclared label-count rule may expand it to 300 before model results are inspected.
