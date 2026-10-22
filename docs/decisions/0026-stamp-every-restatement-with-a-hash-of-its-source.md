---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Stamp every restatement with a hash of its source

## Context and Problem Statement

A unit restates in `docs/context.md` what it takes over from above ([0003](0003-allow-upward-links-only-in-context.md)). Nothing tied a restatement to the text it restates. In a mutation test, 7 of 12 changes to a cited source or to a restatement passed the checker; the large example has 199 restatements that were kept in step by review only.

## Considered Options

- Leave it to review
- Detect staleness from version control: source committed after the citing file
- A generated comment under each item with a hash of the cited file or section; the checker warns when the hash no longer matches

## Decision Outcome

Chosen option: "a stamp with a hash", because it needs no version control and no network, and it says exactly which item to look at.

- The stamp is `<!-- unifold:cites sha=<8 hex> -->`, directly under the item's heading. The hash covers the cited file, or, if the link has a fragment, the section under the heading with that anchor or else the one table row whose first cell gives that anchor, with white space normalised.
- `check` warns when a stamp is missing or the source has changed. `check --fix` writes no stamp at all. Only `unifold stamp` adds or refreshes one, and it prints file, line and cited source of each item, so that the warning is cleared by a deliberate act.
- `cited-by` lists file, line and the `Says` text of every item that cites a file.

### Consequences

- Good: a changed decision or reference points at every restatement of it.
- Bad: a stamp says that somebody ran `unifold stamp`, not that somebody compared the texts.
- Bad: any edit to a cited file without a fragment, even a corrected typing mistake, makes every item that cites it stale. Citing one section or one table row limits this; a table row is no anchor on code hosts, so such a link opens the file at its top.
- Bad: one more generated line in a hand-written file.
- Bad: restated values outside `docs/context.md` are still not covered.
