# What the completed check shows

Restored v9 improves on no skill across all three tested generators. Its advantage over v4 is model-dependent: +15 pp for Astra high, −15 for Sol low, and +10 for Sonnet high. With 20 cases per generator, the intervals against v4 all include zero. The pooled +3.3 pp is 12 wins, 38 ties and 10 losses, with a case-bootstrap interval of −8.3 to +18.3 pp. This supports neither a universal replacement nor a claim that the restoration fixed all prose regressions.

## Argument writing remains uneven

Astra high is +50 pp against v4 on the four argument cases but 0 pp against no skill. In `large-dev-a-10`, the judge prefers the no-skill briefing because it connects the warning signs' purpose to the recommendation immediately, then integrates the unresolved drainage work with reporting. Both versions preserve meaning. The result is about developing the argument, not a banned-word count.

Sol low is −50 pp against v4 on arguments. In the same briefing, v4 places the warning-versus-drainage distinction where it explains the cost comparison. In `large-dev-a-12`, v4 connects reporting counts to inclusion decisions and addresses misuse alongside the raw readings. Restored v9 retains the content but presents those connections less effectively. These are the judge's passage-specific explanations, not evidence of a general architectural difference between models.

## Explicit proof steps do not guarantee the best proof exposition

Across generators, proof-task overall preference is +91.7 pp against no skill but −16.7 pp against v4. The separate proof dimension is +16.7 pp against v4. That difference is possible because the final judgment also considers progression, repetition, and voice.

In `large-dev-a-16`, v4 tells the reader at the start why the algebra will solve the minimization problem; the Astra candidate's extra expansion adds no essential missing argument. In `large-dev-b-14`, Sol's v4 proof introduces the conditional residual calculation immediately after identifying it as the quantity still needed. In `large-dev-a-14`, Sonnet's v4 proof uses one identity across all cells, including zero-probability cells, for a clearer progression. These inspected losses have no material-error flags. The proof reference file stayed unchanged, but the full prompt's behavior did not.

Sonnet's `large-dev-b-16` comparison is qualified by an invalid optional source quote. Its unchanged preference favors v4 for grouping the derivation into two stages and avoiding repeated kernel-scope qualifications. Excluding this verdict and the companion no-skill comparison changes Sonnet's aggregate to +57.9 pp against no skill and +15.8 against v4. The aggregate directions are unchanged. See the reporting amendment and sensitivity file rather than treating these as pristine grades.

## Fidelity and limits

The candidate has two material-error flags, both minor and both referring to the same Sonnet draft in `large-dev-a-12`: it strengthens a possibility claim from “could” to “would.” They are two comparisons of one output, not two independent errors. Preserving useful details also requires preserving their logical force.

This is an economical development check with one frozen author-specific Sol-high judge and no new reversed-order audit. The judge's preferences have not been newly calibrated against human rankings. Saved baselines introduce a possible backend/time confound. The candidate was not changed during evaluation. The full bundle was inlined, so this does not test selective loading or the long revision sequences that motivated the skill. Neither fresh holdout was opened or run. Packaged and installed v4 remain unchanged.
