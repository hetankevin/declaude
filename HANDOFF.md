# Handoff

## Restored v9 check COMPLETE; no more calls

All20 development cases completed on Astra high, Sol low, Sonnet high. 60 valid new drafts,120 comparisons,120 saved baselines reused. 101 total attempts (61 writing including original capacity failure and successful authorized retry;40 judge batches). The continuation added35 calls and670,656 reported tokens. Total known1,919,254 tokens;188.71271 estimated Standard Codex paid-credit equivalents, plus20 Claude calls. Unknown original failure retains30,000-token/8-credit reservation: charged1,949,254 tokens/196.71271 credits, below2.5M/300 guards. No active or queued jobs. Completed outputs and frozen runner/candidate/rubric/cases preserved. Both fresh holdouts untouched. Packaged/installed stillv4.

Net win-minus-loss pp vsnone/v4: Astra+35/+15;Sol+35/−15;Sonnet+60/+10;pooled+43.3/+3.3. Astra argument vsnone0, vsv4+50. Sol argument vsv4−50. Pooled proof-task overall vsv4−16.7 despite a positive proof-dimension score. No universal promotion supported. Four cases/category, previously inspected dev, one frozen author-specific Sol-high judge, no new order audits or long-horizon evidence. See interpretation.md for actual passage-level explanations and limitations.

Final public artifacts: evals/results/prose-repair/v9-restored-20/. README now leads with complete tables and readable light/dark category and dimension heatmaps. stop.json is the historical66-call interruption; completion.json supersedes it without erasing it. 117 verdicts passed original strict validation;1 source-verified initial-letter correction;2 optional source quotes removed (one supplied assertion outside validator pool, one paraphrase). Raw answers/preferences/reasons/severities retained, required evidence strict. Qualified verdicts flagged; sensitivity excluding both preserves aggregate directions. No repair model calls. Post-freeze reporting amendment documented, never claim120 pristine judgments.

Reproduce with no model calls: python3 tools/finalize_restored_results.py, then MPLCONFIGDIR=/tmp/declaude-mpl .local/venv/bin/python tools/plot_restored_check.py. Finalizer verifies continuation preservation hashes, reconstructs raw reporting, applies disclosed evidence repairs, and writes sensitivity. Do not rerun the original report alone over final artifacts, launch a duplicate, reopen holdouts, or install/promote without a new request. Historical notes below describe earlier states.

## Historical: authorized continuation to 101 calls

User explicitly approved the extra call and retrying Astra to finish all20 cases, reusing completed work and leaving holdouts untouched. tools/resume_restored_check.py freezes continuation-plan.json, preserves all prior attempt files and their hashes, and routes exactly the failed generation to a new private retry directory. 35 new calls maximum,101 total including original failure; same2.5M-token/300-credit guards, keeping the unknown failure reservation. Retry first, then34 unrun jobs. No new skill/rubric/case/model changes. Original runner/plan remain frozen. Reproduce final reports via python3 tools/resume_restored_check.py report. Do not launch another runner.

## Historical: initial capacity stop, superseded by completion

Latest authorized 20-case check stopped at66/100 attempts when Astra returned “Selected model is at capacity” without token usage. Frozen unknown-usage guard stopped scheduling and let active judges finish. Nothing running. 40 writing attempts (39 outputs,1 capacity failure),26 judge calls,78/120 valid pairwise comparisons,13/20 complete cases. Known usage1,248,598 tokens;124.51221 estimated Standard Codex paid-credit equivalent, plus13 Claude calls and one unreported failed attempt. Budget accounting reserves8 credits/30,000 tokens for the unknown attempt, not claimed as measured usage. No retries/model substitutions/holdout reads/installations.

Final partial artifacts: evals/results/prose-repair/v9-restored-20/. README prominently marks incomplete. No headline aggregate/new heatmap; summary.json intentionally empty. All completed outputs and raw private evidence preserved. 77 verdicts passed original validation; one first-character quote capitalization mismatch (“Those exchanges” versus source “those exchanges”) repaired deterministically after freeze. Raw answer, reasoning, preferences and severity untouched. Audit in quote-format-repairs.json; rules in formatting-amendment.md. Five format tests and ten budget tests pass.

Reproduce locally without model calls: python3 tools/restored_check.py report, then python3 tools/finish_restored_check.py. The second command revalidates source/response hashes, original accepted grades and the unique-span case-only repair. The plot utility refuses incomplete coverage. Public stop.json records the outcome. Original frozen runner/candidate/inputs remain unchanged. Do not call run or change the frozen plan to resume automatically. A user-authorized continuation would need a new plan/budget amendment, retain all outputs, and address the failed generation. 34 planned calls are unrun; completing all20 cases also requires a replacement for the failed generation, so at least35 more calls under the same batching, exceeding the original100 cap by one. Packaged/installed remain v4.

## Restored v9 20-case check authorized and frozen

Runner tools/restored_check.py; public inputs evals/results/prose-repair/v9-restored-20/. Existing balanced 20-case development validation subset, 4 per category, already inspected historically (not fresh OOS). Astra high, Sol low, Sonnet high. Reuse 120 exact saved baselines and 60 verified historical v4/none grades. New candidate only: 60 writes, 40 blind Sol-high batches, 120 pairwise verdicts. Hard 100-call cap, 20 Claude writes, no automatic retries; scheduling guards 2.5M reported tokens and 300 estimated Standard Codex paid credits with reservations for up to 3 active calls. Guards may overshoot within an in-flight call. Unknown usage stops scheduling. Candidate, rubric, cases, order, code and inputs frozen before run. Both fresh holdouts stay sealed. No installation changes. Run/report via python3 tools/restored_check.py; never resume an ambiguous unfinished reservation or launch another pipeline. Ten mocked/local budget tests pass. Run is active, with one orchestrator holding its lock. Public report/coverage are a partial checkpoint, not headline performance. Do not launch a duplicate. Running commands retain partial outputs and never retry a consumed reservation.

## V9 safeguards restored; no evaluation launched

User requested restoration of the six useful omissions while preserving argument/proof guidance, and asked for rerun costs. New candidate: evals/versions/v9-restored-dev/. Original v9-dev and all recorded results remain frozen. Only the new SKILL.md differs from original v9; all references and UI metadata are byte-identical. Restored concrete logical-force distinctions, personal research semicolon preference, internal-discussion exclusions, adverse-result protection, detailed fidelity/math checks, and the warning against cosmetic “so what” slogans. No generations, judges, installations, or holdout reads/runs. Packaged/installed remain v4. README clearly separates unevaluated restored candidate from tested v9. Cost estimates are in evals/rerun-cost-estimate.md; estimates are not authorization to launch.

## Economical cross-model check complete

Latest user request: complete evaluations without burning too many credits. Completed the announced bounded extension: six v9 writing calls (same three selected development cases on Sol low and Sonnet high) and three batched Sol-high blind judge calls. Exactly NINE new calls,183,559 reported input/output+cache tokens, zero unknown usage, zero automatic retries. All6 drafts and12 new primary pairwise judgments are valid. No jobs remain running/queued. No broad matrix, subagents, skill edits, installations or holdout runs were added.

Results across the three cases (two arguments,one proof), win/tie/loss:
- Astra high, reused: v9 vs none2/1/0 (+66.7pp); v4 vs none1/2/0 (+33.3); v9 vs v4 3/0/0 (+100).
- Sol low: v9 vs none1/2/0 (+33.3); v4 vs none2/1/0 (+66.7); v9 vs v4 1/1/1 (0).
- Sonnet high: v9 vs none3/0/0 (+100); v4 vs none3/0/0 (+100); v9 vs v4 2/0/1 (+33.3).

Argument-only: Astra v9 beats v4 twice; Sol and Sonnet split1win/1loss. Proof: v9 beats v4 on Astra/Sonnet, ties on Sol. Sonnet's two wins over v4 are fidelity-driven: could->would on the policy claim; an added universal dependence assertion in the proof fails at N=2 where Z is constant. Coordinator verified that counterexample, but this is not independent human calibration. No candidate material errors were flagged in the new comparisons. Do not call the small Sonnet edge a general style improvement or extrapolate to Opus. Direct v4/no-skill grades and Astra results were reused after exact response/rubric/context/evidence checks. Pairwise batches may produce nontransitive preferences. n=3 selected development cases do not establish general or OOS performance.

Frozen plan and results: evals/results/prose-repair/v9-cross-model/. Runner: tools/cross_model_small.py. Private attempts: .local/prose-repair/v9-cross-model/. README now leads with the compact three-model comparison and links interpretation.md for actual passage-level findings. All prior broad heatmaps remain historical. Packaged and installed v4 are unchanged. Both fresh holdouts stay sealed/unrun; the long-horizon study remains uncompleted. Do not resume older pipelines or add calls automatically.

Read-only reproduction: `python3 tools/cross_model_small.py report`. All frozen hashes,9-call cap,6-output/12-new-grade coverage, source quotes, balanced anonymous ordering and privacy checks pass. No model calls are needed to reconstruct the report.

## Saved-draft grading complete; no generation or installation changes

Latest user request: finish grading the saved drafts cheaply and regenerate nothing. Completed exactly TWO new Sol-high judge calls using the frozen author-specific rubric, context, A/B order and original saved drafts. No writing generations, no extra judge/reversed-order calls, no Claude calls, no skill or installation edits. Completed museum grades were reused. Both fresh holdouts remain sealed/unrun. No jobs remain running or queued.

All six primary comparisons across three selected Astra-high development cases are accepted and source-quote validated. Museum: tie vs none, win vs v4. Reporting-policy argument: win vs both. Finite-population proof: win vs both, narrow vs v4 for explaining pair counting/centering. No material-error flags in any accepted comparison. Net advantage: +66.7pp vs none (2 wins,1 tie,0 losses); +100pp vs v4 (3 wins,0 ties,0 losses). This deliberately selected n=3 development check with one fallible judge is not a stable population estimate or OOS result. The order audit remains deliberately unrun. V9 clears the grade-only release checks here, but the user's current task was grading only: packaged and installed remain v4. No broad Codex prose fix is established.

New completion usage: two judge calls,42,791 reported input+output tokens. Entire small pass: eight calls including the earlier file-editing smoke and failed judge call; known subtotal211,329 tokens, plus UNKNOWN usage for the original failed judge. Cached input is included; no billing/account-quota inference. Raw failed evidence remains untouched. New private attempts are in .local/prose-repair/v9-small/completion-20261020/. Public completion manifest freezes draft/bundle/rubric/case/plan and exact prompt hashes. All remained unchanged after grading.

README and evals/results/prose-repair/v9-small/report.md show the complete primary results; old heatmaps remain labeled historical. tools/finalize_small_repair.py now revalidates original plus completion judgments and reconstructs the report without model calls. tools/complete_small_grading.py is strictly grading-only and caches both attempts: do not launch more calls or regenerate drafts automatically.

V9-dev simplifies the prose core and retains proofs.md and paper-voice.md byte-identical to v4. The small check inlines the full portable bundle as before, so it does not test selective loading. The manual artifact review remains coordinator inspection, not an independent grade. See observations.json, judge-responses.json, usage.json, coverage.json and release-decision.json.

The earlier long-horizon smoke cost92,604 reported tokens before the validator stopped on the newer response-item user-message format. No matched long-horizon result exists. The runner needs a compatibility fix before reuse; do not restart it. Two independently authored six-turn holdout cases and the earlier30-case isolated holdout remain sealed/unrun and privately backed up. Private storage location is recorded in .local/long-horizon-holdout/storage.json; never publish or inspect the cases during tuning.

Reconstruct without calls: `python3 tools/finalize_small_repair.py`. Focused checks: `python3 -B -m unittest discover -s tools -p test_small_repair.py`. All65 tests had passed before this completion; its four focused checks and frozen-hash/evidence checks pass.

## Codex prose repair experiment complete; v8 not promoted

The user requested a dev-only repair of Codex prose, especially arguments, preserving proof guidance and the author-specific judge, Codex only, with a fresh holdout reserved. Both phases are complete. No jobs or model calls are queued. The requested general repair remains unresolved: v8-dev is a frozen partial improvement, not a release. **Packaged and installed v4 is unchanged.**

Protocol: `evals/large/prose-repair-protocol.md`. Tuning selection: `evals/results/prose-repair/selection.json`. Final decision: `evals/results/prose-repair/release-decision.json`. V8 keeps proofs.md and paper-voice.md byte-for-byte from v4. Its core and translation reference distinguish argument development from compression and preserve useful explanatory steps.

Each phase covers 20 development cases, four Codex generators (Astra medium/high, Sol low, Luna medium), 80 new writing outputs, 320 primary judgments and 64 order audits. Baselines are exact saved no-skill and v4 outputs. Astra high and Sol high use the same frozen author-specific judge. No Claude calls occurred.

- Tuning: nonproof +12.5 pp versus no skill and +24.2 versus v4; argument +18.75 and +40.625. Proof +53.125 and +6.25. Selected unchanged for the second phase.
- Remaining development check: nonproof +9.375 pp [−2.34375,20.3125] versus no skill and +20.3125 [1.5625,38.28125] versus v4. Argument +6.25 [−21.875,31.25] and +12.5 [−21.875,40.625]. Proof +81.25 versus no skill but −15.625 [−31.25,−3.125] versus v4 (0 wins,27 ties,5 losses).
- Astra-high argument score against no skill is −12.5 pp in both phases. In the check it is 1 win,5 ties,2 losses; all nonproof is +12.5 [−15.625,37.5]. Argument versus v4 is +25.0 in the check. Do not hide the unresolved argument result behind the aggregate.
- Check material-error flags: candidate/reference 3/10 against no skill and 4/8 against v4, all minor. They count judgments, not independent errors. Proof losses concern exposition, not flagged mathematical errors.
- Check judge agreement 130/160, order agreement 46/64 with two direct reversals. Full findings and actual examples are in `evals/results/prose-repair/case-review.md`.
- Total two phases: 415 Codex calls (160 writing,255 judge including15 malformed-judgment retries), zero Claude; 4,897,358 CLI-reported tokens. This is not an account-percentage or billing estimate. All attempts retained privately; first valid answers retained without quality regeneration.

Reports and exact synthetic evidence: `evals/results/prose-repair/v8-dev-{tune,validation}/`. Updated two-phase light/dark heatmaps in `evals/results/prose-repair/plots/` and README. Neither phase is OOS. Private runtime directories mirror these phases under `.local/prose-repair/`. The run owned by session63156 is finished; do not restart it. Reports were rebuilt only to fix Markdown table headers and distinguish category/dimension/generator/judge labels; grading and summary values did not change.

A fresh 30-case holdout is sealed and UNRUN. Public manifest: `evals/large/fresh-holdout-20261019-manifest.json`. Independent author/reviewer saw no candidates or development outputs. Two initially faulty cases were corrected privately; second review passes all30. Final hash: 4af1d135109531a68c9810cc90a6e6047539ce8467f98efbbbf47fa5a548541a. Private content and reviews are in ignored `.local/fresh-holdout-20261019/`, with durable-backup location in `.local/holdout-storage.json`. Optimizer must not read these contents. Publish only the manifest; a future performance test requires separate authorization.

The user's interpretive questions matter to future work. Earlier dramatic gains came from regrading unchanged writing with a different setup and coverage. The Claude/Codex relative-gain difference existed with Claude judges too, weakening a judge-family explanation. Many source complaints came from Astra high, but the benchmark transforms long manuscript sessions into isolated complete-passage rewrites. It does not test preservation of the story across successive corrections. README and case review state this limitation; the fresh holdout has the same broad task-format limit. No causal explanation for the family gap has been isolated. A faithful-workflow study would be a distinct experiment, not a reinterpretation of the current holdout.

Next work, if requested: target the remaining organization/overediting failures without weakening proof exposition; use a new development protocol and keep the sealed holdout separate. Do not retune v8 or the judge on the completed check and claim it remains validation. Do not automatically resume any older benchmark. No installation changes are pending from this experiment.

Verification complete: all 44 tests pass; both published evidence sets revalidate; 220 chart point estimates match the summaries; tuning selection hash is unchanged; light/dark category and dimension plots inspected; new public artifacts passed the private-pattern scan. Generated SVG trailing whitespace was removed without changing the rendered figures.

Verification commands (no model calls):

```sh
python3 tools/prose_repair.py report --candidate v8-dev --subset tune --published
python3 tools/prose_repair.py report --candidate v8-dev --subset validation --published
MPLCONFIGDIR=/tmp/declaude-mpl .local/venv/bin/python tools/plot_prose_repair.py evals/results/prose-repair/v8-dev-tune evals/results/prose-repair/v8-dev-validation --out evals/results/prose-repair/plots
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

## Author-specific regrade complete

The user's latest request is fulfilled: regrade saved outputs with the contextual judge, Codex only, without the earlier small-budget restriction. **No further model calls are needed or queued. No skill changes or installation changes were made. Packaged/installed remains v4.**

- Public report: `evals/results/context-regrade/report.md`; interpretation and examples in `case-review.md`; updated light/dark category and dimension heatmaps appear first in README.
- Complete: 652 accepted batches, 2,706 primary judgments, 286 reversed-order checks. Main matched corpus: 40 development and 27 original-held-out cases, ten generation configurations, v4/v5a against no skill. Separate six-output v6/v7 pilots and one partial v4 case are preserved without contaminating headline denominators.
- Judges: Astra high and Sol high, with frozen author-specific rubric/context. 706 Codex attempts, 705 returned answers, one capacity failure, zero Claude calls, zero writing generations. CLI-reported total 12,139,933 tokens; no account-percentage or total-billing inference.
- Both versions help overall, especially saved Claude outputs. Held-out all-config net advantages: v4 +33.1 pp [23.1,43.0], v5a +32.6 [21.5,43.9]. Codex overall remains uncertain; excluding proof tasks it is near neutral: v4 +2.2 [-12.5,16.3], v5a +3.8 [-11.4,17.9]. Codex argument point estimates are negative, while both versions score +81.2 on four held-out proof cases. Preserve proof guidance; do not claim broad Codex prose improvement or promote v5a from these numbers.
- Primary judge agreement 1097/1353; order agreement 226/286, including 14 direct reversals. Explicit user preferences ground the target but do not establish independent human alignment. See the case review for a questionable material-error finding. The original holdout is retrospective for the changed judge and is an availability subset, not a fresh test.
- Original grades, skill versions, writing outputs, rubric and plan remain unchanged. The separately committed retry amendment allows four attempts only for unusable answers. Recoveries repair trailing commas, source-verified English excerpt capitalization, or the pre-existing math delimiters, never verdicts/reasons. All are recorded. The initial coordinator's failed count predates recovery; final `coverage.json` verifies every batch.
- Public observation files and compressed accepted raw answers support portable revalidation. `.local/context-regrade/` retains all CLI attempts privately. Strict checks bind exact source text, prompts, responses, quotes, ordering and normalized outcomes. All 29 tests pass. Portable revalidation from the published raw archive passed. The tests cover missing/duplicate grades, identity/source/context tampering, case-level denominators and conservative syntax recovery. Final light/dark heatmaps were visually inspected, README links checked, and new public artifacts including the compressed raw archive passed the privacy scan.

Reproduce without model calls:

```sh
MPLCONFIGDIR=/tmp/declaude-mpl .local/venv/bin/python tools/report_context_regrade.py --published --plot
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

Do not tune on the retrospective holdout. Any future skill improvement should use development cases and retain a fresh test; this turn authorized regrading, not a new candidate. The small pilots were regraded but are too limited for release claims. All historical no-call limits and runtime notes below describe earlier stages, not active processes.

## Earlier work (historical)

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
