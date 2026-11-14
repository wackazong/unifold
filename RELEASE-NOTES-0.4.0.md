# unifold 0.4.0

Version 0.4 of the standard, with the tool that reads it. The tool reads one version: pin it in hooks and workflows, `uvx --from 'unifold==0.4.*' unifold check`.

## What is new

- **Scenarios tell stories at the level of the design.** A hop is `caller -> target.part`, with an optional note, in the direction of its part; every hop must run along a declared connection, and an included scenario of a child tells a story once per level. A scenario does not model what happens inside a call.
- **Examples are exact.** An examples table has the columns `Case | Input | Expected` (an event: `Case | Action | Emitted`), and each case has an id `<contract>#<part>/<case-slug>` that a test names.
- **From design to code.** `unifold brief` prints what to implement in a unit and what to fake. `unifold trace` lists the examples that no test names, and `unifold trace --active --strict` in a build fails when an active unit has one.
- **Contracts have fixed slots.** `## Use`, `## States`, `## Qualities`, `## Parts`, `## Fake`; the header lines `Binding:`, `Carried by:` and `Version:`; three kinds of part, `operation`, `event` and `type`, with `When:` and `Delivery:` on an event. `## States` is a table for readers, which the explorer draws.
- **Fewer generated files.** A project commits the decision indexes and one `AGENTS.md`, at the root; no diagram is a file. The explorer, `unifold explore`, draws the component, sequence and state diagrams. The root key `diagrams` is gone.
- **A smaller manifest.** `runs-as` says what a unit runs as. An entry that only passes through may be empty and takes its summary and contract from its wiring line.
- **A word limit.** 1,500 words per hand-written document, 250 for `## Why`.
- **A shorter standard.** Four pages on manifests, wiring, scenarios and generated files, six chapters on documents, 18 foundational decisions, and one procedure per task in the `unifold` skill.

## Moving a project of an earlier version

Write `unifold: "0.4"` in the root manifest, run `unifold check --fix`, and work through the findings; each names what to change and how. Then run `unifold init --agents` again to replace the installed skills and the copy of the tool.
