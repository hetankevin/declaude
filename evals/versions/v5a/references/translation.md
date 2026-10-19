# Claudish to plain English

This is the user-supplied translation specification. Its output-only instruction applies to rewriting, not to a request to review or build a skill.

Apply it to the content the user wants retained. An explicit instruction to remove a discussion or caveat overrides this specification's default preservation of that content. Preserve the meaning and logical force of the remaining passage without reintroducing the removed discussion.

Translate the input from **“Claudish”** into plain, direct, idiomatic English.

“Claudish” is the characteristic prose style of Claude and Claude Code: contrast-heavy, structurally metaphorical, process-oriented, rhetorically polished, and prone to expressing a simple point through abstractions, restatements, technical compounds, and emphatic framing.

The goal is to recover the **smallest set of ordinary propositions that preserves every independently meaningful claim in the input**.

**Delete rhetoric, not information.**

## 1. Preserve meaning and logical force

Preserve every independently meaningful:

* fact;
* instruction;
* condition;
* permission or prohibition;
* requirement;
* recommendation or preference;
* comparison;
* causal claim;
* uncertainty or degree of confidence;
* temporal relationship;
* logical dependency.

Do not add new facts, interpretations, recommendations, causal claims, exclusivity rules, implications, or conclusions.

Preserve the speech act exactly. Do not turn:

* a description into an instruction;
* an instruction into a description;
* a recommendation into a requirement;
* a permission into an action;
* a possibility into a fact;
* a prerequisite into a sufficient condition.

Preserve negation, modality, quantifiers, timing, scope, and direction of dependency.

A trigger does not become an exclusivity rule. A prerequisite does not become a definition or causal explanation. A preferred option does not become a mandatory one. “Not started” does not mean “in progress.” “Not tested” does not mean “incorrect.” “Required” does not mean “sufficient.”

When the wording is ambiguous, use the narrowest interpretation directly supported by the input.

## 2. Remove semantic redundancy aggressively

Claudish often expresses one underlying proposition multiple times.

Delete a clause or sentence when it merely:

* restates something already preserved;
* emphasizes or dramatizes it;
* summarizes it;
* gives it a metaphorical label;
* explains an obvious consequence of it;
* characterizes it at a higher level of abstraction;
* justifies it rhetorically without adding a necessary claim;
* creates an artificial contrast around it;
* converts it into a slogan or aphorism.

A grammatically distinct sentence is **not automatically a distinct claim**.

Do not preserve an elaboration merely because it uses different words.

A multi-sentence Claudish passage may legitimately become one short sentence. Do not produce one output sentence for every input sentence.

If a reader who already knows the retained propositions would learn **nothing materially new** about what is true, what happened, what should be done, what is allowed, what is required, what is uncertain, or what to expect, delete the clause.

When an elaboration follows naturally from a simpler retained proposition and does not materially change the reader’s actions, beliefs, permissions, or expectations, prefer the simpler proposition.

## 3. Preserve genuinely meaningful additions

Do not delete a statement merely because it sounds like an elaboration.

Keep it if it independently changes:

* what happened or is true;
* what action should be taken;
* what action is allowed or forbidden;
* what is required or preferred;
* what condition applies;
* what uncertainty remains;
* why something happened;
* what tradeoff or consequence matters.

Compression must remove **redundancy**, not distinct semantic content.

## 4. Remove rhetorical Claudish framing

When it adds no independent meaning, omit rather than paraphrase:

* validation or agreement theater;
* “honest” or “candid” setup phrases;
* announcements of a key, deep, clean, hard, or important point;
* “in one sentence,” “put differently,” “in other words,” and similar orientation;
* “that distinction matters,” “that is the boundary,” and similar aphoristic conclusions;
* “smoking gun,” “load-bearing distinction,” “the verdict here,” and similar staged emphasis;
* rejected framings whose only purpose is rhetorical contrast.

Do not replace these with simpler filler. Delete them.

## 5. Preserve meaningful contrasts

Do not mechanically remove “not X but Y,” “X, not Y,” or similar constructions.

Keep a contrast if the rejected alternative rules out an otherwise plausible action, interpretation, condition, source, or choice.

Remove it if the rejected alternative is merely a rhetorical inverse, redundant restatement, or dramatic characterization of a proposition already preserved.

## 6. Decode structural and process metaphors

Rewrite unnecessary Claudish abstractions as the concrete relationships they express.

Common tendencies include:

* **X-gated / gated on X** → express the actual requirement, restriction, or prerequisite;
* **owner-gated / approval-gated** → state directly who may act or what approval is required;
* **hard gate / hard boundary / hard stop** → state the actual rule, blocker, or condition;
* **load-bearing** → state what is essential or necessary;
* **surface** → name the actual object, interface, issue, or area;
* **path** → name the actual action, option, or process;
* **layer** → name the actual component or responsibility;
* **handoff** → state the actual transfer or transition;
* **spine** → state the actual central structure or requirement;
* **landed** → use the concrete completion action supported by context;
* **surfaced** → use appeared, found, shown, reported, or the contextually correct verb;
* **stale** → use outdated or no longer current when that is what it means;
* **verified / audited** → use tested, checked, confirmed, or the precise technical term;
* **canonical** → use authoritative, official, preferred, or the precise technical term;
* **blocker** → state what prevents progress;
* **drift** → state the actual change or divergence;
* **routing / routing layer / context router** → describe actual routing only if routing really occurs.

Do not mechanically substitute from this list. Recover the relationship first, then choose natural wording.

## 7. Decompress technical compounds

Rewrite dense noun stacks and hyphenated abstractions into ordinary clauses.

For constructions such as:

* **X-gated**
* **X-backed**
* **X-side**
* **X-level**
* **X-first**
* **X-safe**
* **X-matched**
* **X-layer**
* **X-surface**
* **X-path**
* **X-boundary**

recover the concrete relationship between X and the surrounding statement.

Prefer ordinary verbs and clauses over invented conceptual nouns.

Do not preserve an abstraction merely because the input names it.

## 8. Normalize over-formal research language

Simplify terms such as **frontier, horizon, floor, surface, exchange rate, regime, trajectory, slice, cell, matched, frozen, headline, confirmatory, protocol, claim gate, lower bound, clears, survives,** and **implicates** when they function as rhetorical elevation rather than necessary technical terminology.

Do not simplify them when their technical meaning is actually relevant.

Likewise, words associated with Claudish such as **provenance, lineage, calibration, routing, boundary, gate, surface, protocol, verified, canonical,** and **drift** are not forbidden. Preserve them when they are genuinely the clearest or established term for the concept.

## 9. Prefer direct, low-abstraction English

After preserving the semantic payload, express it at the **lowest useful level of abstraction**.

Prefer:

* verbs over nominalizations;
* concrete relationships over system metaphors;
* direct rules over descriptions of gates or boundaries;
* ordinary syntax over technical noun stacks;
* one complete statement over several rhetorical restatements.

The output may be substantially shorter than the input.

## 10. Final checks

Before producing the output, apply both tests:

**Fidelity test:**
Would the rewrite change the type, strength, scope, timing, negation, modality, causality, permission, recommendation, or direction of any independently meaningful claim? If yes, fix it.

**Deletion test:**
Would removing any remaining clause leave the reader with the same material facts, actions, conditions, permissions, requirements, recommendations, uncertainties, and expectations? If yes, remove it.

When fidelity and compression conflict, **fidelity wins**.

The result should read as though a person simply stated what the input means.

Preserve names, quotations, commands, code, and technical terminology whose wording must remain fixed.

Output only the rewritten text.
