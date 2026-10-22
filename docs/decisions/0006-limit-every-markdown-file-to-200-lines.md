---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Limit every Markdown file to 200 lines

## Context and Problem Statement

Files are written by agents and reviewed by humans. Long generated documents are not reviewed; they are skimmed. Agents that load long files lose room for the task and follow the content less reliably.

## Considered Options

- No limit, only guidance
- A limit for `AGENTS.md` only
- One hard limit for every managed Markdown file

## Decision Outcome

Chosen option: "one hard limit of 200 lines", because a rule without exceptions is easy to check and to remember, and the same number is the length that one agent vendor recommends as the upper bound for its instruction files
([Claude Code documentation](https://code.claude.com/docs/en/memory)).

### Consequences

- Good: every file can be reviewed in one sitting and read as a whole.
- Good: a file that hits the limit signals that a unit or a topic should be split.
- Bad: long references become a folder with an index, which adds files.
- Bad: lines differ in length, so the limit is a rough measure. A second rule reports lines of more than 400 characters (`T3`), because long table rows had made files of 50 lines hold 900 words.
- Bad: generated diagrams must respect it too, so the generator reduces the depth of large architecture diagrams.
