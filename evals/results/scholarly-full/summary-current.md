# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 664/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 15 | +43.3 | [+10.0, +73.3] |
| development | sonnet-low | 14 | +75.0 | [+53.6, +92.9] |
| development | sonnet-high | 15 | +53.3 | [+20.0, +83.3] |
| development | opus-low | 13 | +61.5 | [+30.8, +84.6] |
| development | opus-xhigh | 16 | +62.5 | [+34.4, +87.5] |
| development | fable | 15 | +70.0 | [+46.7, +90.0] |
| development | astra-medium | 15 | +20.0 | [-10.0, +50.0] |
| development | astra-high | 13 | +7.7 | [+0.0, +23.1] |
| development | sol-low | 13 | +30.8 | [+3.8, +57.7] |
| development | luna-medium | 14 | -10.7 | [-57.1, +35.7] |
| development | argon-high | 25 | +44.0 | [+18.0, +70.0] |
| development | flash-high | 25 | +72.0 | [+48.0, +92.0] |
| development | claude-all | 11 | +56.1 | [+34.1, +77.3] |
| development | codex-all | 11 | +10.2 | [-13.6, +35.2] |
| development | antigravity-all | 25 | +58.0 | [+41.0, +75.0] |
| development | all | 10 | +33.3 | [+14.2, +52.1] |
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

Combined spend so far: 671/2400 attempts, 14,089,001 known reported tokens, 198/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
