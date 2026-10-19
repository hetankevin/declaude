# Larger writing evaluation

This protocol is fixed before generating candidate responses. The earlier small benchmarks remain historical references.

## Tasks and separation

80 original synthetic tasks: 40 development, 40 fresh holdout. Each split has eight tasks in each category: ordinary prose, research exposition, argument structure, mathematical proofs, and controls. Most tasks contain several paragraphs; controls include already-good prose, legitimate technical language, deliberate voice, and explicitly limited editing requests. Difficulty comes from faithful synthesis and exposition, not an artificial banned-word list. Cases are not selected by whether a baseline fails them.

Independent authors receive category, length, and quality requirements, without the skill or old evals. Separate reviewers check source correctness and task/rubric consistency before any candidate output exists. Holdout contents stay in an ignored sealed directory during tuning; the coordinator reads only aggregate QA and hashes. The test files are released after the selected skill and grader are frozen. Development is split deterministically into 20 tuning and 20 validation cases, balanced by category and author. Validation is selection data, not a fresh test.

## Models and runs

Use all ten configurations from the preceding benchmark: Haiku default, Sonnet low/high, Opus low/xhigh, Fable default, Astra medium/high, Sol low, Luna medium. Candidate generations use isolated CLI environments, one response per task/configuration/arm. Preserve completed responses and execution metadata. Retry execution failures only, never regenerate an answer because it is poor.

Compare no skill, frozen v4, and the development-selected revision. If no revision qualifies, retain v4 and report that outcome; do not manufacture a different winning arm. Four configurations spanning both families and strengths (Haiku, Sonnet high, Astra medium, Luna medium) are used for development selection. The final report covers all ten configurations on all 80 tasks, reusing identical completed generations.

## Development selection

At most two proposed revisions. Use the tuning half to identify problems and refine guidance, keeping revisions general rather than quoting cases. Compare candidates with v4 using blinded pairwise judgments and factual assertions. Evaluate the best tuning candidate once on the validation half. A revision qualifies only if validation pairwise preference (win=1, tie=0.5, loss=0), averaged equally across both judge families, exceeds 0.5, fidelity assertion pass rate does not decline, and material-error frequency does not increase. Ties retain v4. Record all attempts and candidate hashes. No test result changes the selected skill, grader, or rubrics.

## Grading

Preserve binary semantic assertions as checks for meaning, task scope, and proof validity, with holistic 1–5 grades under frozen grader v2. These are secondary to direct writing comparisons.

Pairwise grading sees the task, source, and assertions with anonymous A/B responses, never model, condition, skill, or version. Judges assess overall preference plus meaning, naturalness, progression, author voice, and proof exposition (not applicable when appropriate). Ties are allowed; mere brevity, changed words, and token count earn no credit. Evidence must identify a real difference. Distinguish factual/mathematical errors from stylistic or requested-detail defects.

Every primary pair is independently judged by Opus high and Astra high. Assignment of A/B is deterministic and balanced in expectation. A hash-selected 20% subset is judged again in reversed order by both judges; these repetitions diagnose position sensitivity and are not counted as extra tasks or used to choose favorable verdicts. Report each judge separately, disagreement rates, and reversed-order consistency. Calibration uses separate synthetic known comparisons with ties, material-error tradeoffs, voice controls, and proof-format distinctions. Validate before candidate grading; do not adjust the grader to favor a skill.

## Analysis and publication

Show in-sample and fresh-test results by category, model, and effort: win/tie/loss, tie-adjusted preference, criterion-specific preferences, factual assertion passes, material-error rate, holistic score, and median reply length. Use paired case bootstrap intervals; models, assertions, judges, and swapped-order repeats are not independent tasks. Include case counts and denominators, baseline ceiling rates, and representative failures. Do not claim statistically distinct model ranks from small category samples. Cross-family judges are still models and are not a human validation study.

Publish generic tasks, frozen prompts, hashes, exact model outputs, normalized grading evidence, reproducible summaries, and readable figures. Keep private source lists, personal paths, raw CLI envelopes, authentication details, and credentials out of this public repo. Inspect examples as well as numerical scores. Preserve unfavorable findings.
