# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 270/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 8 | +43.8 | [+0.0, +87.5] |
| development | sonnet-low | 7 | +85.7 | [+57.1, +100.0] |
| development | sonnet-high | 8 | +62.5 | [+25.0, +87.5] |
| development | opus-low | 6 | +66.7 | [+33.3, +100.0] |
| development | opus-xhigh | 7 | +64.3 | [+7.1, +100.0] |
| development | fable | 7 | +85.7 | [+57.1, +100.0] |
| development | astra-medium | 7 | +64.3 | [+28.6, +92.9] |
| development | astra-high | 8 | +12.5 | [+0.0, +37.5] |
| development | sol-low | 8 | +56.2 | [+25.0, +87.5] |
| development | luna-medium | 7 | +21.4 | [-42.9, +78.6] |
| development | argon-high | 8 | +62.5 | [+18.8, +93.8] |
| development | flash-high | 8 | +75.0 | [+50.0, +100.0] |
| development | claude-all | 5 | +60.0 | [+26.7, +90.0] |
| development | codex-all | 6 | +35.4 | [+4.2, +68.8] |
| development | antigravity-all | 8 | +68.8 | [+40.6, +90.6] |
| development | all | 4 | +56.2 | [+38.5, +72.9] |
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

Combined spend so far: 298/2400 attempts, 6,097,221 known reported tokens, 90/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
