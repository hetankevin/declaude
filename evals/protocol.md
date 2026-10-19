# Evaluation protocol

Development: eight synthetic cases inspired by recurring writing corrections, four for tuning and four for validation. Held-out: eight new synthetic cases produced by a separate Claude Sonnet high-effort invocation that received the task scope but neither the skill nor development cases. Held-out tasks and assertions are saved before running them. Do not use held-out outcomes to revise this release.

Paired conditions: the same task with no added editing guidance and with the complete public skill plus its reference files inlined. Personal reading-list files are omitted from both. This tests instruction effects on supplied text, not automatic skill discovery or long-document retrieval. Tasks and rubrics are fixed; candidate models never see assertions.

Configurations: Claude Sonnet 5.5 low effort, Claude Sonnet 5.5 high effort, GPT-6 Astra medium effort. One response per condition per case. Cases, not assertions or model outputs, are the unit resampled for paired 95% bootstrap intervals. Report development and held-out separately. Length is descriptive, not a success metric.

Claude runs use safe mode and no tools. Codex runs use an empty temporary home and CODEX_HOME with only an authentication link, no hooks, and an empty working directory. Candidate prompts request no tools. The same shared writing-task wrapper is used in both conditions.

Blind grading: an isolated Claude Opus 5.5 high-effort call sees all responses for a case in a seeded random order with anonymous labels and no skill text, model identities, or condition identities. It grades preregistered assertions and overall usefulness (1–5). Material meaning or mathematical errors cap the overall grade at 2. The grader is fallible; independently inspect apparent fidelity/proof regressions and report disagreements without silently overwriting its ratings.

Selection: inspect the tuning subset first. If a revision is warranted, compare the exact frozen candidate versions on the tuning and validation subsets. Prefer the incumbent on a tie; do not select a stylistic gain that conceals a material fidelity regression. Evaluate the selected version against no added skill on held-out cases only after selection. Report all development comparisons used for selection. Validation becomes development evidence once used for selection.

No hypothesis of a universal improvement or benchmark ranking is preregistered. Small, synthetic, single-turn tests provide limited evidence. They do not establish voice fidelity on full papers, proof correctness in general, or performance of automatic skill activation. An inspected held-out set cannot be called untouched for a later revision.

Development-rubric correction: after the pilot, the recurrence assertion was clarified to accept both finite-sum evaluation and a complete induction. Requiring an explicit finite sum would unfairly penalize a valid induction. All development arms are regraded together under this corrected rubric before selection. Held-out assertions are unchanged.

The first revision (v2) addressed duplicate proofs, unused abbreviations, index boundaries, and invented matrix orientation. Its development results did not show a consistent advantage over v1. A further candidate (v3) clarifies the precedence of explicitly requested content deletion over generic preservation rules. That change uses observed development-validation feedback, so both development subsets are now selection data. The held-out set remains unused for selection.

If a task or assertion is found objectively invalid (for example, contradictory premises), document the defect and both conditions' outcomes rather than silently editing it or choosing a preferred score. A disputed but valid grader judgment remains in the reported raw ratings, with a separate human-review note.
