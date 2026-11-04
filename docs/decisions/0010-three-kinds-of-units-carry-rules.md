---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Three kinds of units carry rules: logic, stateful, adapter

## Context and Problem Statement

A design that keeps pure calculation apart from state and from external systems is cheaper to test and to change: logic needs no fake, an adapter is the one place where an external protocol lives. The manifest can say what a unit is, and a checker can hold the design to it. Which kinds does the standard know, and what do they promise?

## Decision

- `kind` is free text. Three values carry rules, reported as warnings: `logic`, a pure calculation, which has only `logic` children and whose needs are finally provided by `logic` units, so that it reaches no need of the root; `stateful`, which keeps state and may need anything; `adapter`, the one unit that talks to one external system, whose needs are finally provided by no other adapter.
- A need of the root that is not marked `platform: true` is finally reached only by adapters; `platform` marks a service of the host, such as time or randomness, whose contract describes a controllable fake.
- `runs-as` says what a unit runs as: `library`, `process`, `job`, `ui` or `firmware`. The diagrams show kind and runs-as.
- Any other kind is allowed and carries no rule; the kind of a unit decides nothing about how a scenario is drawn.

## Consequences

- Good: a reviewer sees at a glance where state and external systems live, and the checker reports a logic unit that reaches the outside.
- Bad: the rules fit one architecture style; a project of another style states no kind, or ignores the warnings.
