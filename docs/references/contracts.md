# Contracts

A contract is the one document of a connection. Both sides of the connection name it, the tests of every consumer are written from it, and the stand-in that those tests use is defined in it. This chapter is the standard for its body: the header, the sections and the fake. [contract-parts.md](contract-parts.md) is the standard for the parts, and [scenarios.md](../explanation/scenarios.md#one-contract-three-readers) explains who reads a contract. The contract [host](../../examples/serial-line/docs/references/host.md) of the example serial-line has every section, and `unifold check` reads it.

A contract has these sections, in this order: the header, `## Use`, `## States` where the connection has state, `## Qualities` where the connection promises more than its parts say, `## Parts` and `## Fake`. It SHOULD have `## Use`, `## Parts` with at least one part, and `## Fake`. What the checker reads of a contract is listed in [spec-conformance.md](spec-conformance.md#5-documents); of the header it reads only `Carried by:`, and it reads nothing of what `## Use` and `## States` say. A contract that outgrows the word limit becomes a folder ([writing.md](writing.md#references-and-the-glossary)).

## The header

The `#` title is the name of the contract. Below it, the header says whose contract it is, and holds these lines, each `Name: value`:

| Line | Required | Meaning |
|---|---|---|
| `Notation:` | no | The notation of the signature blocks. Default: `wit`. It may close the sentence that says whose contract it is. |
| `Sources:` | yes | Where the facts come from, such as `proto §4`, or `none`. |
| `Binding:` | no | How the connection travels: `in-process`, `http`, `message`, `cli`, `ble`, `file`, or another word. The diagrams show it. |
| `Carried by:` | no | A link to the contract of the transport this connection rides on, such as an event stream on a message bus. A hop on this contract counts as a use of the carrier too, so the carrier's own parts appear in a scenario only where a unit uses them directly, such as a subscription or a commit. |
| `Version:` | no | The version of the contract. A contract of a capability or a need of the root SHOULD have one, and a change that breaks a consumer of such a contract SHOULD be a decision. |

## Use

`## Use` says how a consumer uses the connection: in which order it calls the parts, what it does when a call fails, who may call at the same time, and the rules that hold for every part, such as the byte order. A reader learns from it how the parts work together before the detail of each part.

```markdown
## Use

A consumer opens the session, sends frames while it is open, and closes it. One call at a time. A lost line closes the session:

1. `open`, then `send` for every frame, then `close`.
2. When `send` fails with `lost`, the session is closed: the consumer calls `open` again before the next `send`.
3. When no frame is sent for 30 seconds, the provider raises `idle` and the session is closed.
```

- Where the order matters, such as for pairing or for a reconnect after a lost line, write it as a numbered list of the calls: the normal path first, then each failure that changes the state. A single call and its result stay a row of `Examples:`.
- A connection without state says so: any part may be called at any time.
- Where `## States` exists, the table holds the order of the calls and `## Use` says only what the table cannot: who may call at the same time, units and byte order, what a consumer does after a failure.

## States

A connection with state says which states a consumer can see or must respect, and which parts move it from one to the next; the states inside the provider stay in its `docs/explanation/runtime.md`. Write them as a line `Start: <state>` and a table `State | Part | Result | Next`, one row per step that changes the state or that a state allows:

```markdown
## States

Start: closed.

| State | Part | Result | Next |
|---|---|---|---|
| closed | `open` | ok | open |
| closed | `open` | `refused` | closed |
| open | `send` | ok | open |
| open | `send` | `lost` | closed |
| open | `close` | ok | closed |
| open | `idle` | | closed |
```

- A part that a state does not list must not be used in that state. A failure that the table does not name leaves the state as it is.
- A deadline is an event that the provider raises when the time is up, such as `idle`, or the error of the next call.
- The `Pre:` of a part does not repeat the state; the table says in which states the part is allowed.
- A table that needs two machines that do not touch each other describes two connections, and becomes two contracts.

The table is for the people who implement and use the connection; no checker follows it, and a scenario does not track it. The explorer draws it as a state diagram below the table.

## Qualities

`## Qualities` holds what the connection promises beyond its parts. It SHOULD be a table `Aspect | Guarantee`, one row per aspect:

```markdown
## Qualities

| Aspect | Guarantee |
|---|---|
| latency | an upload of 500 readings is answered within 200 ms |
| concurrency | one call at a time per session |
| delivery | at least once, in order per sensor id |
```

The aspects that most connections need a word on: latency, throughput, concurrency, ordering, delivery, idempotency, timeout, availability, limits and security. Any other aspect is allowed. The quality goals of a unit's `requirements.md` may link to its rows.

## Parts

A part is one operation, event or type of the contract, a `###` heading under `## Parts`. [contract-parts.md](contract-parts.md) is the standard for the parts: their names, kinds, signatures, examples and types.

## The fake

`## Fake` says what stands in for this contract in the tests of its consumers. Three forms: a replay, a simplified behaviour, or the real implementation.

- **Replay.** The fake answers the calls of the examples with their expected results, follows `## States` where the contract has them, and fails every other call. A consumer that needs more than the table gives has found a gap in the contract, not in the fake.
- **Simplified.** A strongly simplified behaviour that the section describes, with the faults it can inject: a port in memory that replays scripted reads, a clock that stands still until a test moves it. The form for a need of the root, where the real thing is a device, a service or the host.

For a contract whose provider is a `logic` unit, the section may say `the real implementation`: a consumer's tests use the real unit, which is built first.

A capability of the root has its consumers outside the project, so its `## Fake` may take any of the three forms: a fake that the project ships for the tests of its users, or `the real implementation`, against which its users test. Either way the project's own integration tests drive the real units through a test client.
