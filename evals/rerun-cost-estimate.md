# Cost estimate for restored v9

Estimate only, 2026-10-20. No evaluation is authorized or launched by this document. Candidate: `evals/versions/v9-restored-dev/`. Tested `v9-dev` and its results remain frozen. Packaged and installed remain v4.

Restored core safeguards: concrete logical-force distinctions, personal research semicolon preference, internal-discussion exclusions, protection of adverse results, detailed fidelity and separate mathematical checks, and a warning against cosmetic “so what” endings. All reference files and UI metadata are identical to tested v9. Argument organization, correction retention, and proof guidance remain intact. This edit has no performance evidence yet.

## Candidate-only rerun estimates

Assume saved no-skill/v4 drafts pass exact task, model/effort, bundle, and response-hash checks. Generate only the restored candidate. Compare it with both references using the unchanged author-specific rubric and one Sol-high blind judge, packing at most four pairwise comparisons into a call within each case. Calls below exclude retries and order audits. Tokens include cached input and are not a hard cost cap.

| Scope | Writing calls | Judge calls | Total calls | Estimated reported tokens | Estimated Codex paid-credit component at Standard speed |
|---|---:|---:|---:|---:|---:|
| Repeat three selected cases on Astra high, Sol low, Sonnet high | 9 | 6 | 15 | 0.3–0.4M | 30–45, plus separate Claude usage |
| Broader development check: 20 cases, same three models | 60 | 40 | 100 | 2–2.5M | 200–300, plus separate Claude usage |
| Existing fully matched corpus: 67 cases, ten configs | 670 | 335 | 1,005 | roughly 20–30M | roughly 1,300–2,500, plus separate Claude usage |

The broader row is a planning extrapolation across additional models and harder passages, not a calibrated interval. It includes two Astra settings, Sol low, Luna medium, and six Claude configurations. Baseline inventory has 67 cases with all 20 no-skill/v4 entries. Covering the original 80-case design would require at least 800 candidate calls and 400 judge calls, plus any missing baseline work. The 67-case estimate does not claim full 80-case completion.

The economical protocol uses one judge, unlike the earlier two-judge studies. A second judge at the same model/cost approximately doubles the judging component, not the writing component. An Astra second judge can cost substantially more. Reversed-order audits, retries, absolute grading, and fresh baseline generation add cost. Reusing old baselines saves usage but retains the historical backend/time confound. The sealed 30-case and long-horizon holdouts are not read or included here. Previously evaluated holdout passages cannot be treated as fresh for this revision.

## Basis and limitations

Measured recent usage, from `results/prose-repair/v9-small/usage.json` and `results/prose-repair/v9-cross-model/usage.json`:

- Astra-high writing: mean 18,946 reported tokens and 4.79 Standard Codex credits per output at the current rate card.
- Sol-low writing: mean 18,705 tokens and 0.99 credits per output.
- Sonnet-high writing: mean 14,968 tokens per output, billed or metered separately by Claude.
- Sol-high four-comparison judge batches: mean 27,514 tokens and 2.76 credits per batch. Applying that mean to a final two-comparison batch is conservative relative to the saved two-comparison batches, but is not an upper bound.
- The three-model estimate is 3*(4.79+0.99)+6*2.76 = about 34 Codex credits, plus three Sonnet outputs. Token baseline is 3*(18,946+18,705+14,968)+6*27,514 = about 323,000 tokens. The 20-case estimate scales this per-case workload.

Credit calculation: `((input - cached_input)*input_rate + cached_input*cached_rate + output*output_rate)/1e6`. Do not add cached input to Codex input again. Claude reported token totals include cache creation/read as separate fields. Pricing source, accessed 2026-10-20: [official Codex pricing](https://learn.chatgpt.com/docs/pricing). Standard rates per million input/cached/output tokens: Astra 250/25/1250 credits; Sol 50/2.5/250; Luna 2.5/0.25/12.5. These are paid-credit equivalents, not measured debits or estimates of included subscription percentage. Credit purchase prices depend on the account/plan. No dollar conversion or Claude-credit conversion is claimed.

Token ranges allow modest prompt growth and variation but are not spending guarantees. New model-specific output lengths, cache behavior, retries, and batching can change actual cost. Coordinator usage is separate. These estimates cover isolated rewrites, not persistent manuscript revision: the earlier single-turn file-editing smoke alone used 92,604 reported tokens, so a long-horizon suite needs a separate budget.

A 20-case development check is more informative than another three-case check while avoiding the thousand-call rerun. Any approved execution should freeze cases, candidate, rubric, and hard call limit first, reuse valid artifacts, and stop at its budget. This document itself schedules nothing.
