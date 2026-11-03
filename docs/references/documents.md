# Documents

The [standard](spec.md) asks every unit for a manifest and a `README.md`. This chapter says where the rest of a unit's written knowledge goes; [writing.md](writing.md) says how each file is written. Every unit keeps its knowledge in the same places, for the people who use it, the people and agents who work on it, and the end users of the product. A project of one unit keeps all of it in its root.

## The files of a unit

```text
<unit>/
├── unifold.yaml        the manifest: what the unit provides and needs
├── README.md           required: the front page, what the unit is for and why
├── AGENTS.md           generated: where the documents are, for coding agents
└── docs/
    ├── tutorials/      learn: a lesson that leads to a first result
    ├── skills/         do: a procedure for a task, for people and agents
    ├── references/     look up: contracts, glossary.md, constants.md
    ├── explanation/    understand: context.md, requirements.md, reasoning.md,
    │                   invariants.md, runtime.md, deployment.md, risks.md
    ├── decisions/      choices between options, with reasons; index generated
    └── diagrams/       generated: which units exist and how they connect
```

The checker reads the hand-written files in these places and nothing else in `docs/`. Create a file only when it has content: a leaf unit often has a `README.md`, a `context.md` and one decision.

## Four kinds of knowledge

The folders follow [Diátaxis](https://diataxis.fr). Each kind serves one thing the reader is doing and is written in its own way.

| The reader wants to | Kind | Where | How it is written |
|---|---|---|---|
| Be taught, step by step, to a first result | Learn | `docs/tutorials/` | A lesson for a stated reader. It teaches; it does not define or instruct. |
| Finish a task they already understand | Do | `docs/skills/` | A procedure in the Agent Skills format. |
| Find a fact: a contract, a term, a value | Look up | `docs/references/`, the manifest, `README.md`, the generated diagrams | Facts as they are now, complete, with examples. No reasons, no steps. |
| Know why it is so | Understand | `docs/explanation/`, `docs/decisions/` | Reasons, forces, trade-offs. No instructions, no facts that a reference states. |

A fact has one home; other files link to it. A text that teaches, instructs, states and reasons at once is four texts.

Every document but a decision describes the unit as it is now. The history is in the decisions and in version control. Plans and the progress of the work belong to the people and the process that do the work; inside the documents, the state of the work is only `status` in the manifest and the proposed decisions. A change rewrites every document it touches to the new state.

## README.md: the front page

`README.md` is the first file every reader and agent opens. It says what the unit is for and why; the contracts say how to use it. A reader MUST be able to use the unit, or to provide what it needs, after reading `README.md` and the contracts that its manifest names.

| Section | Content |
|---|---|
| `# <name>` | Then one paragraph: what the unit is for, and for whom. |
| `## Why` | Required. Why the unit exists, what makes it change, why it is cut this way, what must stay true: the long form of its `secret` and its `not`. At most 20 lines that are not blank; the long form is `docs/explanation/reasoning.md`. |
| `## Capabilities`, `## Needs` | Only where the summary and the contract do not say everything. One `###` subsection for each such capability or need; the heading is the name in code font, for example ``### `invoices` ``. A subsection says only what the contract does not: what this unit adds beyond it, in a form that can be checked, its own limits, and for an optional need what the unit does without it. It does not repeat the contract or link to it as a matter of course: the manifest names the contract. |
| `## Commands` | Optional. The few commands to build, test and run the unit. |
| `## Read next` | Optional. A few links into `docs/` whose order matters. |

- Every `README.md`, the root's included, has these sections in this order. A section without content is deleted, not left empty. What the unit does not do is `not` in the manifest, not a section. The template is in the `unifold` skill; `unifold init` writes it for a root that has no `README.md`.
- A `README.md` MUST NOT describe how the unit works inside, and SHOULD NOT name the units around it or list children, capabilities or connections: the manifest and the generated diagrams hold those, and `unifold show` prints them.
- The root's `README.md` is also the front page of the project. It adds what a front page needs, such as installation, a comparison or a licence, between `## Why` and `## Capabilities` or after `## Read next`. A `README.md` that a package registry publishes keeps its usual content and links to the project by full URLs.

## AGENTS.md: generated

Coding agents load this file when they work in the folder ([agents.md](agents.md)). It holds no knowledge of the project, only the way to it: the line "unifold unit; run `unifold show` here", a pointer to `README.md`, the documents of the unit by kind, and the skills with their descriptions. At the root it also carries the unifold block with the index of units. The generator writes it, and the checker reports it when it is stale. A hand-written `AGENTS.md` without the generated marker is never overwritten: move its content to `README.md` and `docs/`, delete it, and run `unifold check --fix`.

## docs/explanation: the architecture of the unit

The explanation files are [arc42](https://arc42.org) cut down to what the folder tree and the manifests do not already say. Each has the same fixed name in every unit and exists only when it has content.

| File | Content | arc42 |
|---|---|---|
| `context.md` | What the unit takes over from the units above, restated and stamped. The only file that links upward. | 2, 3 |
| `requirements.md` | What the unit must achieve, for whom it is and is not, and its quality goals in order of priority. | 1, 10 |
| `reasoning.md` | The long form of `## Why`: the forces, the trade-offs, the ideas the unit is built on, the alternatives that were rejected. | 4 |
| `invariants.md` | What must always, or never, be true inside the unit. | 2, 8 |
| `runtime.md` | How the unit behaves while it runs: states and transitions, start and stop, timing, concurrency, limits, failure. A story across several units is a scenario in the manifest. | 6 |
| `deployment.md` | Where things run, instances, volumes, what survives a restart, what is reachable from outside. | 7 |
| `risks.md` | Risks, known limits and technical debt, each with what would remove it. | 11 |

- The other sections of arc42 have homes outside this folder: context and scope (3) are `README.md` and the generated context diagram; building blocks (5) are the manifests and the generated diagrams; decisions (9) are `docs/decisions/`; the glossary (12) is `docs/references/glossary.md`.
- A topic file beside the fixed ones, `docs/explanation/<topic>.md`, holds explanation that users of the unit need and that fits no fixed file.
- No explanation file lists units, capabilities or connections, and none repeats a generated diagram by hand.
- What several children must obey, such as a crosscutting concept (8), is a decision or a reference of the parent, which a child cites in its `context.md`.

## docs/references: what a reader looks up

A reference holds facts as they are now, complete, with examples. Most references of a unit are the contracts of the connections it wires, each a file or a folder of parts ([contracts.md](contracts.md)). Beside them:

| File | Content |
|---|---|
| `glossary.md` | The terms that have one fixed meaning inside the unit, one row each. |
| `constants.md` | The fixed values that the unit and the units below it use, one row each. |
| `<topic>.md` | A fact that several contracts or the code of the unit share and that no contract owns, such as a convention or a format. |

- A reference names no decision and gives no reasons. The decision that settles a fact links the reference.
- A reference holds nothing about the work: no note about a step, a review or a test run, and no list of what is open or planned.
- How a unit works inside is an explanation of that unit, in `runtime.md` or `invariants.md`, not a reference.

## Where a file may point

These rules hold for links in the hand-written files of a unit. Links are relative. Who is on the other side of a capability is not written by hand; `unifold show` and the generated diagrams say it.

| Direction | Rule |
|---|---|
| Within the unit | Free. Plain folders of the unit count as the unit. |
| Down | Only to a direct child: its folder or its `README.md`. Never into its `docs/`, its `AGENTS.md` or its code, and never to a unit below a child. |
| Up | Only from `docs/explanation/context.md`, and only to an ancestor's `README.md`, decisions and references. Each link comes with a restatement and a stamp ([writing.md](writing.md)). |
| Sideways | Never. What the unit wants from a sibling is a need in the manifest. |
| To a contract | Free. A file that the unit's manifest names as `contract` may be linked from any file of the unit, wherever it lies. |
| Outside the project | Full URLs. The standard is cited as `https://unifold.md`. A nested project is linked by its `README.md` only. |

## What belongs where

| You want to write down | It goes to |
|---|---|
| What a capability guarantees | `README.md`, and its `contract` for the exact definition |
| What a connection between two children exchanges | `docs/references/` of this unit, named as `contract` by both sides ([contracts.md](contracts.md)) |
| A wire format or a schema | A part of the contract of the connection that carries it; a reference of its own only where several contracts share it |
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

- **Published packages.** `unifold.yaml`, `AGENTS.md` and `docs/` lie inside package folders. Exclude them where the build tool packs the folder for publication, for example with `exclude` in a `Cargo.toml`.
- **Existing decision records** in [MADR](https://adr.github.io/madr/) format move to `docs/decisions/` of the unit they concern.
- **Generated files in version control.** Commit them; the standard requires it, and the checker reports one that `.gitignore` ignores. Mark `docs/diagrams/*.md`, `docs/decisions/index.md` and `AGENTS.md` as generated for the code host, for example with `linguist-generated` in `.gitattributes`, so that reviews fold them, and run `unifold check --fix` before a commit.

What the reference tool reports for this chapter is in [rules.md](rules.md).
