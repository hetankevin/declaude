# Judge alignment audit

The writing goal is to follow the author's established research prose and proof preferences while removing AI writing tells. Generic readability is not an adequate substitute.

## What the earlier behavioral benchmark actually did

Its judge received the session context, the latest user message, pre-registered assertions tied to that situation, and anonymized responses in shuffled order. It graded assertions separately from a holistic 1–5 assessment of how glad that user would be to receive the response given the context. The anchors were exactly what the user wanted (5), acceptable but missing something they care about (3), and making things worse (1). Case builders carried the user's corrections into concrete expectations. The grader did not see skill/model identities.

The useful precedent is the user-and-context objective, not its particular model provider or a claim that its judgments were validated human preferences. No private cases, transcripts, or source paths are copied into this public report.

## What was missing here

The original pairwise judge sees the editing task, source, assertions, and A/B outputs. Its voice criterion relies on the local sample and requested register. It explicitly says private author notes are unavailable. The harness also discarded any session context outside its task/assertion allowlist. The author's full writing criteria were available to the skill but not comparably explicit for the judge.

The original rubric has useful safeguards for exact quotations, fidelity, proof applicability, and meaningful ties. Those remain. Its synthetic calibration targets were assistant-authored, not independent human choices. On the earlier validation comparisons, the two judges agreed on 36/80 verdicts, including eight direct win/loss disagreements. Swapping response order changed 9/28 verdicts, although none reversed a win into a loss. These figures diagnose variability; they do not measure agreement with the author.

## Changes prepared without model calls

`pairwise-v2-draft.txt` uses the particular user's satisfaction as its overall target and supplies the author's applicable writing priorities: motivation before mechanisms, connected explanations, purpose before notation, a reason for each step, faithful scope without repeated audit commentary, and displayed proof steps with reasons. It requires the overall rationale to identify a decisive user priority in the actual output. The criteria come from explicit directions and writing notes, not from whichever candidate happened to win.

The harness now accepts an explicit `user_context` field, includes it in the hashed blinded request, and validates quotations against it. Case/model IDs, expected winners, and other metadata remain excluded. Existing tasks without context produce the same inputs as before.

The draft rubric is not automatically substituted into frozen experiments. Existing scores remain labeled with their original rubric. Future context must be anonymized, include only task-relevant preferences and corrections, and exclude model identities, skill versions, desired winners, and unrelated private material. The author directions themselves are evidence of preferences; constructed examples are not mislabeled as human-rated comparisons.

## Current result is provisional

The second development pilot completed its already-authorized twelve Codex calls and no Claude calls under the old rubric. It must not establish alignment with the author's preferences or justify a release. No regrading or additional model calls were made during this audit. The new rubric is prepared but unvalidated; generalization and personal alignment remain unestablished.
