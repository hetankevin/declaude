# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 224/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 6 | +25.0 | [-16.7, +66.7] |
| development | sonnet-low | 5 | +80.0 | [+40.0, +100.0] |
| development | sonnet-high | 6 | +66.7 | [+33.3, +100.0] |
| development | opus-low | 4 | +50.0 | [+0.0, +100.0] |
| development | opus-xhigh | 6 | +58.3 | [-8.3, +100.0] |
| development | fable | 6 | +83.3 | [+50.0, +100.0] |
| development | astra-medium | 5 | +70.0 | [+30.0, +100.0] |
| development | astra-high | 6 | +16.7 | [+0.0, +50.0] |
| development | sol-low | 5 | +60.0 | [+20.0, +100.0] |
| development | luna-medium | 5 | +40.0 | [-40.0, +100.0] |
| development | argon-high | 6 | +58.3 | [+8.3, +100.0] |
| development | flash-high | 6 | +66.7 | [+33.3, +100.0] |
| development | claude-all | 4 | +54.2 | [+16.7, +91.7] |
| development | codex-all | 5 | +47.5 | [+20.0, +77.5] |
| development | antigravity-all | 6 | +62.5 | [+29.2, +91.7] |
| development | all | 3 | +58.3 | [+29.2, +79.2] |
| holdout | haiku | 5 | +60.0 | [-20.0, +100.0] |
| holdout | sonnet-low | 5 | +0.0 | [-80.0, +80.0] |
| holdout | sonnet-high | 4 | +75.0 | [+25.0, +100.0] |
| holdout | opus-low | 5 | +50.0 | [-10.0, +100.0] |
| holdout | opus-xhigh | 5 | +100.0 | [+100.0, +100.0] |
| holdout | fable | 4 | +37.5 | [-25.0, +100.0] |
| holdout | astra-medium | 5 | +0.0 | [-40.0, +50.0] |
| holdout | astra-high | 5 | +30.0 | [+0.0, +70.0] |
| holdout | sol-low | 4 | -37.5 | [-75.0, +0.0] |
| holdout | luna-medium | 4 | -37.5 | [-75.0, +0.0] |
| holdout | claude-all | 3 | +38.9 | [+25.0, +50.0] |
| holdout | codex-all | 3 | -33.3 | [-50.0, -25.0] |

Combined spend so far: 237/2400 attempts, 4,918,011 known reported tokens, 72/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
