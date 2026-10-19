# Small development repair

This diagnostic compares v7-dev with saved no-skill outputs on six development/tune tasks. Prose instructions were shortened and reframed as targeted edits rather than a mandatory rewrite. The proof and research-voice reference files are byte-identical to v5a.

Budget: **12/12 Codex calls, zero Claude calls**. Six generation slots use Astra medium, Sol low, or Luna medium. Six blind grading slots use Astra high with the frozen pairwise rubric. No retries, order audits, new baseline generations, or holdout calls.

Positive percentage points favor v7-dev. Net advantage is win rate minus loss rate; ties contribute zero and remain in the denominator.

| Dimension | Win / tie / loss | Net advantage (pp) |
|---|---:|---:|
| Overall | 1 / 4 / 1 | +0.0 |
| meaning | 1 / 4 / 1 | +0.0 |
| naturalness | 0 / 6 / 0 | +0.0 |
| progression | 0 / 6 / 0 | +0.0 |
| voice | 0 / 6 / 0 | +0.0 |
| proof | 0 / 1 / 0 | +0.0 |

| Development case | Generator | Outcome | Organization |
|---|---|---|---|
| large-dev-a-01 | astra-medium | tie | tie |
| large-dev-b-03 | sol-low | tie | tie |
| large-dev-a-07 | luna-medium | win | tie |
| large-dev-a-09 | astra-medium | loss | tie |
| large-dev-a-13 | sol-low | tie | tie |
| large-dev-a-17 | luna-medium | tie | tie |

Material-error flags: 1 candidate, 1 reference. Missing pairs: 0. Missing results are not ties.

These tasks were deliberately selected for diagnosis, not random sampling: two practical documents, one research summary, one argument, one proof, and one already-polished control. Model and task effects are confounded. One same-family judge and one generation per condition cannot establish a reliable ranking. Existing baseline outputs were reused, so stochastic generation differences remain.

The repair was motivated by previously examined holdout feedback. This is development work; the old holdout is no longer fresh evidence for this new revision. Its cases were not used in these calls. The original experiment and its selected candidate remain unchanged.

## Decision

Not promoted. The original judge gives one win, four ties, and one loss (0 pp overall); progression ties in all six comparisons. The non-ties are fidelity findings: the baseline imported an unsupported premise from a tone-only sample, while the candidate strengthened a tentative concession in another task. Proof and polished control tie. These diagnoses are plausible, but the scores do not establish that the judge matches the author’s writing preferences.

The user questioned the evaluator during this run. All twelve calls had already started when scheduling was paused; the two in-flight judgments were saved without adding calls. No personal-alignment regrading has occurred. Read the [judge alignment audit](../judge-audit/report.md) before using these scores to choose a skill. The prepared contextual rubric is a draft, and the installed release remains v4.

[Frozen plan](plan.json) · [Paired outputs](responses.json) · [Original blinded judgments](observations.json) · [Summary](summary.json)
