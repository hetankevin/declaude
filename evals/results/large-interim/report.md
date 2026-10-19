# Interim larger benchmark

**Incomplete snapshot. This is not the final preregistered comparison.** Execution was paused. No new model calls were made to build this report.

Snapshot cutoff: 2026-10-19T21:13:55.094898+00:00.

Saved here: 2012/2400 writing outputs, 1458/2400 absolute scorecards, and 2078/3820 pairwise judgments (including order audits).

Exact available outputs and grades are included, including unfinished cases. The tables below use only cases complete across all ten configurations: both comparisons and both judges, with planned order audits, for pairwise tables; all three arms for absolute tables. Missing work is never scored as zero. The two table types can cover different cases.

Completed cases are an execution-order subset, not a random new sample. Holdout coverage is especially small. These numbers must not be used for further tuning, stable model rankings, or a claim about the full held-out set.

## Pairwise comparison

Net advantage = win rate minus loss rate in percentage points. Ties contribute zero and remain in the denominator. Each complete case has the same ten configurations and two judges. Audits are excluded from performance.

| Split | Complete cases / planned | Comparison | Win / tie / loss | Net advantage (pp) |
|---|---:|---|---:|---:|
| development | 39/40 | v5a vs none | 323 / 266 / 191 | +16.92 |
| development | 39/40 | v5a vs v4 | 213 / 381 / 186 | +3.46 |
| holdout | 3/40 | v5a vs none | 15 / 15 / 30 | -25.00 |
| holdout | 3/40 | v5a vs v4 | 18 / 26 / 16 | +3.33 |

## Absolute grades

Assertion rates are assertion-weighted. Holistic scores are out of 5.

| Split | Complete cases / planned | Arm | Assertions | Fidelity | Holistic | Median words |
|---|---:|---|---:|---:|---:|---:|
| development | 34/40 | none | 98.01% | 98.85% | 4.356 | 345 |
| development | 34/40 | v4 | 99.14% | 99.56% | 4.591 | 312 |
| development | 34/40 | v5a | 98.87% | 99.38% | 4.606 | 314 |
| holdout | 8/40 | none | 96.96% | 98.15% | 4.237 | 411 |
| holdout | 8/40 | v4 | 97.68% | 100.00% | 4.388 | 366 |
| holdout | 8/40 | v5a | 97.68% | 100.00% | 4.350 | 362 |

## Files

- [Available writing outputs](responses.json)
- [Available absolute scorecards](absolute-observations.json)
- [Pairwise judgments: v5a vs no skill](pairwise-v5a-vs-none.json)
- [Pairwise judgments: v5a vs v4](pairwise-v5a-vs-v4.json)
- [Summary, including model/effort breakdowns](summary.json)
- [Coverage and included case IDs](coverage.json)

The selected revision remains v5a under the development-only rule. Neither these results nor later held-out results may change that selection or the frozen grader. Model judgments are not human validation. Raw CLI envelopes and personal source material are not published.
