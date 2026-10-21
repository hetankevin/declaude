# Restored v9: 20-case development check

Complete: 60 candidate drafts and 120 primary pairwise verdicts, reusing 120 exact saved no-skill/v4 baselines. Four cases each of ordinary prose, research, argument, proof, and already-good controls. These are the previously inspected development validation subset, not fresh OOS evidence. Fully inlined bundles do not test selective reference loading or long-horizon retention.

| Generator / effort | Restored v9 vs none | Restored v9 vs v4 |
|---|---|---|
| astra-high | +35.0 pp [+10.0, +60.0]; 8W/11T/1L | +15.0 pp [-5.0, +35.0]; 4W/15T/1L |
| sol-low | +35.0 pp [+5.0, +65.0]; 9W/9T/2L | -15.0 pp [-40.0, +10.0]; 2W/13T/5L |
| sonnet-high | +60.0 pp [+35.0, +85.0]; 13W/6T/1L | +10.0 pp [-20.0, +40.0]; 6W/10T/4L |
| all | +43.3 pp [+26.7, +61.7]; 30W/26T/4L | +3.3 pp [-8.3, +18.3]; 12W/38T/10L |

Win rate minus loss rate, in percentage points; ties contribute zero. Intervals bootstrap cases, not individual model votes. One frozen Sol-high author-specific blind judge, balanced anonymous A/B placement, no extra order audits. Historical baselines retain a possible backend/time confound.

| Category | Model | vs none (pp) | vs v4 (pp) |
|---|---|---:|---:|
| ordinary | astra-high | +50.0 | +0.0 |
| ordinary | sol-low | +0.0 | +25.0 |
| ordinary | sonnet-high | +50.0 | -25.0 |
| research | astra-high | +50.0 | +25.0 |
| research | sol-low | +50.0 | +0.0 |
| research | sonnet-high | +75.0 | +25.0 |
| argument | astra-high | +0.0 | +50.0 |
| argument | sol-low | +50.0 | -50.0 |
| argument | sonnet-high | +25.0 | +25.0 |
| proof | astra-high | +75.0 | -25.0 |
| proof | sol-low | +100.0 | -25.0 |
| proof | sonnet-high | +100.0 | +0.0 |
| control | astra-high | +0.0 | +25.0 |
| control | sol-low | -25.0 | -25.0 |
| control | sonnet-high | +50.0 | +25.0 |

Validation: 117 verdicts passed the original validator. One required source-verified initial-letter capitalization correction. Two verdicts had inadmissible optional source quotes in the voice dimension: one quoted a supplied assertion outside the validator's source/context pool, the other paraphrased an author preference as a quotation. Those optional quotes were removed from accepted evidence, with the raw answers, reasons, scores and severity flags unchanged. Required factual, proof and response quotations still pass the original validator. See quote-format-repairs.json and optional-quote-amendment.md. These two verdicts are flagged and excluded in quote-sensitivity.json. These are post-freeze reporting amendments, not additional model judgments. Reproduce with `python3 tools/finalize_restored_results.py`, then `python3 tools/plot_restored_check.py`.

Usage: 101/101 calls (61 writing, 40 grading), 1,919,254 reported tokens, 1 unknown attempts. Codex paid-credit equivalent at Standard rates: 188.71, plus Claude usage from 20/20 calls. Hard call cap101; scheduling guards2.5M tokens/300 Codex credits. These are not measured account debits or subscription percentages. No additional model calls for formatting repair.

Fresh holdouts remain sealed and unrun. No skill installation or automatic promotion. Case-level judgments, evidence, hashes and error flags are available in the accompanying JSON artifacts.

## Sensitivity to optional quote issues

These figures exclude the two qualified Sonnet proof judgments. The full table above retains their unchanged preferences.

| Model | vs none (pp; judgments) | vs v4 (pp; judgments) |
|---|---:|---:|
| astra-high | +35.0; n=20 | +15.0; n=20 |
| sol-low | +35.0; n=20 | -15.0; n=20 |
| sonnet-high | +57.9; n=19 | +15.8; n=19 |
| all | +43.3; n=59 | +5.0; n=59 |

Execution amendment: one user-authorized Astra capacity retry, 101 total attempts. All prior evidence was preserved. Budget accounting retains 30,000 tokens/8 credits as a reservation for the original failure's unknown usage, not as a measured debit. See continuation-plan.json.
