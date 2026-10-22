---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Compare with code by default and draft manifests from build files

## Context and Problem Statement

[0019](0019-compare-the-wiring-with-dependencies-observed-in-code.md)
defined a format for observed dependencies and left producing the list to each project. Round 3 found that without this comparison the map agrees only with itself, that almost no project will write an exporter, and that hand-writing manifests which repeat the build files (164 lines for the 12 units of ripgrep) is the main cost of adoption. A wired connection without any dependency in code was only an info and never failed a build.

## Considered Options

- Keep the comparison optional and external
- Build extractors into the tool and run them by default
- Additionally let `init` write draft manifests from the same build files

## Decision Outcome

Chosen option: "extractors by default, and drafts from build files", because the promise that the map is true depends on the comparison, and because the first run must show a result before anybody writes text.

- `check` extracts dependencies when it recognises Cargo, npm, pnpm, yarn, Go or Python workspaces; `--no-deps` switches this off; `--deps FILE` adds a list, for example calls between services.
- A dependency in code without a connection is an error. A connection between units covered by an extractor, without an observed dependency, is a warning. An unknown path in a list is an error.
- A dependency that only tests have is listed with a kind of its own (`cargo-dev`). It counts as observed and never demands a connection.
- A child that depends on code of the unit above is wired to `./folder`, or to `./` for the code of that unit itself.
- `init` writes one port per package, one need per dependency between packages, and the wiring. Missing summaries are `TODO` and are reported.

This amends 0019; its exchange format stays, with two optional fields.

### Consequences

- Good: a checked map of an existing workspace in two commands.
- Bad: the tool now knows four ecosystems and must follow their changes. The standard itself stays independent; the extractors are tool features.
- Bad: a draft with one port per package restates the build file. The value starts only when people refine it, and many will not.
- Bad: the comparison is per pair of units. One wired need between two units covers every dependency between them.
- Bad: calls between services are in no build file and still need a list that the project produces.
