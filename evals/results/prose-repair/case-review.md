# What changed in the writing

These are development examples, selected to show the proposed mechanism and a remaining failure. They are not a representative sample or independent human preference labels. The [tuning report](v8-dev-tune/report.md) includes every result, and [responses.json](v8-dev-tune/responses.json) contains the full source-matched outputs.

## Making the reason for a construction explicit

In `large-dev-a-11`, the task is to develop a teacher's modest proposal from an uncontrolled classroom observation. The source distinguishes successful copying from understanding, then proposes asking pupils to explain two methods.

Sol low with v8 connects these steps explicitly: “That gives me a reason to ask for an explanation as well as a calculation.” It then says what the new task enables: “This would give us something to examine beyond whether they can repeat the steps.” These sentences do explanatory work without adding a claim that the proposed worksheet has been shown to improve attainment. The revision retains the time cost and the limited purpose of the trial. Both judges prefer it to both baselines.

The v4 output had also introduced the assurance “without adding a page or taking more lesson time,” although the source acknowledges a lesson-time cost. Astra calls that a minor material error; Sol does not establish a material error but still prefers v8's explicit tradeoff and reasoning. The shared preference therefore does not depend entirely on the severity label.

## Bringing the reasons back to the actual decision

In `large-dev-b-09`, a museum committee must choose between an original object and a handling replica. Astra medium with v8 connects the exhibit's purpose to what visitors would be permitted to do, preserves the historical value of the original, and ends by joining the choice of the replica to the still-needed visitor trial. It does not claim the trial has happened or that handling has been shown to improve understanding.

Both judges prefer v8 to both baselines. Their reasons concern the progression to the decision, not simply shorter prose or fewer prohibited words. The no-skill output is already coherent, so this is a modest editorial advantage, not a rescue of unusable writing.

## Astra high: a usable revision can still lose to a strong baseline

The same museum case, `large-dev-b-09`, goes the other way for Astra high. Both judges prefer its no-skill output to v8. The baseline already links the opening recommendation to the untested learning benefit, considers the original's historical merits before explaining their relevance to this exhibit, and introduces cost with “Cost supports the choice of the replica without deciding it.” V8 is coherent and preserves the substantive constraints, but it does not improve this organization.

Astra's judge prefers the baseline's placement of qualifications and treatment of the objection. Sol treats progression as tied but gives the baseline a modest scope advantage: “Making repair central would require a change in direction” is more precise than v8's “Making fuller use of the original’s history would mean redesigning the exhibit around repair.” Neither judge flags a material error. This loss is a small editorial distinction between usable revisions, not evidence of a catastrophic failure. It illustrates why fixing behavior observed in long Astra-high chats does not imply that every isolated Astra-high rewrite will benefit from more instructions.

## Remaining failure: editing beyond a narrow request

`large-dev-a-19` asks for changes only where a qualification repeats the same scientific point. Luna medium with v8 recasts the accuracy, temperature, and condensation explanations even where they did not repeat a qualification. It is materially faithful, but it exceeds the requested editing scope. Both judges prefer both baselines.

The lesson is not to remove more caveats. The request already identifies which edits are wanted, and some passages should stay unchanged. This failure remains visible in the control results; it is not hidden by the argument or proof gains.

## The unchanged development check

The remaining 20 development cases show a partial repair, not a reason to release v8. Nonproof comparisons improve over v4, but the argument advantage over no skill is uncertain and Astra-high arguments remain negative. The [complete report](v8-dev-validation/report.md) and [outputs](v8-dev-validation/responses.json) preserve every case.

In `large-dev-a-12`, Astra high must separate a proposed reporting policy from its examples. Both judges prefer no skill. Its opening states the purpose before the proposed fields; it labels the supporting examples as examples, then gives the requirement to include runs without readings its own paragraph and rationale. V8 retains these facts but combines the examples, rule, missing-reading problem, and counts in one dense paragraph. This is an observable organization failure against the actual request, not merely a penalty for a banned phrase. The result directly limits the claimed argument repair.

In the finite-population proof `large-dev-b-14`, both judges prefer Sol low with v4 to v8. V4 first expresses the residual second moment as an average of pairwise squared differences, establishing why the sum is needed. It then evaluates that sum and explains the counting in prose. V8 announces “The required sum satisfies” before showing how that sum enters the residual moment. Its displayed double-sum derivation is valid, but the purpose arrives later and the algebra receives less explanation. This is the kind of reader-order distinction the author's proof directions ask the judge to recognize. All five proof-task losses to v4 in the check have no material-error flag on either output; they concern exposition, including proof purpose, displayed expectation steps, and sequencing.

The new outputs do have minor fidelity flags elsewhere. One methods rewrite turns a question about completeness into a claim that field-counting was actually performed first. Another changes optional disclosure into recommended disclosure, and a control drops who decides whether further checks are needed. The flags are published without treating them as infallible or counting repeated judgments as independent errors.

The decision is to retain v4. V8 remains a frozen experimental candidate. Its proof and research-voice reference bytes are unchanged, but the complete prompt changed, so proof-output preservation had to be measured. The fresh holdout remains unrun; no candidate or grader is revised from this check.

## Limits of the comparison

The skill files were frozen before writing generation. The author-specific rubric and context were unchanged, and judges received anonymous A/B pairs containing the source and actual outputs. The new core and translation instructions change together, so this experiment does not isolate which individual sentence caused the gains. There is only one generation per case/configuration/condition. Saved baselines were generated earlier, and requested model labels do not independently verify an unchanged backend. Case-bootstrap intervals do not capture all generation or judge uncertainty.

The new judge is grounded in the author's explicit directions, but it has not been independently calibrated against a fresh set of the author's own choices. Relative gains over a model's own baseline do not identify why Claude historically benefited more than Codex or rank their absolute writing quality. The historical family gap appeared under Claude judging too, weakening a Codex-only judge-bias explanation. Different baseline headroom and different responses to the same instructions remain plausible, unisolated mechanisms.

## The source-chat format does not survive this benchmark

The user observed that many source complaints came from Astra high, which still trails its no-skill baseline on tuning prose. This is not resolved by the aggregate gain. The benchmark supplies a fresh, complete synthetic passage and an explicit editing request, with tools disabled. A long revision session instead requires retaining a document's purpose across edits and feedback, coordinating local changes, and preserving the intended argument in the finished artifact. Those conditions are largely absent here.

Removing that context may make the baseline task easier and change which failures occur. This is a plausible explanation, not an experimentally isolated cause. Current results support claims about isolated rewriting only. The reserved holdout uses new passages in the same broad format and cannot establish transfer to long revision workflows. A later faithful-workflow study should retain anonymized initial drafts, sequential corrections, and document-level outcomes; it would be a distinct benchmark, not a reason to reinterpret or tune on the sealed holdout.
