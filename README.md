# declaude

A Claude Code and Codex skill for plain English, research exposition in the author's voice, and mathematical proofs with explicit displayed steps.

It removes rhetorical repetition and unnecessary abstractions while preserving facts, logical force, uncertainty, permissions, and scientific qualifications. It also supports drafting connected explanations rather than merely shortening text.

## Larger benchmark: interim snapshot

The new 80-task, ten-configuration experiment is **paused and incomplete**. The [interim report](evals/results/large-interim/report.md) contains 2,012 of 2,400 writing outputs, 1,458 absolute scorecards, and 2,078 of 3,820 pairwise judgments, including order audits. No additional model calls were made to publish this snapshot.

| Split | Cases with complete pairwise coverage | V5a vs no skill | V5a vs v4 |
|---|---:|---:|---:|
| Development | 39/40 | 58.46% | 51.73% |
| Fresh holdout | 3/40 | 37.50% | 51.67% |

Percentages count wins plus half of ties, with both judge families and all ten configurations represented for every included case. **Three completed holdout cases cannot establish generalization.** They are an execution-order subset. Missing results are not counted as ties or zeros, and neither these results nor subsequent test results may be used to tune the selected revision.

[Exact outputs and grading evidence](evals/results/large-interim/report.md#files) · [Coverage](evals/results/large-interim/coverage.json) · [Development selection](evals/large/selection.json) · [Frozen protocol](evals/large/protocol.md).

V5a narrowly qualified on reserved development validation. The packaged and installed skill remains v4 pending completion and release. The following results describe the earlier, smaller experiment.

## Earlier 16-case results

The final comparison covers **10 configurations and 480 outputs**: eight development cases and eight fresh held-out cases, each run with no skill, v3, and v4. V4 improves assertion passes over no skill on the fresh cases, but **does not establish an improvement over v3**. Its development advantage did not generalize clearly.

| Split | No skill: passes / holistic | v3: passes / holistic | v4: passes / holistic |
|---|---:|---:|---:|
| In sample: 8 development cases | 90.8% / 4.36 | 97.8% / 4.64 | 98.6% / 4.75 |
| Out of sample: 8 fresh cases | 95.9% / 4.55 | 98.8% / 4.74 | 98.5% / 4.72 |

Holistic scores are out of 5. On the fresh set, v4 versus no skill is **+2.68 percentage points** in assertions (95% paired case-bootstrap interval **+0.48 to +4.77**) and **+0.175 holistic points** (**−0.075 to +0.425**). Against v3, v4 is **−0.24 pp** (**−1.58 to +0.89**) and **−0.0125 holistic points** (**−0.1375 to +0.0875**). These are small synthetic tests with substantial ceiling effects, not evidence of universal improvement. Of the 50 fresh-test assertion cells across individual configurations and five metrics, 33 show zero difference; 30 of those have both conditions at 100%. The 480 outputs cover only 16 distinct tasks, eight of them fresh. This test is too small and easy for detailed model-by-category conclusions.

| Model | Effort settings tested |
|---|---|
| Claude Haiku 5.5 | default |
| Claude Sonnet 5.5 | low, high |
| Claude Opus 5.5 | low, xhigh |
| Claude Fable 5.1 | default |
| GPT-6 Astra | medium, high |
| GPT-6.1 Sol | low |
| GPT-6 Luna | medium |

### V4 versus no skill

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="evals/results/final-v4/assertions-dark.svg">
  <img src="evals/results/final-v4/assertions-light.svg" alt="V4 minus no skill, grouped by criterion and in-sample versus fresh held-out results, across ten model and effort configurations plus Claude, Codex and overall aggregates.">
</picture>

IS means development; OOS means the fresh held-out set. Cells show differences, in percentage points for assertions, score points for holistic grades, and words for median length. Gray length cells are descriptive: there are no length-threshold assertions. Model-family and overall aggregates weight configurations equally within each pool. The proof group has only two cases per split. Exact denominators, case counts, and intervals are in [groups_by_config.json](evals/results/final-v4/groups_by_config.json).

### V4 versus v3

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="evals/results/v4-vs-v3/assertions-dark.svg">
  <img src="evals/results/v4-vs-v3/assertions-light.svg" alt="V4 minus v3 on the same cases under the same calibrated grader, showing small mixed changes by model, effort, and writing criterion.">
</picture>

The two figures use separate color ranges; read the legends. The modest average hides differences across configurations. On fresh cases, Haiku's holistic score rises from 4.12 to 4.75 with v4 versus v3, while Luna falls from 4.38 to 4.00. Eight cases and one response per condition do not support a stable model ranking.

<details>
<summary>Absolute rates and scores</summary>

No skill:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="evals/results/final-v4/levels-none-dark.svg">
  <img src="evals/results/final-v4/levels-none-light.svg" alt="Absolute no-skill assertion rates, holistic scores and median word counts.">
</picture>

V4:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="evals/results/final-v4/levels-skill-dark.svg">
  <img src="evals/results/final-v4/levels-skill-light.svg" alt="Absolute v4 assertion rates, holistic scores and median word counts.">
</picture>

</details>

[Full v4 versus no-skill report](evals/results/final-v4/report.md) · [V4 versus v3](evals/results/v4-vs-v3/report.md) · [V3 versus no skill, same grader](evals/results/v3-calibrated/report.md) · [Exact outputs and grades](evals/results/final-v4/observations.json)

## What changed, and what still fails

V4 adds a short procedure for reconstructing a passage from its meaning instead of paraphrasing each source sentence. It makes consolidation of repeated claims and motivation-before-construction more explicit. It was selected before the fresh test under a development rule requiring improved mean holistic score without a decrease in aggregate fidelity passes. The selection gain was small: 4.6375 → 4.725, with fidelity 98.33% → 98.89%. The final regrading is reported separately from those selection grades. V4 is the packaged version; its fresh-test tie with v3 is retained rather than advertised as a further generalization gain.

The grader was also revised. V2 distinguishes rhetorical packaging from factual content and mathematical validity from requested exposition. On ten fixed calibration cases, both graders matched all 22 expected assertion judgments. V1 matched 19/20 expected holistic bands; v2 matched 20/20, fixing one overpenalty for minor equation formatting. These reference judgments were assistant-authored, with four cases reserved for validation. This is limited calibration evidence, **not independent human validation**. [Calibration details](evals/results/grader-calibration/report.md).

The new grader still makes questionable judgments. It penalizes some outputs for omitting an explicitly requested arithmetic difference while retaining both percentages, but correctly avoids treating that as a material factual error. It also gives debatable penalties to a proof whose displayed equations already identify indicator expectations with probabilities and to a coherent introduction's motivation. The ratings remain unchanged. [Inspection and disagreements](evals/results/final-v4/failure-review.md).

A concrete remaining skill failure is Luna's interval-merging explanation: it omits the final output step, even though its example gives the right final intervals. This is an actual completeness issue, not just a forbidden-word check. Both the technical and personal-voice controls are retained in the benchmark.

## Method and limits

- Candidate tasks request actual edited text or proofs, not plans. The final set includes a three-paragraph introduction, an algorithm explanation, scientific qualifications, two mathematical proofs, and technical/personal-voice controls.
- The complete public skill and references are inlined. Private reading lists are excluded. Claude tools are disabled. Codex runs in a read-only temporary environment and is instructed not to use tools. Personal global instructions are isolated from candidate calls. This tests the effect of supplied guidance, not automatic discovery or full-manuscript retrieval.
- An isolated Opus 5.5 high-effort grader sees anonymous outputs in seeded random order, without model/condition identities or skill text. All final conditions use grader v2. Matched conditions stay in the same pool, with up to ten responses per call. The grader is from one of the model families being evaluated and may share its preferences.
- Four development cases were initially used for tuning and four for validation. Both subsets became selection data. V4 was then compared with v3 across all ten configurations. The fresh test author saw neither skill nor development cases. [Frozen candidate/test plan](evals/improvement-plan.json), [selection](evals/revision-selection.json), and [final matrix](evals/revision-matrix.json) record the sequence.
- Final grading was rerun in balanced three-condition pools. Development-selection grades remain separately published; no preferred repeated grade was chosen. Two schema-invalid grading batches were retried, preserving completed valid batches. All 480 outputs now have valid scorecards; no candidate output was regenerated based on its quality.
- Bootstrap intervals resample paired cases, not individual assertions or model outputs. They do not capture all generation and grader variability. There is one candidate response per condition and no independent human preference study. The fresh tasks have high baseline scores, so small differences should not be overinterpreted.
- Neither inspected test set is untouched for a future revision. No fresh-test outcome was used to change v4. A later improvement needs a new holdout.

### Earlier reference runs

The original three-configuration report is [archived](evals/results/initial-three-configs/report.md). Expanding frozen v3 to all ten configurations under the original grader produced **87.7% → 91.2%** passes and **3.89 → 4.26** holistic scores on the original held-out set, with a proof-detail regression. [Expanded v3 reference](evals/results/expanded-v3/report.md) · [Failures](evals/results/expanded-v3/failure-review.md).

That reference uses different held-out cases and the old grader. Its numbers must not be compared directly with the fresh set to claim that the skill or grader improved. The final v3/v4 comparison above holds cases and grader fixed.

## Install

```sh
git clone https://github.com/hetankevin/declaude.git
cd declaude
python3 install.py
```

The installer copies `skill/` into the current user's Claude and Codex skill directories and backs up existing copies. It does not change global instructions or hooks. Invoke `/declaude` in Claude Code or `$declaude` in Codex. Normal skill discovery is enabled; this is not an always-on injection.

A private reading list can be placed in `skill/references/papers.local.md` and installed with `python3 install.py --personal`. That file is ignored by Git. The public skill works without it using writing samples and project notes supplied with the task.

## Reproduce

Rebuild reports and charts from published observations without model calls:

```sh
python3 -m venv .local/venv
.local/venv/bin/pip install -r requirements.txt
.local/venv/bin/python tools/report.py \
  --observations evals/results/final-v4/observations.json \
  --cases evals/development.json evals/heldout2.json \
  --matrix evals/revision-matrix.json \
  --reference none --selected v4 --out .local/reproduced --plot
```

Use `--reference v3 --selected v4` for the direct revision comparison, or `--reference none --selected v3` for the incumbent baseline comparison.

With authenticated, compatible Claude and Codex CLIs, generate a fresh comparison. These calls consume the accounts' available capacity:

```sh
for split in development heldout2; do
  python3 tools/bench.py run --cases evals/$split.json \
    --arms none,v3,v4 --skills v3=evals/versions/v3,v4=skill \
    --out .local/rerun
  python3 tools/bench.py grade --cases evals/$split.json \
    --grader-version v2 --out .local/rerun
done
.local/venv/bin/python tools/report.py --runs .local/rerun \
  --cases evals/development.json evals/heldout2.json \
  --matrix evals/revision-matrix.json \
  --reference none --selected v4 --out .local/rerun-report --plot
```

The runner rejects ambiguous multi-version labeling. Task, skill, model, and effort metadata are checked before cached results are reused; reports check the full matrix. Earlier skill snapshots are in `evals/versions/`, and grader prompts are in `evals/graders/`. To reproduce the expanded original reference, use `evals/heldout.json`, v3, and `--grader-version v1`.

## Sources and scope

The skill incorporates a user-supplied translation specification, recurring directions in research-workspace writing notes, direct author corrections about proofs and prose, and structural editing patterns from an existing humanizer skill. The public package contains generalized directions and synthetic examples. Source conversations, personal workspace paths, and private reading lists are not included.

See [translation](skill/references/translation.md), [research writing](skill/references/paper-voice.md), and [proof guidance](skill/references/proofs.md). This is an editing tool, not an AI-authorship detector or a promise to evade one.
