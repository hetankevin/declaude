# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 470/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 11 | +50.0 | [+18.2, +81.8] |
| development | sonnet-low | 11 | +77.3 | [+54.5, +100.0] |
| development | sonnet-high | 12 | +66.7 | [+41.7, +91.7] |
| development | opus-low | 10 | +60.0 | [+30.0, +90.0] |
| development | opus-xhigh | 11 | +54.5 | [+18.2, +86.4] |
| development | fable | 11 | +81.8 | [+54.5, +100.0] |
| development | astra-medium | 10 | +45.0 | [+15.0, +75.0] |
| development | astra-high | 11 | +9.1 | [+0.0, +27.3] |
| development | sol-low | 11 | +36.4 | [+9.1, +68.2] |
| development | luna-medium | 10 | +5.0 | [-50.0, +60.0] |
| development | argon-high | 16 | +65.6 | [+34.4, +90.6] |
| development | flash-high | 16 | +87.5 | [+68.8, +100.0] |
| development | claude-all | 9 | +61.1 | [+37.0, +84.3] |
| development | codex-all | 9 | +19.4 | [-6.9, +48.6] |
| development | antigravity-all | 16 | +76.6 | [+57.8, +92.2] |
| development | all | 6 | +52.8 | [+36.8, +68.1] |
| holdout | haiku | 10 | +15.0 | [-40.0, +70.0] |
| holdout | sonnet-low | 9 | +22.2 | [-33.3, +66.7] |
| holdout | sonnet-high | 9 | +55.6 | [+22.2, +88.9] |
| holdout | opus-low | 10 | +50.0 | [+5.0, +90.0] |
| holdout | opus-xhigh | 10 | +75.0 | [+35.0, +100.0] |
| holdout | fable | 9 | +61.1 | [+22.2, +88.9] |
| holdout | astra-medium | 10 | +15.0 | [-30.0, +55.0] |
| holdout | astra-high | 10 | +25.0 | [+0.0, +55.0] |
| holdout | sol-low | 9 | +5.6 | [-44.4, +55.6] |
| holdout | luna-medium | 9 | -16.7 | [-61.1, +33.3] |
| holdout | claude-all | 7 | +36.9 | [+9.5, +64.3] |
| holdout | codex-all | 8 | +1.6 | [-28.1, +35.9] |

Combined spend so far: 473/2400 attempts, 9,881,656 known reported tokens, 140/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
