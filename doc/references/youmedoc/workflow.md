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

Small files and generated structure exist to make the human part quick.

## Design first: documents before code

The folder tree with its documents is the design. It is written before the
code and reviewed like code.

1. **Root.** Create the root unit: `README.md` with a manifest that has
   `youmedoc`, the provided ports the project offers to the world and its
   external needs; `AGENTS.md` with the why. Copy the standard into the root
   with `youmedoc init` ([checker.md](checker.md)).
2. **Decompose.** Create one folder per part, in the layout the code will
   have. Give each a `README.md` with a manifest: `status: planned`, provided
   ports, needs. Write each child without looking at its siblings: state what
   it needs, not who has it.
3. **Wire.** In the parent's manifest, connect every need to a provider. A
   need that no child can meet shows a missing unit or a missing external
   need. A provided port that nobody needs shows an unnecessary feature.
4. **Check.** Run the checker until it reports no errors. Read the warnings.
5. **Generate** the diagrams and look at them. A diagram that is hard to read
   usually shows a decomposition that is hard to understand.
6. **Explain.** Write `AGENTS.md` for each unit. Record the choices that had
   alternatives as decisions with status `proposed`. Write contracts of ports
   as references.
7. **Match.** For every wiring line, compare what the need expects with
   what the provider's `README.md` offers. Children are written without
   looking at each other, so this is where their texts meet for the first
   time. Change the side that is wrong.
8. **Repeat** steps 2 to 7 inside each child that is big enough to have
   children.
9. **Review.** A human reads the tree top down, corrects it and accepts the
   decisions.
10. **Build.** Write the code of a unit. Set its `status` to `active` when
    the code does what the documents say. Point `contract` to the real
    interface file as soon as one exists.

## Changing an interface

1. Change the manifest and `README.md` of the unit whose port changes.
2. Change the wiring in its parent. If a need can no longer be met inside the
   parent, add a need to the parent and repeat one level up.
3. Run the checker. It reports every unit whose need is no longer met.
4. Regenerate.
5. If the change had alternatives, record a decision in the unit that owns
   the changed interface, or in the parent if it concerns two siblings.

## Changing the insides of a unit

Nothing outside the unit changes. Update `AGENTS.md`, `doc/architecture.md`,
references and skills of the unit as needed. If you find that a file outside
the unit must change, the change was not internal.

## Recording a decision

1. Find the lowest unit whose insides the decision fully covers.
2. Add `doc/decisions/NNNN-short-title.md` with the next free number and
   status `proposed`.
3. Regenerate, so that the index lists it.
4. Units below that depend on the decision cite it in their
   `doc/context.md`.
5. A human sets the status to `accepted` or `rejected`.

## Adopting youmedoc in an existing repository

1. Make the repository root a unit. Its ports are what the project offers
   and needs as a whole.
2. Pick the few folders that others depend on most and make them units. Do
   not convert every folder.
3. Wire them in the root. Needs that are met by folders that are not yet
   units point at missing units. Convert those next, or mark the need
   `optional` for the time being and note it in the root `AGENTS.md`.
4. Move existing documentation into the unit it describes. Split files that
   exceed 200 lines. Convert existing decision records to MADR file names.
5. Go deeper only where it helps.

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
3. Open `doc/context.md`. Every link is broken. For each item decide:
   the new project has an equivalent, then cite it; or it has none, then keep
   the restatement as plain text and add where it came from.
4. Run the checker and regenerate.

The copy is a fork. Later changes to the original do not reach it.

## Updating the standard

Replace `doc/references/youmedoc/` and the three skills in the root unit with
the files of the new version, set `youmedoc` in the root manifest, run the
checker, and fix what the new version reports.
