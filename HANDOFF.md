# Handoff

## Goal and completed work

Create and evaluate declaude: plain English that preserves meaning, research exposition informed by the author's writing directions, and mathematical proofs with displayed derivations and no skipped substantive steps. The reusable package is published at https://github.com/hetankevin/declaude (public).

The selected skill is v3. The earlier versions are in evals/versions/. Its exact public bundle and case hashes were frozen in evals/freeze.json before the held-out evaluation. Do not modify this release based on the inspected held-out results and continue calling those cases held out for a later version.

## Sources and privacy

The core draws on the supplied translation prompt, 14 local writing-note paths, direct proof corrections, a remote chat defining Claudish, and the existing humanizer skill. Newer instructions preserve meaningful technical terms and contrasts instead of older blanket bans. The remote discussion matches the definition and vocabulary; the exact meme transcript was not confirmed verbatim in that old chat.

Only generic directions and synthetic examples belong here. Personal source inventory and CLI outputs remain in ignored .local/. The optional private paper reading list is skill/references/papers.local.md and must remain untracked. Never publish source-project identifiers, paths, transcript snippets, or private exclusion patterns. Research assumptions and source-project notation are not global style requirements.

## Results

All 96 outputs in the final comparison are complete and blind-graded: 8 development + 8 held-out cases, 3 configurations, no skill versus v3. Development passes 89.2% → 100.0%, holistic 3.96 → 4.71. Held-out passes 89.1% → 95.3%, holistic 4.04 → 4.54. The held-out assertion difference's case-bootstrap interval includes zero. See evals/results/report.md and failure-review.md.

The 64 development-selection outputs have separate grades, not mixed with final balanced six-response grading. There were 128 distinct candidate outputs total, including older versions. Both development subsets were used for selection. Held-out tasks were authored separately and preregistered before execution. Some rubric judgments are arguable; retain raw grades and inspection notes. No claim of full-manuscript or automatic-activation performance follows from this short-text benchmark.

## Installation and validation

Installed the personal skill, including the untracked paper reading list, into the requesting user's Claude and Codex skill directories on both requested machines. All four installed copies matched the seven source files by SHA-256. Existing copies were backed up. No hooks or global instructions were changed.

Claude activation was smoke-tested on both machines. Local and remote Codex correctly returned an exact sentence from the skill in explicit invocation probes. The remote CLI (0.145.0) rejected the Astra model as requiring a newer client; the successful probe used its catalog-supported gpt-5.6-sol. No CLI was upgraded. All four personal installations and activation probes are verified.

Skill metadata validation, Python compilation, and an isolated installer smoke test passed. Charts are rendered and visually inspected. Public observations omit raw CLI envelopes and personal paths.

## Reproduction and next work

README has report-only and model-rerun commands. tools/bench.py isolates candidates from personal instructions and inlines the public guidance. tools/report.py requires a complete paired matrix, publishes exact outputs/grades, bootstraps cases, and draws light/dark annotated heatmaps. Dependencies are in requirements.txt.

Future improvements require a fresh holdout. Conservative editing and literal proof-detail requests remain weaknesses. The benchmark does not establish voice fidelity across full papers. Do not silently tune on inspected held-out cases or overwrite existing observations with preferred repeats.

## Active follow-up: broader model coverage

User requested the full neurotypical matrix. Frozen v3 and existing tasks are unchanged. evals/expanded-matrix.json preregisters ten configurations and 320 outputs. Existing 96 responses are reused in .local/expanded; initial reports are preserved in evals/results/initial-three-configs. Generate the remaining 224 outputs, blind-grade all 320 in matched-condition pools, publish stratified IS/OOS heatmaps and provider aggregates. Do not claim this expansion complete until model runs and grading finish.

User also authorized improving the skill and grader. A fixed synthetic grader calibration compares v1/v2 (both match 22/22 assertions; holistic bands 19/20 versus 20/20). v2 is selected, with calibration limitations documented. v4 is a development-only candidate stressing reconstruction from meaning; installed skill remains v3 until selection. All ten configs compare v3/v4 on development under v2. A separate author created heldout2 without seeing either skill or development cases; pre-execution QA fixed a scheduling-rubric inference and scoped a technical control. See improvement-plan.json for hashes and the development selection rule. Old ten-config benchmark remains graded by v1 and must be reported separately.
