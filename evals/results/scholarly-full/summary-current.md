# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 542/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 13 | +42.3 | [+3.8, +76.9] |
| development | sonnet-low | 13 | +73.1 | [+50.0, +92.3] |
| development | sonnet-high | 13 | +65.4 | [+38.5, +88.5] |
| development | opus-low | 12 | +58.3 | [+33.3, +83.3] |
| development | opus-xhigh | 14 | +57.1 | [+25.0, +85.7] |
| development | fable | 14 | +71.4 | [+50.0, +92.9] |
| development | astra-medium | 13 | +26.9 | [-3.8, +57.7] |
| development | astra-high | 12 | +8.3 | [+0.0, +25.0] |
| development | sol-low | 12 | +33.3 | [+4.2, +62.5] |
| development | luna-medium | 12 | -4.2 | [-54.2, +45.8] |
| development | argon-high | 19 | +55.3 | [+23.7, +84.2] |
| development | flash-high | 19 | +68.4 | [+42.1, +89.5] |
| development | claude-all | 10 | +55.0 | [+30.0, +79.2] |
| development | codex-all | 10 | +15.0 | [-8.8, +43.8] |
| development | antigravity-all | 19 | +61.8 | [+39.5, +82.9] |
| development | all | 9 | +32.9 | [+11.6, +54.2] |
| holdout | haiku | 11 | +22.7 | [-31.8, +72.7] |
| holdout | sonnet-low | 10 | +15.0 | [-35.0, +65.0] |
| holdout | sonnet-high | 10 | +40.0 | [+0.0, +80.0] |
| holdout | opus-low | 11 | +45.5 | [+4.5, +81.8] |
| holdout | opus-xhigh | 11 | +59.1 | [+9.1, +100.0] |
| holdout | fable | 10 | +45.0 | [+0.0, +90.0] |
| holdout | astra-medium | 11 | +4.5 | [-36.4, +45.5] |
| holdout | astra-high | 11 | +13.6 | [-22.7, +45.5] |
| holdout | sol-low | 10 | +0.0 | [-45.0, +50.0] |
| holdout | luna-medium | 10 | -25.0 | [-70.0, +20.0] |
| holdout | claude-all | 8 | +27.1 | [-3.1, +57.3] |
| holdout | codex-all | 9 | -8.3 | [-40.3, +26.4] |

Combined spend so far: 544/2400 attempts, 11,399,014 known reported tokens, 162/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
