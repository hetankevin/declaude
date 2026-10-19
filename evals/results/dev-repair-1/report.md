# Small development repair

This diagnostic compares v6-dev with saved v5a outputs on six development/tune tasks. The revision prioritizes document organization and keeps operational conditions together. It also changes the translation guidance to discourage compression that sacrifices explanation.

Budget: **12/12 Codex calls, zero Claude calls**. Six generation slots use Sol low or Luna medium. Six blind grading slots use Astra high with the frozen pairwise rubric. No retries, order audits, new baseline generations, or holdout calls.

Positive percentage points favor v6-dev. Net advantage is win rate minus loss rate; ties contribute zero and remain in the denominator.

| Dimension | Win / tie / loss | Net advantage (pp) |
|---|---:|---:|
| Overall | 1 / 3 / 2 | -16.7 |
| meaning | 0 / 6 / 0 | +0.0 |
| naturalness | 0 / 5 / 1 | -16.7 |
| progression | 1 / 3 / 2 | -16.7 |
| voice | 0 / 5 / 1 | -16.7 |
| proof | 0 / 1 / 0 | +0.0 |

| Development case | Generator | Outcome | Organization |
|---|---|---|---|
| large-dev-a-01 | sol-low | loss | loss |
| large-dev-b-01 | luna-medium | tie | tie |
| large-dev-b-03 | sol-low | win | win |
| large-dev-a-07 | luna-medium | loss | loss |
| large-dev-a-13 | sol-low | tie | tie |
| large-dev-a-17 | luna-medium | tie | tie |

Material-error flags: 0 candidate, 0 reference. Missing pairs: 0. Missing results are not ties.

These tasks were deliberately selected for diagnosis, not random sampling: three practical documents, one research summary, one proof, and one already-polished control. Model and task effects are confounded. One same-family judge and one generation per condition cannot establish a reliable ranking. Existing baseline outputs were reused, so stochastic generation differences remain.

The repair was motivated by previously examined holdout feedback. This is development work; the old holdout is no longer fresh evidence for this new revision. Its cases were not used in these calls. The original experiment and its selected candidate remain unchanged.

## Decision

Do not promote v6-dev: the pilot has one win, three ties, and two losses, with no advantage on progression or overall quality. The handover improved its grouping, while the access notice grouped access details less cleanly and the research summary ended less effectively. Meaning tied in every comparison; the proof and polished control tied overall. These are small diagnostic observations, not causal estimates.

A narrower v6b-dev draft retains all v5a instructions and references and adds one paragraph limited to organizing practical documents. It is **untested and not installed**. The packaged and installed release remains v4. No more calls were made. See [follow-up status](followup.json).

[Frozen plan](plan.json) · [Paired outputs](responses.json) · [Blinded judgments](observations.json) · [Summary](summary.json)
