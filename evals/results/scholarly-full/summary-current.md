# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 204/1920. Both judges must be present for a case/model pair to enter the table.

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
| development | argon-high | 6 | +58.3 | [+8.3, +100.0] |
| development | flash-high | 6 | +66.7 | [+33.3, +100.0] |
| development | claude-all | 3 | +38.9 | [+8.3, +83.3] |
| development | codex-all | 4 | +43.8 | [+12.5, +81.2] |
| development | antigravity-all | 6 | +62.5 | [+29.2, +91.7] |
| development | all | 2 | +47.9 | [+29.2, +66.7] |
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

Combined spend so far: 218/2400 attempts, 4,416,462 known reported tokens, 66/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
