# Generated files and the explorer

What the [reference tool](tool.md) writes: the generated files of a project, and the explorer, a view of the map outside the repository.

## Generated files

`check --fix` writes the files of [spec-conformance.md](spec-conformance.md#7-generated-files) and the skill stubs. It removes generated files it no longer writes, and it never overwrites a file that lacks the generated marker ([documents.md](documents.md#agentsmd-generated-at-the-root)). Links to files that do not exist are left out.

## The explorer

`unifold explore` writes the explorer and opens it in the browser: one HTML page with the unit tree, the component, context and architecture diagram of every unit with its tables, every document of every unit, and a page per scenario with its sequence diagram, its lifelines and its steps, and its path on the map. No diagram is a file of the project; the explorer is the one place where they are drawn. Without `-o` the page goes to the temporary folder of the system, outside the repository; `-o FILE` or `-o DIR` writes it where a project publishes it, `--no-open` leaves the browser closed, and `--mermaid URL` or `--mermaid FILE` takes Mermaid from another address, or embeds a local copy so that the page works offline.

A component diagram shows the children of the unit, each with its responsibility, kind and `runs-as`; an arrow points from what needs to what provides; a need of the unit to which three or more children pass up is listed once below the picture; a `planned` unit is marked.

A scenario diagram:

- **Lifelines.** Each lifeline shows its name, its kind and what it runs as, at the top, and again at the bottom when the picture has more than 24 arrows and notes. A table below the steps says what each lifeline does.
- **Steps.** Each hop is one arrow, in order, from its caller to its target as the hop is written: an operation with a solid arrowhead, an event with an open one. The arrow carries the number of the step, the part and the note. A step wider than 34 characters wraps at a space.
- **Includes.** An included scenario is a shaded block with its name, its hops rewritten to the names of this level, end to end across levels. The tab `folded` shows each include as one step instead, `scenario <unit>.<name> (<n> steps)`, numbered with the range of its steps in the table, so that the picture shows one level: an arrow from the caller of its first step, with an open arrowhead when that step is an event, or a note on the unit when that caller lies inside the unit.
- **Expectation.** A note at the end holds what the scenario expects.

A state diagram stands below the `## States` table on the page of its contract. It shows every row of the table: a part that leaves the state as it is stands inside the state's box, and a part that moves it stands on the arrow to the next state.
