---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Add a command that writes a connection through every level

## Context and Problem Statement

Every connection is written out ([0032](0032-write-every-unit-out-in-the-wiring.md), [0048](0048-write-every-connection-out-and-let-a-unit-wire-its-own-need.md)). A need that is used deep in the tree costs a need and a line at every level on the way up, and a capability that is provided deep in the tree costs a capability and a line at every level on the way to the common ancestor. In plantwatch, the need `push` of `cloud/services/alerts/notifier` reaches the push service outside the project through three manifests: `alerts` declares `push` and passes it up, `cloud` connects `alerts.push` to its need `push-service`, and the root connects `cloud.push-service` to its own need.

People and agents make these edits by hand. The fix of `W2` describes one level ("Add `alerts.push: <provider>` to the wiring"). A mistake at one level gives a cascade of `W1` and `W2` findings on the levels above.

`check --fix` cannot write wiring. A line that `--fix` chose would connect a need to a provider because the names fit, and 0048 decided that nothing connects by an equal name: a wiring line is a decision.

## Considered Options

- Keep writing every level by hand
- Let `check --fix` write a wiring line where exactly one provider fits
- A command `unifold wire` that writes every line of one connection that a person or an agent asks for, and a `W2` fix that names the command with a candidate

## Decision Outcome

Chosen option: "a command `unifold wire`", because the person or agent decides which provider meets a need, and the tool does the mechanical part on every level.

```sh
unifold wire cloud/services/alerts/notifier push --outside
unifold wire mobile/sync cloud-api cloud public-api
```

- `unifold wire USER NEED PROVIDER CAPABILITY` connects the need `NEED` of the unit `USER` to the capability `CAPABILITY` of the unit `PROVIDER`. Units are given as paths, relative to the current folder.
- `unifold wire USER NEED --outside` passes the need up to the root, where it becomes a need of the project.
- The command finds the nearest common ancestor of the two units. On the way up from the user, it declares the need in every unit between, with the summary, kind and contract of the user's need, and writes the line that passes it up. On the way up from the provider, it declares the capability in every unit between and writes the line that implements it by the child. In the common ancestor it writes the line that connects the two.
- A contract is copied only where [0052](0052-let-a-wired-need-take-the-contract-of-its-provider.md) still requires one.
- Names stay the same on every level. When a unit already has an entry of that name that is not the same need, the command stops with exit code 2 and names the entry. `--as NAME` gives the name to use above the user.
- The command edits the text of the manifests. It adds lines to the blocks `needs`, `capabilities` and `wiring`, and keeps comments and order. Where it cannot place a line, for example in a block in flow style, it changes nothing and prints the lines to add.
- `--dry-run` prints the change as a diff, and `--json` names every file and line it writes ([tool-json.md](../references/tool-json.md)).
- After writing, it runs `check` on the units it touched and prints the findings.
- The fix of `W2` names one candidate where there is exactly one: a capability of a sibling with the same contract, or else with the same name. It gives the `unifold wire` command for that candidate. `check --fix` still writes no wiring.
- The skill `unifold` tells an agent to connect with `unifold wire` and to read the diff.
- A command that removes a connection is not part of this decision.

### Consequences

- Good: one command for a connection across several levels, and no cascade of findings from a missed level.
- Good: an agent gets a command it can run, not a sentence to interpret.
- Good: the decision about the provider stays with a person or an agent.
- Bad: the tool edits hand-written YAML. A layout that the command does not expect can be damaged, and the fallback that prints lines must be tested well.
- Bad: when a connection across the whole tree is cheap, a design that needs one gets less scrutiny. The diff of `wire` still shows every level it touches.
