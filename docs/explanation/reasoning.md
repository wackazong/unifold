# Reasoning behind unifold

Why the standard looks the way it does: where its parts come from, what it adds, and the established ideas that predict it. Nothing here is a rule; the rules are in the [standard](../references/spec.md). How ports and adapters, domain-driven design, SOLID and test-first design show in it: [principles.md](principles.md).

## Where the parts come from

| Taken from | What it is | What unifold adopts | What unifold does not replace |
| --- | --- | --- | --- |
| Ports and adapters; component models such as the [WebAssembly Component Model](https://component-model.bytecodealliance.org/), the Fuchsia component framework and TOSCA | A manifest declares what a component offers and requires, and the level above routes it | Capabilities and needs per unit, wiring in the parent, and a rule that every need is connected. Only names and one-line summaries are declared, in a file per folder ([0002](../decisions/0002-needs-never-name-a-provider-the-unit-above-wires.md), [0001](../decisions/0001-a-unit-is-a-folder-with-a-manifest.md)). | The runtime: unifold wires nothing when the program runs |
| Module boundary checkers such as [Tach](https://github.com/gauge-sh/tach) | Declared dependencies between modules, checked against imports | Declared dependencies, in any language; a unit does not name its providers. Units are chosen by a person or an agent ([0016](../decisions/0016-one-tool-two-skills-and-the-way-in-for-agents.md)). | The check against imports: unifold reads no code ([0013](../decisions/0013-from-design-to-code-brief-trace-and-named-tests.md)); use such a checker beside it |
| [C4](https://c4model.com/), [Structurizr](https://github.com/structurizr/structurizr), [LikeC4](https://github.com/likec4/likec4) | One central architecture model with generated diagrams in zoom levels | Diagrams that zoom from the whole to the parts, generated and never drawn: one component diagram at every unit with children, and the explorer that zooms; no fixed levels, no central model ([0005](../decisions/0005-structure-is-generated-reasons-are-written.md)). | A model that cuts across the folder tree |
| [arc42](https://arc42.org) | A template for architecture documentation | The blackbox and whitebox of the [building block view](https://docs.arc42.org/section-5/), cut up and stored in the folder of each block; the concerns of the explanation files, one file per concern ([0006](../decisions/0006-every-unit-has-a-readme-and-docs-sorted-by-what-the-reader-does.md)). | The questions arc42 asks |
| [Diátaxis](https://diataxis.fr) | Four kinds of documentation | The kinds as the folders of `docs/`; the explanation kind has fixed file names ([0006](../decisions/0006-every-unit-has-a-readme-and-docs-sorted-by-what-the-reader-does.md)). | The way of writing each kind |
| [Backstage catalog](https://github.com/backstage/backstage) | YAML beside code for a portal across repositories | A YAML file beside the code that says what a folder is and what it depends on | A catalogue across repositories; keep both |
| ADRs ([MADR](https://adr.github.io/madr/)) | Decision records | The format, stored per unit with numbers local to the unit; agents propose, people accept ([0007](../decisions/0007-decisions-use-madr-agents-propose-people-accept.md)). | An existing log: its records move to `docs/decisions/` as they are |
| [AGENTS.md](https://agents.md/) | Free-text instructions for agents | One `AGENTS.md` at the root, generated: a pointer to the documents, the skills, the unit index. The why is in `README.md` ([0005](../decisions/0005-structure-is-generated-reasons-are-written.md)). | The convention: agents still read `AGENTS.md` first |
| [Agent Skills](https://agentskills.io/specification) | A format for how-to guides that agents load | The format of `docs/skills/`: the how-to kind for people and agents alike, with generated stubs where agents search ([0016](../decisions/0016-one-tool-two-skills-and-the-way-in-for-agents.md)). | The format: a skill of a unit is a plain Agent Skill |
| Controlled language such as [ASD-STE100](https://www.asd-ste100.org/) | Rules for technical writing | One term for one thing, short files. | The full rule set and its dictionary |
| Domain-driven design, SOLID, test-first design | Where boundaries go | Explained below, not enforced ([0010](../decisions/0010-three-kinds-of-units-carry-rules.md), [0011](../decisions/0011-the-checker-reports-what-the-standard-lists-and-only-that.md)). | The practices themselves |

## What unifold adds

The first is **wiring by the parent with a completeness rule**. A unit states needs and never providers; the nearest unit above must connect every need, with one line each, and nothing connects by an equal name. We know of no other project that combines a manifest per folder, needs that do not name the provider, wiring by the parent, a completeness check and generated diagrams; absence in a search is not proof.

The second is the **context file** ([0008](../decisions/0008-context-items-link-the-source-and-no-link-goes-sideways.md)). Hierarchical documentation usually lets children inherit silently from parents, which makes a child impossible to understand alone. unifold keeps the hierarchy and makes the inheritance explicit in one file per unit.

The third is **scenarios as checked declarations** ([0004](../decisions/0004-scenarios-are-hops-in-the-direction-of-the-call.md)). A story of the system is written as hops, each a call from a unit to a part of a contract, and the checker resolves every hop against the wiring and the contracts. A story that needs a connection nobody declared is an error; a connection that no story uses is a warning; and the sequence diagram is generated, so it cannot disagree with the map. Sequence diagrams exist in every architecture method; here they are derived from declarations that a tool checks, across levels of the tree.

## Three principles

1. **The folder is the unit.** Units are folders of the real code layout, and a unit holds code. unifold adds no folders of its own except `docs/`. Something that several units share, such as a protocol definition, is a document in the references of the unit above them, which every side names as its contract.
2. **Knowledge points inward and downward.** A unit knows its own insides and the interfaces of its direct children. It does not know its siblings or its users; what it wants from them is a need. This keeps a parent small and lets a child be understood alone.
3. **Declare once, generate the rest.** Structure is declared in the manifests, and every picture, table and pointer is generated: structure is cheap to derive and expensive to keep correct by hand. Reasons are written, in `README.md`, the explanation files and the decisions, because they cannot be derived.

## Why three ways in for agents

A skill alone is not enough. In an evaluation by Vercel, agents did not call an available skill in 56 % of the cases and passed 53 % of the tasks; with a compact index in `AGENTS.md` they passed all of them ([source](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)). In another study, 58 % of the trials never called an available dependency-graph tool ([CodeCompass](https://arxiv.org/abs/2602.20048)). So there is a generated `AGENTS.md` with the index, a skill, and a tool that every agent with a shell can run.

What studies say about instruction files, and what unifold does with it:

- Context files that repeat what the code shows cost steps and money and do not raise success; files written by developers that state only what is not discoverable help a little ([Gloaguen et al.](https://arxiv.org/abs/2602.11988)). So `## Why` holds reasons and never the structure, and `AGENTS.md` holds only pointers.
- With an `AGENTS.md`, agents finished 124 pull requests with 28.6 % less run time and 16.6 % fewer output tokens; correctness was not measured ([Lulla et al.](https://arxiv.org/abs/2601.20404)).
- Skills curated by people raised success by 16.6 points, skills that the model wrote for itself lowered it by 1.3, and two or three skills worked better than four or more ([SkillsBench](https://arxiv.org/abs/2602.12670)). So a person reviews a skill before others rely on it, and a unit has few skills.
- Descriptions of the architecture cut the steps an agent needs to find its way by 33 to 44 % ([Jin](https://arxiv.org/abs/2604.13108)).

None of these studies tested unifold. Whether declared and checked structure helps agents more than a well-kept root file is not measured.
