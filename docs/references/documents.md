# Documents

The [standard](spec.md) asks every unit for a manifest and a `README.md`. This chapter says where the rest of a unit's written knowledge goes; [writing.md](writing.md) says how each file is written, and [placement.md](placement.md) where a file may link and which file holds what. Every unit keeps its knowledge in the same places, for the people who use it, the people and agents who work on it, and the end users of the product. A project of one unit keeps all of it in its root.

## The files of a unit

```text
<unit>/
├── unifold.yaml        the manifest: what the unit provides and needs
├── README.md           required: the front page, what the unit is for and why
├── AGENTS.md           generated, at the root only: the way in for coding agents
└── docs/
    ├── tutorials/      learn: a lesson that leads to a first result
    ├── skills/         do: a procedure for a task, for people and agents
    ├── references/     look up: contracts, glossary.md, constants.md
    ├── explanation/    understand: context.md, requirements.md, reasoning.md,
    │                   invariants.md, runtime.md, deployment.md, risks.md
    └── decisions/      choices between options, with reasons; index generated
```

The checker reads the hand-written files in these places and nothing else in `docs/`. Create a file only when it has content: a leaf unit often has a `README.md`, a `context.md` and one decision.

## Four kinds of knowledge

The folders follow [Diátaxis](https://diataxis.fr). Each kind serves one thing the reader is doing and is written in its own way.

| The reader wants to | Kind | Where | How it is written |
|---|---|---|---|
| Be taught, step by step, to a first result | Learn | `docs/tutorials/` | A lesson for a stated reader. It teaches; it does not define or instruct. |
| Finish a task they already understand | Do | `docs/skills/` | A procedure in the Agent Skills format. |
| Find a fact: a contract, a term, a value | Look up | `docs/references/`, the manifest, `README.md`, the diagrams that the tool draws | Facts as they are now, complete, with examples. No reasons, no steps. |
| Know why it is so | Understand | `docs/explanation/`, `docs/decisions/` | Reasons, forces, trade-offs. No instructions, no facts that a reference states. |

A fact has one home; other files link to it. A text that teaches, instructs, states and reasons at once is four texts.

Every document but a decision describes the unit as it is now. The history is in the decisions and in version control. Plans and the progress of the work belong to the people and the process that do the work; inside the documents, the state of the work is only `status` in the manifest and the proposed decisions. A change rewrites every document it touches to the new state.

## README.md: the front page

`README.md` is the first file every reader and agent opens. It starts with `# <name>` and one paragraph: what the unit is for, and for whom. Then comes `## Why`, which is required: why the unit exists, what makes it change, why it is cut this way, and what must stay true. Its first sentence says what the unit hides because it is hard to get right or likely to change, and the section is the long form of the unit's `not`; the longer form is `docs/explanation/reasoning.md`. Any further section is the unit's choice, such as the commands to build and test it, or the installation on the front page of the project.

- A reader MUST be able to use the unit, or to provide what it needs, after reading `README.md` and the contracts that its manifest names.
- A `README.md` MUST NOT describe how the unit works inside, and SHOULD NOT name the units around it or list children, capabilities or connections: the manifest holds those, `unifold show` prints them, and the explorer draws them. What the unit does not do is `not` in the manifest.
- The template is in the `unifold` skill; `unifold init` writes it for a root that has no `README.md`. A `README.md` that a package registry publishes keeps its usual content and links to the project by full URLs.

## AGENTS.md: generated at the root

Coding agents load `AGENTS.md` when they work in a repository ([agents.md](agents.md)). The generator writes one, at the root of the project. It holds no knowledge of the project, only the way to it: the line "unifold unit; run `unifold show` here", a pointer to `README.md`, the documents and skills of the root by kind, and the unifold block with the index of units. A hand-written `AGENTS.md` at the root is never overwritten: move its content to `README.md` and `docs/`, delete it, and run `unifold check --fix`. A hand-written `AGENTS.md` below the root belongs to the project, and the checker does not read it; a generated one there is a leftover that `check --fix` removes.

## docs/explanation: the architecture of the unit

Each explanation file has the same fixed name in every unit, so that a reader and an agent find it without a search.

| File | Content |
|---|---|
| `context.md` | What the unit takes over from the units above: a link to each decision, convention or term that applies, and what it means here. |
| `requirements.md` | What the unit must achieve, for whom it is and is not, and its quality goals in order of priority. |
| `reasoning.md` | The long form of `## Why`: the forces, the trade-offs, the ideas the unit is built on, the alternatives that were rejected. |
| `invariants.md` | What must always, or never, be true inside the unit. |
| `runtime.md` | How the unit behaves while it runs: its inner states and what moves the unit from one to the next, start and stop, timing, concurrency, limits, failure. A story across several units is a scenario in the manifest. |
| `deployment.md` | Where things run, instances, volumes, what survives a restart, what is reachable from outside. |
| `risks.md` | Risks, known limits and technical debt, each with what would remove it. |

- A topic file beside the fixed ones, `docs/explanation/<topic>.md`, holds explanation that users of the unit need and that fits no fixed file.
- No explanation file lists units, capabilities or connections, and none draws by hand a diagram that the tool draws.
- What several children must obey is a decision or a reference of the parent, which a child cites in its `context.md`.

## docs/references: what a reader looks up

Most references of a unit are the contracts of the connections it wires, each a file or a folder of parts ([contracts.md](contracts.md)). Beside them:

| File | Content |
|---|---|
| `glossary.md` | The terms that have one fixed meaning inside the unit, one row each. |
| `constants.md` | The fixed values that the unit and the units below it use, one row each. |
| `<topic>.md` | A fact that several contracts or the code of the unit share and that no contract owns, such as a convention or a format. |

- A reference gives no reasons. Where a decision settled a fact, the reference may link that decision.
- A reference holds nothing about the work: no note about a step, a review or a test run, and no list of what is open or planned.
- How a unit works inside is an explanation of that unit, in `runtime.md` or `invariants.md`, not a reference.
