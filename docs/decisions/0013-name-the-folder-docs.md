---
status: proposed
date: 2026-10-07
---
# Name the folder docs

## Context and Problem Statement

Every unit may have a folder for its documents. The folder needs one fixed
name so that agents and tools find the files without configuration. The
common name for such a folder in open-source repositories is `docs/`, and
code hosts and documentation generators expect that name.

## Considered Options

- `docs/`
- `doc/`
- A hidden folder such as `.unifold/`
- A name the project chooses

## Decision Outcome

Chosen option: "`docs/`", because it is the name people and tools already
expect, is visible when browsing, and one fixed name lets agents and tools
find the files without configuration. The first draft chose `doc/` to avoid
colliding with an existing `docs/` site source; the collision is rare in
practice, and a second name beside `docs/` invites typing mistakes and
surprises readers.

### Consequences

- Good: an existing `docs/` folder becomes the unit's document folder; the
  files that belong to this standard sit beside whatever else is there.
- Good: a hidden folder would hide the documents from people browsing the
  repository, which defeats the purpose.
- Bad: a unit whose `docs/` folder holds other content, such as a site
  source, gets a warning per unknown entry. The tool leaves those entries
  unchecked.
