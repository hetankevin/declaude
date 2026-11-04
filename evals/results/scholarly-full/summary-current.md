# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 1030/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 19 | +44.7 | [+13.2, +73.7] |
| development | sonnet-low | 18 | +61.1 | [+36.1, +83.3] |
| development | sonnet-high | 19 | +50.0 | [+23.7, +73.7] |
| development | opus-low | 17 | +58.8 | [+35.3, +82.4] |
| development | opus-xhigh | 19 | +65.8 | [+39.5, +86.8] |
| development | fable | 19 | +60.5 | [+34.2, +84.2] |
| development | astra-medium | 19 | +13.2 | [-13.2, +39.5] |
| development | astra-high | 17 | +0.0 | [-17.6, +17.6] |
| development | sol-low | 16 | +31.2 | [+6.2, +56.2] |
| development | luna-medium | 18 | -2.8 | [-44.4, +36.1] |
| development | argon-high | 39 | +38.5 | [+15.4, +60.3] |
| development | flash-high | 40 | +67.5 | [+50.0, +82.5] |
| development | claude-all | 14 | +49.4 | [+29.2, +69.0] |
| development | codex-all | 14 | +6.2 | [-14.3, +28.6] |
| development | antigravity-all | 39 | +52.6 | [+36.5, +67.3] |
| development | all | 13 | +30.4 | [+14.4, +46.5] |
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
| holdout | argon-high | 39 | +21.8 | [-2.6, +44.9] |
| holdout | flash-high | 38 | +76.3 | [+63.2, +89.5] |
| holdout | claude-all | 14 | +32.7 | [+11.9, +51.8] |
| holdout | codex-all | 14 | -1.8 | [-25.9, +24.1] |
| holdout | antigravity-all | 38 | +50.7 | [+36.2, +65.8] |
| holdout | all | 11 | +33.3 | [+16.7, +50.0] |

Combined spend so far: 1444/2400 attempts, 29,811,774 known reported tokens, 249/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
