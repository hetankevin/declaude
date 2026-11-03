# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 58/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 4 | +12.5 | [-37.5, +75.0] |
| development | sonnet-low | 2 | +100.0 | [+100.0, +100.0] |
| development | sonnet-high | 3 | +66.7 | [+0.0, +100.0] |
| development | opus-low | 2 | +50.0 | [+0.0, +100.0] |
| development | opus-xhigh | 3 | +33.3 | [-100.0, +100.0] |
| development | fable | 4 | +100.0 | [+100.0, +100.0] |
| development | astra-medium | 2 | +100.0 | [+100.0, +100.0] |
| development | astra-high | 3 | +0.0 | [+0.0, +0.0] |
| development | sol-low | 3 | +66.7 | [+0.0, +100.0] |
| development | luna-medium | 3 | +33.3 | [-100.0, +100.0] |
| development | claude-all | 2 | +54.2 | [+25.0, +83.3] |
| development | codex-all | 2 | +37.5 | [+25.0, +50.0] |

Combined spend so far: 85/2400 attempts, 1,667,764 known reported tokens, 30/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
