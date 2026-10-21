# Quote-format validation amendment

During the frozen run, the original validator rejected a verdict whose source quote began “Those exchanges”, while the source contained “those exchanges”. The sentence and outcome were otherwise retained. No model retry is authorized for this.

After the run, `tools/finish_restored_check.py` may repair an evidence quote only if it differs in the case of its first character and has exactly one otherwise identical matching span in the supplied source. It must then pass the original validator. Internal capitalization changes, paraphrases, ambiguous matches, missing evidence, and substantive errors are not repaired by this rule. The same rule applies irrespective of candidate identity or verdict.

The raw answer remains unchanged. An audit artifact records each before/after quote, its field, original response hash, and validation-input hash. All reasons, preferences, error flags and severity labels must remain identical. The final report discloses original-validator and format-repaired coverage separately. This is a post-freeze deterministic formatting amendment, not a change to the judge's rubric or an extra model call. Failed repairs remain missing, never ties. Tests cover uniqueness, paraphrase rejection, internal capitalization rejection and preservation of existing verbatim evidence.
