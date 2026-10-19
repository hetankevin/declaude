# Research exposition and the author's voice

These directions distill recurring author corrections across research projects. They describe how to explain the work, not a fixed paper template or a license to import another paper's results.

## Read before rewriting

Read the current manuscript, its local `writing.md`, `WRITING_STYLE.md`, `WRITING_NOTES.md`, or `notation_and_style.md`, and the relevant passages in the author's selected writing samples. Check neighboring sections too. Distinguish explicit author instructions from an earlier agent's inferred preferences and self-assessment. A reviewer saying “style passed” is not a writing sample.

Use the samples to understand the order in which the reader encounters the problem, obstacle, construction, and result. Do not copy generic opening claims, claims of novelty, author identity, technical assumptions, notation, or confidence from them. A voice sample supplies rhythm and stance, not its objects, examples, conclusions, or recommendations. Transfer the way it develops an explanation, not its topic or sentence pattern. When samples are unavailable, follow the supplied directions and say so if making a claim of voice fidelity.

## Build the argument

Introduce the setting and what we want to accomplish. Use the closest relevant prior work to explain what remains unresolved. Develop the mechanism because the reader now understands the obstacle it addresses. State what is inherited, what changes, and why the change helps. Broader related work can follow later; do not exile the comparisons needed to motivate the contribution.

Explain each object before discussing its difficulty. Define what an algorithm samples, observes, stores, or optimizes before introducing the corresponding notation. When an example makes the setup easier, develop it and use it through the construction. Do not replace a method illustration with a toy numerical calculation unless that serves the requested purpose.

Contributions should state the actual result, its conditions, and its consequence. Do not announce contributions before motivating the problem. Do not substitute a list of components, error terms, or fashionable methods for an explanation of what was achieved.

## Write connected technical prose

Use conversational “we” to guide the reader through a choice or calculation. “Now, suppose” and “We write” can help, but repeating them mechanically does not produce the author's voice. Allow longer sentences and necessary connective explanation. Avoid clipped strings of imperatives.

For example, given a set of key vectors and a query vector, an explanation might read:

> We want to compare the query with every stored key. Let the rows of Q be the transposed key vectors. The entries of Qq are then their inner products with the query q, so we can select the largest score.

This example illustrates purpose, definition, and consequence. It is not a phrase template, and its notation and dimensions must match the actual application.

Each paragraph should develop an idea and give the next paragraph a reason to follow. Ask what the reader now knows and what remains unexplained. Edit the passage's organization before replacing conspicuous phrases. Do not turn a manuscript into a series of terse, technically correct summaries.

Use established terminology. Name a bound as a bound, a matrix as a matrix, and a condition as a condition. Avoid rhetorical headings such as “One honest caveat,” “The real win,” or “What this does and doesn't guarantee.” Prefer headings that identify the mathematical or scientific subject.

## Notation and claims

Introduce each symbol with its purpose, domain, and role. Keep distributions, scalar probabilities, matrices, vectors, indices, and parameters distinct. Preserve the current project's conventions. Where the project uses bold matrices and vectors, carry that convention consistently through prose, displays, captions, and diagrams; do not blindly bold scalars or sets.

Do not fill unspecified details with a convenient convention during a faithful rewrite. For example, “stack the vectors into Z” does not specify rows versus columns. Preserve that level of detail unless the existing equations establish it or the user authorizes a mathematical clarification. Explanatory prose must not quietly add a modeling or implementation choice.

Do not introduce a new named constant for a short expression used once merely to shorten a theorem. Avoid chains of definitions the reader must chase. Keep explicit dependence on meaningful dimensions, horizons, coverage, confidence, and approximation errors. Use local abbreviations when they genuinely help a long proof.

State assumptions where the result needs them and explain their role. Distinguish a condition necessary for the conclusion from one sufficient for the present proof. Do not call an assumption mild or standard without support. Avoid repeating a defensive disclaimer after every result.

Keep theorem scope exact: comparator, estimator, event, quantifiers, constants, probability, and regime. An upper bound is not a lower bound or an unavoidable error floor. An iteration rate with growing sample budgets is not the same sample-complexity rate. A small diagnostic is not a completed experiment for the full method. Preserve these distinctions without making the paper read like an internal audit.

## Proofs and main-text space

Use [proofs.md](proofs.md) for the full derivation. A main-text theorem can be compact while its proof is complete elsewhere. Keep central identities, constructions, and comparisons in the main text when they carry the contribution. Do not meet a page target by skipping proof steps or deleting the explanation that makes the method intelligible. Remove repetition and move genuinely supplementary work before cutting the central argument.

## Citations, figures, and discussion

Cite literature claims where they occur and explain the relationship to the closest work. An introduction may need frequent citations, but do not insert unrelated citations to satisfy a quota. Verify references and avoid importing a sample paper's bibliography as decoration.

Keep scientific figures focused on data or the intended mechanism. Plots normally need axes, ticks, and a legend, with at most a minimal title or panel label. Setup, interpretation, caveats, and provenance belong in the caption or surrounding text. Remove cute slogans and narrative banners. Inspect the author's actual figures and reuse the established style. Readability of a rendered artifact is a separate check from successful compilation.

Discussion should interpret supported findings and material limitations. Remove development logs, superseded arguments, and replies to objections that the reader never encountered. Retain reproducible settings and relevant unfavorable results. Do not add unsolicited comparisons or disclaimers, and do not turn a failure to establish the intended contribution into a different contribution during a style pass.

Before finishing, compare the revised passage with the actual sample: argument order, degree of explanation, sentence rhythm, notation, and transitions. Matching a few words or passing a build does not establish fidelity to the author's writing.
