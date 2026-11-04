# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 398/1920. Both judges must be present for a case/model pair to enter the table.

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
| development | argon-high | 13 | +61.5 | [+23.1, +92.3] |
| development | flash-high | 13 | +84.6 | [+61.5, +100.0] |
| development | claude-all | 7 | +57.1 | [+28.6, +84.5] |
| development | codex-all | 7 | +26.8 | [-3.6, +60.7] |
| development | antigravity-all | 13 | +73.1 | [+50.0, +92.3] |
| development | all | 4 | +56.2 | [+38.5, +72.9] |
| holdout | haiku | 9 | +16.7 | [-50.0, +77.8] |
| holdout | sonnet-low | 8 | +25.0 | [-37.5, +75.0] |
| holdout | sonnet-high | 8 | +62.5 | [+25.0, +87.5] |
| holdout | opus-low | 9 | +66.7 | [+33.3, +94.4] |
| holdout | opus-xhigh | 9 | +94.4 | [+83.3, +100.0] |
| holdout | fable | 8 | +68.8 | [+25.0, +100.0] |
| holdout | astra-medium | 9 | +11.1 | [-33.3, +55.6] |
| holdout | astra-high | 9 | +27.8 | [-5.6, +61.1] |
| holdout | sol-low | 8 | -6.2 | [-56.2, +43.8] |
| holdout | luna-medium | 8 | -18.8 | [-68.8, +37.5] |
| holdout | claude-all | 6 | +48.6 | [+29.2, +72.2] |
| holdout | codex-all | 7 | -3.6 | [-33.9, +33.9] |

Combined spend so far: 411/2400 attempts, 8,558,958 known reported tokens, 125/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
