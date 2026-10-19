# Handoff

## Current task

Public repo: https://github.com/hetankevin/declaude. Installed and packaged skill remains v4. User requested a much larger, harder evaluation, blinded pairwise grading, the full model/effort matrix, a fresh holdout, and development-only skill improvement. Work is running; do not report the final benchmark as complete.

## Frozen experiment

- Protocol: `evals/large/protocol.md`.
- 80 synthetic tasks: 40 development, 40 fresh holdout. Each split has eight ordinary prose, research, argument, proof, and control cases. Full tasks span about 240–720 words.
- Independent authors and reviewers checked correctness, task/rubric agreement, and overlap before candidate runs. Only generic synthetic content belongs in this public repo.
- Development: `evals/large/development.json`; balanced 20-case tuning and 20-case validation subsets. Both are development/selection data.
- Holdout was sealed through selection and has now been released unchanged as `evals/large/holdout.json`; its hash matches `evals/large/dataset-manifest.json`. No holdout outcome may change the skill, grader, or rubric. Author/reviewer notes remain private.
- Ten configs: Haiku default; Sonnet low/high; Opus low/xhigh; Fable default; Astra medium/high; Sol low; Luna medium. These are requested CLI identities, not an independent backend audit.
- Selection configs: Haiku, Sonnet high, Astra medium, Luna medium.
- Candidate snapshots and hashes: `evals/versions/v4`, `v5a`, `v5b`; `evals/large/candidate-plan.json`. Two-candidate limit is reached. Do not tune on validation or holdout outcomes.

## Completed tuning

Twenty cases, four configs. First batch: none/v4/v5a, 240 responses. Second: 80 new v5b responses, reusing exact v4 artifacts. Candidate responses had no execution failures and were never regenerated for quality.

| Candidate versus v4 | Pairwise preference | Wins / ties / losses | Fidelity: v4 → candidate | Material-error flags: v4 → candidate |
|---|---:|---:|---:|---:|
| v5a | 55.625% | 50 / 78 / 32 | 99.25% → 99.63% | 10/160 → 13/160 |
| v5b | 53.75% | 49 / 74 / 37 | 99.25% → 99.25% | 12/160 → 14/160 |

Two judges assess each pair. Intervals include 50% for both candidates. Neither clears every provisional tuning check. V5a has the higher preference and factual pass rate and is undergoing the one reserved validation comparison. This choice was committed before validation in `evals/large/validation-plan.json`. V5b came from qualitative inspection of 25 matched triples across seven tuning cases, not validation or holdout.

Reports: `evals/results/large-tuning/`. Selection summaries: `evals/large/tuning-v5a.json` and `tuning-v5b.json`. The v4 absolute grades differ across candidate comparisons because pools were graded separately; the reference response texts are identical.

## Validation and final run

V5a qualified narrowly under the fixed validation rule: 46 wins, 72 ties, 42 losses (51.25%, case CI 45.6–57.2), equal fidelity at 98.48%, material-error flags 15/160 versus 23/160 for v4. Absolute style/holistic scores fell, so do not call this a broad or statistically established improvement. Both kinds of evidence are published in `evals/results/large-validation/`. Selection was frozen before opening the holdout in `evals/large/selection.json`; matrix in `evals/large/final-matrix.json`, commit `2e24b27`.

All 800 development no-skill/v4 outputs completed with no generation failures. Reused those and 160 selected-candidate outputs. The final streamed matrix is now running:

```
python3 tools/large_run.py --cases evals/large/development.json evals/large/holdout.json --selected v5a --skill evals/versions/v5a --out .local/large-final --pairs-out .local/large-final-pairs --generation-workers 16 --pairwise-workers 28 --grading-workers 8
```

Expected: 2,400 responses and absolute scorecards; 3,820 pairwise judgments including 620 order audits, split over v5a-versus-none and v5a-versus-v4. Log: `.local/large-final-pipeline.log`. Status/failures: `.local/large-final/.private/failures.json`. No concurrent writers to these roots. Inspect schema/transport failures and preserve raw attempts before resuming; never regenerate a poor candidate answer.

Remaining: finish run and recover invalid grading jobs, publish reports with complete-matrix validation, inspect failures and actual plots, update README/release, install selected bundle locally and remotely, verify hashes, push. The report auditor is checking aggregation and completeness handling. Do not change the selected skill or grading criteria based on test results. Packaged/installed skill remains v4 until release.

## Grading and reliability

- Absolute semantic assertions and 1–5 holistic grades use frozen `evals/graders/v2.txt`.
- Pairwise prompt: `evals/graders/pairwise-v1.txt`; two judges: Opus high and Astra high. Anonymous A/B assignment is hash-stable across subsets. Both judge families assess every primary pair. A hash-threshold 20% sample receives reversed-order audits; actual sample counts are reported. Audit repetitions do not inflate independent task counts.
- Calibration: 12 assistant-authored fixtures, eight tuning/four validation, both judges/both orders. One tuning-only clarification improved target agreement from 26/32 to 28/32. Reserved validation matched 13/16. Some target ties are themselves debatable. No validation outcome changed the prompt. Details: `evals/results/large-calibration/`, `evals/large/grader-freeze.json`.
- Tuning judges agreed exactly on 38/80 pairs for v5a and 48/80 for v5b; each comparison had four direct win/loss disagreements. Order audits had one direct reversal for v5a and none for v5b. Report model judgments as such, not human validation.
- Two initial absolute-grade jobs failed schema checks and were repaired without regenerating candidate outputs. Their first invalid raw answers were not retained by the old runner. A subsequent stored answer was recovered by removing one trailing JSON comma outside strings; judgments and evidence were unchanged. The runner now saves raw answers before parsing and records syntax-only repairs. One validation order-audit answer omitted a closing math delimiter from a source quote. It was recovered from the first stored answer by restoring one dollar sign only where the actual response uniquely verifies it; its tie judgment was unchanged. The second raw attempt was not selected. Normalized records disclose every such evidence-format repair; original raw bytes remain intact. Preserve this limitation in reporting.
- `tools/pairwise_report.py` requires a complete expected matrix and checks record hashes. `tools/report.py` validates frozen matrix/task/skill/rubric hashes when given a manifest. Case bootstrap, not assertion/judge/model count, determines intervals. Length is descriptive only.

## Installation and earlier results

V4 is verified in the user's personal Claude and Codex installations on this Mac and the remote machine, including the private paper list. Existing copies were backed up. No global hooks or instructions were changed by this release.

Earlier final comparison: 480 outputs on eight development and eight fresh cases, ten configs, none/v3/v4. Fresh assertions: 95.9% / 98.8% / 98.5%; holistic: 4.55 / 4.7375 / 4.725. V4 tied v3; those small tests had severe ceilings. Keep historical reports under `evals/results/final-v4`, `v4-vs-v3`, `v3-calibrated`, and `expanded-v3` separate from this experiment. Neither old holdout is fresh for future tuning.

## Privacy and conventions

Keep source transcripts, personal paths, project identifiers, private reading lists, raw CLI envelopes, auth links, and credentials out of this public repo. Do not publish private exclusion patterns. `.local/` and `skill/references/papers.local.md` remain ignored. Install with `python3 install.py --personal` when the selected bundle changes; preserve the private overlay. Use terse lowercase commits without AI attribution. The parent neurotypical repo is separate and private; do not commit declaude work there.
