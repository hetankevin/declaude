"""Two synthetic multi-turn development cases; contains no private source excerpts."""
import json
from pathlib import Path

cases=[]
cases.append(dict(id='lh-dev-01',category='research',source_pattern_ids=['LH-01','LH-02'],is_proof=True,
initial_document=r'''# Two ways to interpret repeated measurements

## Why repeat a reading?

Averaging is the spine of the measurement pipeline. Repeated readings give a clean route from several uncertain numbers to one reported value. But the uncertainty comes in more than one form. A reading can have an error that is bounded on every use, or it can have a random error that is centered only over repeated use. This distinction is load-bearing. We consider a fixed unknown real quantity theta and n readings x_i=theta+e_i, where n is a positive integer. The reported value is m_n=n^{-1} sum_i x_i. The point of this note is to explain what averaging guarantees in each of these two settings. We are not choosing one setting as the correct description of every instrument.

A fixed error bound is useful when an operator needs a guarantee for the actual readings on the bench. A random-error calculation instead describes average squared performance over hypothetical repetitions under its statistical assumptions. It is tempting to report whichever bound shrinks with the number of readings. That choice would conflate the assumptions supporting the two guarantees. We want a reader to see when each conclusion is available and why one does not replace the other.

## Two guarantees

Under the deterministic condition |e_i|<=b for each i, with b>=0, the claimed bound is |m_n-theta|<=b. This conclusion holds for every permitted collection of errors. It does not promise improvement as n grows. If every error equals b, the averaged error also equals b, so the bound can be attained.

In the separate random setting, assume that the e_i are mutually independent, square-integrable, have E[e_i]=0 and E[e_i^2]<=s^2, with s>=0. Here we claim E[m_n]=theta and E[(m_n-theta)^2]<=s^2/n. We impose no almost-sure bound on these random errors. Conversely, the deterministic assumption above says nothing about their means or independence. The guarantees thus answer different questions even though the same arithmetic mean appears in both.

## Proofs

Write the error. Apply the triangle inequality. The conclusion follows from the uniform bound. More explicitly, m_n-theta=n^{-1} sum_i e_i, and |m_n-theta|<=n^{-1} sum_i |e_i|<=n^{-1} nb=b. Taking all e_i=b establishes the stated tight example.

For the random setting, taking expectations in the same identity gives E[m_n]-theta=n^{-1} sum_i E[e_i]=0. Expand the square. The cross terms vanish by independence and zero means. In full, E[(m_n-theta)^2]=n^{-2}(sum_i E[e_i^2]+2 sum_{i<j} E[e_i e_j]). For i not equal to j, E[e_i e_j]=E[e_i]E[e_j]=0. Therefore the expression is at most n^{-2}ns^2=s^2/n. None of this shows that every realized average has an error at most s/sqrt(n).

Both proofs start with the same error identity. They differ in what can be done after that identity. Repeating the setup under two separate theorem introductions would make the note longer without helping the reader, but removing either conclusion would change its purpose.

## Presentation notes

The first draft put the random result first because its bound looks more attractive. During editing we considered moving the deterministic statement into an appendix. These are drafting decisions, not evidence. A conceptual illustration could show errors pointing in the same direction and errors pointing in mixed directions. It should explain the two possibilities rather than pretend to provide measured data.

## Discussion

Neither calculation is an experiment on an instrument. In particular, a slowly varying shared offset would violate the random model's independence assumption, and merely taking more readings would not justify the random guarantee. The calculations explain why an operator needs to decide which assumptions describe the task before interpreting the benefit of averaging. No instrument comparison or empirical accuracy improvement is reported here.
''',
initial_request='Revise this short technical note for readers who know basic probability. Develop its argument and remove clumsy AI prose across the whole note. Keep both mathematical guarantees and their separate assumptions. Present the proofs in displayed steps with reasons for the nontrivial transitions. Edit document.md rather than writing a review.',
feedback=[
 'Consolidate the repeated setup and genuinely duplicated proof material. Make clear what each guarantee lets the reader conclude. A result is not redundant merely because the other proof does not use it.',
 'Focus this turn on the conceptual illustration description near the end. Make it useful to a reader comparing the two error models, without introducing a numerical example or an experiment. Keep it as a description for an illustrator.',
 'Remove the discussion of earlier drafts and editorial choices. Keep the useful illustration description and the substantive interpretation of the two error models. Do not replace the removed history with another account of our revision process.',
 'The note needs to be shorter. Aim to cut repetitive prose by roughly a tenth, but do not meet a word target by dropping a guarantee, an assumption, a substantive qualification, or a displayed proof step. Keep enough explanation for a first reading.',
 'Make a final pass through the whole note. The introduction, statements, proof introductions, illustration description, and discussion should tell the same story. Repair missing connections between paragraphs and then leave effective passages alone. Do not add experiments or citations.'
],invariants=[
 {'id':'distinct-guarantees','since_turn':0,'text':'Retains both the deterministic error guarantee and the random unbiasedness/MSE guarantee; neither replaces the other.'},
 {'id':'mathematical-scope','since_turn':0,'text':'Preserves all assumptions and quantifiers, the tight deterministic example, the constant b, and the exact s^2/n bound without claiming a realized-error bound.'},
 {'id':'proof-exposition','since_turn':0,'text':'Displays the error identity, triangle bound, expectation, square expansion and vanishing cross-term justification; explains their purpose and does not skip substantive steps under shortening pressure.'},
 {'id':'whole-story','since_turn':0,'text':'Explains why two error models answer different reader questions, with connected paragraph-level exposition throughout.'},
 {'id':'illustration-form','since_turn':2,'text':'Keeps a conceptual illustration description connecting the models, not a fabricated experiment or numerical example.'},
 {'id':'history-removed','since_turn':3,'text':'Removes draft/revision history and does not reintroduce it while retaining scientific limitations.'}
]))
cases.append(dict(id='lh-dev-02',category='argument',source_pattern_ids=['LH-02','LH-01'],is_proof=False,
initial_document='''# Choosing which records to inspect twice

## The decision

A local history group has copied dates from a collection of shipping registers into an index. We propose a targeted second reading of ambiguous entries, followed by a small audit of entries considered clear. The double-check is the engine of trust. The point is not that more checking is always better, but that checking is how the workflow earns its confidence. There are 1,200 entries. The proposal would change how review time is allocated, not declare any entry correct automatically.

The volunteers have two hours of review time available for this trial. That is a scheduling limit, not a completed measurement of how long every option will take. A complete second reading of every entry has been suggested as an alternative. We have not timed that alternative and cannot claim that it is impossible within the time available. Our reason for proposing a targeted trial is to learn whether the ambiguity flags help direct attention, while retaining a way to discover mistakes among the unflagged entries.

## What the first check tells us

A preliminary comparison used 60 entries whose images were especially easy to obtain. Two readers disagreed on nine dates. Seven of those nine entries had already been flagged as ambiguous by the first reader, and two had not. This is a convenience sample, not a random sample from the collection. It does not estimate a collection-wide error rate, and disagreement is not itself proof that either reader is wrong. The comparison suggests that the flags may be useful, but it also gives a concrete reason not to ignore unflagged records.

## Proposed review procedure

Take flags. Sort entries. Allocate attention. The first reader would record a flag when a date could reasonably be read in more than one way, and briefly note the source of that ambiguity. A second reader would independently inspect all flagged images before seeing the first transcription. The readers would then discuss disagreements and retain both readings when the image does not support a resolution. The database would distinguish a resolved correction from an unresolved alternative.

Unflagged entries require a different operation. Choose a simple random sample of 40 from the unflagged entries without replacement, assuming at least 40 remain. Apply the same independent second-reading procedure. This audit checks whether the flagging process has missed disagreements. Forty is the proposed trial size, not a claimed sufficient sample for an accuracy guarantee. We have not derived a collection-wide precision bound from it. If fewer than 40 unflagged entries remain, review all of them instead. That fallback does not change how flagged entries are handled.

## Why not inspect everything?

A complete second reading might reveal disagreements that the targeted trial misses. It also creates review work on entries the first reader found unambiguous, though we have not measured the total cost. The proposed trial deliberately accepts incomplete coverage in exchange for learning how flags and a small unflagged audit work together. A committee that wants complete coverage should choose the complete second reading explicitly, rather than describe this proposal as equivalent to it.

Independent readings can still share a mistake. Even unanimous readings do not establish that a date is historically correct. Where the image is inconclusive, the index should keep the uncertainty visible instead of forcing a single date. The trial has not yet been run. Its immediate output would be a record of review decisions, unresolved alternatives, and time spent, not proof that the final index has a known error rate.

## Editorial note

An earlier outline gave the nine disagreements their own dramatic heading. A reviewer then suggested calling the flags a confidence layer. We are removing that description because it is not how the volunteers talk. The table heading is provisionally “Review record.” The committee still needs to approve the trial and decide what to do if review exceeds the available time.

## Closing recommendation

Approve the limited trial if the committee wants evidence about the usefulness of the flags. Record the review time and unresolved cases alongside the outcomes. Decide whether to extend or change the review after seeing those results. This recommendation leaves the tradeoff between coverage and workload open rather than pretending that the targeted procedure dominates a complete second reading.
''',
initial_request='Rewrite this proposal for the committee. Make it sound like connected, direct human prose and develop the reasoning, rather than swapping individual words. Preserve the proposed decision, the concrete facts, and the unresolved tradeoff. Apply the improvement throughout the document. Edit document.md.',
feedback=[
 'The method paragraph beginning with clipped commands is an example of the problem, not the whole assignment. Make the transitions explain why the next operation is needed wherever the reader would otherwise have to reconstruct that reasoning.',
 'For this turn, improve the proposed table heading and the short explanation of what it records. Use a name volunteers can understand. Keep this a local edit; preserve the other improvements already made.',
 'Remove the editorial history and discussion of prior wording choices. Keep the useful table description and the still-unresolved approval and timing decisions. Do not turn a proposal into a report of work already completed.',
 'Tighten repeated cautionary language. Preserve qualifications that limit different claims, and keep each beside the relevant claim. Do not collapse the evidence, procedure, and tradeoff into one dense paragraph just to shorten the document.',
 'Read the final proposal as a whole. Make sure a committee member can follow the evidence through the procedure to the decision, and that the local table edit has not displaced the main argument. Leave already-effective passages alone; keep the recommendation conditional and the trial unrun.'
],invariants=[
 {'id':'same-proposal','since_turn':0,'text':'Retains targeted review of every flagged entry plus random review of 40 unflagged entries, the all-remaining fallback, and the distinct complete-review alternative.'},
 {'id':'facts-and-status','since_turn':0,'text':'Retains 1200 entries, two available hours, convenience sample of60, nine disagreements with seven flagged and two unflagged; no trial completion, timing estimate, or collection-wide accuracy claim is invented.'},
 {'id':'global-explanation','since_turn':0,'text':'The reason for flags, independent readings, unflagged auditing, and unresolved alternatives is clear across whole passages, not just corrected command words.'},
 {'id':'honest-tradeoff','since_turn':0,'text':'Keeps incomplete coverage, shared-error possibility, uncertainty, and untimed complete-review alternative without turning the note into repeated disclaimers.'},
 {'id':'local-edit-retention','since_turn':2,'text':'The table heading and explanation remain comprehensible while the proposal retains its broader evidence-to-decision progression.'},
 {'id':'editorial-removal','since_turn':3,'text':'Removes editorial process history without deleting actual approval/timing decisions or restoring removed discussion under new wording.'}
]))

if __name__=='__main__':
 p=Path(__file__).with_name('development.json');p.write_text(json.dumps(dict(version='long-horizon-v1',split='development',cases=cases),indent=2)+'\n')
 print([(c['id'],len(c['initial_document'].split()),1+len(c['feedback'])) for c in cases])
