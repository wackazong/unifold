# Contracts

A contract is the one document of a connection. Both sides of the connection name it, the tests of every consumer are written from it, and the stand-in that those tests use is defined in it. This chapter is the standard for its body: the sections, the parts, the fake and the folder form; [qualities.md](qualities.md) is the standard for `## Qualities`, and [scenarios.md](../explanation/scenarios.md#one-contract-three-readers) explains who reads a contract. [contract-example.md](contract-example.md) shows a contract written out in full.

A contract has these sections, in this order: the header, `## Use`, `## States` where the connection has state, `## Qualities` where the connection promises more than its parts say ([qualities.md](qualities.md)), `## Parts` and `## Fake`. What the checker reads of a contract is listed in [spec-conformance.md](spec-conformance.md#5-documents); it does not read the header or what `## Use` says. A contract that outgrows the word limit becomes a folder ([writing.md](writing.md#references-and-the-glossary)).

## The header

The `#` title is the name of the contract. Below it, the header says whose contract it is, and holds these lines, each `Name: value`:

| Line | Required | Meaning |
|---|---|---|
| `Notation:` | yes | The notation of the signature blocks; `wit` by default. |
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
- The checker reads only that the section exists. `## States` makes the order exact, and the scenarios in the manifests follow it ([spec-wiring.md](spec-wiring.md), section 4).

## States

A connection with state declares its states. They are the states that a consumer can see or must respect; the states inside the provider stay in its `docs/explanation/runtime.md`.

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

- `Start:` names the state of a new connection.
- A row says that the part, in this state, with this result, leads to the next state. The result is empty for any result, `ok` for any result that is not an error, or an error case that `Errors:` of the part names in code font, such as `too-long` or `Pairing Not Supported`.
- A part that a state does not list must not be called in that state. A failure that the table does not name leaves the state as it is. A success in a state that lists only failures of the part is not allowed.
- Every row names a part. A deadline is an event that the provider raises when the time is up, such as `idle`, or the error of the next call.
- The `Pre:` of a part does not repeat the state; the table says in which states the part is allowed.
- A table that needs two machines that do not touch each other describes two connections, and becomes two contracts.

The checker reads the table; `unifold states` and the explorer draw it.

## Parts

A part is one operation, event or type. The parts stand in the order in which a consumer uses them. The name of a part is the anchor of its `###` heading: the heading in lower case, with spaces as `-` and everything but letters, digits, `-` and `_` dropped; in a contract folder it is the file name without `.md`. The manifests of the units that use only some of the parts list those names under `parts`:

```yaml
needs:
  frames:
    summary: Frames for the line
    contract:
      path: ../docs/references/frames.md
      parts:
        - encode
        - frame
```

| Kind | What it is | Has |
|---|---|---|
| `command` | A call that changes something | signature, `Pre:`, `Result:`, `Errors:`, `Examples:` |
| `query` | A call that answers without changing anything | the same |
| `event` | Something the provider emits and a consumer receives | signature, `When:` (what raises it), `Delivery:` (at-most-once, at-least-once or exactly-once, and the order key), `Examples:` with the columns `Case \| Action \| Emitted`, or with `Given` before `Action` |
| `callback` | A call that the consumer implements and the provider makes, such as a plug-in hook or a handler | signature, `Pre:`, `Result:`, `Errors:`, `Examples:` |
| `type` | A record, variant or resource the parts share | signature, a table of fields or cases where they need words |

The signature is a fenced code block. The notation is named once in the header; the default is [WIT](https://component-model.bytecodealliance.org/design/wit.html), the interface language of the WebAssembly component model. WIT is plain text and language-neutral, and it has records, variants, enums, `result<T, E>`, `option<T>`, `list<T>` and resources with methods. Any other notation is allowed, for example an OpenAPI fragment, a `.proto` message or a signature in the project's own language. The checker verifies that the block exists and reads only its type names.

The `Examples:` table of a command or query has the columns `Case | Input | Expected`, or `Case | Given | Input | Expected` where a row needs a state of the connection or of a fake first, and at least one row. `Input` is a call in the notation of the signature; `Expected` is its result: a value, `ok`, or an error case that `Errors:` names. The `Case` names the row, once within the part; where a source gives the vector, name it there too (`empty payload, proto §4.2`). The id of an example is `<contract>#<part>/<case-slug>`, for example `frames#encode/empty-payload-proto-42`, with the slug formed like the anchor of a heading; a test that proves the example names the id, and `unifold trace` lists the examples that no test names ([tool.md](tool.md#brief-and-trace)). Examples are the first tests of the provider and the whole behaviour of a replay fake. Boundaries on both sides of every `Pre:` and one row per error make the table complete enough that two people would write the same tests.

A type is defined once within the subtree of the unit that holds the contract. A contract that uses a type of another contract links to its definition instead of repeating it. Remove a type no part names in its signature or links to.

## The fake

`## Fake` says what stands in for this contract in the tests of its consumers. Three forms: a replay, a simplified behaviour, or the real implementation.

- **Replay.** The fake answers the calls of the examples with their expected results, follows `## States` where the contract has them, and fails every other call. A consumer that needs more than the table gives has found a gap in the contract, not in the fake.
- **Simplified.** A strongly simplified behaviour that the section describes, with the faults it can inject: a port in memory that replays scripted reads, a clock that stands still until a test moves it. The form for a need of the root, where the real thing is a device, a service or the host.

For a contract whose provider is a `logic` unit, the section may say `the real implementation`: a consumer's tests use the real unit, which is built first.

A capability of the root has its consumers outside the project, so its `## Fake` may take any of the three forms: a fake that the project ships for the tests of its users, or `the real implementation`, against which its users test. Either way the project's own integration tests drive the real units through a test client.
