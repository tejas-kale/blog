# Laya for the private email triage evaluation

## Question

Does `convaiinnovations/laya-typed-decisions` provide a comparable typed-decision model that should be included alongside Kev 0.8B and Kev 4B in a 100-email personal email evaluation?

## Agreed operationalisation

Compare the models on the same frozen email records, the same semantic questions and options, and the same hand-labelled reference decisions. Model-specific serialisation is allowed. Record exact model revisions, inputs, outputs, latency, errors, probability quality, selective coverage, robustness, and privacy-relevant data movement. Published benchmark figures provide context only.

## Evidence method

The inquiry inspected the official Hugging Face model repositories and cards, the official Laya and Kev GitHub repositories, configuration files, implementation code, benchmark notes, and licences on 21 September 2026. No third-party benchmark number was treated as direct comparative evidence.

## Findings

### Laya is a small, downloadable typed-decision model

**Claim.** `convaiinnovations/laya-typed-decisions` is a self-hostable 421M-parameter English specialist built from `answerdotai/ModernBERT-large` with a two-layer decision head.

**Operationalisation.** A model is self-hostable when its weights, configuration, tokenizer, licence, and local loading code are available without sending inference inputs to a hosted model service.

**Evidence.** The [model card](https://huggingface.co/convaiinnovations/laya-typed-decisions) describes the architecture, parameter count, four synthetic workflow families, and Apache-2.0 licence. The [checkpoint tree](https://huggingface.co/convaiinnovations/laya-typed-decisions/tree/main) contains an 843 MB F16 safetensors file plus configuration and tokenizer files. The [Laya package](https://github.com/NandhaKishorM/laya) loads a repository or local path and is also Apache-2.0.

**Not searched or run.** The model was not downloaded or executed. No independent security audit or licence opinion was obtained.

**Uncertainty and failure modes.** The published artefacts establish technical availability, not suitability for personal email.

**Verdict.** Settled: the checkpoint can be downloaded and self-hosted for this experiment.

### Laya supports the same semantic question families as Kev

**Claim.** Laya can answer the `choice`, `score`, and `noul` question families needed for a shared evaluation, although it does not promise wire-level compatibility with Kev's HTTP API.

**Operationalisation.** Semantic compatibility means that every evaluated question can have the same evidence, instructions, options, and reference answer even if an adapter serialises it differently for each model.

**Evidence.** The [model card quick start](https://huggingface.co/convaiinnovations/laya-typed-decisions) and [agent implementation](https://github.com/NandhaKishorM/laya/blob/main/laya/agent.py) accept a state plus keyed questions of all three types. Laya returns full option probabilities for each type, along with an answer and derived confidence. Its packaged limits are 1,024 input tokens and a 256-token question-head budget, recorded in [`rl_agent_config.json`](https://huggingface.co/convaiinnovations/laya-typed-decisions/blob/main/rl_agent_config.json). The model card advises keeping choices below about 20 options.

**Not searched or run.** The exact adapter mapping has not been implemented or tested against fixtures.

**Uncertainty and failure modes.** Tokenisation differs between Laya and Kev. Identical raw text can therefore produce different truncation. The evaluation must record model-specific token counts and forbid silent truncation.

**Verdict.** Settled: the same semantic email decisions can be evaluated through model-specific adapters.

### Laya probabilities are available but not validated for personal email

**Claim.** Laya exposes temperature-scaled probability distributions, but its shipped calibration is not evidence that probabilities are calibrated on personal email.

**Operationalisation.** Calibration means that predicted probabilities agree with observed frequencies on the target population, within the limits of the evaluation sample.

**Evidence.** The [agent implementation](https://github.com/NandhaKishorM/laya/blob/main/laya/agent.py) applies softmax after configured temperature scaling. The [configuration](https://huggingface.co/convaiinnovations/laya-typed-decisions/blob/main/rl_agent_config.json) contains per-type and option-count temperature values. The model card reports ECE 0.213 and warns that the checkpoint remains over-confident and should be recalibrated on separate held-out target data before its probabilities are relied upon.

**Not searched or run.** No personal-email calibration set exists, and no recalibration was performed.

**Uncertainty and failure modes.** One hundred test emails are too few to both fit a calibration transform and give an honest final comparison. The test labels must not be used to tune temperatures or thresholds.

**Verdict.** Settled: score the returned probabilities as supplied, describe calibration cautiously, and do not recalibrate on the 100 test emails.

### Published Laya and Kev performance is not directly comparable

**Claim.** No published apples-to-apples Laya-versus-Kev result was found.

**Operationalisation.** A direct comparison requires the same held-out items, questions, labels, scoring definitions, and model-selection rules.

**Evidence.** Laya's [model card](https://huggingface.co/convaiinnovations/laya-typed-decisions) reports 0.766 accuracy, Brier 0.062, and ECE 0.213 on 400 cases and 2,000 decisions drawn from its specialised benchmark family. It explicitly calls its Jev comparison indicative because prompts and sample sizes differ. Kev's [current repository](https://github.com/jaredpalmer/kev) reports different `decision-v7` and `transfer-v4` evaluations. Kev's own [Qwen3.5 plan](https://github.com/jaredpalmer/kev/blob/main/PLAN_Qwen35.md) lists a future Laya run on Kev's frozen items, confirming that a shared public comparison was not yet available.

**Not searched or run.** No unpublished maintainer results or private benchmark data were requested. No independent peer-reviewed evaluation was found or run.

**Uncertainty and failure modes.** Maintainer-reported benchmark numbers may be correct within their own protocols, but comparing the headline numbers would confound model quality with dataset and task differences.

**Verdict.** Settled: published numbers cannot support an “as good as Kev” claim. The frozen 100-email evaluation is the relevant comparison.

### Current Kev revisions differ from the older notes

**Claim.** The current `jaredpalmer/kev-0.8b` and `jaredpalmer/kev-4b` revisions use Qwen3.5 bases and have newer results than the older Qwen3 notes in the repository's top-level `FINDINGS.md`.

**Operationalisation.** A reproducible result names the exact Hugging Face revision and base-model revision rather than using a moving repository name alone.

**Evidence.** The current [Kev 0.8B card](https://huggingface.co/jaredpalmer/kev-0.8b), [Kev 4B card](https://huggingface.co/jaredpalmer/kev-4b), and [Kev repository](https://github.com/jaredpalmer/kev) document Qwen3.5 bases, current evaluation results, fitted temperatures, and tags for earlier checkpoints.

**Not searched or run.** The exact commit hashes to freeze for the implementation have not yet been selected or downloaded.

**Uncertainty and failure modes.** The model repositories are active. Re-running against an unpinned `main` revision could change results.

**Verdict.** Settled: pin and record exact revisions before the first prediction.

## Shared reading

Laya belongs in the controlled personal-email evaluation because its question families and probability outputs can be mapped to the same semantic decisions as Kev. Its small size makes local execution plausible. The evaluation may compare efficacy on the 100 frozen emails, but it must not claim that the public Laya and Kev benchmark numbers are directly comparable.

## Remaining bounded unknowns

- Actual Laya latency and memory use on the user's M1 Mac will be measured with synthetic and then frozen email inputs.
- Adapter equivalence will be checked with hand-written micro-fixtures before real messages are scored.
- Target-domain calibration cannot be established strongly from 100 emails; probability scores and a descriptive reliability view will be reported with uncertainty.

## Inquiry status

Confirmed by the user on 21 September 2026. Laya will be included through a model-specific adapter and judged on the shared frozen email evaluation. Published Laya and Kev headline figures will not be compared as though they came from one benchmark.
