---
status: proposed
date: 2026-10-07
---
# Name the folder doc

## Context and Problem Statement

Every unit may have a folder for its documents. Many repositories already
have a folder named `docs/` at the root, usually the source of a
documentation site, sometimes served directly by the code host.

## Considered Options

- `docs/`
- `doc/`
- A hidden folder such as `.youmedoc/`
- A name the project chooses

## Decision Outcome

Chosen option: "`doc/`", because it does not collide with a `docs/` site
source, is visible when browsing, and one fixed name lets agents and tools
find the files without configuration.

### Consequences

- Good: an existing `docs/` folder stays what it is.
- Good: a hidden folder would hide the documents from people browsing the
  repository, which defeats the purpose.
- Bad: `doc/` and `docs/` side by side at the root invite typing mistakes.
- Bad: a unit that already has a `doc/` folder with other content gets a
  warning per unknown entry. The tool leaves those entries unchecked.
