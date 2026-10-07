# Diagrams

Structural diagrams are generated from the [manifests](manifest.md). Nobody
draws them by hand. They are Mermaid flowcharts inside Markdown files, so they
render on common code hosts and in editors. For people who want to click
through the system, the tool also writes an interactive HTML explorer.

## The three diagrams

Each unit gets up to three files in `doc/diagrams/`:

| File | Shows | Generated for |
|---|---|---|
| `context.md` | The unit among its siblings inside its parent, with the connections that touch it. Below the picture: who provides each need and who uses each port, resolved through all levels. | every unit |
| `component.md` | The direct children of the unit and all wiring between them. | units with children |
| `architecture.md` | The unit next to its siblings, opened up three levels down. | units with children |

For the root unit, `context.md` shows the project and the outside world, and
`architecture.md` shows the whole project three levels deep.

The names `context.md` and `architecture.md` also exist as hand-written files
directly in `doc/` ([doc-folder.md](doc-folder.md)). The files in
`doc/diagrams/` are always the generated ones.

## How to read a diagram

- A box is a unit. A frame around boxes is a unit that is opened up.
- An arrow points from the side that needs something to the side that
  provides it. The label names the need; if the provider's port has another
  name, it reads `need → port`. Several connections between the same two
  boxes share one arrow.
- A rounded node is a port that the framing unit provides to the outside. A
  hexagon is a need of the framing unit.
- A dashed arrow is an alternative provider; its label carries the name of
  the alternative.
- A dashed border marks a unit with `status: planned`. A dotted box is a
  plain folder that provides something and is not a unit yet.
- The unit the diagram is about has a thick border.

In an opened-up unit, arrows end at the innermost visible unit that implements
or uses the port.

## The text below the picture

Agents read text, not pictures, and a picture cannot be searched. Every
generated file therefore carries the same information as tables:

- a breadcrumb from the root to the unit, each step linked,
- a table of the units shown, each linked to its `README.md` and to its most
  detailed diagram,
- in `context.md`, two tables with the unit's resolved neighbours: for each
  need the unit and port that finally provide it, with a link to the
  contract; for each provided port the units that finally use it.

The neighbour tables are the place where a unit can see who is on the other
side of its ports. A unit's own files never say that
([rules.md](rules.md)).

## Clicking through

The link tables work everywhere. Whether the boxes themselves can be clicked
depends on where the file is viewed. GitHub renders Mermaid inside a frame
from another address, so a relative link in a box leads nowhere there. Users
report that boxes with full URLs can be clicked, and that this has changed
more than once
([discussion](https://github.com/orgs/community/discussions/46096)). The
root manifest key `diagram-links` chooses what the generator emits:

| Value | Boxes link with | Use it when |
|---|---|---|
| `none` (default) | nothing | You do not know where the files are viewed. The tables are the navigation. |
| `relative` | relative paths | The files are viewed in editors or built into a site that keeps relative links |
| a base URL, for example `https://github.com/owner/repo/blob/HEAD` | that URL plus the path, opened in a new tab | The files are viewed on a code host |

With a base URL the links always lead to the same branch, also when the file
is viewed on another branch or in a fork.

A box links to the most detailed diagram of its unit, so that a click drills
down. Frames of opened-up units cannot carry links in Mermaid.

## The explorer

`unifold site` writes one HTML file that contains the whole model: a tree of
all units, the three diagrams of each, and the tables of ports with their
resolved providers and users. Every box, frame and table entry is clickable
and leads to that unit. Open the file in a browser, or publish it with the
project's pages. It loads the Mermaid renderer from the network. The file is
derived data and need not be committed. See [checker.md](checker.md).

## Generated files

- A generated file starts with a marker comment that begins with
  `<!-- unifold:generated`.
- Generated files MUST NOT be edited. Change the manifests and regenerate.
- Generated Markdown files are committed. They are what a reader sees when
  browsing the folder tree.
- `doc/diagrams/` MUST NOT contain hand-written files.
- The 200-line limit applies. If the architecture diagram of a unit would
  exceed it, the generator opens up fewer levels and says so in the file.
- The link rules do not apply to generated files.

The second kind of generated file is the decision index,
`doc/decisions/index.md` ([doc-folder.md](doc-folder.md)).

Regenerate after every change to a manifest, to a decision's title or
status, or to the folder tree. The [checker](checker.md) reports missing and
stale generated files.

## Hand-drawn diagrams

Some views cannot be derived from the manifests: a sequence of calls, a state
machine, a deployment layout. Draw them as Mermaid in `doc/architecture.md` or
in a reference. They MUST NOT repeat what the generated diagrams show.

In such a diagram the participants may be the unit's direct children, by
name, and things outside the unit. Show what passes between participants.
Do not show what happens inside a child.

## Linking to diagrams

`README.md` MUST link to `doc/diagrams/context.md`. `AGENTS.md` SHOULD link
to `doc/diagrams/component.md` when it exists.
