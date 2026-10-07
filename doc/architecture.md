# Architecture of youmedoc

Why the standard looks the way it does, where its parts come from, and what
it knowingly leaves out. The decisions are listed in
[decisions/index.md](decisions/index.md).

## Reasoning

youmedoc combines existing practices and adds one mechanism of its own.

| Part | Taken from | What youmedoc changes |
|---|---|---|
| A unit described from outside (`README.md`) and from inside (`doc/`) | The blackbox and whitebox of the [arc42](https://docs.arc42.org/section-5/) building block view | The description is cut up and stored in the folder of each building block. The building block is the folder. |
| Provided ports, needs, wiring in the parent | Component models with imports and exports, for example the [WebAssembly Component Model](https://component-model.bytecodealliance.org/) | Only names, kinds and summaries are declared. The precise contract stays in whatever format the code uses. |
| Three diagrams with drill-down | The zoom levels of the [C4 model](https://c4model.com/) | No fixed levels. The same three diagrams exist at every unit. They are generated. |
| Decision records | [MADR](https://adr.github.io/madr/) | Stored per unit, with numbers local to the unit. |
| `AGENTS.md` per folder | The [AGENTS.md](https://agents.md/) convention | The content is fixed: the why, pointers, skills. |
| Skills | [Agent Skills](https://agentskills.io/specification) | Stored in `doc/skills/` of the unit and announced in `AGENTS.md`. |

The mechanism of its own is the pair of **context file and direction rules**
([0003](decisions/0003-allow-upward-links-only-in-context.md)). Hierarchical
documentation normally lets children inherit silently from parents, which
makes a child impossible to understand alone. Self-contained units normally
are flat. youmedoc keeps the hierarchy and makes the inheritance explicit in
one file per unit.

The second deliberate choice is the split between declared and written
knowledge ([0009](decisions/0009-explain-the-why-and-never-write-structure-by-hand.md)).
Structure is cheap to derive and expensive to keep correct by hand, and a
controlled study of agent context files found that overviews of structure do
not help agents find the relevant files. Reasons cannot be derived at all. So structure is
declared once and generated, and the written files hold reasons, guarantees,
facts and procedures.

## Invariants

- The four folders that are copied into projects (`references/youmedoc/` and
  the three skills) form a closed set under links.
- Every tool rule in the text has the same ID and meaning in the tool.
- The tool derives everything from manifests and Markdown files. It never
  needs to parse code.
- No rule depends on a programming language, a build system or a hosting
  platform.
- The standard obeys itself, as far as a rule can apply to a single unit.

## Known limits

These follow from the decisions and are accepted for version 0.1.

- **The tree is the only structure.** A unit has one parent. Views that cut
  across the folder tree are hand-drawn and unchecked
  ([0010](decisions/0010-units-follow-the-code-layout.md)).
- **Documents are not checked against code.** A project can conform and still
  describe software that does not exist or differs.
- **Mentions in prose are not checked by the tool.** A file can name a
  sibling without linking to it. Only review finds that.
- **Skills are not discovered automatically** by today's agents in
  `doc/skills/`. Discovery depends on the agent reading `AGENTS.md`
  ([0004](decisions/0004-keep-skills-in-doc-skills-and-list-them-in-agents-md.md)).
- **One provider per need.** Sets of simultaneous providers cannot be wired
  ([0002](decisions/0002-declare-ports-and-wire-them-in-the-parent.md)).
- **Copies of the standard can fall behind.** A project's copy is as old as
  its last update
  ([0008](decisions/0008-copy-the-standard-into-every-project.md)).
- **No evidence yet.** The standard is new. No study has measured whether
  per-folder documentation of this kind helps agents or humans more than a
  single well-kept root file.
