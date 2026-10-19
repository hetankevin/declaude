# Author-specific regrade of saved writing

Status: **complete**, 652/652 batches. This report grades saved outputs only. No writing was regenerated and no Claude judge was called.

Two blind Codex judges (Astra high and Sol high) apply the frozen author-specific rubric and category-relevant context. The target is the requested author's writing goal, including argument progression, connected prose, appropriate scope, and explicit proof steps. This is model-based assessment against stated preferences, not validation against independent human choices.

Net advantage is **win rate minus loss rate**, in percentage points. Ties contribute zero. Primary results average cases equally; intervals bootstrap cases, not judge votes or configurations. Reversed-order audits never contribute to performance.

The development set contains tuning and validation cases used during skill development. The original holdout is regraded retrospectively: prior outcomes informed the grader discussion, so this is not a new untouched test of the revised evaluation procedure.

| Skill vs no skill | Split | Net advantage, pp [95% case CI] | Win / tie / loss judgments | Cases |
|---|---|---:|---:|---:|
| v4 | development | +38.8 [+29.5, +48.0] | 415 / 280 / 105 | 40 |
| v4 | holdout | +33.1 [+23.1, +43.0] | 270 / 179 / 91 | 27 |
| v5a | development | +38.0 [+28.2, +47.4] | 409 / 286 / 105 | 40 |
| v5a | holdout | +32.6 [+21.5, +43.9] | 267 / 182 / 91 | 27 |

The stopped original generation run supplies only 27 of the 40 original holdout cases with complete writing outputs. This is an availability subset, with unequal category counts, rather than a new random test sample. Development/holdout gaps can therefore reflect case composition as well as generalization.

Main tables use the same complete cases for both versions, all ten generation configurations, and both judges. Incomplete cases are listed in coverage.json rather than scored as ties. The six-output development pilots are separate.

For concrete strengths and questionable verdicts, read [the case review](case-review.md). These inspections did not change any score.

## Saved generation model families

Columns identify the models that produced the saved writing. Both new judges are Codex models; these numbers involve no new Claude calls.

| Skill | Split | Saved Claude outputs | Saved Codex outputs | Codex, excluding proofs |
|---|---|---:|---:|---:|---:|
| v4 | development | +57.7 [+47.5, +67.9] | +10.3 [-3.4, +24.4] | -3.9 [-17.2, +9.4] |
| v4 | holdout | +46.0 [+33.6, +58.0] | +13.9 [-3.2, +30.6] | +2.2 [-12.5, +16.3] |
| v5a | development | +57.5 [+46.7, +67.1] | +8.7 [-3.1, +20.3] | -3.5 [-14.1, +7.4] |
| v5a | holdout | +44.1 [+30.2, +58.0] | +15.3 [-1.4, +31.9] | +3.8 [-11.4, +17.9] |

## Writing categories

| Skill | Split | Ordinary | Research | Argument | Proof | Control |
|---|---|---:|---:|---:|---:|---:|
| v4 | development | +31.9 [+19.4, +43.8] | +48.1 [+30.6, +61.9] | +20.6 [-1.9, +46.2] | +75.0 [+60.6, +87.5] | +18.1 [+8.1, +28.1] |
| v4 | holdout | +18.1 [-1.2, +36.9] | +32.9 [+21.4, +45.0] | +26.2 [+15.0, +38.8] | +75.0 [+57.5, +92.5] | +28.8 [+18.8, +37.5] |
| v5a | development | +29.4 [+13.8, +46.9] | +51.2 [+35.0, +65.0] | +19.4 [+2.5, +40.0] | +75.0 [+65.0, +83.1] | +15.0 [+1.9, +30.0] |
| v5a | holdout | +10.0 [-6.9, +24.4] | +39.3 [+24.3, +53.6] | +23.8 [+11.2, +32.5] | +85.0 [+67.5, +97.5] | +22.5 [+12.5, +32.5] |

Category counts per split: {"development": {"ordinary": 8, "research": 8, "argument": 8, "proof": 8, "control": 8}, "holdout": {"ordinary": 8, "research": 7, "argument": 4, "proof": 4, "control": 4}}.

## Dimensions

| Skill | Split | Meaning | Naturalness | Progression | Voice | Proof |
|---|---|---:|---:|---:|---:|---:|
| v4 | development | +10.8 [+6.0, +15.5] | +23.2 [+16.3, +30.1] | +16.6 [+7.5, +25.9] | +39.2 [+29.8, +48.5] | +58.8 [+43.1, +73.1] |
| v4 | holdout | +13.7 [+6.9, +20.9] | +26.1 [+19.6, +32.4] | +8.5 [-2.8, +19.8] | +36.1 [+26.5, +46.3] | +76.2 [+56.2, +95.0] |
| v5a | development | +11.5 [+7.8, +15.4] | +24.9 [+18.0, +31.5] | +18.4 [+9.9, +26.9] | +38.5 [+28.8, +47.9] | +55.6 [+41.9, +66.9] |
| v5a | holdout | +12.8 [+6.1, +20.2] | +23.7 [+16.9, +30.6] | +11.5 [+0.2, +22.0] | +35.6 [+23.5, +47.6] | +76.2 [+57.5, +95.0] |

## Judges and reliability

| Skill | Split | Astra high | Sol high |
|---|---|---:|---:|
| v4 | development | +39.8 [+30.0, +49.2] | +37.8 [+28.5, +47.5] |
| v4 | holdout | +34.8 [+25.2, +44.4] | +31.5 [+20.0, +43.0] |
| v5a | development | +37.8 [+27.8, +47.5] | +38.2 [+28.2, +47.8] |
| v5a | holdout | +35.9 [+24.4, +47.8] | +29.3 [+17.4, +40.7] |

Cross-judge: 1097/1353 identical overall verdicts; 47 direct win/loss disagreements, across 68 distinct cases. Counts include configurations and versions and are not independent tasks.

Reversed-order: 226/286 identical overall verdicts; 14 direct win/loss disagreements, across 57 distinct cases. Counts include configurations and versions and are not independent tasks.

These are edits of synthetic supplied passages, not end-to-end manuscript work. Both judges belong to the OpenAI model family. Agreement does not establish human preference alignment or remove shared-model bias. Batching can affect judgments; pairs are anonymous, same-task, and independently graded, but batch composition is not randomized across repetitions.

## Matched historical comparison

Astra high is common to the old and new runs. The following uses only matching v5a/no-skill responses and complete configurations. The rubric, supplied author context, prompt batching, and A/B ordering changed together; this cannot identify the causal effect of any one of those changes.

| Split | Old Astra judgment | New Astra judgment | Changed / pairs |
|---|---:|---:|---:|
| development | +25.5 [+16.3, +34.5] | +37.8 [+27.8, +47.5] | 115 / 400 |
| holdout | -10.0 [-30.0, +0.0] | +0.0 [-40.0, +30.0] | 10 / 30 |

## Small development pilots

| Candidate vs no skill | Net advantage, pp [95% case CI] | Win / tie / loss | Cases |
|---|---:|---:|---:|
| v6-dev | +75.0 [+41.7, +100.0] | 9 / 3 / 0 | 6 |
| v7-dev | +25.0 [-16.7, +66.7] | 4 / 7 / 1 | 6 |

These pilots have only six saved case/configuration outputs each and do not share the full matrix. The original v6 pilot compared against v5a; this table compares against no skill, so its change from the old pilot score is not an isolated judge effect. They were developed after inspecting earlier results and cannot establish generalization. Packaged/installed v4 is unchanged.

## Evidence and execution

706 Codex judge attempts; 705 returned answers; 56 schema/evidence-invalid attempts; 1 transport failures. CLI-reported token total: 12,139,933 from 705 attempts. Failed calls without token reports are not estimated as zero. No account-percentage or billing-total claim is made.

plan.json binds the source datasets, exact saved writing, rubric, context, judge identities, ordering and retry limit. Observation files retain full verdicts, exact evidence quotes, source/prompt/response/raw hashes and any source-verified quotation-format repair. Validation reconstructs each blinded prompt and rechecks every verdict against the actual source. judge-responses.jsonl.gz contains the accepted raw text for independent revalidation; attempts.json accounts for unsuccessful attempts, whose raw answers remain local. Syntax-only recoveries disclose deleted trailing-comma offsets without changing any JSON value; see execution-notes.md. Original grades and response files are retained unchanged.

Reproduce without model calls: `MPLCONFIGDIR=/tmp/declaude-mpl .local/venv/bin/python tools/report_context_regrade.py --published --plot`. This verifies the portable public evidence and requires every frozen batch. Omit `--published` to read original local CLI artifacts. `--partial --out <folder>` writes an explicitly provisional local snapshot and never treats missing votes as ties.
