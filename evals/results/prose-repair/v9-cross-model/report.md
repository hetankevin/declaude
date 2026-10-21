# V9 small cross-model check

Same three selected development cases: two arguments and one proof. The skill, source tasks, author context, rubric and A/B order were frozen. Sol-high blind judging is used for all rows. Astra results and direct v4-vs-no-skill grades are reused from source-verified saved comparisons. These are selected development diagnostics, not fresh OOS evidence or a complete multi-model benchmark.

| Model / effort | v9 vs no skill | v4 vs no skill | v9 vs v4 |
|---|---|---|---|
| astra-high | 2W / 1T / 0L (+66.7 pp; n=3) | 1W / 2T / 0L (+33.3 pp; n=3) | 3W / 0T / 0L (+100.0 pp; n=3) |
| sol-low | 1W / 2T / 0L (+33.3 pp; n=3) | 2W / 1T / 0L (+66.7 pp; n=3) | 1W / 1T / 1L (+0.0 pp; n=3) |
| sonnet-high | 3W / 0T / 0L (+100.0 pp; n=3) | 3W / 0T / 0L (+100.0 pp; n=3) | 2W / 0T / 1L (+33.3 pp; n=3) |

Ties contribute zero. No confidence intervals or broad family ranking are claimed from three cases. Saved baselines/grades were produced earlier; requested model labels do not prove an unchanged backend. No reversed-order audit was added in this economical pass.

| Case | Model / effort | Comparison | Outcome |
|---|---|---|---|
| large-dev-a-12 | astra-high | v4 vs none | tie |
| large-dev-a-12 | astra-high | v9-dev vs none | win |
| large-dev-a-12 | astra-high | v9-dev vs v4 | win |
| large-dev-a-12 | sol-low | v4 vs none | win |
| large-dev-a-12 | sol-low | v9-dev vs none | tie |
| large-dev-a-12 | sol-low | v9-dev vs v4 | loss |
| large-dev-a-12 | sonnet-high | v4 vs none | win |
| large-dev-a-12 | sonnet-high | v9-dev vs none | win |
| large-dev-a-12 | sonnet-high | v9-dev vs v4 | win |
| large-dev-b-09 | astra-high | v4 vs none | tie |
| large-dev-b-09 | astra-high | v9-dev vs none | tie |
| large-dev-b-09 | astra-high | v9-dev vs v4 | win |
| large-dev-b-09 | sol-low | v4 vs none | tie |
| large-dev-b-09 | sol-low | v9-dev vs none | tie |
| large-dev-b-09 | sol-low | v9-dev vs v4 | win |
| large-dev-b-09 | sonnet-high | v4 vs none | win |
| large-dev-b-09 | sonnet-high | v9-dev vs none | win |
| large-dev-b-09 | sonnet-high | v9-dev vs v4 | loss |
| large-dev-b-14 | astra-high | v4 vs none | win |
| large-dev-b-14 | astra-high | v9-dev vs none | win |
| large-dev-b-14 | astra-high | v9-dev vs v4 | win |
| large-dev-b-14 | sol-low | v4 vs none | win |
| large-dev-b-14 | sol-low | v9-dev vs none | win |
| large-dev-b-14 | sol-low | v9-dev vs v4 | tie |
| large-dev-b-14 | sonnet-high | v4 vs none | win |
| large-dev-b-14 | sonnet-high | v9-dev vs none | win |
| large-dev-b-14 | sonnet-high | v9-dev vs v4 | win |

New work: 6 writing calls and 3 judge calls, 183,559 known reported tokens; 0 calls with unknown usage. The limit is nine calls with no automatic retries. The token guard is soft and includes cached input; this is not a credit or billing total.

Coverage: 12/12 new primary judgments. Missing or invalid judgments are not ties. Both fresh holdouts stay sealed. No long-horizon result, skill update, or installation change is produced by this check.
