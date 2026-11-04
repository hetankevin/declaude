# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 732/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 18 | +41.7 | [+8.3, +72.2] |
| development | sonnet-low | 17 | +67.6 | [+44.1, +88.2] |
| development | sonnet-high | 18 | +52.8 | [+25.0, +77.8] |
| development | opus-low | 16 | +56.2 | [+31.2, +81.2] |
| development | opus-xhigh | 18 | +66.7 | [+38.9, +88.9] |
| development | fable | 18 | +69.4 | [+50.0, +86.1] |
| development | astra-medium | 18 | +13.9 | [-13.9, +41.7] |
| development | astra-high | 16 | +6.2 | [+0.0, +18.8] |
| development | sol-low | 15 | +33.3 | [+6.7, +60.0] |
| development | luna-medium | 17 | +2.9 | [-38.2, +41.2] |
| development | argon-high | 28 | +42.9 | [+14.3, +67.9] |
| development | flash-high | 28 | +71.4 | [+50.0, +89.3] |
| development | claude-all | 13 | +51.9 | [+30.8, +72.4] |
| development | codex-all | 13 | +10.6 | [-9.6, +32.7] |
| development | antigravity-all | 28 | +57.1 | [+38.4, +74.1] |
| development | all | 12 | +33.0 | [+16.3, +49.7] |
| holdout | haiku | 14 | +35.7 | [-7.1, +75.0] |
| holdout | sonnet-low | 13 | +15.4 | [-23.1, +57.7] |
| holdout | sonnet-high | 13 | +50.0 | [+15.4, +80.8] |
| holdout | opus-low | 15 | +46.7 | [+6.7, +80.0] |
| holdout | opus-xhigh | 15 | +50.0 | [+6.7, +86.7] |
| holdout | fable | 14 | +53.6 | [+17.9, +85.7] |
| holdout | astra-medium | 15 | +6.7 | [-26.7, +36.7] |
| holdout | astra-high | 13 | +11.5 | [-19.2, +38.5] |
| holdout | sol-low | 13 | +0.0 | [-34.6, +34.6] |
| holdout | luna-medium | 14 | -14.3 | [-50.0, +25.0] |
| holdout | claude-all | 11 | +32.6 | [+7.6, +56.8] |
| holdout | codex-all | 11 | -6.8 | [-34.1, +21.6] |

Combined spend so far: 733/2400 attempts, 15,385,714 known reported tokens, 216/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
