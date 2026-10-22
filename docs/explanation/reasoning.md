# Reasoning behind unifold

Why the standard looks the way it does: where its parts come from, what it adds of its own, and the established ideas a reader can use to predict it. Nothing here is a rule; the rules are in the
[standard](../references/spec.md).

## Where the parts come from

| Taken from | What it is | What unifold adopts | What unifold does not replace |
| --- | --- | --- | --- |
| Ports and adapters; component models such as the [WebAssembly Component Model](https://component-model.bytecodealliance.org/), the Fuchsia component framework and TOSCA | A manifest declares what a component offers and requires, and the level above routes it | Capabilities and needs per unit, wiring in the parent, and a rule that every need is connected. Only names and one-line summaries are declared, in a file per folder ([0002](../decisions/0002-declare-ports-and-wire-them-in-the-parent.md), [0022](../decisions/0022-make-unifold-yaml-the-only-marker-of-a-unit.md)). | The runtime: unifold wires nothing when the program runs |
| Module boundary checkers such as [Tach](https://github.com/gauge-sh/tach) | Declared dependencies between modules, checked against imports | Declared dependencies compared with imports and build files, in any language; a unit does not name its providers ([0025](../decisions/0025-compare-with-code-by-default-and-draft-manifests-from-build-files.md)). Units are chosen by a person or an agent ([0034](../decisions/0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md)). | A checker per language; use one beside unifold |
| [C4](https://c4model.com/), [Structurizr](https://github.com/structurizr/structurizr), [LikeC4](https://github.com/likec4/likec4) | One central architecture model with generated diagrams in zoom levels | Diagrams that zoom from the whole to the parts, generated and never drawn: the same three at every unit with children, no fixed levels, no central model ([0005](../decisions/0005-generate-diagrams-as-mermaid-with-link-tables.md), [0029](../decisions/0029-generate-diagrams-only-for-units-with-children.md)). | A model that cuts across the folder tree |
| [arc42](https://arc42.org) | A template for architecture documentation | The blackbox and whitebox of the [building block view](https://docs.arc42.org/section-5/), cut up and stored in the folder of each block; the concerns of the explanation files, one file per concern ([0037](../decisions/0037-split-the-explanation-into-one-file-per-arc42-concern.md)). | The questions arc42 asks |
| [Diátaxis](https://diataxis.fr) | Four kinds of documentation | The kinds as the folders of `docs/`; the explanation kind has fixed file names ([0035](../decisions/0035-sort-the-docs-folder-by-diataxis.md)). | The way of writing each kind |
| [Backstage catalog](https://github.com/backstage/backstage) | YAML beside code for a portal across repositories | A YAML file beside the code that says what a folder is and what it depends on | A catalogue across repositories; keep both |
| ADRs ([MADR](https://adr.github.io/madr/)) | Decision records | The format, stored per unit with numbers local to the unit; agents propose, people accept ([0007](../decisions/0007-use-madr-with-numbers-local-to-the-unit.md)). | An existing log: its records move to `docs/decisions/` as they are |
| [AGENTS.md](https://agents.md/) | Free-text instructions for agents | One `AGENTS.md` per unit, generated: a pointer to the documents, the skills, the unit index. The why is in `README.md` ([0036](../decisions/0036-generate-agents-md-and-keep-knowledge-in-readme-and-docs.md)). | The convention: agents still read `AGENTS.md` first |
| [Agent Skills](https://agentskills.io/specification) | A format for how-to guides that agents load | The format of `docs/skills/`: the how-to kind for people and agents alike, with generated stubs where agents search ([0027](../decisions/0027-ship-one-skill-and-generate-stubs-where-agents-look.md)). | The format: a skill of a unit is a plain Agent Skill |
| Controlled language such as [ASD-STE100](https://www.asd-ste100.org/) | Rules for technical writing | One term for one thing, the present tense, the main statement first, short files. | The full rule set and its dictionary |
| Domain-driven design, SOLID, test-first design | Where boundaries go | Explained below, not enforced ([0014](../decisions/0014-build-the-design-principles-into-the-rules.md), [0031](../decisions/0031-reduce-the-rule-set-and-turn-review-rules-into-a-checklist.md)). | The practices themselves |

## What unifold adds

The first mechanism of its own is **wiring by the parent with a completeness rule**. A unit states needs and never providers; the nearest unit above must connect every need. A search during the third review found no other project that combines a manifest per folder, needs that do not name the provider, wiring by the parent, a completeness check and generated diagrams. Absence in a search is not proof.

The second is the pair of **context file and direction rules**
([0003](../decisions/0003-allow-upward-links-only-in-context.md)).
Hierarchical documentation normally lets children inherit silently from parents, which makes a child impossible to understand alone. unifold keeps the hierarchy and makes the inheritance explicit in one file per unit, with a stamp that shows when a restatement is stale
([0026](../decisions/0026-stamp-every-restatement-with-a-hash-of-its-source.md)).

A deliberate split runs through the standard: structure is declared once and generated, because it is cheap to derive and expensive to keep correct by hand; reasons are written, because they cannot be derived.

## Three principles

1. **The folder is the unit.** Units are folders of the real code layout, and a unit holds code. unifold adds no folders of its own except `docs/`. Something that several units share, such as a protocol definition, is a document in the references of the unit above them, which every side names as its contract.
2. **Knowledge points inward and downward.** A unit knows its own insides and the interfaces of its direct children. It does not know its siblings or its users; what it wants from them is a need. This keeps a parent small and lets a child be understood alone.
3. **Declare once, generate the rest.** Structure is declared in the manifest, and every picture, table and pointer is generated. Reasons are written: in `README.md`, in the explanation files and in decisions.

## Ports and adapters

| Idea | In unifold |
|---|---|
| A port that the application offers | An entry of `capabilities` |
| A port that the application requires, in its own terms | An entry of `needs`. It names the contract that it and its provider share. |
| Adapter | A unit that needs one thing and provides another, usually of a different `kind` |
| Composition root | The `wiring` of the parent |
| Test double | Another provider for the same need, as a named alternative |
| Two adapters for one port | Capabilities that name the same contract |

A unit that holds rules of the domain names its needs in the words of the domain. If such a need is met behind a network or a device, an adapter unit stands in between ([wiring](wiring.md)).

## Domain-driven design

| Idea | In unifold |
|---|---|
| Bounded context | A unit with a glossary of its own, usually near the top of the tree |
| Ubiquitous language | The glossary of that unit |
| Context map | The generated diagrams; the wiring is the list of relationships |
| Published language | The contract of a connection, a document both sides name; a language that many share lives in the references of the unit above them |
| Customer and supplier | One contract for the connection: a change to it is a change for both sides, and the checker refuses a connection whose sides disagree |
| Shared kernel | A contract in the references of the parent, named by several children |
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

- A guarantee names something that can be observed. "Fast" is not a guarantee; "answers within 200 ms for a batch of 500" is.
- A contract contains examples: inputs with expected results. They become the first tests.
- `verified-by` points at the tests that hold a unit to a contract. It is honest to leave it out. It is not honest to point it at something that does not test the capability.
- The order of work for a new capability is: example in the contract, failing test, code, then `status: active`.

## Small steps

The standard does not ask for the whole tree to be described before use. In an existing repository, start with the few units that matter most and improve the parts you touch ([first map](../tutorials/first-map.md)). A first map costs a manifest per unit and one document per connection: the contract that both sides name. In a new design, describe the root and one level, then build one thin path through the system before widening. Manifests of planned units are guesses; the first running path corrects them.

## Four kinds of documents

Diátaxis sorts documentation by what the reader is doing, and says that a text which tries to serve two of these at once serves neither.

| Kind | The reader is | In unifold |
|---|---|---|
| Tutorial | Learning, by doing | `docs/tutorials/` |
| How-to guide | Working on a task | `docs/skills/`: one format for people and agents |
| Reference | Looking something up while working | The manifest, `README.md`, `docs/references/`, the generated diagrams |
| Explanation | Studying, to understand | `README.md` `## Why`, `docs/explanation/`, `docs/decisions/` |

The standard's own documents follow the same sorting: reference chapters in `docs/references/`, this and the other explanation files in `docs/explanation/`, a tutorial in `docs/tutorials/`.

## arc42 per unit

| arc42 section | In a unit |
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

A skill alone is not enough. In an evaluation by Vercel, agents did not call an available skill in 56 % of the cases and passed 53 % of the tasks; with a compact index in `AGENTS.md` they passed all of them
([source](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)).
In another study, 58 % of the trials never called an available dependency-graph tool ([CodeCompass](https://arxiv.org/abs/2602.20048)). So there is a generated `AGENTS.md` with the index, a skill, and a tool that every agent with a shell can run.

What studies say about instruction files, and what unifold does with it:

- Context files that repeat what the code shows cost steps and money and do not raise success; files written by developers that state only what is not discoverable help a little ([Gloaguen et al.](https://arxiv.org/abs/2602.11988)). So `## Why` holds reasons and never the structure, and `AGENTS.md` holds only pointers.
- With an `AGENTS.md`, agents finished 124 pull requests with 28.6 % less run time and 16.6 % fewer output tokens; correctness was not measured ([Lulla et al.](https://arxiv.org/abs/2601.20404)).
- Skills curated by people raised success by 16.6 points, skills that the model wrote for itself lowered it by 1.3, and two or three skills worked better than four or more ([SkillsBench](https://arxiv.org/abs/2602.12670)). So a person reviews a skill before others rely on it, and a unit has few skills.
- Descriptions of the architecture cut the steps an agent needs to find its way by 33 to 44 % ([Jin](https://arxiv.org/abs/2604.13108)).

None of these studies tested unifold. Whether declared and checked structure helps agents more than a well-kept root file is not measured.

## What the principles do not decide

They do not say how big a unit is, how deep the tree goes, or which folder is a unit. That stays a judgement. Fewer, well-chosen units are better than many: a unit costs attention every time its surroundings change.
