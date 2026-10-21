# V10: several repairs, fidelity requirement not met

V10 changes only the core instructions. It asks the writer to place decisions with reasons and qualifications with the claims they limit, rather than allocating separate blocks to every rhetorical role. It directs proof calculations to appear when their purpose has been established, and finished artifacts to omit unsolicited production notes. All references, including proof and research-voice guidance, are byte-identical to restored v9. The existing fidelity distinctions and final checks remain.

The targeted check covers six Sol-low drafts and seven Sonnet-high drafts, selected before running to include known regressions and retained-gain checks. All no-skill, v4 and restored-v9 comparators were reused. One frozen author-specific Sol-high judge evaluated anonymous pairs. The samples differ across models and were chosen after inspecting previous failures; aggregate differences cannot rank model families or establish OOS generalization.

## Changes that helped

- **Sonnet, drainage study:** v10 integrates the causal limitation with the result and explains why cleaning remains a competing explanation. It avoids the repeated defensive commentary in restored v9. It wins against all three comparators.
- **Sonnet, warning signs:** limitations now support the recommendation and operational conditions. The judge prefers this to restored v9's repeated disclaimer and awkward backward reference. It wins against all three comparators, with no new fidelity flag.
- **Sonnet, travel invitation:** the artifact ends as an invitation, without appended production advice. It wins against restored v9 and ties v4.
- **Sonnet, projection proof:** two connected proof phases preserve the calculations and the reason for projection while avoiding repeated scope remarks. It wins against restored v9 and ties v4. Its no-skill verdict remains invalid because of a required nonverbatim source quotation; it is not counted as a win or a tie.
- **Sol, maintenance note:** the logging location and timing are stated once. It wins against restored v9 and ties v4.

Sol's variance proof now places the conditional residual calculation after the variance decomposition establishes the need for it. Both the revised and restored-v9 proofs are nevertheless judged comparably suitable: a tie. This is an observed change in order, not a confirmed preference gain. The survey conclusions and the worksheet explanation-order check also tie restored v9.

## Failures that prevent promotion

**Sol's excluded-runs argument worsens.** V10 repeats the accounting explanation and discusses the shared-explanation compromise before returning to the workload that motivates it. Restored v9 keeps that compromise with its rationale. V10 loses to both restored v9 and v4. Thus Sol's direct comparison with restored v9 is one win, four ties, and one loss: 0 pp.

**Sonnet loses a mathematical fidelity gain.** In the variance proof, it adds: “Indeed they are dependent, since Y is one of the two values averaged in Z.” The source did not establish dependence. When N=2, the pair is the entire fixed population and Z is constant, so Z is independent of Y. The added universal assertion is false. The judge flags the same draft in all three comparisons; those three flags are one distinct output defect. Restored v9 avoided the assertion, so v10 loses that direct comparison. This is an explicit failure of the user's requirement to keep fidelity gains despite preserving the written safeguards and proof reference.

Sonnet still has four wins, two ties and one loss against restored v9 (+42.9 pp) on these selected cases. That favorable aggregate does not compensate for the fidelity regression. V10 is retained as an unpromoted development candidate. Packaged and installed v4 remain unchanged. No fresh holdout was opened or run, and no additional calls will automatically follow.

## Completion and evidence limits

All 13 drafts and all 10 planned grading batches finished. There are 38 validated comparisons out of 39. One batch repeated an identical empty source-quote key. Collapsing that duplicate without changing any values recovered two valid verdicts; the remaining proof-source quotation is nonverbatim and remains rejected. The raw response and repair log are retained. There are no optional-source-quote-qualified verdicts in this run. Missing grades are never ties. Sonnet/no-skill has six accepted comparisons; Sonnet's other comparisons have seven; Sol has six throughout.

The planned work used 23 model calls. Two initial sandbox transport attempts produced no draft, making 25 CLI attempts total. Known usage is 484,495 reported tokens and 29.44 estimated Standard Codex paid-credit equivalents, plus seven successful Sonnet calls. Claude's initial authentication failure reports zero API usage; the original Codex routing failure retains a 30,000-token/3-credit reservation. Charged totals are 514,495 tokens and 32.44 credits, below the 700k/90 guards. These figures exclude coordinator usage and are not account debits or subscription percentages. No model calls were used for reporting repairs.
