# Long-horizon revision pilot

This bounded development experiment asks whether the skill preserves a document's contribution, reasoning and earlier corrections through successive edits. Two synthetic documents instantiate two verified revision patterns from two private transcripts: deleting distinct guarantees while removing redundancy, and treating a broad prose correction as a local example. Only abstract patterns and independently written content are public. Private source locations and excerpts remain ignored. These sequences support the patterns, not claims that every reported revision was independently verified.

The user subsequently requested economical usage and permitted other model families. The pilot remains Astra high for writing, with Sol high for blind grading. No broad matrix or new Claude campaign is scheduled.

## Frozen candidate and comparisons

Use `v9-dev` versus no skill, with the same source document and six user turns in both arms. The core distinguishes argument editing, proof exposition and rhetorical cleanup. Proof and research-voice reference bytes remain identical to v4. All candidate files are frozen before execution. This experiment does not tune instructions or grading on the new holdout.

There are two development cases, one generator (`gpt-6-astra`, high), two conditions and six sequential turns: 24 writing turns. Each condition has its own isolated persistent Codex session and editable `document.md`. Later requests resume the same session with the same current artifact and actual conversation history. They do not start fresh chats with a summary substituted for history. Intermediate documents are saved after every turn. The feedback sequence is fixed before any outputs, and each request is applicable even if an earlier edit already addressed part of it.

The skill condition places the entrypoint in `AGENTS.md` with portable reference files available for selective reading. The no-skill condition has neither. Host user instructions, hooks and other skills are excluded from both environments. This tests the complete v9 setup, including progressive disclosure; it does not isolate shorter instructions from reference-loading behavior or directly compare v9 with v4.

## Usage limits

One writer at a time. Limit generation to 24 completed turns and at most two extra attempts for explicit transport failures with no completed edit. Never redraw an unfavorable answer or replay an ambiguous completed turn. The private ledger enforces a 250,000 reported-token scheduling budget with a 20,000-token reservation before another writing call. This is a soft guard: a single call can exceed its reservation, cached tokens may count, and CLI usage is not account quota or billing. Stop on missing successful-call usage. Schedule rounds across the four trajectories to retain comparable intermediate checkpoints if the guard stops the pilot.

Grading is limited to four Sol-high calls, with a separate 50,000 reported-token scheduling allowance and a 12,500-token reservation per call. No automatic quality retries. Preserve invalid grading answers and report missing judgments rather than treating them as ties. No other model runs are authorized by this protocol. Dataset authoring and coordination are separate from benchmark-call accounting.

## Assessment

The author-specific pairwise rubric from the preceding regrade is retained. A small adapter supplies the original document and every applicable user instruction in chronological order. Assess the first revision and the final common completed checkpoint separately. The first checkpoint includes only its initial instructions. The final checkpoint includes all instructions delivered up to it, with earlier constraints continuing unless explicitly superseded. Future instructions are never supplied to an earlier checkpoint's judge.

One primary call per case compares anonymous A/B outputs at both checkpoints. Two further calls reverse the final A/B order, one per case. Candidate identities are withheld. The order checks are diagnostics and never enter performance scores. Reasons need verbatim supporting excerpts; strict evidence validation and recorded syntax-only recovery apply. The source record and chronological requests govern fidelity, not intermediate model prose as ground truth. Score final document quality, contribution/scope preservation, paragraph progression, author voice, proof exposition where applicable, and instruction retention. Inspect actual artifacts as well as grades.

Report signed win-minus-loss percentage points with ties neutral, exact wins/ties/losses, stage, model/effort, and actual case counts. With only two cases, do not imply a stable population estimate or statistical confirmation. Report early stopping and the deepest common completed checkpoint honestly; fewer than six turns is not a completed six-turn evaluation. Preserve every trajectory, including failures.

## Holdout and release

An independent author, without candidate or development-case access, creates two new synthetic six-turn cases from the abstract pattern descriptions. Their contents remain private, unopened by the coordinator and unrun. Publish only a hash, counts and design provenance. Shared failure patterns mean this is a passage/trajectory holdout, not a holdout of entirely unseen failure mechanisms. The earlier 30-case isolated-rewrite holdout also remains sealed and unrun.

A pilot can identify a failure or support a provisional practical revision; it cannot establish general success. Retain the current installed release if the candidate loses a final primary comparison, introduces a major material error, or drops essential guarantees or proof steps. Otherwise inspect the complete documents before deciding whether to install the candidate provisionally, explicitly reporting the small sample and any order disagreement. Do not infer superiority to v4 from this no-skill comparison. Keep all proof guidance intact in any installation.
