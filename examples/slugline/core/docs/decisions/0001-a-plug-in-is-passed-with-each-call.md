---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# A plug-in is passed with each call

## Context and Problem Statement

`slugify` must replace `é` by `e` without holding the tables. How does a table reach it?

## Considered Options

- An argument `&dyn Transliterate`
- A global registry of plug-ins
- A Cargo feature that pulls in a table

## Decision Outcome

Chosen option: "An argument `&dyn Transliterate`", because the result then depends on the arguments alone.

### Consequences

- Good: two callers in one process can use different plug-ins.
- Bad: every caller passes a plug-in itself.
