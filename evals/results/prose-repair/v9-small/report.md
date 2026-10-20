# Small v9 development check

6/6 primary pairwise judgments accepted across three selected Astra-high development drafts. The original museum comparison is reused. The authorized completion grades saved drafts only, with the same Sol-high judge, author-specific rubric, context and anonymous A/B order. No text was regenerated or edited.

| Selected development case | vs no skill | vs v4 |
|---|---|---|
| Museum recommendation | tie | win |
| Reporting-policy argument | win | win |
| Finite-population proof | win | win |

| Comparison | Wins | Ties | Losses | Net advantage (pp) |
|---|---:|---:|---:|---:|
| none | 2 | 1 | 0 | +66.7 |
| v4 | 3 | 0 | 0 | +100.0 |

Ties contribute zero. These are three deliberately selected development cases, not a fresh test or stable population estimate. One fallible judge was used. The reversed-order audit is omitted to save usage; it is not counted as a tie. Saved baselines were generated earlier, so matching model labels do not prove an unchanged backend.

## Decision

Primary grade checks pass on three selected development cases. This task completed grading only; no installation change.. Packaged and installed v4 remain unchanged. No further calls are queued.

## Decisive comparisons

**Reporting-policy argument versus none: win. Neither has a material error. B better meets this user’s decisive priority: explain the problem and governing distinction before elaborating the construction. Its closing paragraph keeps the compromise and remaining costs together without A’s additional recap.

**Reporting-policy argument versus v4: win. Neither has a material error, and both retain the unresolved tradeoff. A better serves this user’s requested argument development: it establishes why exclusions need documentation before detailing the table, and presents the counts beside the problem they solve. B’s comprehensive opening is usable but creates more repetition.

**Finite-population proof versus none: win. Neither has a material error. A is the better completed appendix for this user because its pairwise-sum derivation explains the counting and centering steps, directly addressing the request to unpack the valid but compressed source. B remains a sound alternative.

**Finite-population proof versus v4: win. Neither has a material error, and both are usable proofs. B wins narrowly because its explanation of the pairwise identity more directly serves this user's explicit priority of laying out operations and their reasons; A leaves those particular justifications largely to the display.

## Scope and usage

The full bundle was inlined, matching the prior benchmark format. Selective reference loading was not tested. The [artifact review](artifact-review.md) is coordinator inspection, not an independent human grade. Proof and research-voice references remain byte-identical to v4.

The separate file-editing pilot stopped after one no-skill turn and a transcript-format validation failure. There is no matched long-horizon result. The fresh two-case six-turn holdout and earlier 30-case holdout remain sealed/unrun.

The grading completion used 2 new judge calls and zero writing calls, reporting 42,791 tokens. The full small pass now has 8 benchmark calls and a known subtotal of 211,329 reported tokens. The earlier failed judge call has unknown usage and is retained. These counts include cached inputs and are not billing or account quota. No automatic retry or order audit was run in the completion.

Reproduce without model calls: `python3 tools/finalize_small_repair.py`. Original frozen plans, completed grades and failed-attempt evidence are preserved.
