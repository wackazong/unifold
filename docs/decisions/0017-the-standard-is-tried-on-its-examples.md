---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The standard is tried on its examples, and this repository is not a unit

## Context and Problem Statement

A rule that was never applied is a guess. The repository of the standard holds documents and a tool, not a product; if it were a unit, its own documents would have to follow rules that were written for software. Where is the standard tried, and does the standard apply to itself?

## Decision

- Every rule is tried on the examples in `examples/` before a project has to follow it: `slugline`, a small Rust workspace with code and tests; `serial-line`, a design without code; `plantwatch`, a design of a product with firmware, an app and services. The examples check clean and are checked in continuous integration, together with the tool's conformance tests and the links of the site.
- This repository is a specification, not a unit: it has no manifest. Its documents follow the document conventions by choice, and its own decisions live in `docs/decisions/`.
- A change to the standard is a decision here, proposed in a pull request and accepted by a maintainer; the examples change in the same pull request.

## Consequences

- Good: every rule has at least one project that follows it, and the examples show what a map looks like.
- Bad: the three examples are the authors' own; evidence from other repositories is still to come.
