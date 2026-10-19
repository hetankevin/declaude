# Handoff

## Bounded dev repair complete — no more calls authorized

Completed exactly 12 Codex calls, zero Claude calls. Six development/tune outputs and six blind Astra-high judgments against saved v5a: 1 win / 3 ties / 2 losses, −16.7 pp overall and progression. Meaning tied all six; no material flags; proof and polished control tied. `evals/results/dev-repair-1/` contains frozen plan, outputs, exact judgments, summary, and report. `tools/dev_repair.py` enforces the persistent cap; it is exhausted. Do not run further model calls or resume the large benchmark.

Tested `v6-dev` is not promoted. A narrower `v6b-dev` draft restores all v5a guidance and references and adds one practical-organization paragraph. It is untested, uninstalled, and must not be represented as an improvement. Packaged/installed release remains v4. Old holdout has been inspected and motivated the revision; it cannot serve as fresh evaluation for this line of development. No new holdout calls or case inspection occurred in the pilot. Historical snapshot plots were regenerated from saved aggregates.

Verification: 10 pairwise-report tests pass (including signed win/loss and neutral-tie checks). The report validates task/skill hashes, exact responses, prompt/record hashes, source-grounded quotations and normalized verdicts. Reported token total from 12 CLI calls: 93,434, not an account quota percentage. Plot changes and frozen plan pushed in `13fd70f`; subsequent commit records completed outcomes.

User requested signed percentage-point reporting: win rate minus loss rate, centered at zero, ties neutral. Historical raw judgments and frozen selection decisions must remain unchanged.

## Large benchmark usage pause — do not resume

Interim charts now live in `evals/results/large-interim/plots/`, with both themes and comparisons. README shows the current pairwise/absolute plots first and collapses historical plots. `tools/plot_interim.py` reproduces them using published snapshot files only, without model calls. Chart aggregates were checked against the saved tables; rendered category, dimension, and absolute heatmaps were visually inspected. Row labels report case counts and unavailable cells display NA. Pairwise coverage is 39 development / three holdout cases; absolute coverage is 34 / eight.

The user then requested publication of intermediate results. Snapshot and exact available outputs/grades are in `evals/results/large-interim/`, linked prominently in README. It captures 2,012 responses, 1,458 absolute scorecards, and 2,078 pairwise judgments. Tables use cases complete across all configurations; paired comparisons share 39 development and only three holdout cases. This is explicitly incomplete and was built without model calls. `tools/interim_report.py` can export another snapshot without invoking a model.

The user reported unexpected Claude account depletion after the handoff. The coordinator stopped its queued benchmark calls with SIGINT; active calls may still drain. Do not automatically resume or launch more model calls. Explain cost/usage and agree on a cap before continuing. Completed artifacts remain intact. The local audit is `.local/claude-usage-audit.json`; process/pause details are in `.local/opus-handoff-runtime.json` and `.local/benchmark-paused-for-usage.txt`. This supersedes the resume instructions below.

## Current task

Public repo: https://github.com/hetankevin/declaude. Installed and packaged skill remains v4. User requested a much larger, harder evaluation, blinded pairwise grading, the full model/effort matrix, a fresh holdout, and development-only skill improvement. Work is paused; the final benchmark is incomplete.

## Opus handoff — resume here

The user explicitly requested handoff to Opus while the larger benchmark was running. Do not start a second matrix or change frozen skill/rubrics. Continue the existing run and finish reporting/release.

- Live process details and remote host are in ignored `.local/opus-handoff-runtime.json`. Current run log: `.local/large-final-resumed.log`. The wrapper `.local/resume_large_final.py` owns the run. It was started through exec session 43481, but use the saved PIDs if this runtime cannot access that session.
- At handoff, approximately 1,240/2,400 responses existed. The scheduler had completed 373/3,820 pairwise jobs and 9/80 absolute case jobs. Counts are a snapshot; read `.local/large-final/.private/failures.json` for current state.
- Three absolute grading jobs had schema assertion failures at the latest check: `large-dev-a-05`, `large-dev-a-14`, and `large-dev-b-02`. Raw answers are retained under `.local/large-final/.grading-raw/`. Candidate outputs succeeded and must not be redrawn. Inspect failures, archive the failure manifest, and rerun the same runner after the current writer exits. Valid cache entries are preserved; the first schema-valid stored grade is reused. Pairwise now allows up to four schema attempts, retaining all of them and accepting the first valid one, not a preferred score.
- The first runner was gracefully interrupted to raise concurrency. It cancelled queued calls and waited for every active writer to finish. The resumed run reuses 1,132 completed generation artifacts. The original 960 reused outputs were development baselines and selected-candidate runs; the additional 172 completed in that first final-run segment. No candidate output was discarded or quality-selected.
- The report auditor finished and pushed `53c8a50` and `3af89ec`. Strict pairwise publication now requires complete matrices, exact hashes, identities, ordering, and source responses. Absolute reports verify pool fingerprints and reject imported split mismatches. Existing assertion-weighted rates are explicitly labeled, rather than changing the estimand after selection. Validation is no longer an OOS alias. Order diagnostics now include unique-case and split/judge breakdowns. The auditor reported all 19 tests passing with model calls stubbed. Run `python3 -B -m unittest discover -s tools -p 'test_*.py' -v` if changing reporting code. The auditor could not finish a synthetic chart render because macOS font discovery stalled in `system_profiler`; its process termination was unconfirmed. Inspect actual final charts under the established venv and `MPLCONFIGDIR=/tmp/declaude-mpl`; do not treat the tests as visual verification.
- Public package and all installations are still v4. V5a is the frozen development-selected revision. The remote connection was reverified immediately before handoff; the host is in the ignored runtime file. Preserve the personal reading-list overlay when installing.

### Finish commands

After the running writer ends, inspect its failures. Resume the exact command below as needed, preserving earlier manifests and raw failures. Require complete status and all artifacts before reporting.

```sh
python3 tools/large_run.py --cases evals/large/development.json evals/large/holdout.json --selected v5a --skill evals/versions/v5a --out .local/large-final --pairs-out .local/large-final-pairs --generation-workers 24 --pairwise-workers 64 --grading-workers 8

MPLCONFIGDIR=/tmp/declaude-mpl .local/venv/bin/python tools/report.py --runs .local/large-final --cases evals/large/development.json evals/large/holdout.json --matrix evals/large/final-matrix.json --reference none --selected v5a --out evals/results/large-final --plot

python3 tools/pairwise_report.py --inputs .local/large-final-pairs/v5a-vs-none --cases evals/large/development.json evals/large/holdout.json --out evals/results/large-pairwise-none --strict --matrix evals/large/final-matrix.json --runs .local/large-final --candidate v5a --reference none
```

Also report v5a versus v4 and v4 versus none from the same absolute observations. Run strict pairwise reporting separately for `v5a-vs-v4`, with `--reference v4`. Render pairwise heatmaps using `tools/plot_pairwise.py --summary <report>/summary.json --out <report>` under the venv and inspect the PNGs. Show IS/OOS, model/effort, categories, dimensions, judge-specific results, actual denominators, bootstrap intervals, material errors, and length descriptively. Inspect representative losses and judge disagreements, not just charts.

Rewrite README around the new results while keeping earlier reports linked as history. Do not imply that the narrow validation qualification proves a revision benefit. Publish exact synthetic outputs and normalized grades, never raw CLI envelopes. If releasing the selected bundle, copy `evals/versions/v5a/` to `skill/` while preserving `references/papers.local.md`, update `evals/release.json`, install personally on both local and remote Claude/Codex, and verify hashes. The fresh test is now consumed and cannot be reused as untouched selection data.

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
python3 tools/large_run.py --cases evals/large/development.json evals/large/holdout.json --selected v5a --skill evals/versions/v5a --out .local/large-final --pairs-out .local/large-final-pairs --generation-workers 24 --pairwise-workers 64 --grading-workers 8
```

Expected: 2,400 responses and absolute scorecards; 3,820 pairwise judgments including 620 order audits, split over v5a-versus-none and v5a-versus-v4. Current log: `.local/large-final-resumed.log`; the first scheduler was gracefully drained to increase concurrency, preserving all active artifacts. Its log remains `.local/large-final-pipeline.log`. Status/failures: `.local/large-final/.private/failures.json`. No concurrent writers to these roots. Inspect schema/transport failures and preserve raw attempts before resuming; never regenerate a poor candidate answer.

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
