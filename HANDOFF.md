# Handoff

## Current outcome

Public repo: https://github.com/hetankevin/declaude. Packaged skill: v4. It combines plain-English editing, author-informed research exposition, and displayed proof derivations. The original supplied translation specification remains in references/translation.md. V4 adds a meaning-first reconstruction procedure rather than sentence-by-sentence paraphrasing.

User asked for neurotypical's full model/effort matrix and authorized improving both skill and grader. Both follow-ups are complete. The remote installation update is the sole pending operational item, awaiting the user's gateway sign-in.

## Results and interpretation

Final calibrated comparison: 480 outputs, 8 development + 8 fresh heldout2 cases, 10 configurations, none/v3/v4. Configurations: Haiku 5.5 default; Sonnet 5.5 low/high; Opus 5.5 low/xhigh; Fable 5.1 default; GPT-6 Astra medium/high; GPT-6.1 Sol low; GPT-6 Luna medium. See evals/revision-matrix.json.

Final IS passes: none 90.8%, v3 97.8%, v4 98.6%. Holistic: 4.3625, 4.6375, 4.75.
Fresh OOS passes: none 95.9%, v3 98.8%, v4 98.5%. Holistic: 4.55, 4.7375, 4.725.
V4 beats no skill on assertions, but is effectively tied with v3 out of sample. Do not claim the latest revision establishes a further generalization gain. The fresh baseline is high and the set is small.

V4 was selected before fresh testing under a development-only rule: holistic mean improves without a decrease in fidelity passes. Selection scores (two-condition pools) are preserved separately from final three-condition regrading. Exact selection: holistic 4.6375 → 4.725, fidelity 98.33% → 98.89%. Hashes and decision are in evals/improvement-plan.json, revision-selection.json, and release.json. evals/freeze.json records the earlier v3 release, not the current bundle.

Grader v2 separates factual meaning from rhetorical packaging and proof correctness from exposition. Ten fixed calibration cases, six development/four validation: both graders match 22/22 assertion targets; v1 matches 19/20 holistic bands, v2 20/20. Targets are assistant-authored, not human validation. It still makes debatable judgments; failure-review.md identifies them without changing ratings.

Historical expanded reference: frozen v3, original grader, original heldout. 320 outputs; OOS passes 87.7% → 91.2%, holistic 3.89 → 4.26, proof detail regresses. Keep this separate from the final calibrated/fresh comparison. The initial three-configuration report is archived too.

## Artifacts

- evals/results/final-v4/: primary no-skill comparison, all 480 responses/grades, counts, intervals, light/dark heatmaps, failure inspection.
- evals/results/v4-vs-v3/: same-run direct revision comparison.
- evals/results/v3-calibrated/: incumbent baseline comparison under the same grader/cases.
- evals/results/expanded-v3/: original-grader ten-configuration reference.
- evals/results/revision-selection/ and grader-calibration/: selection evidence, not fresh-test evidence.
- README: all ten configurations, IS/OOS metrics, family aggregates, median lengths, methods, caveats, reproduction commands.

## Validation and remaining installation item

All 480 candidate outputs have matching frozen task/skill/model/effort metadata and valid v2 scorecards. Two grading batches failed schema validation; only failed/uncompleted batches were retried. Valid completed batches and all candidate outputs were preserved. No candidate response was regenerated for quality. Scorecards retain pool identifiers and hashes. Logs and unfiltered CLI artifacts are private under .local/.

Local personal Claude and Codex installations are updated to v4, including the untracked paper reading list, with file hashes verified. Existing copies are backed up. No hooks or global instructions were changed.

Remote personal Claude and Codex still contain the previously installed and activation-tested v3. The attempt to update them to v4 failed at the SSH gateway before installation because login expired. An asynchronous user-input request asks the user to complete that browser sign-in. Once they confirm, transfer install.py plus skill/ (including the private paper reading list) into a temporary remote directory, run install.py --personal, and verify both installed file hashes. Do not claim remote v4 is installed until verified. The remote CLI needs a supported model for activation tests; its earlier v3 probe succeeded with its catalog-supported model after Astra was rejected by the old CLI.

## Reproduction and future work

Run commands in README. tools/bench.py supports --skills for multiple versions and refuses relabeling one bundle as several arms. Use --grader-version v1 for historical original-grader runs; v2 is now the default. The final report verifies the preregistered matrix, hashes, and paired completeness. Bootstrap resamples cases. Length is descriptive, not a success threshold.

No heldout2 result changed v4 or the grader. Both test sets have now been inspected; future tuning needs a new holdout. Actual full-paper author-voice fidelity and general proof correctness remain unestablished.

## Source and privacy boundaries

The skill draws on the supplied translation prompt, 14 local writing-note paths, direct proof corrections, a remote Claudish discussion, and prior humanizer guidance. The exact meme transcript was not confirmed verbatim in that old chat. Only generic directions and synthetic examples belong in the public repository.

The private source inventory and CLI outputs stay in ignored .local/. skill/references/papers.local.md stays untracked. Never publish source-project identifiers, personal paths, transcript excerpts, exclusion patterns, credentials, or authentication links. Research assumptions and source-project notation do not become global style requirements.
