# AGENTS.md: plant-lookup

This folder is a [youmedoc](https://youmedoc.example) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `youmedoc`. From
there, `python3 doc/skills/check-docs/scripts/youmedoc.py show cloud/services/alerts/plant-lookup`
prints this unit with its neighbours.

## Why

The logic that judges a reading must not know that thresholds live behind a
network. This unit exists to hold that knowledge in one place: the path of
the request, the time limit, the repeats, the meaning of each status and how
long an answer may be reused. It changes when the way the registry of plants
is reached changes, and for no other reason.

It is cut as an adapter with a plain function on one side and HTTP on the
other, so that its caller can be tested with a stand-in that returns fixed
answers, and so that a different source of thresholds replaces this unit and
nothing else.

The one real choice is what to do between asking every time and answering
from memory. Answers are kept for at most 60 seconds, and an outage of the
registry yields `unavailable` instead of an old answer
([0001](doc/decisions/0001-keep-an-answer-for-at-most-60-seconds.md)).
A late alert is better than an alert judged by thresholds that the owner has
already changed.

What must stay true: no answer is older than 60 seconds, and no failure
reaches the caller as anything but `unavailable`.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its
   surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/thresholds.md](doc/references/thresholds.md): the
   function, how answers of the registry are mapped, the kept answers

## Rules for work here

- No logic about readings, alerts or quantities. This unit passes
  thresholds on and compares nothing with them.
- Never return a kept answer that is older than 60 seconds, not even as a
  fallback.
- Never keep `unavailable`. The next call asks again.
- Map a status you do not know to `unavailable`, never to `unattached`. A
  wrong `unattached` drops a reading from evaluation for good.
- The names of the function and of its answers are part of the port. Do not
  change them here alone.
