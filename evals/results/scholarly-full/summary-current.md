# Reconciled skill versus no skill

INCOMPLETE: results below are a progress checkpoint, not a full-suite headline.

Valid paired primary judgments: 40/1920. Both judges must be present for a case/model pair to enter the table.

| Split | Model / effort | Cases | Win − loss (pp) | 95% case-bootstrap interval |
|---|---|---:|---:|---:|
| development | haiku | 2 | -25.0 | [-50.0, +0.0] |
| development | sonnet-low | 2 | +100.0 | [+100.0, +100.0] |
| development | sonnet-high | 2 | +100.0 | [+100.0, +100.0] |
| development | opus-low | 2 | +50.0 | [+0.0, +100.0] |
| development | opus-xhigh | 2 | +0.0 | [-100.0, +100.0] |
| development | fable | 2 | +100.0 | [+100.0, +100.0] |
| development | astra-medium | 2 | +100.0 | [+100.0, +100.0] |
| development | astra-high | 2 | +0.0 | [+0.0, +0.0] |
| development | sol-low | 2 | +50.0 | [+0.0, +100.0] |
| development | luna-medium | 2 | +0.0 | [-100.0, +100.0] |
| development | claude-all | 2 | +54.2 | [+25.0, +83.3] |
| development | codex-all | 2 | +37.5 | [+25.0, +50.0] |

Combined spend so far: 53/2400 attempts, 993,732 known reported tokens, 20/557 Claude writes. Includes the private companion suite; cached tokens count. Not a subscription percentage or measured bill.

Forty development and forty retrospective test cases. The candidate was frozen before this run. The two new Antigravity models use fresh paired baselines; other configurations reuse validated historical baselines, leaving a timing/backend confound. Astra-high and Sol-high judges use the same author-specific rubric. Judge agreement and reversed-order sensitivity are in summary-current.json. Neither missing nor invalid judgments count as ties. Reserved fresh holdouts remain sealed.
