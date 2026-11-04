# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 756/1920. Both judges must be present for a case/model pair to enter the table.

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
| development | argon-high | 29 | +44.8 | [+19.0, +69.0] |
| development | flash-high | 30 | +73.3 | [+53.3, +90.0] |
| development | claude-all | 13 | +51.9 | [+30.8, +72.4] |
| development | codex-all | 13 | +10.6 | [-9.6, +32.7] |
| development | antigravity-all | 29 | +58.6 | [+42.2, +75.9] |
| development | all | 12 | +33.0 | [+16.3, +49.7] |
| holdout | haiku | 14 | +35.7 | [-7.1, +75.0] |
| holdout | sonnet-low | 13 | +15.4 | [-23.1, +57.7] |
| holdout | sonnet-high | 13 | +50.0 | [+15.4, +80.8] |
| holdout | opus-low | 16 | +37.5 | [-3.1, +75.0] |
| holdout | opus-xhigh | 17 | +55.9 | [+17.6, +88.2] |
| holdout | fable | 16 | +59.4 | [+28.1, +87.5] |
| holdout | astra-medium | 16 | +6.2 | [-25.0, +34.4] |
| holdout | astra-high | 14 | +17.9 | [-14.3, +46.4] |
| holdout | sol-low | 15 | +6.7 | [-26.7, +40.0] |
| holdout | luna-medium | 14 | -14.3 | [-50.0, +25.0] |
| holdout | claude-all | 11 | +32.6 | [+7.6, +56.8] |
| holdout | codex-all | 11 | -6.8 | [-34.1, +21.6] |

Combined spend so far: 785/2400 attempts, 16,480,094 known reported tokens, 230/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
