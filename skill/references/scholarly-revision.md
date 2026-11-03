# Revising scholarly manuscripts

Adapted from the supplied *scholarly-paper-revision* skill, with acknowledgment to [Gappy (@__paleologo) on X](https://x.com/__paleologo/status/2116602494428299632). Use this alongside [paper-voice.md](paper-voice.md) and, for mathematical arguments, [proofs.md](proofs.md). The user's current task and writing samples govern the revision.

## Preserve the manuscript's purpose

Read the actual root, relevant included files, and neighboring passages before editing. Identify the audience, contribution, local writing notes, notation conventions, class, macros, bibliography, and build engine. For a focused edit, read enough context to avoid inconsistencies and leave unrelated material alone.

Preserve the requested artifact: a paper does not become a survey, and a chapter does not become a teaching monograph merely because more explanation is possible. Do not invent length limits, standard sections, boxes, titles, or extra deliverables. Keep the existing structure unless the requested revision calls for changing it.

Separate stylistic editing from scientific correction. Check in-scope derivations, assumptions, units, regimes, and citations. An equivalent expansion can expose a hidden step, but it must not silently introduce a premise or change the theorem. Repair a demonstrable error when the user authorized substantive correction and the repair is justified. Otherwise identify the gap and the concrete change needed. Do not substitute a weaker provable contribution for the one the author is pursuing.

## Integrate sources without importing their claims

Distinguish research evidence from writing samples, templates, and macro files. For source integration, read the relevant full text and appendices, not just an abstract or another model's summary. Keep a small working record of which claim comes from which source, with a page, theorem, or equation reference and any translation into the manuscript's notation. This record supports the work; do not insert it as an unsolicited audit table in the paper.

Verify bibliographic details and attach citations where claims occur. Preserve attribution, conflicting assumptions, unresolved disagreements, and the difference between what a source proves and what it suggests. Compare methods by what each enables under its own conditions. A style sample supplies neither evidence nor transferable theorem assumptions.

Distinguish reported experiments, worked examples, reproductions, new results, and proposed work. A theoretical illustration does not establish empirical performance. Do not invent observations or launch substantial experiments merely to complete a narrative. If a source is inaccessible, state the access gap rather than implying it was read. Check extracted equations against the rendered source when OCR or formatting could have changed them.

## Make the argument teachable

Start from the reader's stated prerequisites. Motivate a construction through the obstacle it resolves, then define its objects and conditions before using them. Build unfamiliar objects from familiar ones when that reveals the mechanism. A dependency-aware sequence is more useful than a catalogue of definitions.

Develop a worked specialization after a general result when it helps the reader understand what the result computes. Explain boundary and limiting regimes, including where an approximation degenerates. Reuse a mechanism across examples when that shows what carries over and what changes. Do not import an exemplar's chapter count, length, notation, or organization.

Scale explanation to the argument's difficulty. Keep the substantive intermediate steps visible as required by [proofs.md](proofs.md). Remove repeated commentary, unused abstractions, and routine background that the intended audience already knows. Do not equate teaching quality with length, a fixed template, or a box after every result. Read the whole section for the recurring patterns in [tells.md](tells.md).

## Use independent review where it helps

For extensive or difficult work, an independent review can test whether the paper works for its intended reader. Use it when available and within the authorized scope and resources; small edits do not require extra agents.

Give the reviewer the actual task, audience, explicit constraints, draft, rendered pages, notation conventions, bibliography, relevant sources, and any evidence behind empirical claims. Disclose exclusions and inaccessible sources. Before its first assessment, do not supply your intended verdict, assurances that the work is correct, or a list of fixes to endorse.

Ask for location-specific findings with severity, source support where relevant, and actionable revisions. The reviewer should assess definitions before use, assumptions and intermediate steps, translations between sources, fidelity of synthesis, evidence behind numerical claims, and whether the level of explanation suits the audience. It should identify both missing explanation and expendable material rather than optimize a word count.

Resolve material findings and record their disposition in working notes. For a disputed finding, check the source and explain the resolution. Recheck materially changed arguments when needed rather than repeatedly reviewing unchanged text. Reviewer agreement does not waive an unresolved error or prove the prose is effective.

## Preserve the LaTeX project and verify the final artifact

Use the project's actual root and normal build command, with its existing engine and bibliography passes. Keep its macro setup. Prefer definitions already in the project or supplied by the user, define necessary additions locally, and resolve collisions without changing shared libraries. Do not import a template or macro collection from this skill into an existing manuscript. New standalone work should follow the user's chosen format.

After the final source edit, compile and inspect errors, unresolved citations or references, and relevant overfull boxes. Render affected pages at a readable size and inspect equations, figures, tables, and page transitions; review more broadly when layout changes propagate. Rebuild after further edits. Successful compilation is not mathematical or visual validation.

Use page limits only when the user or venue supplies them. Preserve build dependencies for requested portable deliverables. Report what remains unverified if compilation or visual inspection is unavailable, and identify unresolved scientific issues without claiming the manuscript is ready. Deliver the requested source or rendered artifact, with a short account of substantive changes and verification.
