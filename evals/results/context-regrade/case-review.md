# Reading the judgments against the writing

These are post hoc analyst inspections of synthetic examples, not independent human ratings or a measured judge-accuracy estimate. They illustrate what the new scores capture and where judgment remains questionable. Full sources and outputs are in `../large-interim/responses.json`; case IDs and generation configurations below identify the exact comparisons. They did not change the frozen rubric, skill, or reported votes.

## A proof improvement that reflects the stated preference

In `large-dev-a-16`, Astra high with v4 opens the projection proof by explaining the point of its decomposition:

> We will show that choosing any other \(y\in S\) adds exactly \(\|Px-y\|^2\) to the squared distance.

The no-skill proof is already correct and detailed. It begins by establishing membership and idempotence, then introduces residual and difference vectors. The skill version tells the reader why that algebra will prove minimization before doing it, while retaining displayed equalities and the roles of symmetry and idempotence. Both judges prefer v4. This is a modest explanatory improvement, not a correction of an invalid baseline proof.

## Purpose before a research comparison

In `large-dev-a-05`, Sol low with v5a starts with the existing manual-entry requirement, then introduces importing a blank reading to reduce transcription. The no-skill output starts with the proposed worksheet and describes what it replaces. Both preserve the experiment, discrepancy and limits. Both judges prefer v5a because the revised order first establishes the practical problem and purpose. The difference is small but follows the author's explicit narrative preference; a binary win does not measure the size of that improvement.

## A genuine fidelity concern

In `large-test-a-05`, Luna medium with v5a changes the source's statement that “several jobs were still waiting for parts” to “sixteen jobs were still waiting for parts.” The source supplies a count of unfinished jobs but does not establish that every unfinished job awaited parts. Both judges flag this as a minor material error. That is a specific inference changed by the edit, rather than a penalty for style or length.

## Organization that serves the artifact

In `large-test-a-03`, Astra high with v4 loses to its no-skill handover note under both judges. The baseline groups the equipment topics with labels and immediately states the cap's current status. Those choices help the next user locate the relevant checks without turning the note into terse commands. Removing that organization does not improve this practical document merely because the result has smoother paragraphs.

## A questionable interpretation by the judge

In `large-dev-b-01`, Fable with v4 says maps “will be retrieved from the store once a day rather than on demand.” Astra flags the last phrase as an unsupported claim that the previous service operated on demand. That historical reading is not required by the sentence: it can contrast two retrieval arrangements during the stated trial. The passage also retains the separately arranged fragile-map appointments.

The model's flag is preserved in the aggregate. This example shows why source quotations and a detailed rubric do not, by themselves, validate a judge's interpretation. It also matters that overall judgments are forced toward the side with lower worst material-error severity: an overread qualifier can outweigh a genuine prose improvement. Dimension-level results and judge disagreement should therefore be read alongside the overall scores.
