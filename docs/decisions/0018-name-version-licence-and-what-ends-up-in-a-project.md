---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Name, version 0.4, licence, and what ends up in a project

## Context and Problem Statement

A standard needs a name, a version that says which rules apply, a licence that lets anyone use it, and a clear answer to what it puts into a repository that adopts it. The reference tool must know which version it reads.

## Decision

- The standard is called unifold and published at `https://unifold.md`, with its manifest schema at `https://unifold.md/<version>/unifold.schema.json`; a published version stays there.
- The current version is 0.4. A root manifest names it as a string, `unifold: "0.4"`. The tool reads one version, the current one, and a manifest never changes its meaning while its version string stays the same; a project of an earlier version is rewritten by hand, and the fix text of the checker says what to change.
- Nothing of the standard is copied into a project. A project holds its manifests, its documents, the generated files, and, with `init --agents`, the skills and the tool.
- The standard, the tool and the skills are licensed under MIT or Apache-2.0, at the user's option; the templates and everything the tool generates may be used without attribution.

## Consequences

- Good: a project pins a version by one line, and a tool knows exactly what to read.
- Bad: a new version of the standard asks every project to move, by hand.
