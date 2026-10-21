# Focused development repair: final results

The two inspected defects are absent in the new drafts. Sol's excluded-runs argument keeps the facts while reducing repeated explanation. Sonnet's variance proof now says independence is not required without asserting dependence. Neither final draft has a material-error flag. This is a repair of two known development failures, not fresh generalization evidence.

| Draft / generator / effort | vs no skill | vs v4 | vs restored v9 | vs v10 | vs v11 |
|---|---|---|---|---|---|
| v11 excluded-runs / Sol low | Win | Tie | Win | Tie | — |
| v12 variance proof / Sonnet high | Win | Win | Loss | Win | Win |

Each cell is one blind comparison against a saved draft. The two rows use different candidate versions and cases. Sol was not rerun after the proof-only v12 amendment, so its row is evidence for the v11 core, which v12 retains exactly, not a tested v12 Sol result.

## What changed and what remains

V11 gives each explanation one place in the argument, keeps qualifications beside the claims they limit, and requires informal mathematical explanations to hold in allowed boundary cases. All supporting references remain unchanged from v10. The Sol draft groups exclusions with their reasons and places the methodological compromise with its cost. It beats restored v9 but does not beat v4 or v10.

The first Sonnet attempt with v11 still added a false universal dependence claim. A shared construction does not establish dependence: when the sample covers the population, the average is constant. V12 changes only the proof reference to make both directions explicit: a shared construction proves neither independence nor dependence, and not requiring independence does not assert its negation. The rest of the proof guidance and the v11 core remain unchanged.

The final Sonnet draft states: “It does not require $Y$ and $Z$ to be independent, and we do not assume that they are.” Its conditional-expectation proof and displayed derivation remain. However, it loses to restored v9 on exposition: the judge prefers v9's displayed intermediate centering and pair-count normalization calculations to v12's partly inline treatment. Both drafts are mathematically faithful. Correcting the requested claim does not establish that every earlier writing gain survived.

No other cases were rerun. Existing argument and proof instructions were retained, but earlier wins on other cases were not revalidated. Packaged and installed v4 remain unchanged. No promotion is claimed.

## Evidence and validation

The author-specific Sol-high rubric, baseline drafts and case material were reused, with anonymous alternating A/B positions. There were no new order audits or independent human calibration. V12 has five of five valid judgments with no quotation qualifications. V11 has eight of eight after a disclosed reporting-only repair: one batch duplicated quotation-list keys. The review preserves both lists and validates every quotation against supplied text. Reasons, preferences and severity are unchanged; conflicting non-quotation values are rejected. One Sol/restored-v9 verdict contains these list repairs. Dropping it leaves the Sol/no-skill win and v4/v10 ties intact. Original raw answers and frozen artifacts are retained.

The unsuccessful v11 Sonnet output remains reported: it wins against no skill and v4, loses against restored v9, and ties v10, despite the dependence error. Those comparisons show why relative preference alone cannot establish fidelity.

- [V11 reviewed judgments](../v11-targeted/validated-observations.json), [repair audit](../v11-targeted/evidence-review.json), [original report](../v11-targeted/report.md).
- [V12 judgments](observations.json), [raw judge answer](judge-responses.json), [responses](responses.json), [frozen plan](plan.json).
- [V11 candidate](../../../versions/v11-dev/SKILL.md), [V12 candidate](../../../versions/v12-dev/SKILL.md).

## Cost and scope

Six model calls total: three drafts and three batched judge calls, including one additional Sonnet draft/judge pair after the first repair failed. All comparator drafts were reused. There were no automatic retries or unknown-usage attempts.

Reported usage is **150,998 tokens**, including cached input, and **9.91822 estimated Codex paid-credit equivalents**, plus **two Sonnet generation calls**. These stay below the combined 160,000-token and 20-credit guards. Credit estimates are not measured account debits or subscription percentages; coordinator usage is excluded. Both fresh holdouts remain untouched. No calls remain queued.

Revalidate without model calls with `python3 tools/review_v11_evidence.py` and `python3 tools/v12_check.py report`. The original v11 report preserves the pre-review coverage; use its reviewed observations for final outcomes. Do not regenerate drafts or reopen holdouts to reproduce reporting.
