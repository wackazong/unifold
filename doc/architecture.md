# Architecture of youmedoc

Why the standard looks the way it does, where its parts come from, and what
it knowingly leaves out. The decisions are listed in
[decisions/index.md](decisions/index.md).

## Reasoning

youmedoc combines existing practices and adds one mechanism of its own.

| Part | Taken from | What youmedoc changes |
|---|---|---|
| A unit described from outside (`README.md`) and from inside (`doc/`) | The blackbox and whitebox of the [arc42](https://docs.arc42.org/section-5/) building block view | The description is cut up and stored in the folder of each building block. The building block is the folder. |
| Provided ports, needs, wiring in the parent | Ports and adapters; component models with imports and exports, for example the [WebAssembly Component Model](https://component-model.bytecodealliance.org/) | Only names, kinds and summaries are declared. The precise contract stays in whatever format the code uses. |
| Three diagrams with drill-down | The zoom levels of the [C4 model](https://c4model.com/) | No fixed levels. The same three diagrams exist at every unit. They are generated. |
| Decision records | [MADR](https://adr.github.io/madr/) | Stored per unit, with numbers local to the unit. Agents propose, humans accept. |
| `AGENTS.md` per folder | The [AGENTS.md](https://agents.md/) convention | The content is fixed: the why, pointers, skills. |
| Skills | [Agent Skills](https://agentskills.io/specification) | Stored in `doc/skills/` of the unit and announced in `AGENTS.md`. |
| Where boundaries go | Domain-driven design, SOLID, test-first design | Each principle is tied to a field or a rule ([0014](decisions/0014-build-the-design-principles-into-the-rules.md)). |

The mechanism of its own is the pair of **context file and direction rules**
([0003](decisions/0003-allow-upward-links-only-in-context.md)). Hierarchical
documentation normally lets children inherit silently from parents, which
makes a child impossible to understand alone. Self-contained units normally
are flat. youmedoc keeps the hierarchy and makes the inheritance explicit in
one file per unit.

The second deliberate choice is the split between declared and written
knowledge ([0009](decisions/0009-explain-the-why-and-never-write-structure-by-hand.md)).
Structure is cheap to derive and expensive to keep correct by hand. Reasons
cannot be derived at all. So structure is declared once and generated, as
pictures for people and as tables for agents, and the written files hold
reasons, guarantees, facts and procedures.

## Invariants

- The four folders that are copied into projects (`references/youmedoc/` and
  the three skills) form a closed set under links.
- Every tool rule in the text has the same ID and meaning in the tool, and a
  test case.
- The tool derives everything from manifests and Markdown files. It never
  needs to parse code.
- No rule depends on a programming language, a build system or a code host.
- The standard obeys itself, as far as a rule can apply to a single unit.

## Known limits

- **No evidence from use.** The standard has been tried on one example
  without code, written by agents. No study has measured whether per-folder
  documentation of this kind helps agents or humans more than a single
  well-kept root file.
- **A clean check is not a correct project.** The tool compares documents
  with each other and does not judge meaning. It compares the wiring with
  the code only if the project supplies the dependencies observed in the
  code ([0019](decisions/0019-compare-the-wiring-with-dependencies-observed-in-code.md)).
- **Restatements can drift.** A value that several files repeat, in a
  context item or in the contract of a need, is kept in step by review only.
- **The volume can get out of hand.** The example has about eight
  hand-written files per unit. The rules ask for two; the rest is optional
  and should stay so.
- **The tree is the only structure.** A unit has one parent. Views that cut
  across the folder tree are hand-drawn and unchecked
  ([0010](decisions/0010-units-follow-the-code-layout.md)).
- **Needs are passed level by level.** A need used deep in the tree is
  declared at every level above it
  ([0002](decisions/0002-declare-ports-and-wire-them-in-the-parent.md)).
- **Mentions in prose are checked only in code font** (`L6`). Other mentions
  are found by review.
- **Skills are not discovered automatically** by today's agents in
  `doc/skills/`
  ([0004](decisions/0004-keep-skills-in-doc-skills-and-list-them-in-agents-md.md)).
- **Boxes are fully clickable only in the explorer.** On code hosts it
  depends on the host
  ([0005](decisions/0005-generate-diagrams-as-mermaid-with-link-tables.md)).
- **The copy is heavy for a small project**
  ([0008](decisions/0008-copy-the-standard-into-every-project.md)).
- **One repository.** Relations between repositories are external needs.
