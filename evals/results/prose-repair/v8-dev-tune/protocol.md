# Codex prose repair

The requested outcome is clearer prose, especially a developed argument, while preserving the existing proof guidance. The author-specific judge is frozen at `evals/results/context-regrade/rubric.txt` with its associated author context. No Claude calls are permitted.

## Development and selection

Use only the existing 40 development tasks. The existing 20-task `tune` subset is available for diagnosis and up to two candidate revisions. Test each candidate on Astra medium/high, Sol low, and Luna medium. Reuse exact saved development outputs for no skill and packaged v4. The remaining 20 development tasks provide one final check of the selected candidate. These tasks were examined in earlier experiments: they are development data, not an untouched test.

The first candidate, v8-dev, separates argument development from compression and makes the logical work of explanations explicit. It retains `proofs.md` and `paper-voice.md` byte for byte from packaged v4. References are bundled exactly as in the earlier benchmark for comparability.

Judge anonymous pairs against both no skill and v4 using Astra high and Sol high. Retain ties and report win percentage minus loss percentage in signed percentage points. Report argument, all nonproof categories, proof, individual generator configurations, material errors, and judge/order disagreement. Case bootstrap intervals reflect independent tasks, not the larger number of judgments. Reversed-order checks do not enter performance estimates.

Choose at most one candidate for the final development check. Prefer improvements in argument and nonproof writing against both references, with no increase in material errors or loss of proof performance. Do not choose on the proof-heavy aggregate. If two candidates trade off, prioritize argument improvement, then nonproof improvement; report category regressions explicitly. Qualitatively inspect the actual revisions and the judges' reasons before selection. Scores do not replace checking whether the writing improved. If neither candidate provides a credible repair, retain v4 and report the unresolved regressions.

Freeze candidate bytes, cases, references, rubric, context, model configurations, A/B ordering, and retry policy before each phase. Accept the first valid writing output and first fully valid judgment. Schema/transport retries cannot select a more favorable answer. Preserve failed attempts privately. Publish synthetic responses and exact accepted judgments with hashes. Keep historical results unchanged.

## Fresh holdout

An independent Codex agent creates 30 synthetic tasks without access to candidates, development cases, model outputs, grades, or prior holdouts. Store the contents privately and publish only their hash, category counts, and creation policy. The optimizer must not inspect or run these cases during this repair. Reserve them for a later, separately authorized test of the frozen candidate. Existing consumed holdouts are not used to tune this repair.
