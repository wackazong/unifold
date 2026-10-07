# AGENTS.md: rules

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show cloud/services/alerts/rules`
prints this unit with its neighbours.

## Why

When an alert opens and closes is the part of the product that owners
feel and that changes most. This unit holds exactly that logic and
nothing else, so that it can be read in one sitting and tested with a
table of readings and expected alerts. It changes when the rules of
judging change: a new quantity, a different margin, another way to look
at light.

To stay testable it has no state and knows no technology. What it
concluded from earlier readings travels in a value that the caller keeps.
Plant and thresholds come through a need that it states in its own words;
a test meets that need with a table ([context](doc/context.md)).

An alert must not flap when a value hovers at its threshold, and it must
not wait when a plant runs dry. Both are met by opening at the threshold
and closing only beyond a margin
([0001](doc/decisions/0001-flapping-is-prevented-by-a-margin-on-closing.md)).

Light shows why judging needs memory: a reading at night is dark for
every plant, so light is judged by the brightest reading of a day.

What must stay true: the function is deterministic, and it never asks to
open what is open.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its
   surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/evaluation.md](doc/references/evaluation.md): the
   function, the rules, the margins, the state
6. [doc/references/thresholds.md](doc/references/thresholds.md): the
   lookup that the unit expects to be given

## Skills

| Skill | Use it when |
|---|---|
| [rules-add-a-quantity](doc/skills/rules-add-a-quantity/SKILL.md) | A measured quantity that is not judged yet shall be able to open an alert |

## Rules for work here

- No clock. "Now" does not exist in this unit; the only times are those
  of readings. A rule that needs the current time belongs to the caller.
- No storage, no globals and no network. Nothing is remembered between
  two calls; not even an answer of `thresholds`.
- The need `thresholds` is of kind `library` on purpose. If judging needs
  something that lives behind a network, state it as a function in the
  words of this unit and leave the fetching to whoever provides it.
- The state has a version field. A change of its form keeps reading the
  old form, or the alerts that were open are forgotten at the next
  release.
- Every rule gets a row in the tables of the
  [evaluation reference](doc/references/evaluation.md) and a test that is
  a sequence of readings. A rule that cannot be shown as such a sequence
  is not a rule of this unit.
- A margin is in the unit of its quantity. Do not introduce a margin that
  is smaller than the resolution of the quantity.
