---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Write machine lines as HTML comments that start with `unifold:`

## Context and Problem Statement

The tool writes lines into Markdown files: the stamp under a context item ([0026](0026-stamp-every-restatement-with-a-hash-of-its-source.md)), the header of a generated file, and the fences of a generated block in `AGENTS.md`. The stamp is the first of them that sits inside a hand-written file, between a heading and its prose, so its form decides what a reader sees, what a formatter does with it, and how a grep finds it. [0026](0026-stamp-every-restatement-with-a-hash-of-its-source.md) fixed the text of the stamp without saying why it has that shape.

## Considered Options

- A visible Markdown construct: a footnote, a link title, or a column in a table
- Front matter of the context file with one entry per item
- A sidecar file next to the context file that holds the hashes
- An HTML comment on one line, `<!-- unifold:<kind> ... -->`, directly where it applies

## Decision Outcome

Chosen option: "an HTML comment with the prefix `unifold:`", because every Markdown renderer hides it, every formatter leaves it alone, and one grep finds all of them.

- The prefix `unifold:` says who owns the line. The word after it names what the line does: `generated`, `begin`, `end`, `cites`. A second kind of machine line takes a new word, not a new syntax.
- Fields are written `key=value` and separated by spaces, as in `sha=b9ccc2dd`. A field can be added later without breaking the pattern that reads the line.
- The stamp is `<!-- unifold:cites sha=<8 hex> -->`. Eight hexadecimal characters are the length that abbreviated git hashes made familiar, enough to tell items apart and short enough to read in a diff.
- A machine line stands on a line of its own, directly below what it belongs to, so that a diff shows the two together and the tool needs no other way to pair them. The tool reads the line with a strict pattern and only outside fenced code, so a near-miss typed by hand and an example in a code block do not count.

### Consequences

- Good: a rendered context file shows the heading, `Says` and `Here`, and nothing else.
- Good: rumdl, Prettier and the reflow of [0043](0043-write-one-line-per-paragraph.md) leave the line as it is. A footnote or a table column would be reflowed or renumbered.
- Good: `grep 'unifold:'` lists every machine-written line of a repository, and `grep 'unifold:cites'` every stamp.
- Good: the item and its stamp move together when an item is cut and pasted. A sidecar file or front matter would key on the heading and go stale on a rename.
- Bad: a reader of the raw file sees a comment that means nothing without the standard.
- Bad: an HTML comment is not Markdown. A renderer that strips HTML drops the line; one that escapes it shows it as text. Neither has been seen on GitHub, GitLab or the site.
- Bad: `key=value` is a convention of this standard, not of Markdown, and nothing checks a field that the tool does not know.
