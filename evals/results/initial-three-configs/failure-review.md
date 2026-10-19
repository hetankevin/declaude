# Inspection of held-out failures

This is an inspection by the implementing assistant after grading, not an independent human review. The frozen skill, tasks, assertions, and recorded grades have not been changed. Exact responses and assertion evidence are in observations.json.

## Already-clear sorting definitions

In `oos-stable-inplace-control`, the source says, “We call a sort in-place if it uses O(1) auxiliary memory beyond the input array.” All six responses dropped the local “we call” convention marker. That loses a qualification under the preregistered rubric, so all six fail that assertion. It is a shared failure rather than an improvement attributable to the skill.

With the skill, Astra changed “being in-place says nothing about stability” to “An in-place sort uses O(1) auxiliary memory beyond the input array, regardless of stability.” The grader treated this as a material logical distortion and assigned 2/5, versus 4/5 without the skill. That severity is debatable: the intended independence is still inferable, and the paragraph still gives heapsort as a counterexample. Nevertheless, the rewrite is less explicit and was unnecessary. The observed regression remains in the results.

The task says “tighten,” whereas its style assertion prefers unchanged text or trivial edits. This tests restraint on a passage that is already concise; it is also a stricter reading than a general request to rewrite. The result should not be described as a mathematical error in sorting.

## Proof arithmetic

In `oos-variance-unbiased-proof`, Astra with the skill correctly expands the square, shows the independent cross terms vanish, obtains the variance of the mean, and preserves the Jensen remark. It jumps from `(nσ² − n·σ²/n)/(n−1)` to `σ²`, omitting the explicitly requested intermediate `(n−1)σ²` step. This is a failure to display requested arithmetic, not an invalid proof. It accounts for the held-out proof-group regression: one failed assertion out of 18 paired skill-side proof assertions, against zero without the skill.

Without the skill, Astra displayed the arithmetic more fully but dropped the supplied remark. The grader assigned 2/5 for that omission. The skill output received 4/5: better overall preservation, less complete arithmetic. Keeping these dimensions separate is necessary to interpret the aggregate scores.

## Fidelity gains and rubric limitations

Astra without the skill dropped the supplied remarks in both held-out proof tasks. The preregistered assertions require preserving them. The tasks ask for a revised theorem/claim and proof without explicitly saying “and remark,” so that expectation is arguable even though the remarks are part of the supplied source. Both conditions were graded identically, but part of the fidelity and holistic gain depends on this strict preservation reading. No assertion has been removed after seeing the answers.

In the editor-response task, Astra without the skill added an extended-revision-timeline condition. The source already says that the authors would add the experiment here if the editor judged it essential; it does not merely offer to discuss feasibility. The skill response preserves that wording. The grader penalized the added timeline and the switch from ‘and’ to ‘or’. This is a defensible strict-editing distinction, but calling the baseline an invented commitment is too strong: the source already makes a conditional commitment, and the timeline is a plausible inference from the stated scheduling obstacle. Its 2/5 grade should therefore be treated cautiously. The published rating is unchanged.

The memoir control retained the narrator's voice without failures in either condition. Both controls should remain in future development coverage, but this inspected set is no longer an untouched test set.
