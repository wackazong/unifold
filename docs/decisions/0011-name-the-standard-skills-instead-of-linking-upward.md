---
status: superseded by 0027
date: 2026-10-06
---

# Below the root, name the standard's skills instead of linking to them

## Context and Problem Statement

Writing the example showed a conflict. A skill of a unit below the root often ends with "check the documents". The skill that does this sits in the root unit. A link to it is an upward link, which is allowed only in `docs/context.md`, and `docs/context.md` may not cite skills. At the same time every mention of a file must be a link.

## Considered Options

- Exempt links to the root's copy of the standard from the direction rules
- Let `docs/context.md` cite skills of ancestors
- Refer to the three skills by name, without a relative link

## Decision Outcome

Chosen option: "by name", because the three skills exist in every unifold project at the same place, an agent learns of them from the root `AGENTS.md`, and a name does not break when a unit is copied.

### Consequences

- Good: no exception to the direction rules for links.
- Good: a copied unit needs no repair for these references.
- Bad: one exception to "every mention is a link".
- Bad: a reader who starts in a deep unit and has never seen the root must know, or look up, where the standard's skills are.
