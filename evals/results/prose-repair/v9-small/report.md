# Small v9 development check — incomplete

V9 simplifies the prose instructions, separates argument editing from rhetorical compression, and preserves proof and research-voice reference files byte-for-byte. Three new Astra-high drafts are saved. A Sol-high transport timeout stopped grading after the first case. V4 remains packaged and installed; the general Codex prose repair is unresolved.

| Selected development case | vs no skill | vs v4 |
|---|---|---|
| Museum recommendation | tie | win |
| Reporting-policy argument | ungraded | ungraded |
| Finite-population proof | ungraded | ungraded |

The two accepted judgments concern one case only. They use the unchanged author-specific rubric and anonymous A/B texts. There is no aggregate improvement claim, order check, or new OOS result. Missing judgments are not ties. These cases were selected from known development weaknesses, and saved baselines were generated earlier.

The full bundle is inlined, matching the prior benchmark format. This does not test selective reference loading. The [manual artifact review](artifact-review.md) finds the proof valid and the argument changes mixed; it is not an independent blind grade.

The separate persistent file-editing pilot stopped after its first no-skill turn used 92,604 reported tokens. Its validator also encountered a newer transcript format. That completed draft is retained privately without replay. No matched or long-horizon result exists. The new two-case six-turn holdout and the earlier 30-case holdout remain sealed/unrun and privately backed up.

This pass made 6 benchmark calls: one file-editing smoke, three isolated rewrites, and two grading calls. The known subtotal is 168,538 CLI-reported tokens, including cached input; the failed grading call reported no usage. This is not a complete token total, billing estimate, or account-quota measurement. No Claude calls, replacement generations, or application-level retries were made. The failed call attempted internal transport reconnection. No jobs remain running.

The original frozen plans and raw failed evidence are retained. This report uses a read-only finalizer because the original runner deliberately stops on missing successful usage. Reproduce without model calls: `python3 tools/finalize_small_repair.py`. Do not resume the benchmark automatically.
