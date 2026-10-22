# Reasoning behind unifold

Why the standard looks the way it does: where its parts come from, what it
adds of its own, and the established ideas a reader can use to predict it.
Nothing here is a rule; the rules are in the
[standard](../references/unifold/spec.md).

## Where the parts come from

| Part | Taken from | What unifold changes |
|---|---|---|
| Capabilities, needs, wiring in the parent | Ports and adapters; component models such as the [WebAssembly Component Model](https://component-model.bytecodealliance.org/), the Fuchsia component framework and TOSCA, where a manifest declares what it offers and requires and the level above routes it | Only names and one-line summaries are declared, in a file per folder ([0002](../decisions/0002-declare-ports-and-wire-them-in-the-parent.md), [0022](../decisions/0022-make-unifold-yaml-the-only-marker-of-a-unit.md)). |
| Declared dependencies checked against code | Module boundary checkers such as [Tach](https://github.com/gauge-sh/tach) | Not tied to one language; a unit does not name its providers; the parent must connect every need ([0025](../decisions/0025-compare-with-code-by-default-and-draft-manifests-from-build-files.md)). The units are chosen by a person or an agent, never derived by a script ([0034](../decisions/0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md)). |
| Diagrams with drill-down | The zoom levels of the [C4 model](https://c4model.com/) | No fixed levels, no central model. The same diagrams exist at every unit with children and are generated ([0005](../decisions/0005-generate-diagrams-as-mermaid-with-link-tables.md), [0029](../decisions/0029-generate-diagrams-only-for-units-with-children.md)). |
| A unit described from outside and from inside | Blackbox and whitebox in the [arc42](https://docs.arc42.org/section-5/) building block view | The description is cut up and stored in the folder of each building block. |
| The explanation files of a unit | The sections of arc42 | Cut down to what the manifests and diagrams do not say, one file per concern, in every unit ([0037](../decisions/0037-split-the-explanation-into-one-file-per-arc42-concern.md)). |
| Four kinds of documents | [Diátaxis](https://diataxis.fr) | The kinds are folders of the unit; the explanation kind has fixed file names ([0035](../decisions/0035-sort-the-docs-folder-by-diataxis.md)). |
| Decision records | [MADR](https://adr.github.io/madr/) | Stored per unit, with numbers local to the unit. Agents propose, people accept ([0007](../decisions/0007-use-madr-with-numbers-local-to-the-unit.md)). |
| `AGENTS.md` per folder | The [AGENTS.md](https://agents.md/) convention | The file is generated: a pointer to the documents, the skills, the unit index. The why is in `README.md` ([0036](../decisions/0036-generate-agents-md-and-keep-knowledge-in-readme-and-docs.md)). |
| Skills | [Agent Skills](https://agentskills.io/specification) | A skill is the how-to kind for people and agents alike, stored in `docs/skills/` of the unit, with generated stubs where agents search ([0027](../decisions/0027-ship-one-skill-and-generate-stubs-where-agents-look.md)). |
| Writing style | Controlled language such as [ASD-STE100](https://www.asd-ste100.org/) | One term for one thing, the present tense, the main statement first, short files. |
| Where boundaries go | Domain-driven design, SOLID, test-first design | Explained below, not enforced ([0014](../decisions/0014-build-the-design-principles-into-the-rules.md), [0031](../decisions/0031-reduce-the-rule-set-and-turn-review-rules-into-a-checklist.md)). |

## What unifold adds

The first mechanism of its own is **wiring by the parent with a
completeness rule**. A unit states needs and never providers; the nearest
unit above must connect every need. A search during the third review found
no other project that combines a manifest per folder, needs that do not
name the provider, wiring by the parent, a completeness check and generated
diagrams. Absence in a search is not proof.

The second is the pair of **context file and direction rules** at level
`full` ([0003](../decisions/0003-allow-upward-links-only-in-context.md)).
Hierarchical documentation normally lets children inherit silently from
parents, which makes a child impossible to understand alone. unifold keeps
the hierarchy and makes the inheritance explicit in one file per unit, with
a stamp that shows when a restatement is stale
([0026](../decisions/0026-stamp-every-restatement-with-a-hash-of-its-source.md)).

A deliberate split runs through both levels: structure is declared once
and generated, because it is cheap to derive and expensive to keep correct
by hand; reasons are written, because they cannot be derived.

## Three principles

1. **The folder is the unit.** Units are folders of the real code layout.
   unifold adds no folders of its own except `docs/`. Something that
   several units share, such as a protocol definition, is a unit with a
   folder.
2. **Knowledge points inward and downward.** A unit knows its own insides
   and the interfaces of its direct children. It does not know its
   siblings or its users; what it wants from them is a need. This keeps a
   parent small and lets a child be understood alone.
3. **Declare once, generate the rest.** Structure is declared in the
   manifest, and every picture, table and pointer is generated. Reasons
   are written: in `README.md`, in the explanation files and in decisions.

## Ports and adapters

| Idea | In unifold |
|---|---|
| A port that the application offers | An entry of `capabilities` |
| A port that the application requires, in its own terms | An entry of `needs`. It belongs to the unit that has it and MAY carry that unit's own `contract`. |
| Adapter | A unit that needs one thing and provides another, usually of a different `kind` |
| Composition root | The `wiring` of the parent |
| Test double | Another provider for the same need, as a named alternative |
| Two adapters for one port | Capabilities that say `conforms-to` the same definition |

A unit that holds rules of the domain names its needs in the words of the
domain. If such a need is met behind a network or a device, an adapter
unit stands in between ([wiring](wiring.md)).

## Domain-driven design

| Idea | In unifold |
|---|---|
| Bounded context | A unit with a glossary of its own, usually near the top of the tree |
| Ubiquitous language | The glossary of that unit |
| Context map | The generated diagrams; the wiring is the list of relationships |
| Published language | A capability with a `contract`; for a language that many share, a unit that provides the definition |
| Customer and supplier | A need with its own `contract`: the user states what it requires |
| Conformist | A need without a contract that takes the provider's definition as it is |
| Anticorruption layer | An adapter unit |

## SOLID

| Principle | Where it shows |
|---|---|
| Single responsibility | `## Why` in `README.md` states the one reason the unit exists. A summary that needs "and" to join unrelated things suggests a split. |
| Open for extension | New behaviour arrives as a new unit or a new provider. The wiring changes; the users do not. |
| Substitution | Every alternative meets all that the need expects. |
| Interface segregation | Several narrow capabilities instead of one that every user depends on in full. |
| Dependency inversion | A unit depends on its needs, which it states itself. It never names a provider. |
| Acyclic dependencies | Children of one unit should not need each other in a circle. |

## Test first

- A guarantee names something that can be observed. "Fast" is not a
  guarantee; "answers within 200 ms for a batch of 500" is.
- A contract contains examples: inputs with expected results. They become
  the first tests.
- `verified-by` points at the tests that hold a unit to a contract. It is
  honest to leave it out. It is not honest to point it at something that
  does not test the capability.
- The order of work for a new capability is: example in the contract,
  failing test, code, then `status: active`.

## Small steps

The standard does not ask for the whole tree to be described before use.
In an existing repository, start with the few units that matter most and
improve the parts you touch ([first map](../tutorials/first-map.md)). In a
new design, describe the root and one level, then build one thin path
through the system before widening. Manifests of planned units are
guesses; the first running path corrects them.

## Four kinds of documents

Diátaxis sorts documentation by what the reader is doing, and says that a
text which tries to serve two of these at once serves neither.

| Kind | The reader is | In unifold |
|---|---|---|
| Tutorial | Learning, by doing | `docs/tutorials/` |
| How-to guide | Working on a task | `docs/skills/`: one format for people and agents |
| Reference | Looking something up while working | The manifest, `README.md`, `docs/references/`, the generated diagrams |
| Explanation | Studying, to understand | `README.md` `## Why`, `docs/explanation/`, `docs/decisions/` |

The standard's own documents follow the same sorting: reference chapters
in `docs/references/unifold/`, this and the other explanation files in
`docs/explanation/`, a tutorial in `docs/tutorials/`.

## arc42 per unit

| arc42 section | In a unit at level `full` |
|---|---|
| 1 Introduction and goals | `docs/explanation/requirements.md`; the guarantees of each capability in `README.md` |
| 2 Constraints | From outside: `docs/explanation/context.md`. Own: `invariants.md` and `docs/references/conventions.md` |
| 3 Context and scope | `README.md` (capabilities, needs, out of scope) and the generated context diagram |
| 4 Solution strategy | `docs/explanation/reasoning.md` |
| 5 Building block view | The manifests and the generated diagrams; each child's `README.md` is its blackbox |
| 6 Runtime view | `docs/explanation/runtime.md` |
| 7 Deployment view | `docs/explanation/deployment.md` |
| 8 Crosscutting concepts | References of the unit that covers all the parts, cited by the children's `context.md` |
| 9 Architecture decisions | `docs/decisions/` |
| 10 Quality requirements | `requirements.md`, and the guarantees in `README.md` |
| 11 Risks and technical debt | `docs/explanation/risks.md` |
| 12 Glossary | `docs/references/glossary.md` |

## Why three ways in for agents

A skill alone is not enough. In an evaluation by Vercel, agents did not
call an available skill in 56 % of the cases and passed 53 % of the tasks;
with a compact index in `AGENTS.md` they passed all of them
([source](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)).
In another study, 58 % of the trials never called an available
dependency-graph tool ([CodeCompass](https://arxiv.org/abs/2602.20048)).
So there is a generated `AGENTS.md` with the index, a skill, and a tool
that every agent with a shell can run.

What studies say about instruction files, and what unifold does with it:

- Context files that repeat what the code shows cost steps and money and
  do not raise success; files written by developers that state only what
  is not discoverable help a little
  ([Gloaguen et al.](https://arxiv.org/abs/2602.11988)). So `## Why` holds
  reasons and never the structure, and `AGENTS.md` holds only pointers.
- With an `AGENTS.md`, agents finished 124 pull requests with 28.6 % less
  run time and 16.6 % fewer output tokens; correctness was not measured
  ([Lulla et al.](https://arxiv.org/abs/2601.20404)).
- Skills curated by people raised success by 16.6 points, skills that the
  model wrote for itself lowered it by 1.3, and two or three skills worked
  better than four or more
  ([SkillsBench](https://arxiv.org/abs/2602.12670)). So a person reviews a
  skill before others rely on it, and a unit has few skills.
- Descriptions of the architecture cut the steps an agent needs to find
  its way by 33 to 44 % ([Jin](https://arxiv.org/abs/2604.13108)).

None of these studies tested unifold. Whether declared and checked
structure helps agents more than a well-kept root file is not measured.

## What the principles do not decide

They do not say how big a unit is, how deep the tree goes, or which folder
is a unit. That stays a judgement. Fewer, well-chosen units are better
than many: a unit costs attention every time its surroundings change.
