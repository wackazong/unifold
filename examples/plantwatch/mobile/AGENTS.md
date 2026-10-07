# AGENTS.md: mobile

This folder is a [youmedoc](https://youmedoc.example) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `youmedoc`. From
there, `python3 doc/skills/check-docs/scripts/youmedoc.py show mobile`
prints this unit with its neighbours.

## Why

The app exists because a sensor stick reaches nothing but a phone: the app
carries its readings on and is the owner's window on their plants. It
changes when what the owner can see or do on the phone changes, or when iOS
or Android change what an app may do in the background.

It does three jobs that run at different moments and fail for different
reasons. The radio works only while a sensor stick is near and the operating
system lets the app run. The exchange with the server works only while there
is a network. The screens work whenever the owner looks. The app is cut
along these three rhythms, so that each job runs, fails and is tested
without the other two.

The main trade-off: everything the owner sees comes from a store on the
phone, never straight from the radio or the network
([0001](doc/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md)).
The screens are fast and work offline. The price is a second copy of the
server's data, and rules for the case that the two copies differ.

What must stay true: a reading is stored on the phone before the sensor
stick is told to forget it, and it stays there until the server has it. The
reasoning in full is in [doc/architecture.md](doc/architecture.md).

## Read next

1. [README.md](README.md): what the app provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/architecture.md](doc/architecture.md): invariants, background
   fetching, the way of a reading through the app
4. [doc/diagrams/component.md](doc/diagrams/component.md): the children and
   their wiring
5. [doc/decisions/index.md](doc/decisions/index.md): decisions
6. [doc/references/data-model.md](doc/references/data-model.md): the things
   the app handles and who may change them
7. [doc/references/platform-limits.md](doc/references/platform-limits.md):
   what iOS and Android allow in the background
8. [doc/references/app-ui.md](doc/references/app-ui.md): what the owner can
   rely on
9. [doc/references/glossary.md](doc/references/glossary.md): the app's own
   terms

## Skills

| Skill | Use it when |
|---|---|
| [mobile-add-a-screen](doc/skills/mobile-add-a-screen/SKILL.md) | The owner shall see or do something new in the app |
| [mobile-review-a-new-os-version](doc/skills/mobile-review-a-new-os-version/SKILL.md) | A new major version of iOS or Android is announced |

## Rules for work here

- What two children exchange is a port of one of them. Change the port and
  the wiring, and record a decision here. Do not let one child reach into
  another.
- Use the names of the [data model](doc/references/data-model.md) and of
  the [glossary](doc/references/glossary.md) for the things the app handles
  and does. Do not invent a second word for one of them.
- Background behaviour cannot be judged in a simulator or a debug build. The
  operating systems treat an installed release build on a real phone
  differently. Verify every change to background fetching there.
- The limits in
  [platform-limits.md](doc/references/platform-limits.md) change with every
  major release of an operating system. Treat a number from memory as
  outdated and look it up.
- Code that exists once per platform belongs to the radio part and nowhere
  else. A second place needs a new decision.
