---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Describe how a contract is used and which states it has, give every hop a result, and call the standard 0.4

## Context and Problem Statement

A contract defines each of its parts well, but not how the parts are used together. A project that coding agents build with [maike](https://github.com/wackazong/maike) shows the gap:

- The label that the agents added to its contracts most often is `Order:`, 37 times, each on a single part: "draw the initialization vector once per physical connection", "timeout, stop and disconnect take priority over ordinary work".
- One contract has 16 parts. Nothing says that pairing is `begin-pairing`, then `peer-key`, then `commit-key`, and that a connection is `begin-connection`, then `iv`, then `encrypt`.
- The questions of its builder checks are mostly about the lifecycle, the order of calls and partial failure, not about what a single part does.
- None of its 34 scenarios runs along a single connection, and a fake that replays single calls cannot stand in for a connection with state.

A scenario of [0069](0069-declare-scenarios-with-hops-across-levels.md) is a story across units. Its hops have no input and no result, and `expect` says only what holds at the end. In plantwatch, 58 parts are used by no hop. How does a contract say how the connection is used, and how does a checked path through the software show what each step returns?

## Considered Options

- A table of call sequences in each contract, beside the scenarios of the manifests
- Scenarios of two uses: contract scenarios in the contract, feature scenarios in the manifest, and the states of a connection in its contract
- The order of use in words in `## Use`, the states of a connection in its contract, and one kind of scenario, in the manifest

## Decision Outcome

Chosen option: "the order of use in words, the states in the contract, one kind of scenario", because it gives a contract what was missing, how its parts are used together, without a second syntax for a path. The `## States` table makes the order checkable, and the scenarios in the manifests follow it hop by hop. A contract scenario would have been a second form of a path, written as a Markdown table instead of hops, with its own rule and its own parser. A path along one connection is a scenario of the unit that wires it. The contract stays the one document of a connection ([0038](0038-make-a-contract-the-document-of-a-connection.md)).

**A contract** has these sections, in this order:

- `## Use` says how a consumer uses the connection: in which order it calls the parts, what it does when a call fails, who may call when, and the rules that hold for every part. Where the order matters, such as for pairing or for a reconnect after a lost line, it is a numbered list of the calls, the normal path first, then each failure that changes the state. A connection without state says so: any part may be called at any time. The checker reads only that the section exists.
- `## States`, for a connection with state: a line `Start: <state>` and a table `State | Part | Result | Next`. It holds only the states that a consumer can see or must respect; the states inside the provider stay in its `runtime.md`. A result is empty for any result, `ok` for any result that is not an error, or an error case of the part. A part that a state does not list must not be called in it. A failure that the table does not name leaves the state as it is.
- `## Parts` and `## Fake`. A replay fake answers the examples and follows the states. In a contract folder, `index.md` holds every section except the parts.

A trigger in `## States` is always a part. A deadline is an event that the provider raises when the time is up, or the error of the next call, so that a scenario, which consists of calls, can follow the table.

**A scenario** stays in the manifest of the lowest unit that contains every unit it names, and gains two things:

- `given`: a list of sentences and of items `connection: state`. A connection is named as a hop names its target, `unit.capability` or a need of the holding unit. Every other connection starts in the start state of its contract.
- A hop is `caller -> target.part(input): result`. The input is optional; the result is required.

**The checker** reports a hop without a result (`N2`), a `given` that names no state of a contract with states (`N5`), and a hop that the states of its connection do not allow (`N6`), all as errors. It reports a contract without `## Use` as a warning (`C6`), and a wrong `## States` table as an error (`C7`). The sequence diagram of a scenario shows each result and, on the provider's lifeline, each state. A contract with states gets `docs/diagrams/states-<contract>.md`. The model has the input, the result and the states of each hop, the `given` of each scenario, and the states of each contract.

**The version.** A required result makes every map of 0.3 invalid. By [0063](0063-publish-a-change-policy-and-the-conditions-for-1-0.md), such a change raises the minor version, so the standard is 0.4. 0063 also asks for 30 days between two versions and 14 days in which a decision stays proposed. This decision departs from both: 0.4 follows 0.3 after six days, and it is accepted on the day it is written. As [0076](0076-call-the-standard-0-3-and-read-0-3-only.md) does for 0.3, the tool reads 0.4 only. The fix of `S1` lists what a 0.3 project changes. The package of the tool is 0.4.0, and maike requires it.

This amends [0069](0069-declare-scenarios-with-hops-across-levels.md) in the form of a hop and of a scenario, [0068](0068-give-a-contract-a-body-with-parts-and-a-fake.md) in the sections of a contract, and 0063 in the time between versions.

### Consequences

- Good: a reader of a contract learns how the connection is used before the detail of each part.
- Good: a path that a connection does not allow is an error in the map, before anyone writes code.
- Good: a contract whose `## States` needs two separate machines shows that it holds two connections.
- Good: a path has one form, the hops of a scenario in a manifest, and one rule set.
- Bad: every hop of every existing map needs a result, and every project changes `unifold: "0.3"` to `"0.4"`.
- Bad: the order of use in `## Use` is not checked. Only the `## States` table and the scenarios that follow it are.
- Bad: a replay fake has only the single calls of `Examples:` and the states to replay, and a path along one connection names units once it is a scenario in a manifest.
- Bad: the checker judges only what the tables say. Whether the states and results are those of the sources is a review question.
