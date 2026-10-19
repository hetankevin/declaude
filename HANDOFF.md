# Handoff

## Current outcome

Public repo: https://github.com/hetankevin/declaude. Packaged skill: v4. It combines plain-English editing, author-informed research exposition, and displayed proof derivations. The original supplied translation specification remains in references/translation.md. V4 adds a meaning-first reconstruction procedure rather than sentence-by-sentence paraphrasing.

User asked for neurotypical's full model/effort matrix and authorized improving both skill and grader. Both follow-ups are complete. After the user renewed gateway sign-in, the remote personal installations were updated and verified.

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

## Validation and installation

All 480 candidate outputs have matching frozen task/skill/model/effort metadata and valid v2 scorecards. Two grading batches failed schema validation; only failed/uncompleted batches were retried. Valid completed batches and all candidate outputs were preserved. No candidate response was regenerated for quality. Scorecards retain pool identifiers and hashes. Logs and unfiltered CLI artifacts are private under .local/.

Local personal Claude and Codex installations are updated to v4, including the untracked paper reading list, with file hashes verified. Existing copies are backed up. No hooks or global instructions were changed.

Remote personal Claude and Codex are now updated to v4. After the user renewed gateway sign-in, install.py --personal completed and all seven installed files in each app matched the local source by SHA-256, including the private reading list. Existing copies were backed up. No hooks or global instructions were changed.

## Reproduction and future work

Run commands in README. tools/bench.py supports --skills for multiple versions and refuses relabeling one bundle as several arms. Use --grader-version v1 for historical original-grader runs; v2 is now the default. The final report verifies the preregistered matrix, hashes, and paired completeness. Bootstrap resamples cases. Length is descriptive, not a success threshold.

No heldout2 result changed v4 or the grader. Both test sets have now been inspected; future tuning needs a new holdout. Actual full-paper author-voice fidelity and general proof correctness remain unestablished.

## Source and privacy boundaries

The skill draws on the supplied translation prompt, 14 local writing-note paths, direct proof corrections, a remote Claudish discussion, and prior humanizer guidance. The exact meme transcript was not confirmed verbatim in that old chat. Only generic directions and synthetic examples belong in the public repository.

The private source inventory and CLI outputs stay in ignored .local/. skill/references/papers.local.md stays untracked. Never publish source-project identifiers, personal paths, transcript excerpts, exclusion patterns, credentials, or authentication links. Research assumptions and source-project notation do not become global style requirements.

## Evaluation resolution

The user questioned the many zero-improvement cells. Across the ten individual configurations and five assertion metrics (excluding family aggregates), development has 31 zero differences out of 50 cells, 29 with both conditions at 100%. Fresh heldout2 has 33 zero differences out of 50, 30 with both at 100%. The comparison has only eight distinct fresh cases, including two proofs. The 480 outputs are not 480 independent tasks. The current test is too small and easy to support detailed model-by-category conclusions. A follow-up should expand independent, longer and harder cases, preserve ordinary controls, use graded or blinded pairwise prose judgments alongside factual assertions, and reserve a fresh test set before further tuning. Do not manufacture difficulty by selecting only baseline failures.

## Active expansion: 80-case benchmark

User authorized a much larger/harder set, pairwise grading, the full model matrix, and development-only skill improvement. Protocol: evals/large/protocol.md. Independent authors are preparing 40 development and 40 holdout cases, five categories with eight per split. Holdout contents stay sealed in .local/large-authoring until skill selection; independent QA sees them, tuner does not. Two pairwise judge families and reversed-order audits supplement fixed semantic grading. At most two skill revisions, selected on a balanced development validation subset with fidelity and material-error guards. Existing small tests are historical only. No new results yet.

All80cases now pass independent QA. Development is public in evals/large/development.json; freshholdout remains .local/large-authoring/sealed-holdout.json, hash preregistered in dataset-manifest.json. Do not read holdout before skill selection. Bothcalibration phases complete; finalpairwisegrader frozen. Firsttuning pipeline: .local/large_tune_pipeline.py, runs .local/large-tune-runs, logs .local/large-tune-*.log. Firstcandidatev5a; v5b is only an unused untracked placeholder. Next: inspectdevelopmentonly, optionally createv5b, selectonvalidation, then openholdout.

Execution checkpoint: first 240 tuning responses completed with no failures (20cases x4configs xnone/v4/v5a). Binary grading and pairwise v5a-v4 grading are running, alongside all10config development none/v4 baselines in .local/large-final. Second candidatev5b is now committed and running on the same20tuningcases and4configs, using copied exactv4responses. Its changes came from qualitative analysis of25triples across7tunecases, notvalidationorholdout. Candidate hashes/basis are in evals/large/candidate-plan.json. Two candidates maximum now reached; do notinventanother without explicitly revising the experiment design. Use tools/large_select.py after completegrading to compare tuning candidates; then evaluate the best once on the20developmentvalidationcases. Qualifying rule: pairwise preference>.5, fidelity no worse, materialerrorrate no worse. Onlyafterselection open the sealed40caseholdout andcomplete final10configcomparison. Logs: .local/large-tune-pipeline.log, large-tune-absolute.log, large-tune-pairwise.log, large-development-baselines.log; .local/large-v5b-pipeline.log and correspondinggeneration/absolute/pairwise logs. .local/large_progress.py prints artifactcounts without exposingholdout. Pairwise primaryassignment is hashstable acrosssubsets; orderaudits are20% bycase/config, bothjudgefamilies. Frozenbinarygraderv2 andpairwiseprompt havepassed schema/livecalibration; calibrationlimitations recorded in evals/results/large-calibration. No largebenchmarkresultclaimed yet.
