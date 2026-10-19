# Inspection of final calibrated results

This is an inspection by the implementing assistant after all ratings were recorded, not an independent human review. No score, assertion, task, or skill was changed based on this inspection. Compare conditions under the same grader and cases; raw outputs are in observations.json.

## Skill comparison

V4 versus no skill improves fresh-set assertion passes from 95.85% to 98.54%. Against v3, however, v4 is effectively tied: 98.54% versus 98.78%, with holistic scores 4.725 versus 4.7375. V4's development advantage does not establish a fresh-test advantage. The selection decision was made before these results, and no fresh-test tuning followed.

## Real remaining omissions

Luna's v4 interval-merging explanation omits the general step that outputs the current interval after traversal ends. Its worked example gives the correct final output, but that does not supply the missing algorithm instruction. The grader's failed completeness assertion is justified. Its opening also leaves the tempting predecessor-only comparison implicit; the source asked to make that obstacle explicit.

Luna's diagnostic abstract says “news headlines, forum posts, or the five other planned domains.” This can be read as seven domains, whereas the task intended five additional domains including the two examples. The source's own parenthetical wording is less precise than ideal, so the penalty is debatable in severity, but the revised wording adds an avoidable ambiguity. No task fix was made after seeing the answer.

## Strict assertions that are not material factual errors

Three v4 diagnostic abstracts preserve both accuracies, counts, and the bootstrap interval but do not explicitly write the derived 3.5-point difference. The fixed assertion requires that number. The grader marks the assertion false while assigning two of those outputs holistic 5/5. That separation is appropriate: the specific requested detail is missing, but the numerical information has not been falsified. A fidelity-assertion failure therefore does not always mean a material factual error.

## Disputed grading judgments

Luna's v4 union-bound proof explicitly displays P(B)=E[1_B] for the union and its component events and gives a pointwise indicator inequality. The grader says E[1_B]=P(B) is not stated; that part of its evidence is contradicted by the display. Monotonicity of expectation is used without being named, which can reasonably count as a missing requested justification. The proof is mathematically valid. The failed assertion and 4/5 score are retained, with this disagreement visible.

The grader gives Luna's v4 introduction 3/5 because it connects the inability to store all values to the 2 KB budget rather than directly to the number of metrics. The output begins by stating that dashboards track many metrics and immediately gives the per-metric memory budget. It preserves the requested motivation, obstacle, construction, numbers, and lack of a guarantee. I consider the severity of this holistic penalty excessive. Its assertions all passed, and the rating is left unchanged.

These disagreements remain evidence that the calibrated grader is imperfect. The calibration gain was one score-band correction on 20 constructed outputs, not a validation of its every judgment. No post-hoc rescoring is used to improve the skill's headline numbers.

## Interpretation

The fresh tasks have high no-skill pass rates and only eight cases. Both skill versions perform well under this rubric, with small average differences. The controls check restraint and voice preservation, but the experiment does not establish fidelity to the author's voice across a full paper. The proof tasks test two elementary arguments, not general theorem correctness. A later revision needs a fresh test set and would benefit from independent human judgments.
