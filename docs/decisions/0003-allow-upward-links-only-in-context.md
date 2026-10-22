---
status: proposed
date: 2026-10-06
---
# Allow upward links only in docs/context.md

## Context and Problem Statement

Two goals pull in different directions. A unit should contain everything
needed to understand it. But units depend on decisions and conventions made
above them, and repeating those in every unit creates copies that drift.

Portability here means comprehension: a copied folder must explain itself. It
does not mean that the copy builds or runs.

## Considered Options

- Forbid all upward references; each unit repeats what it needs in full
- Allow upward links anywhere
- Allow upward links in one file per unit, `docs/context.md`, and require a
  short restatement next to every link

## Decision Outcome

Chosen option: "one file with restatements", because it keeps a single source
for each decision, shows in one place what a unit inherits, and leaves the
unit readable when the links are dead.

### Consequences

- Good: the limited redundancy is confined to one-line restatements in a
  known file.
- Good: after a move or copy, the broken links in this one file are the
  exact list of things to re-establish.
- Bad: a restatement can fall out of step with its source. The tool lists
  the files that cite a source (`cited-by`) and warns when a cited decision
  is no longer in force (`L7`); whether the text still matches is a matter
  of review (`C5`).
- Bad: context files grow. In the first version of the example they held an
  eighth of all hand-written words, in table rows of up to 790 characters.
  Items are now short sections with a restatement of at most two lines.
- Bad: sideways references stay forbidden without exception, which sometimes
  forces a shared thing into a unit of its own or up into the parent.
