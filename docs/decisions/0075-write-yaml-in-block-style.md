---
status: proposed
date: 2026-10-27
---

# Write YAML in block style

## Context and Problem Statement

The examples of the standard mixed block style and flow style, `{summary: ..., contract: ...}`. Flow style needs quotes around a value with a colon or a comma, which was the most common manifest error, and a mapping with `parts` and `scenarios` with lists do not fit on one line.

## Considered Options

- Keep mixing
- Block style in every example, template and generated file; flow style stays valid

## Decision Outcome

Chosen option: "block style everywhere in our text", because what the standard shows is what agents copy. The short form `name: one-line summary` stays.

### Consequences

- Good: fewer quoting errors, and every example has one shape.
- Bad: longer examples.
