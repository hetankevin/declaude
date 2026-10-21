# V11 targeted development repair

Two requested known development failures: Sol-low excluded-runs argument and Sonnet-high variance proof. One case per model. This diagnostic cannot establish generalization or preservation of earlier gains on untested cases. One frozen author-specific Sol-high judge with anonymous alternating A/B positions, no new order audits. All comparator drafts are reused.

Coverage: 2/2 drafts; 4/8 comparisons. Missing grades are never ties.

| Model | vs none | vs v4 | vs restored v9 | vs v10 |
|---|---|---|---|---|
| sol-low | ungraded | ungraded | ungraded | ungraded |
| sonnet-high | 1W/0T/0L; +100.0 pp | 1W/0T/0L; +100.0 pp | 0W/0T/1L; -100.0 pp | 0W/1T/0L; +0.0 pp |

Win rate minus loss rate in percentage points; ties zero. Small selected samples, no general superiority claim. Inspect actual cases and fidelity flags before promotion.

| Case | Model | Reference | Outcome | Candidate error |
|---|---|---|---|---|
| large-dev-b-14 | sonnet-high | none | win | True |
| large-dev-b-14 | sonnet-high | v4 | win | True |
| large-dev-b-14 | sonnet-high | v9-restored-dev | loss | True |
| large-dev-b-14 | sonnet-high | v10-dev | tie | True |

Usage: 4/4 attempts, 94,657 reported tokens, 0 unknown attempts, 6.14 estimated Codex credits plus 1/1 Claude calls. Guards:160k tokens/20 Codex credits with reservations; no automatic retries. Estimates are not account debits.

Evidence qualification: 0 optional-source-quote qualified verdicts, disclosed with raw evidence and exclusion sensitivity. Required factual/proof/response evidence remains strict.

Fresh holdouts untouched. Proof and all supporting reference files byte-identical to restored v9. Candidate frozen before execution; installed release remains v4. Reproduce without calls: python3 tools/v11_check.py report.
