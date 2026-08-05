# PRBench B sweep — results

Items: 200 (100 standard + 100 hard single-turn); judged responses: 600; batched-criteria judging (deviation documented in sweep_judge.py).

## Tier ladder (mean PRBench-style score)

| model | overall | standard | hard | hard − standard |
|---|---|---|---|---|
| Haiku 4.5 | 0.303 | 0.405 | 0.201 | -0.204 |
| Sonnet 4.6 | 0.380 | 0.481 | 0.278 | -0.203 |
| Opus 4.6 | 0.397 | 0.514 | 0.279 | -0.235 |

## Unsatisfied rate by criteria category (positive criteria)

| category | Haiku 4.5 | Sonnet 4.6 | Opus 4.6 | n/model |
|---|---|---|---|---|
| Process Transparency & Auditability | 78% | 73% | 70% | 228 |
| Supplemental Insight | 76% | 65% | 67% | 118 |
| Risk & Regulatory Disclosure | 71% | 61% | 60% | 664 |
| Financial Accuracy | 69% | 59% | 56% | 830 |
| Handling Uncertainty | 68% | 66% | 73% | 183 |
| Practical Utility | 64% | 63% | 64% | 773 |
| Instruction Following | 50% | 44% | 48% | 127 |
