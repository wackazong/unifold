---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Try the standard on repositories that are not ours, with a measure agreed beforehand

## Context and Problem Statement

The first risk in [risks.md](../explanation/risks.md) is the lack of evidence from use. The standard has been tried by its authors' agents on two examples written for it. The [reasoning](../explanation/reasoning.md) cites studies of instruction files and skills, which point both ways, and says: "Whether declared and checked structure helps agents more than a well-kept root file is not measured."

[0034](0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md) withdrew the overlay examples for [ripgrep](https://github.com/BurntSushi/ripgrep) and [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) "until the standard has settled". Only trials can tell when it has settled. A standard without results from repositories that it was not written for cannot ask others to adopt it.

## Considered Options

- Wait until others adopt it and report
- Bring the overlays back as demonstrations
- Bring the overlays back as trials, and measure agents with and without the map, under a protocol that is published before the first run

## Decision Outcome

Chosen option: "trials under a published protocol", because a result counts only if its measure was fixed before the result was known.

### The repositories

- ripgrep, a Cargo workspace.
- Online Boutique, services in several languages that call each other over the network.
- A third shape that the examples do not cover: a framework application with feature folders, such as a Django project. The protocol names it.

### The conversions

- An agent converts each repository with the skill `unifold-convert`, and a person reviews the result.
- Each overlay is kept as manifests and documents only, with the commit of the upstream repository that it describes, and is checked against a checkout of that commit. The code is not copied.
- The trial records: the time to a green check; the number of units; the findings of the first check, by rule; the guesses that the agent reports; and what the reviewer corrects. The findings of the first check are the evidence for [0054](0054-make-two-claims-of-conformance-the-map-and-the-full-standard.md) and [0055](0055-report-a-link-sideways-or-deeper-as-a-warning.md).

### The comparison with agents

- The tasks come from closed issues and merged pull requests of the three repositories. Each task changes an interface between at least two units.
- Three conditions: the repository as it is; the repository with a hand-written root `AGENTS.md` of comparable effort; the repository with the unifold map.
- Every condition uses the same agent and model, at least 20 tasks, and at least three runs per task.
- Measures: success by the tests of the upstream repository; steps and tokens; files read outside the units of the task; whether `unifold check` is green after the change; whether the agent changed the map when it changed an interface.
- The protocol fixes the threshold beforehand. The proposal is: the map counts as helping when its success rate is at least that of the hand-written `AGENTS.md`, with fewer steps.

### Publication

- The protocol is written as a reference, `docs/references/trials.md`, and committed before the first run.
- The results, the logs of the runs and the overlays are published, including a result that shows no effect or a negative effect.
- The results replace the first risk in risks.md, and they are a condition of [0063](0063-publish-a-change-policy-and-the-conditions-for-1-0.md).

This amends 0034: the overlays come back now, as trials, and not after the standard has settled.

### Consequences

- Good: the first evidence from repositories that the standard was not written for.
- Good: the first check of each conversion shows which rules hurt adoption most.
- Bad: the trials cost agent runs and review time. Upstream repositories move, and overlays age.
- Bad: the authors try their own standard. Publishing the protocol before the runs, publishing the raw logs and inviting others to repeat the runs reduce that bias but do not remove it.
