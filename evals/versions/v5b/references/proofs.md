# Mathematical proofs

The author's repeated correction is specific: proofs should use displaystyle mathematics, lay out the steps, and avoid long prose paragraphs filled with inline formulas that conceal the derivation. Concision in a theorem statement is not permission to skip steps in its proof.

## Show the argument

Begin with the quantity, event, or identity being proved. Define the objects actually used, including probability laws, conditioning information, norms, and index ranges. Expand an abstract abbreviation when its concrete structure matters. Do not replace a structured sum or estimator by an arbitrary functional and thereby lose the property the proof needs.

Use displayed equations for identities, decompositions, recurrences, bounds, and intermediate calculations. In LaTeX, use `equation`, `align`, or `aligned` as appropriate; these already use display style. Use `\displaystyle` where the surrounding environment would otherwise compress the mathematics. Do not force every short inline symbol into a display or merely insert `\displaystyle` into an unchanged paragraph.

Break a derivation across readable lines with aligned equality or inequality signs. Give each nontrivial transition a reason at the relevant line or immediately next to the display: substitution, conditioning, a named inequality, an assumption, a previously proved identity, or an explicitly cited result. A wall of aligned formulas with unexplained jumps is not an improvement.

Use short connective prose to explain what is being bounded and why the next step is valid. Avoid paragraphs that narrate the entire proof without doing it. “By standard arguments,” “a straightforward calculation,” and “concentration gives the claim” do not replace the calculation where the step is material. Do not number every elementary operation or explain routine arithmetic at textbook length.

Before a limit, substitution, or conditioning step, check what varies and what is held fixed against the displayed expression. A correct formula does not rescue a contradictory explanation of how it was obtained. Give one complete proof unless alternatives are requested or serve distinct mathematical purposes. Do not append a second derivation, a redundant remark, or an extra conclusion after the claim is proved. Avoid unused abbreviations and headings for every line of algebra. Completeness means the necessary steps are visible, not that the same steps are explained twice. Check the first and last index before displaying a chain: a line containing a_{t-2} is not defined for t=1 unless negative indices were explicitly provided.

## Preserve the mathematics

Show the substitutions and parameter choices when invoking a lemma. Check its hypotheses on the actual object. If it applies to individual summands, establish that and then sum; do not assert it for the aggregate without justification.

Keep conditioning and expectations explicit when they matter. State which cross terms vanish and why. Do not infer independence, zero covariance, interchange of limits or expectations, or uniformity in a parameter without the required premise. Preserve signs, normalization, dimensions, constants, quantifiers, endpoint cases, probability events, and parameter ranges.

Distinguish an equality from an upper bound, an asymptotic relation from a finite-sample result, and a conditional result from an unconditional one. Trace how each intermediate bound gives the claimed rate, including the final summation or tuning step. Do not conceal a factor inside an unexplained constant.

If expanding a step exposes a gap, show where the proof stops and what would be needed. Do not invent an assumption, weaken the target, or present a plausible derivation as established. A request to edit prose permits mathematically equivalent expansion, not an unannounced new theorem.

## Example: expand a recurrence

Suppose the source states, for every integer t >= 0,

\[
e_{t+1}\leq \rho e_t+b,\qquad 0<\rho<1,\quad b\geq0.
\]

The case t=1 is the given recurrence, and t=0 holds with an empty sum. For t>=2, instead of “Iterating yields the usual geometric bound,” show the expansion:

\[
\begin{aligned}
e_t
&\leq \rho e_{t-1}+b\\
&\leq \rho^2e_{t-2}+b(1+\rho)\\
&\leq \rho^te_0+b\sum_{j=0}^{t-1}\rho^j\\
&=\rho^te_0+b\frac{1-\rho^t}{1-\rho}.
\end{aligned}
\]

The third line follows by repeated substitution (or induction); the last uses the finite geometric sum. The first term records the initial error and the second accumulates the additive errors. Do not claim the error converges to zero when b is positive.

## Example: justify the missing cross term

Let X be square-integrable and let F be a sigma-algebra. Set m = E[X | F]. For an F-measurable square-integrable Y, first write

\[
X-Y=(X-m)+(m-Y).
\]

The mixed term vanishes because m-Y is F-measurable:

\[
\begin{aligned}
\mathbb E[(X-m)(m-Y)]
&=\mathbb E\!\left[(m-Y)\mathbb E[X-m\mid F]\right]\\
&=0.
\end{aligned}
\]

Expanding the square therefore gives

\[
\mathbb E[(X-Y)^2]
=\mathbb E[(X-m)^2]+\mathbb E[(m-Y)^2].
\]

This example shows the conditioning that justifies orthogonality. It does not establish independence, and it cannot be reused for a non-F-measurable Y without a different argument.

## Final proof check

Read the proof without the conversation. Can the reader reproduce every substantive transition from the displayed premises, definitions, and citations? Are the expressions readable at the final page size? Preserve the manuscript's theorem environments, numbering, labels, and references. For a rendered document, inspect the actual mathematical layout after compiling. Compilation and reviewer agreement do not by themselves establish mathematical correctness.
