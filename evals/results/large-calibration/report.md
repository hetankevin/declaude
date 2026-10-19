# Pairwise grader calibration

Twelve synthetic fixtures: eight tuning and four reserved validation. Each is graded by two model families in both orders. These are assistant-authored targets, not human ground truth; the repeated judgments do not create additional independent fixtures.

| Grader / subset | Expected preferences matched | Fixtures |
|---|---:|---:|
| initial_tune | 26/32 | 8 |
| final_tune | 28/32 | 8 |
| validation | 13/16 | 4 |

One tuning-only clarification requires a concrete changed inference before labeling explanatory shorthand a material error. It corrected a persistent-map assessment; no target labels were changed. The prompt was frozen before validation.

All four tuning disagreements for the final prompt concern a supposed equivalent-paraphrase pair: one response drops the circumstance under which friend collection is mentioned. Both judges consistently prefer retaining it. The source does not explicitly make that circumstance necessary, but the unconditional rewrite can be read as broadening permission. The expected tie is therefore debatable.

Three validation disagreements concern a supposed length-neutral tie. Judges sometimes prefer one version because the other broadens a preparation assurance or ends redundantly. One judge changes tie versus preference with response order. These results remain unchanged and demonstrate remaining subjectivity. The independent factual-error, voice, bounded-edit, and proof-edge fixtures are retained.

Calibration supports proceeding with explicit disagreement/order reporting; it does not establish human-level grading reliability. No validation outcome changes the grader.
