# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 828/1920. Both judges must be present for a case/model pair to enter the table.

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
| development | argon-high | 32 | +40.6 | [+14.1, +65.6] |
| development | flash-high | 33 | +66.7 | [+45.5, +84.8] |
| development | claude-all | 13 | +51.9 | [+30.8, +72.4] |
| development | codex-all | 13 | +10.6 | [-9.6, +32.7] |
| development | antigravity-all | 32 | +53.1 | [+35.9, +70.3] |
| development | all | 12 | +33.0 | [+16.3, +49.7] |
| holdout | haiku | 17 | +26.5 | [-14.7, +64.7] |
| holdout | sonnet-low | 16 | +18.8 | [-18.8, +59.4] |
| holdout | sonnet-high | 16 | +50.0 | [+18.8, +75.0] |
| holdout | opus-low | 19 | +42.1 | [+7.9, +73.7] |
| holdout | opus-xhigh | 20 | +47.5 | [+12.5, +80.0] |
| holdout | fable | 19 | +60.5 | [+31.6, +86.8] |
| holdout | astra-medium | 19 | +7.9 | [-18.4, +34.2] |
| holdout | astra-high | 17 | +20.6 | [-11.8, +50.0] |
| holdout | sol-low | 18 | +8.3 | [-19.4, +38.9] |
| holdout | luna-medium | 17 | -11.8 | [-41.2, +17.6] |
| holdout | claude-all | 14 | +32.7 | [+11.9, +51.8] |
| holdout | codex-all | 14 | -1.8 | [-25.9, +24.1] |

Combined spend so far: 846/2400 attempts, 17,790,552 known reported tokens, 246/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
