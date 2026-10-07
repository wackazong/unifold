# Workflows

How a youmedoc project is created and changed. The step-by-step procedures
for agents are in the [write-docs](../../skills/write-docs/SKILL.md) and
[check-docs](../../skills/check-docs/SKILL.md) skills. This chapter gives the
order of work and the reasons.

## Roles

| Who | Does |
|---|---|
| Agent | Writes and updates files, keeps manifests and wiring consistent, runs the checker and the generator, proposes decisions |
| Human | States intent, reads and corrects, accepts or rejects decisions, judges warnings |
| Owner of a unit | The human who decides for that unit. A change to a wiring line concerns the owners of both ends. |

## Design first, in small steps

The folder tree with its documents is the design. It is written before the
code and reviewed like code. It is not written all at once.

1. **Root.** Create the root unit: a manifest with `youmedoc`, the ports the
   project offers to the world and its external needs; `README.md`;
   `AGENTS.md` with the why. Copy the standard into the root with
   `youmedoc init` ([checker.md](checker.md)).
2. **Decompose one level.** Create one folder per part, in the layout the
   code will have. Give each a manifest with `status: planned`, provided
   ports and needs. Write each child without looking at its siblings: state
   what it needs, not who has it.
3. **Wire.** In the parent's manifest, connect every need to a provider. A
   need that no child can meet shows a missing unit or a missing external
   need. A provided port that nobody needs shows an unnecessary feature.
4. **Check and generate.** Run the generator and the checker until no error
   remains. Look at the diagrams. A diagram that is hard to read usually
   shows a decomposition that is hard to understand.
5. **Match.** For every wiring line, compare what the need expects with what
   the provider offers. Children are written without looking at each other,
   so this is where their texts meet for the first time (`C13`).
6. **Explain.** Write `AGENTS.md` for each unit. Record the choices that had
   alternatives as decisions with status `proposed`.
7. **Review.** A human reads the level, corrects it and accepts the
   decisions.
8. **Build one slice.** Pick one thin path through the system. For each unit
   on it: write examples into the contract of each port, turn them into
   failing tests, write the code, name the tests in `verified-by`, set
   `status: active`.
9. **Correct and widen.** The running slice shows where the documents were
   wrong. Fix them. Then decompose the next level or build the next slice.

Do not document three levels of `planned` units before the first one runs.

## Changing an interface

1. Change the manifest and `README.md` of the unit whose port changes, and
   its contract with its examples.
2. Change the wiring in its parent. If a need can no longer be met inside the
   parent, add a need to the parent and repeat one level up.
3. Run the checker. It reports every unit whose need is no longer met.
4. For every wiring line that touches the changed port, compare both ends
   again (`C13`).
5. If the change had alternatives, record a decision in the unit that owns
   the changed interface, or in the parent if it concerns two siblings.

## Changing a guarantee or a value

A limit, a default or a timing can be relied on by units that never mention
it by name.

1. Find who uses the port: `youmedoc show` on the unit lists the resolved
   users of each port.
2. Read the `## Needs` text of each user for the same value.
3. If the value is defined in a reference or decision, list the files that
   cite it with `youmedoc cited-by` and correct each restatement.
4. Record a decision if the change had alternatives.

## Changing the insides of a unit

Nothing outside the unit changes. Update `AGENTS.md`, `doc/architecture.md`,
references and skills of the unit as needed, in the same commit as the code.
If a file outside the unit must change, the change was not internal.

## Adopting youmedoc in an existing repository

Adoption proceeds one folder at a time. The project conforms at every step.
Start at level `core` ([core.md](core.md)): manifests, wiring and generated
diagrams, nothing copied. Move to the full standard when that has proved
useful.

1. Make the repository root a unit: `youmedoc init . --level core`, or
   without the option for the full standard. A project of one unit conforms.
2. Pick the few folders that others depend on most and make them units.
3. Wire them in the root. Where a need is met by a folder that is not a unit
   yet, name the folder as the provider: `billing.ledger: ./legacy/ledger`.
   The checker lists these lines (`W8`) as the remaining work.
4. Move existing documentation into the unit it describes
   ([coexistence.md](coexistence.md)).
5. Go deeper only where it helps.
6. If the build system knows the dependencies between the folders, export
   them and run `check --deps` ([checker.md](checker.md)). It shows where
   the wiring and the code disagree.

## For contributors who are not agents

A person who changes code in a youmedoc project does five things:

1. Reads the `README.md` and `AGENTS.md` of the unit they change.
2. Changes code and tests.
3. If behaviour that the `README.md` promises changed, changes the
   `README.md`; if a port was added, removed or renamed, changes the manifest
   and the parent's wiring.
4. Runs the generator and the checker.
5. Commits code, documents and regenerated files together.

A text for a project's `CONTRIBUTING.md` is among the templates of the
[write-docs](../../skills/write-docs/SKILL.md) skill.

## Moving a unit inside the project

1. Move the folder.
2. Remove its wiring lines from the old parent and add them to the new one.
3. Run the checker. `L1` reports every broken link in the unit's
   `doc/context.md`. For each one, find the corresponding item in the new
   ancestors and cite that, or record that the unit no longer inherits it.
4. Regenerate.

## Copying a unit into another project

A copied unit carries everything needed to understand it: its interface, its
reasons, its decisions, its procedures, and a restatement of what it
inherited.

1. Copy the folder.
2. In the new parent, wire the unit's needs.
3. Open `doc/context.md`. Every link is broken. For each item decide: the new
   project has an equivalent, then cite it; or it has none, then keep the
   restatement as plain text and add where it came from.
4. Run the checker and regenerate.

The copy is a fork. Later changes to the original do not reach it.
