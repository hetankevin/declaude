# V10 targeted development repair

Six selected Sol-low cases and seven selected Sonnet-high cases. Selection targets known v9 regressions plus fidelity and explanation-order wins. The samples differ across models. This is a tuning diagnostic, not fresh OOS evidence or a model-family ranking. One frozen author-specific Sol-high judge with anonymous alternating A/B positions, no new order audits. All comparator drafts are reused.

Coverage: 13/13 drafts; 38/39 comparisons. Missing grades are never ties.

| Model | vs none | vs v4 | vs restored v9 |
|---|---|---|---|
| sol-low | 2W/4T/0L; +33.3 pp | 1W/4T/1L; +0.0 pp | 1W/4T/1L; +0.0 pp |
| sonnet-high | 6W/0T/0L; +100.0 pp | 3W/4T/0L; +42.9 pp | 4W/2T/1L; +42.9 pp |

Win rate minus loss rate in percentage points; ties zero. Small selected samples, no general superiority claim. Inspect actual cases and fidelity flags before promotion.

| Case | Model | Reference | Outcome | Candidate error |
|---|---|---|---|---|
| large-dev-a-06 | sonnet-high | none | win | False |
| large-dev-a-06 | sonnet-high | v4 | win | False |
| large-dev-a-06 | sonnet-high | v9-restored-dev | win | False |
| large-dev-a-08 | sol-low | none | tie | False |
| large-dev-a-08 | sol-low | v4 | tie | False |
| large-dev-a-08 | sol-low | v9-restored-dev | tie | False |
| large-dev-a-10 | sol-low | none | win | False |
| large-dev-a-10 | sol-low | v4 | win | False |
| large-dev-a-10 | sol-low | v9-restored-dev | tie | False |
| large-dev-a-10 | sonnet-high | none | win | False |
| large-dev-a-10 | sonnet-high | v4 | win | False |
| large-dev-a-10 | sonnet-high | v9-restored-dev | win | False |
| large-dev-a-12 | sol-low | none | tie | False |
| large-dev-a-12 | sol-low | v4 | loss | False |
| large-dev-a-12 | sol-low | v9-restored-dev | loss | False |
| large-dev-a-14 | sonnet-high | none | win | False |
| large-dev-a-14 | sonnet-high | v4 | tie | False |
| large-dev-a-14 | sonnet-high | v9-restored-dev | tie | False |
| large-dev-b-02 | sonnet-high | none | win | False |
| large-dev-b-02 | sonnet-high | v4 | tie | False |
| large-dev-b-02 | sonnet-high | v9-restored-dev | win | False |
| large-dev-b-06 | sol-low | none | tie | False |
| large-dev-b-06 | sol-low | v4 | tie | False |
| large-dev-b-06 | sol-low | v9-restored-dev | tie | False |
| large-dev-b-06 | sonnet-high | none | win | False |
| large-dev-b-06 | sonnet-high | v4 | win | False |
| large-dev-b-06 | sonnet-high | v9-restored-dev | tie | False |
| large-dev-b-14 | sol-low | none | win | False |
| large-dev-b-14 | sol-low | v4 | tie | False |
| large-dev-b-14 | sol-low | v9-restored-dev | tie | False |
| large-dev-b-14 | sonnet-high | none | win | True |
| large-dev-b-14 | sonnet-high | v4 | tie | True |
| large-dev-b-14 | sonnet-high | v9-restored-dev | loss | True |
| large-dev-b-16 | sonnet-high | v4 | tie | False |
| large-dev-b-16 | sonnet-high | v9-restored-dev | win | False |
| large-dev-b-20 | sol-low | none | tie | False |
| large-dev-b-20 | sol-low | v4 | tie | False |
| large-dev-b-20 | sol-low | v9-restored-dev | win | False |

Usage: 25/25 process attempts, 484,495 reported tokens, 1 unknown attempts, 29.44 estimated Codex credits plus 8/8 Claude attempts (one failed before API use). Guards:700k tokens/90 Codex credits with reservations; no automatic retries. Estimates are not account debits.

Evidence qualification: 0 optional-source-quote qualified verdicts, disclosed with raw evidence and exclusion sensitivity. Required factual/proof/response evidence remains strict.

Fresh holdouts untouched. Proof and all supporting reference files byte-identical to restored v9. Candidate frozen before execution; installed release remains v4. Reproduce without calls: python3 tools/v10_check.py report.

Transport amendment: two sandbox failures preserved, retried once with network access. 23 planned model calls, at most25 CLI process attempts. Original Codex failure charged30k tokens/3 credits for unknown usage; Claude reports zero API usage. Scientific inputs unchanged. Use python3 tools/v10_network.py report to reproduce.

One batch repeated the same empty source-quote key. A no-call reporting repair collapses identical values only, retaining the raw answer and all preferences/reasons. Two verdicts then pass validation. Its no-skill comparison still fails a required proof source quotation and remains ungraded, never a tie. Thus Sonnet vs none has n=6; its other comparisons have n=7. Sol has n=6 throughout. See identical-duplicate-repairs.json. Reproduce final artifacts with python3 tools/finalize_v10.py.
