# Restored v9: incomplete development check

Stopped after 66/100 calls: Astra reported model capacity and returned no usage. The frozen unknown-usage guard stopped scheduling. 39/60 drafts and 78/120 verdicts are validated, covering 13/20 complete cases. No retries or model substitutions.

No aggregate headline or new heatmap is published from this incomplete, uneven category sample. Existing skill results remain historical. The unrun cases are missing, never ties.

77 verdicts passed the original validator; 1 needed source-verified first-letter quote capitalization repair, with raw answers and outcomes unchanged. See quote-format-repairs.json and formatting-amendment.md. No extra model call was used.

| Case | Model | Reference | Outcome |
|---|---|---|---|
| large-dev-a-02 | astra-high | none | win |
| large-dev-a-02 | astra-high | v4 | tie |
| large-dev-a-02 | sol-low | none | win |
| large-dev-a-02 | sol-low | v4 | tie |
| large-dev-a-02 | sonnet-high | none | win |
| large-dev-a-02 | sonnet-high | v4 | tie |
| large-dev-a-04 | astra-high | none | tie |
| large-dev-a-04 | astra-high | v4 | tie |
| large-dev-a-04 | sol-low | none | tie |
| large-dev-a-04 | sol-low | v4 | tie |
| large-dev-a-04 | sonnet-high | none | win |
| large-dev-a-04 | sonnet-high | v4 | tie |
| large-dev-a-06 | astra-high | none | win |
| large-dev-a-06 | astra-high | v4 | tie |
| large-dev-a-06 | sol-low | none | tie |
| large-dev-a-06 | sol-low | v4 | tie |
| large-dev-a-06 | sonnet-high | none | win |
| large-dev-a-06 | sonnet-high | v4 | loss |
| large-dev-a-08 | astra-high | none | win |
| large-dev-a-08 | astra-high | v4 | win |
| large-dev-a-08 | sol-low | none | win |
| large-dev-a-08 | sol-low | v4 | win |
| large-dev-a-08 | sonnet-high | none | win |
| large-dev-a-08 | sonnet-high | v4 | win |
| large-dev-a-10 | astra-high | none | loss |
| large-dev-a-10 | astra-high | v4 | win |
| large-dev-a-10 | sol-low | none | win |
| large-dev-a-10 | sol-low | v4 | loss |
| large-dev-a-10 | sonnet-high | none | win |
| large-dev-a-10 | sonnet-high | v4 | win |
| large-dev-a-12 | astra-high | none | win |
| large-dev-a-12 | astra-high | v4 | win |
| large-dev-a-12 | sol-low | none | win |
| large-dev-a-12 | sol-low | v4 | loss |
| large-dev-a-12 | sonnet-high | none | loss |
| large-dev-a-12 | sonnet-high | v4 | tie |
| large-dev-a-14 | astra-high | none | win |
| large-dev-a-14 | astra-high | v4 | tie |
| large-dev-a-14 | sol-low | none | win |
| large-dev-a-14 | sol-low | v4 | tie |
| large-dev-a-14 | sonnet-high | none | win |
| large-dev-a-14 | sonnet-high | v4 | loss |
| large-dev-a-16 | astra-high | none | tie |
| large-dev-a-16 | astra-high | v4 | loss |
| large-dev-a-16 | sol-low | none | win |
| large-dev-a-16 | sol-low | v4 | tie |
| large-dev-a-16 | sonnet-high | none | win |
| large-dev-a-16 | sonnet-high | v4 | win |
| large-dev-a-18 | astra-high | none | tie |
| large-dev-a-18 | astra-high | v4 | tie |
| large-dev-a-18 | sol-low | none | tie |
| large-dev-a-18 | sol-low | v4 | tie |
| large-dev-a-18 | sonnet-high | none | tie |
| large-dev-a-18 | sonnet-high | v4 | tie |
| large-dev-a-20 | astra-high | none | tie |
| large-dev-a-20 | astra-high | v4 | win |
| large-dev-a-20 | sol-low | none | tie |
| large-dev-a-20 | sol-low | v4 | tie |
| large-dev-a-20 | sonnet-high | none | win |
| large-dev-a-20 | sonnet-high | v4 | win |
| large-dev-b-02 | astra-high | none | win |
| large-dev-b-02 | astra-high | v4 | tie |
| large-dev-b-02 | sol-low | none | loss |
| large-dev-b-02 | sol-low | v4 | win |
| large-dev-b-02 | sonnet-high | none | tie |
| large-dev-b-02 | sonnet-high | v4 | loss |
| large-dev-b-06 | astra-high | none | tie |
| large-dev-b-06 | astra-high | v4 | tie |
| large-dev-b-06 | sol-low | none | win |
| large-dev-b-06 | sol-low | v4 | loss |
| large-dev-b-06 | sonnet-high | none | win |
| large-dev-b-06 | sonnet-high | v4 | win |
| large-dev-b-10 | astra-high | none | tie |
| large-dev-b-10 | astra-high | v4 | tie |
| large-dev-b-10 | sol-low | none | tie |
| large-dev-b-10 | sol-low | v4 | tie |
| large-dev-b-10 | sonnet-high | none | win |
| large-dev-b-10 | sonnet-high | v4 | tie |

Usage: 66/100 calls (40 writing, 26 grading), 1,248,598 reported tokens, 1 unknown attempts. Codex paid-credit equivalent at Standard rates: 124.51, plus Claude usage from 13/20 calls. Hard call cap100; scheduling guards2.5M tokens/300 Codex credits. These are not measured account debits or subscription percentages. No retries or additional calls for formatting repair.

Fresh holdouts remain sealed and unrun. No skill installation or automatic promotion. Case-level judgments, evidence, hashes and error flags are available in the accompanying JSON artifacts.
