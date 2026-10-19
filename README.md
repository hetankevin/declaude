# declaude

A Claude Code and Codex skill for plain English, research exposition in the author's voice, and mathematical proofs with explicit displayed steps.

It removes rhetorical repetition and unnecessary abstractions while preserving facts, logical force, uncertainty, permissions, and scientific qualifications. It can also draft connected explanations rather than merely shorten existing text.

## Install

```sh
git clone https://github.com/hetankevin/declaude.git
cd declaude
python3 install.py
```

The installer copies `skill/` into the current user's Claude and Codex skill directories and backs up existing copies. It does not change global instructions or hooks. Invoke `/declaude` in Claude Code or `$declaude` in Codex. Normal skill discovery is enabled; this is not an always-on injection.

A private reading list can be placed in `skill/references/papers.local.md` and installed with `python3 install.py --personal`. That file is ignored by Git. The public skill works without it using the writing samples and project notes supplied with the task.

## What it does

- Removes staged candor, redundant contrasts, slogans, metaphorical process language, and dense invented compounds.
- Preserves real technical terms, distinctions, author voice, and meaningful qualifications.
- Develops research motivation before notation and mechanisms.
- Expands proof steps into readable displays with brief justifications, without altering assumptions or results.

This is an editing tool, not an AI-authorship detector or a promise to evade one.

## Evaluation

Paired development and held-out evaluations are in progress. See [the fixed protocol](evals/protocol.md). Results will be reported separately, including fidelity and proof regressions.

## Sources

The skill incorporates a user-supplied translation specification, recurring directions in research-workspace writing notes, direct author corrections about proofs and prose, and structural editing patterns from an existing humanizer skill. The public package contains generalized directions and synthetic examples; source conversations and personal workspace paths are not included. See [the translation specification](skill/references/translation.md) and [research writing guidance](skill/references/paper-voice.md).
