---
status: proposed
date: 2026-10-27
---

# Declare the secret and the not of a unit

## Context and Problem Statement

A good unit hides one piece of knowledge that is hard to get right or likely to change. The reason lives in `## Why` as prose, where no tool and no reviewer can find it fast, and what a unit leaves to others is a README section, `## Out of scope`, that nothing connects to the map.

## Considered Options

- Keep both in prose
- A `secret` key with one line and a decision, and a `not` list whose items may name the need through which the thing is delegated

## Decision Outcome

Chosen option: "two keys in the manifest", because the secret is the one fact a map reviewer checks for every unit, and a delegation that names a need is a checked declaration: the need must exist.

- `secret` has `what`, one line, and `decision`, a path to a decision of the unit or an ancestor that says why this is the secret and where that knowledge comes from.
- `not` is a list; an item is one line, or one line mapped to a need: `frame layout: frames`.
- The README template loses `## Out of scope`; `## Why` stays as the long form.

### Consequences

- Good: a reviewer reads one line per unit and one decision per secret.
- Bad: two more keys, and the README of every 0.2 unit moves one section into the manifest.
