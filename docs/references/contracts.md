# Contracts

A contract is the one document of a connection. Both sides of the connection name it, the tests of every consumer are written from it, and the stand-in that those tests use is defined in it. The rules of its body are in [writing.md](writing.md#contracts); this chapter describes the parts, the fake and the folder form, and holds the template.

## One document, three readers

The provider reads the contract as what it must guarantee: every part with its signature, preconditions, result and errors, and the examples as its first tests. A consumer reads it as what it may rely on, and takes from `## Fake` the stand-in its own tests use. A reviewer reads it as the one place where a change to the connection shows: when the two sides disagree, one of them disagrees with this file.

A contract is a reference: it states the connection as it is and nothing else. When the connection changes, the change rewrites the parts it touches, and the decision behind the change links the contract. The contract names no decision and gives no reasons. It holds no notes about the work, such as what is still open or what a step added. It does not describe how the provider works inside; that is an explanation of the provider.

A contract has these sections, in this order: the header, `## Use`, `## States` where the connection has state, `## Parts` and `## Fake`.

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
- The checker reads only that the section exists. `## States` makes the order exact, and the scenarios in the manifests follow it ([spec.md](spec.md), section 4).

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
- The `Pre:` of a part names the state it needs: "the session is open".
- A table that needs two machines that do not touch each other describes two connections, and becomes two contracts.

The checker reads the table, and the generated `docs/diagrams/states-<contract>.md` draws it.

## Parts

A part is one operation, event or type. The parts stand in the order in which a consumer uses them. Its heading is its name, in lower-case kebab-case, and the manifests of the units that use only some of the parts list those names under `parts`:

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
| `event` | Something the provider emits and a consumer receives | signature |
| `type` | A record, variant or resource the parts share | signature, a table of fields or cases where they need words |

The signature is a fenced code block. The notation is named once in the header; the default is [WIT](https://component-model.bytecodealliance.org/design/wit.html), the interface language of the WebAssembly component model. WIT is plain text and language-neutral, and it has records, variants, enums, `result<T, E>`, `option<T>`, `list<T>` and resources with methods. Any other notation is allowed, for example an OpenAPI fragment, a `.proto` message or a signature in the project's own language. The checker verifies that the block exists and reads nothing inside it.

Examples are inputs with expected results, one row each, named after the case and, where the source gives the vector, after the source. They are the first tests of the provider, and they are the whole behaviour of a replay fake. Boundaries on both sides of every `Pre:` and one row per error make the table complete enough that two people would write the same tests.

A type is defined once within the subtree of the unit that holds the contract. A contract that uses a type of another contract links to its definition instead of repeating it.

## The fake

`## Fake` says what stands in for this contract in the tests of its consumers. Two forms:

- **Replay.** The fake answers the calls of the examples with their expected results, follows `## States` where the contract has them, and fails every other call. A consumer that needs more than the table gives has found a gap in the contract, not in the fake.
- **Simplified.** The fake shows a strongly simplified behaviour that the section describes, with the faults it can inject: a port in memory that records writes and replays scripted reads, a clock that stands still until a test moves it. This is the form for a need of the root, where the real thing is a device, a service or the host platform.

For a contract whose provider is a `logic` unit, the section may say `the real implementation`. A consumer's tests then use the real unit, and the provider is built before its consumers.

A capability of the root has no consumer inside the project: its consumers are other projects and programs, and its `## Fake` may take any of the three forms. When the section describes a fake, the project ships that fake for the tests of its users, so a library comes with a stand-in they can test against; when it says `the real implementation`, there is none, and its users test against the real code. Either way the project's own integration tests drive the real units through a test client. Which form fits is the project's choice.

## Folders

A contract that outgrows the line limit becomes a folder: `docs/references/<topic>/index.md` holds the header, `## Use`, `## States`, `## Parts` as a list of links in the order of use, one line each, and `## Fake`. Every part is a file `<topic>/<part>.md` whose body is what a `###` section would hold. The manifests name `index.md` as the contract; a part name resolves to a heading in the file or to a file in the folder.

## Template

The template of a contract, with the outer fence shown as four backticks only here:

````markdown
# frames

Contract of `codec.frames`, the layout of a frame. Notation: wit.
Sources: proto §4

## Use

A consumer encodes a payload into a frame. The connection has no state: any part may be called at any time, also at the same time.

## Parts

### encode

Kind: query

```wit
encode: func(payload: list<u8>) -> result<frame, encode-error>;
```

Pre: `len(payload) <= MAX_PAYLOAD`.
Result: a frame whose first byte is `MAGIC_BYTE`, then the payload.
Errors: `too-long` when the payload exceeds `MAX_PAYLOAD`.
Examples:

| Case | Input | Expected |
|---|---|---|
| empty payload, proto §4.2 | `encode([])` | `1F 00` |
| one over the limit | 256 bytes | `too-long` |

### frame

Kind: type

```wit
record frame { magic: u8, payload: list<u8> }
```

| Field | Meaning |
|---|---|
| magic | always `MAGIC_BYTE` |

### encode-error

Kind: type

```wit
variant encode-error { too-long }
```

## Fake

Replays the examples. Any other call fails with `unexpected-call`. Faults it can inject: none.
````

The template is also in the `unifold` skill, with one for a contract folder.
