# V12 targeted development repair

One additional Sonnet-high variance proof after the v11 core-only repair failed. The only change from v11 is a proof-reference warning against inferring dependence. No other cases rerun. This is a known-case repair diagnostic, not generalization evidence. One frozen author-specific Sol-high judge with anonymous alternating A/B positions, no new order audits. All comparator drafts are reused.

Coverage: 1/1 drafts; 5/5 comparisons. Missing grades are never ties.

| Model | vs none | vs v4 | vs restored v9 | vs v10 | vs v11 |
|---|---|---|---|---|---|
| sonnet-high | 1W/0T/0L; +100.0 pp | 1W/0T/0L; +100.0 pp | 0W/0T/1L; -100.0 pp | 1W/0T/0L; +100.0 pp | 1W/0T/0L; +100.0 pp |

Win rate minus loss rate in percentage points; ties zero. Small selected samples, no general superiority claim. Inspect actual cases and fidelity flags before promotion.

| Case | Model | Reference | Outcome | Candidate error |
|---|---|---|---|---|---|
| large-dev-b-14 | sonnet-high | none | win | False |
| large-dev-b-14 | sonnet-high | v4 | win | False |
| large-dev-b-14 | sonnet-high | v9-restored-dev | loss | False |
| large-dev-b-14 | sonnet-high | v10-dev | win | False |
| large-dev-b-14 | sonnet-high | v11-dev | win | False |

Usage: 2/2 attempts, 56,341 reported tokens, 0 unknown attempts, 3.77 estimated Codex credits plus 1/1 Claude calls. Combined v11+v12 guards:160k tokens/20 Codex credits with reservations; no automatic retries. Estimates are not account debits.

Evidence qualification: 0 optional-source-quote qualified verdicts, disclosed with raw evidence and exclusion sensitivity. Required factual/proof/response evidence remains strict.

Fresh holdouts untouched. Core and all other reference files unchanged from v11; only the proof-reference fidelity warning is added. Candidate frozen before execution; installed release remains v4. Reproduce without calls: python3 tools/v12_check.py report.
