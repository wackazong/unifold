---
status: proposed
date: 2026-10-27
---

# Replace summary on a unit with responsibility

## Context and Problem Statement

A unit's `summary` said what the unit is. A reviewer who asks whether a unit does one thing needs the one thing it is responsible for, in a sentence that shows an "and" between unrelated things. The build process maike writes such a sentence for every component and reads it back from the manifest.

## Considered Options

- Keep `summary` and ask for a sentence about responsibility in the guide
- Add `responsibility` beside `summary`
- Replace `summary` on a unit with `responsibility`; capabilities and needs keep `summary`

## Decision Outcome

Chosen option: "replace it on the unit", because two lines that say nearly the same thing drift apart, and a capability or need is described, not responsible. A manifest with `summary` on a unit is an error that names the new key.

### Consequences

- Good: every unit states its one responsibility, and the diagrams and `AGENTS.md` show it.
- Bad: every 0.2 manifest changes one key.
