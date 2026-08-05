# P2 results summary

## Accuracy by model and grader (n=148 items: 38 basic + 46 assumption + 64 conceptual)

| model | grader | overall | basic | assumption | conceptual |
|---|---|---|---|---|---|
| claude-haiku-4-5 | naive_em | 0.0% | 0.0% | 0.0% | 0.0% |
| claude-haiku-4-5 | improved | 50.0% | 55.3% | 6.5% | 78.1% |
| claude-sonnet-4-6 | naive_em | 0.0% | 0.0% | 0.0% | 0.0% |
| claude-sonnet-4-6 | improved | 53.4% | 52.6% | 13.0% | 82.8% |
| claude-opus-4-6 | naive_em | 0.0% | 0.0% | 0.0% | 0.0% |
| claude-opus-4-6 | improved | 56.1% | 50.0% | 17.4% | 87.5% |

## Tier separation (adjacent-tier accuracy gaps)

| grader | haiku | sonnet | opus | sonnet-haiku | opus-sonnet | monotone? |
|---|---|---|---|---|---|---|
| naive_em | 0.0% | 0.0% | 0.0% | +0.0% | +0.0% | yes |
| improved | 50.0% | 53.4% | 56.1% | +3.4% | +2.7% | yes |

## Format-invariance probe (correct-by-construction gold variants)

Probes: 462 total, 340 non-identity.

| grader | acceptance (all) | acceptance (non-identity) |
|---|---|---|
| naive_em | 26.8% | 0.6% |
| numeric stage of improved | 100.0% | 100.0% |

## Grader vs. human adjudication

Labeled pairs: 63

| grader | agreement | Cohen's kappa |
|---|---|---|
| naive_em | 60.3% | -0.000 |
| improved | 92.1% | 0.840 |

## Adjudicator failure categories (incorrect responses only)

| model | category | count |
|---|---|---|
| claude-haiku-4-5 | missing_assumption | 37 |
| claude-haiku-4-5 | wrong_value_or_arithmetic | 20 |
| claude-haiku-4-5 | wrong_concept | 17 |
| claude-sonnet-4-6 | missing_assumption | 46 |
| claude-sonnet-4-6 | wrong_value_or_arithmetic | 16 |
| claude-sonnet-4-6 | wrong_concept | 6 |
| claude-sonnet-4-6 | refused_or_incomplete | 1 |
| claude-opus-4-6 | missing_assumption | 44 |
| claude-opus-4-6 | wrong_value_or_arithmetic | 15 |
| claude-opus-4-6 | wrong_concept | 6 |

Incorrect responses flagged as *defensible alternative convention*: 114 / 208
