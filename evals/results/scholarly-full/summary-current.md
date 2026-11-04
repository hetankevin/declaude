# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 598/1920. Both judges must be present for a case/model pair to enter the table.

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
| development | argon-high | 21 | +54.8 | [+23.8, +81.0] |
| development | flash-high | 21 | +66.7 | [+38.1, +90.5] |
| development | claude-all | 10 | +55.0 | [+30.0, +79.2] |
| development | codex-all | 10 | +15.0 | [-8.8, +43.8] |
| development | antigravity-all | 21 | +60.7 | [+40.5, +79.8] |
| development | all | 9 | +32.9 | [+11.6, +54.2] |
| holdout | haiku | 13 | +30.8 | [-15.4, +76.9] |
| holdout | sonnet-low | 12 | +20.8 | [-20.8, +62.5] |
| holdout | sonnet-high | 12 | +45.8 | [+8.3, +79.2] |
| holdout | opus-low | 14 | +42.9 | [+3.6, +78.6] |
| holdout | opus-xhigh | 14 | +46.4 | [+0.0, +85.7] |
| holdout | fable | 13 | +57.7 | [+19.2, +92.3] |
| holdout | astra-medium | 14 | +7.1 | [-28.6, +39.3] |
| holdout | astra-high | 12 | +12.5 | [-20.8, +41.7] |
| holdout | sol-low | 12 | +0.0 | [-37.5, +37.5] |
| holdout | luna-medium | 13 | -15.4 | [-53.8, +26.9] |
| holdout | claude-all | 10 | +30.0 | [+4.2, +56.7] |
| holdout | codex-all | 10 | -7.5 | [-36.2, +25.0] |

Combined spend so far: 606/2400 attempts, 12,755,395 known reported tokens, 181/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
