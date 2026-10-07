# AGENTS.md: test-rig

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show test-rig`
prints this unit with its neighbours.

## Why

Some promises hold only if several separately built things agree: a reading
arrives once, a plant that needs attention gets one alert. Each thing can
pass its own tests while the chain is broken at a seam. The rig exists to
test the seams, and it is a unit of its own because these promises belong
to none of the things it tests. It changes when such a promise is added or
changed, or when one of the public interfaces it uses changes.

Three choices shape it. It touches only public interfaces, so its tests
survive any rewrite behind them
([0002](doc/decisions/0002-tests-observe-only-public-interfaces.md)). One
catalogue runs against a real sensor stick and a simulated device, so a
difference between the two is a finding in itself
([0001](doc/decisions/0001-one-catalogue-for-real-and-simulated-devices.md)).
And it plays the central itself instead of driving a phone
([0003](doc/decisions/0003-the-rig-is-its-own-central.md)): runs are fast
and repeatable, and nothing that happens on a phone is covered.

What must stay true: a test that cannot run is reported as skipped with a
reason. It is never dropped and never counted as passed.

## Read next

1. [README.md](README.md): what the rig provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the rig among its
   neighbours
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/test-catalogue.md](doc/references/test-catalogue.md):
   the promises under test
6. [doc/references/configurations.md](doc/references/configurations.md):
   `real` and `simulated`, settings, waiting times
7. [doc/references/test-report.md](doc/references/test-report.md): the
   contract of the report
8. [doc/references/glossary.md](doc/references/glossary.md): promise,
   stimulus, configuration, group

## Skills

| Skill | Use it when |
|---|---|
| [test-rig-add-an-end-to-end-test](doc/skills/test-rig-add-an-end-to-end-test/SKILL.md) | A promise that spans several parts shall be tested, or a tested promise changes |
| [test-rig-run-against-real-hardware](doc/skills/test-rig-run-against-real-hardware/SKILL.md) | The catalogue shall run against a real sensor stick, for example before a release |

## Rules for work here

- A test states a promise from the
  [catalogue](doc/references/test-catalogue.md). Add its entry there before
  writing the test. A test without an entry tests an implementation detail.
- Never look behind an interface to make a test easier: no database
  queries, no log files, no debug endpoints, no shared code with anything
  under test.
- The rig implements the central side from `link-profile` alone and
  builds readings from `reading-format` alone. If the rig and something
  under test disagree, first check the definition; the rig can be the one
  that is wrong.
- A run against a real sensor stick confirms its readings, and the sensor
  stick then deletes them. Never run against a sensor stick that is in
  somebody's flower pot.
- Waiting times belong in
  [configurations.md](doc/references/configurations.md). A test contains no
  waiting time of its own.
- A test that fails now and then is a failed test. Do not add a retry
  around a promise.
