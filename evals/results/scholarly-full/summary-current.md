# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 138/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 5 | +10.0 | [-30.0, +60.0] |
| development | sonnet-low | 4 | +75.0 | [+25.0, +100.0] |
| development | sonnet-high | 5 | +60.0 | [+20.0, +100.0] |
| development | opus-low | 3 | +33.3 | [+0.0, +100.0] |
| development | opus-xhigh | 5 | +50.0 | [-30.0, +100.0] |
| development | fable | 5 | +80.0 | [+40.0, +100.0] |
| development | astra-medium | 4 | +75.0 | [+25.0, +100.0] |
| development | astra-high | 5 | +20.0 | [+0.0, +60.0] |
| development | sol-low | 4 | +50.0 | [+0.0, +100.0] |
| development | luna-medium | 4 | +25.0 | [-50.0, +100.0] |
| development | argon-high | 3 | +16.7 | [-50.0, +100.0] |
| development | flash-high | 3 | +33.3 | [+0.0, +100.0] |
| development | claude-all | 3 | +38.9 | [+8.3, +83.3] |
| development | codex-all | 4 | +43.8 | [+12.5, +81.2] |
| development | antigravity-all | 3 | +25.0 | [+0.0, +50.0] |
| development | all | 1 | +29.2 | [+29.2, +29.2] |
| holdout | haiku | 2 | +0.0 | [-100.0, +100.0] |
| holdout | sonnet-low | 2 | +0.0 | [-100.0, +100.0] |
| holdout | sonnet-high | 2 | +100.0 | [+100.0, +100.0] |
| holdout | opus-low | 2 | +50.0 | [+0.0, +100.0] |
| holdout | opus-xhigh | 2 | +100.0 | [+100.0, +100.0] |
| holdout | fable | 2 | -25.0 | [-50.0, +0.0] |
| holdout | astra-medium | 2 | +0.0 | [+0.0, +0.0] |
| holdout | astra-high | 2 | +25.0 | [+0.0, +50.0] |
| holdout | sol-low | 2 | -50.0 | [-100.0, +0.0] |
| holdout | luna-medium | 1 | +0.0 | [+0.0, +0.0] |
| holdout | claude-all | 2 | +37.5 | [+25.0, +50.0] |
| holdout | codex-all | 1 | -25.0 | [-25.0, -25.0] |

Combined spend so far: 152/2400 attempts, 3,035,473 known reported tokens, 48/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
