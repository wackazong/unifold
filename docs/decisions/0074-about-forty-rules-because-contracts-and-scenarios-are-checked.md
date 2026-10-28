---
status: proposed
date: 2026-10-27
---

# About forty rules, because contracts and scenarios are checked

## Context and Problem Statement

[0031](0031-reduce-the-rule-set-and-turn-review-rules-into-a-checklist.md) cut the rules to about 25 so that the part a tool checks stays short enough to read. Version 0.3 checks the body of a contract, the kinds of units, the secret and the not, and the hops of scenarios.

## Considered Options

- Keep the count by dropping rules
- Raise the count to about 40 and say why

## Decision Outcome

Chosen option: "about 40", because each new rule stands for one thing a build process otherwise checks with a script of its own, and the principle stays: an error is what makes the map inconsistent, everything else is a warning.

This amends 0031: the count is about 40. The rest of 0031 stands, in particular that prose does not cite rule ids and that the review checklist holds what no tool can check.

### Consequences

- Good: one checker instead of two.
- Bad: a longer table to read.
