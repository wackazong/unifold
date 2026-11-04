# Where things go

Where a file of a unit may not link, which file holds which kind of knowledge, and how the documents sit beside what a repository already has. [documents.md](documents.md) says which files a unit has.

## Where a file may point

Do not link to a sibling; declare a need. Every other relative link is free: within the unit, up to the units above and down to the units below. Things outside the project are linked by full URL.

## What belongs where

| You want to write down | It goes to |
|---|---|
| What a capability guarantees | Its `contract` |
| What a connection between two children exchanges | `docs/references/` of this unit, named as `contract` by both sides ([contracts.md](contracts.md)) |
| A wire format or a schema | A part of the contract of the connection that carries it; a reference of its own only where several contracts share it |
| A setting that differs per build, deployment or run | A need of the unit, with a contract whose parts are the settings: name, type, default, and who sets it (build, deployment or run); its fake is a table of values |
| What a connection promises beyond its parts: latency, throughput, concurrency, delivery, limits | `## Qualities` of its contract ([contracts.md](qualities.md)) |
| How a connection travels, and what a unit runs as | `Binding:` in the contract's header; `runs-as` in the manifest |
| A term, a fixed value | `docs/references/glossary.md`, `docs/references/constants.md` |
| Why the unit exists or is cut this way | `README.md` `## Why`, long form `docs/explanation/reasoning.md` |
| A choice between options, and its reasons | `docs/decisions/` |
| What changed and when | The decision that changed it, and version control |
| What is planned, open or in progress | `status` in the manifest and the proposed decisions; the plan stays with the people and the process that do the work |
| A note about a step of the work, a review or a test run | Not in the documents of a unit |
| How the unit behaves while it runs | `docs/explanation/runtime.md` |
| A rule that holds in this unit | `docs/explanation/invariants.md`; conventions in `docs/references/conventions.md` |
| A rule that units below must follow | A decision or a reference of this unit, cited by their `context.md` |
| A decision or term from above that matters here | `docs/explanation/context.md` |
| How to do a recurring task | `docs/skills/` |
| How a newcomer gets to a first result | `docs/tutorials/` |
| Which units exist and how they connect | Nowhere by hand: the manifests and `docs/diagrams/` |
| What the unit does not do, and who does it instead | `not` in the manifest |
| How a connection is used, step by step | `## Use` and `## States` of its contract ([contracts.md](contracts.md)) |
| How a feature runs through several units | `scenarios` in the manifest of the lowest unit that contains them, with `given` and a result per hop; the diagram is generated |

## Beside what is already there

- **Published packages.** `unifold.yaml` and `docs/` lie inside package folders. Exclude them where the build tool packs the folder for publication, for example with `exclude` in a `Cargo.toml`.
- **Existing decision records** in [MADR](https://adr.github.io/madr/) format move to `docs/decisions/` of the unit they concern.
- **Generated files in version control.** Commit them; the standard requires it, and the checker reports one that `.gitignore` ignores. Mark `docs/diagrams/component.md`, `docs/decisions/index.md` and the root `AGENTS.md` as generated for the code host, for example with `linguist-generated` in `.gitattributes`, so that reviews fold them, and run `unifold check --fix` before a commit.

What the reference tool reports for this chapter is in [rules.md](rules.md).
