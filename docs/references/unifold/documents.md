# Documents: level full

The [standard](spec.md) at level `core` asks for a manifest and nothing
else. A unit whose manifest says `level: full`, or that lies below one that
does, also follows this chapter and [writing.md](writing.md). It puts
written knowledge in fixed places, so that whoever opens a folder finds the
same files everywhere, and it holds all documentation of the unit: for the
people who use it, for the people and agents who work inside it, and for
the end users of a product. A project of one unit keeps all of this in its
root.

## The files of a unit

```text
<unit>/
├── unifold.yaml        the manifest: what the unit provides and needs
├── README.md           required: the front page, what the unit is for and why
├── AGENTS.md           generated: where the documents are, for coding agents
└── docs/
    ├── tutorials/      learn: a lesson that leads to a first result
    ├── skills/         do: a procedure for a task, for people and agents
    ├── references/     look up: contracts, formats, glossary.md
    ├── explanation/    understand: context.md, requirements.md, reasoning.md,
    │                   invariants.md, runtime.md, deployment.md, risks.md
    ├── decisions/      choices between options, with reasons; index generated
    └── diagrams/       generated: which units exist and how they connect
```

The checker reads the hand-written files in these places and nothing else
in `docs/`. Create a file only when it has content: a leaf unit often has a
`README.md`, a `context.md` and one decision.

## Four kinds of knowledge

The folders follow [Diátaxis](https://diataxis.fr). Each kind serves one
thing the reader is doing, and is written in its own way.

| The reader wants to | Kind | Where | How it is written |
|---|---|---|---|
| Be taught, step by step, to a first result | Learn | `docs/tutorials/` | A lesson for a stated reader. It teaches; it does not define or instruct. |
| Finish a task they already understand | Do | `docs/skills/` | A procedure in the Agent Skills format. |
| Find a fact: a contract, a format, a term | Look up | `docs/references/`, the manifest, `README.md`, the generated diagrams | Facts in the present tense, complete, with examples. No reasons, no steps. |
| Know why it is so | Understand | `docs/explanation/`, `docs/decisions/` | Reasons, forces, trade-offs. No instructions, no facts that a reference states. |

A fact has one home; other files link to it. A text that wants to teach,
instruct, state and reason at once is four texts.

## README.md: the front page

`README.md` is the first file every reader and agent opens. A reader MUST be
able to use the unit, or to provide what it needs, after reading this file
alone.

| Section | Content |
|---|---|
| `# <name>` | Then one paragraph: what the unit is for, and for whom. |
| `## Why` | Required. Why the unit exists, what makes it change, why it is cut this way, what must stay true. At most 20 lines that are not blank; the long form is `docs/explanation/reasoning.md`. |
| `## Capabilities`, `## Needs` | One `###` subsection for each capability or need whose summary does not say everything. The heading is the name in code font, for example ``### `invoices` ``. A subsection says what can be relied on, in a form that can be checked: a value, a limit, an order, a response. For an optional need it says what the unit does without it. |
| `## Out of scope` | What the unit does not do. |
| `## Commands` | Optional. The few commands to build, test and run the unit. |
| `## Read next` | Optional. A few links into `docs/` whose order matters. |

- It MUST NOT describe how the unit works inside, and it SHOULD NOT name
  the units around it or list child units, capabilities or connections:
  the manifest and the generated diagrams hold those, and `unifold show`
  prints them.
- The root's `README.md` is also the front page of the project and keeps
  whatever a front page needs. A `README.md` that a package registry
  publishes keeps its usual content and links to the project by full URLs.

## AGENTS.md: generated

Coding agents load this file when they work in the folder
([agents.md](agents.md)). It holds no project knowledge, only the way to it:
the line "unifold unit; run `unifold show` here", a pointer to `README.md`,
the documents of the unit by kind, and the skills with their descriptions.
At the root it also carries the unifold block with the unit index. The
generator writes it; the checker reports it when it is stale, like a
diagram. A hand-written `AGENTS.md` without the generated marker is never
overwritten: move its content to `README.md` and `docs/`, delete it, and
run `unifold check --fix`.

## docs/explanation: the architecture of the unit

The explanation files are modelled on [arc42](https://arc42.org) and cut
down to what the folder tree and the manifests do not already say. Each has
a fixed name, so that it is found in every unit; each exists only when it
has content.

| File | Content | arc42 |
|---|---|---|
| `context.md` | What the unit takes over from the units above, restated and stamped. The only file that links upward. | 2, 3 |
| `requirements.md` | What the unit must achieve, for whom it is and is not, and its quality goals in order of priority. | 1, 10 |
| `reasoning.md` | The long form of `## Why`: the forces, the trade-offs, the ideas the unit is built on, the alternatives that were rejected. | 4 |
| `invariants.md` | What must always, or never, be true inside the unit. | 2, 8 |
| `runtime.md` | Sequences, state machines, the order of a start. | 6 |
| `deployment.md` | Where things run, instances, volumes, what survives a restart, what is reachable from outside. | 7 |
| `risks.md` | Risks, known limits and technical debt, each with what would remove it. | 11 |

- Context and scope are `README.md` and the generated context diagram; they
  are written nowhere else. Building blocks are the manifests and the
  generated diagrams. Decisions have their own folder, the glossary is a
  reference.
- A topic file beside the fixed ones, `docs/explanation/<topic>.md`, holds
  explanation that users of the unit need and that fits no fixed file.
- No explanation file lists units, capabilities or connections, and none
  repeats a generated diagram by hand.
- Something that several children must obey is written as a decision or a
  reference of the parent, because those are the files a child can cite
  in its `context.md`.

## Where a file may point

These rules keep a parent small and a child understandable alone. They hold
for links in the hand-written files of a unit. Links are relative. Who is
on the other side of a capability is not written by hand; `unifold show`
and the generated diagrams say it.

| Direction | Rule |
|---|---|
| Within the unit | Free. Plain folders of the unit count as the unit. |
| Down | Only to a direct child: its folder or its `README.md`. Never into its `docs/`, its `AGENTS.md` or its code, and never to a unit below a child. |
| Up | Only from `docs/explanation/context.md`, and only to an ancestor's `README.md`, decisions and references. Each link comes with a restatement and a stamp ([writing.md](writing.md)). |
| Sideways | Never. What the unit wants from a sibling is a need in the manifest. |
| Outside the project | Full URLs. The standard is cited as `https://unifold.md`. A nested project is cited by its `README.md` only. |

## What belongs where

| You want to write down | It goes to |
|---|---|
| What a capability guarantees | `README.md`, and its `contract` for the exact definition |
| A wire format, a schema, a convention, a term | `docs/references/` |
| Why the unit exists or is cut this way | `README.md` `## Why`, long form `docs/explanation/reasoning.md` |
| A choice between options, and its reasons | `docs/decisions/` |
| A rule that holds in this unit | `docs/explanation/invariants.md`; conventions in `docs/references/conventions.md` |
| A rule that units below must follow | A decision or a reference of this unit, cited by their `context.md` |
| A decision or term from above that matters here | `docs/explanation/context.md` |
| How to do a recurring task | `docs/skills/` |
| How a newcomer gets to a first result | `docs/tutorials/` |
| Which units exist and how they connect | Nowhere by hand: the manifests and `docs/diagrams/` |

## Beside what is already there

- **Published packages.** `unifold.yaml`, `AGENTS.md` and `docs/` lie
  inside package folders. Exclude them where the build tool packs the
  folder for publication, for example with `exclude` in a `Cargo.toml`.
- **Existing decision records** in [MADR](https://adr.github.io/madr/)
  format move to `docs/decisions/` of the unit they concern. Whether
  [adr-tools](https://github.com/npryce/adr-tools) or
  [log4brains](https://github.com/thomvaill/log4brains) work on such a
  folder has not been tested.
- **Owners files.** The `owner` key names who is responsible for a unit and
  is inherited downward; a CODEOWNERS file can be written from it. A change
  to a wiring line concerns the owners of both sides.
- **Generated files in version control.** Commit them. Mark
  `docs/diagrams/*.md` and `AGENTS.md` as generated for the code host, for
  example with `linguist-generated` in `.gitattributes`, so that reviews
  fold them, and run `unifold check --fix` before a commit.

What the reference tool reports for this chapter is in [rules.md](rules.md);
how each file is written is in [writing.md](writing.md).
