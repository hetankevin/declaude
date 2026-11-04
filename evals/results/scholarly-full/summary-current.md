# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 352/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 9 | +38.9 | [+0.0, +77.8] |
| development | sonnet-low | 9 | +77.8 | [+44.4, +100.0] |
| development | sonnet-high | 10 | +60.0 | [+30.0, +90.0] |
| development | opus-low | 8 | +62.5 | [+25.0, +100.0] |
| development | opus-xhigh | 9 | +61.1 | [+11.1, +94.4] |
| development | fable | 9 | +77.8 | [+44.4, +100.0] |
| development | astra-medium | 8 | +56.2 | [+25.0, +87.5] |
| development | astra-high | 9 | +11.1 | [+0.0, +33.3] |
| development | sol-low | 9 | +50.0 | [+22.2, +77.8] |
| development | luna-medium | 8 | +6.2 | [-56.2, +68.8] |
| development | argon-high | 11 | +54.5 | [+13.6, +90.9] |
| development | flash-high | 11 | +81.8 | [+54.5, +100.0] |
| development | claude-all | 7 | +57.1 | [+28.6, +84.5] |
| development | codex-all | 7 | +26.8 | [-3.6, +60.7] |
| development | antigravity-all | 11 | +68.2 | [+45.5, +88.6] |
| development | all | 4 | +56.2 | [+38.5, +72.9] |
| holdout | haiku | 7 | +21.4 | [-42.9, +78.6] |
| holdout | sonnet-low | 7 | +14.3 | [-42.9, +71.4] |
| holdout | sonnet-high | 6 | +50.0 | [+16.7, +83.3] |
| holdout | opus-low | 7 | +57.1 | [+14.3, +92.9] |
| holdout | opus-xhigh | 7 | +92.9 | [+78.6, +100.0] |
| holdout | fable | 6 | +58.3 | [+8.3, +100.0] |
| holdout | astra-medium | 7 | +14.3 | [-28.6, +57.1] |
| holdout | astra-high | 7 | +28.6 | [+7.1, +57.1] |
| holdout | sol-low | 6 | -41.7 | [-75.0, -8.3] |
| holdout | luna-medium | 6 | -25.0 | [-75.0, +33.3] |
| holdout | claude-all | 5 | +38.3 | [+25.0, +51.7] |
| holdout | codex-all | 5 | -17.5 | [-37.5, +5.0] |

Combined spend so far: 363/2400 attempts, 7,433,147 known reported tokens, 110/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
