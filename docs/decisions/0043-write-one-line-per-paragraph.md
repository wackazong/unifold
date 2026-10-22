---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Write one line per paragraph

## Context and Problem Statement

Prose was wrapped by hand at about 80 characters, and the generator wrote `AGENTS.md`, the skill stubs and the README of `init` the same way. Editors with a Markdown formatter, such as rumdl or Prettier, reflow a paragraph on save. A wrapped file and a reflowed one differ in every line, and a generated file was rewritten by each side in turn. The limit of 200 lines counted wrapped lines, so it measured width as much as length.

## Considered Options

- Keep wrapping by hand at 80 characters and exclude generated files from formatters
- Write one line per paragraph and per list item, in hand-written and generated files alike
- Wrap at a fixed width in the generator and ask adopters to use the same width

## Decision Outcome

Chosen option: "one line per paragraph", because a paragraph is the unit on which a formatter, a diff and a reader agree. No two tools have to agree on a width.

- [writing.md](../references/writing.md) says so, and the generator and the templates of the skill follow it.
- A formatter that reflows paragraphs is welcome; one that wraps them is not.

### Consequences

- Good: `check --fix` and a formatter no longer fight over generated files.
- Good: a diff shows the changed paragraph, not a reflowed block.
- Bad: a long paragraph is one long line in an editor without soft wrap.
- Bad: the limit of 200 lines now allows far more text than before. A tighter number may follow.
