# AGENTS.md: ui

This folder is a [youmedoc](https://youmedoc.example) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `youmedoc`. From
there, `python3 doc/skills/check-docs/scripts/youmedoc.py show mobile/ui`
prints this unit with its neighbours.

## Why

The screens are the part that changes most often and for reasons that have
nothing to do with radios or servers: wording, layout, a new chart, a new
thing the owner can do. They are a unit of their own so that such a change
touches nothing else, and so that they can be built and tested against
prepared data alone.

The screens are deliberately dumb. They draw what `plant-data` holds and
hand the owner's actions to `plant-data` and `pairing`. They keep no copy,
compute no state of a plant and wait for nothing. This is what makes them
behave the same with and without a network connection. Notifications are
no exception: ui registers the phone and follows a tap to a plant, and
what it then shows comes from `plant-data`.

The main trade-off: the screens cannot be cleverer than their data. A
reading far below a threshold is not shown as a problem until an alert
exists. The owner gets one consistent answer to "does this plant need me",
and the price is that the answer can be late. The screens make up for it by
always saying how old their data is. The navigation follows from the same
question
([0001](doc/decisions/0001-the-plant-list-is-home-and-alerts-have-no-screen-of-their-own.md)).

## Read next

1. [README.md](README.md): what ui provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): ui among its
   neighbours
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/app-ui.md](doc/references/app-ui.md): the screens, the
   ways between them, and the states every screen has
6. [doc/references/plant-data.md](doc/references/plant-data.md): what the
   screens expect of `plant-data`, and the prepared data they are tested
   with
7. [doc/references/presets.md](doc/references/presets.md): threshold
   presets
8. [doc/references/glossary.md](doc/references/glossary.md): screen, state,
   mark, bar, span

## Skills

| Skill | Use it when |
|---|---|
| [ui-build-a-screen](doc/skills/ui-build-a-screen/SKILL.md) | A screen is added or changed, after its data is available through `plant-data` or `pairing` |

## Rules for work here

- A screen has no loading state for data that is on the phone. If you feel
  the need for a spinner, the data is being asked for in the wrong place.
- Never compare a reading with a threshold to colour, sort or label
  anything. Only an alert makes a plant "need" something.
- Never keep data in a screen longer than the screen lives. Observe the
  query again instead.
- Register for notifications and follow a tap; take nothing else from a
  notification. What a screen shows comes from `plant-data`.
- Every text exists in English and German. A text that is built from parts,
  such as "2 hours ago", is built by the platform's formatting, not by
  joining words.
- Times arrive in UTC. Convert to the phone's time zone at the last moment,
  for display only.
- Describe a screen in [app-ui.md](doc/references/app-ui.md) before
  building it, with all its states. A screen with an undescribed state is
  not finished.
