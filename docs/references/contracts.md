# Contracts

A contract is the one document of a connection. Both sides of the connection name it, the tests of every consumer are written from it, and the stand-in that those tests use is defined in it. The rules of its body are in [writing.md](writing.md#contracts); this chapter explains them and holds the template.

## One document, three readers

The provider reads the contract as what it must guarantee: every part with its signature, preconditions, result and errors, and the examples as its first tests. A consumer reads it as what it may rely on, and takes from `## Fake` the stand-in its own tests use. A reviewer reads it as the one place where a change to the connection shows: when the two sides disagree, one of them disagrees with this file.

## Parts

A part is one operation, event or type. Its heading is its name, in lower-case kebab-case, and the manifests of the units that use only some of the parts list those names under `parts`:

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

The signature is a fenced code block. The notation is named once in the header; the default is [WIT](https://component-model.bytecodealliance.org/design/wit.html), the interface language of the WebAssembly component model, because it is plain text, language-neutral, and has records, variants, enums, `result<T, E>`, `option<T>`, `list<T>` and resources with methods. Any other notation is allowed, for example an OpenAPI fragment, a `.proto` message or a signature in the project's own language. The checker verifies that the block exists and reads nothing inside it.

Examples are inputs with expected results, one row each, named after the case and, where the source gives the vector, after the source. They are the first tests of the provider, and they are the whole behaviour of a replay fake. Boundaries on both sides of every `Pre:` and one row per error make the table complete enough that two people would write the same tests.

A type is defined once within the subtree of the unit that holds the contract. A contract that uses a type of another contract links to its definition instead of repeating it.

## The fake

`## Fake` says what stands in for this contract in the tests of its consumers. Two forms:

- **Replay.** The fake answers the calls of the examples table with their expected results and fails every other call. It cannot be wrong about anything the table does not say, which is the point: a consumer that needs more than the table gives has found a gap in the contract, not in the fake.
- **Simplified.** The fake shows a strongly simplified behaviour that the section describes, with the faults it can inject: a port in memory that records writes and replays scripted reads, a clock that stands still until a test moves it. This is the form for a need of the root, where the real thing is a device, a service or the host platform.

For a contract whose provider is a `logic` unit, the section may say `the real implementation`: the code is small, deterministic and has no side effects, and a replay fake would answer only the inputs its author foresaw. A consumer's tests then use the real unit, and whoever plans the work builds the provider first.

A capability of the root has no consumer inside the project: its consumers are other projects and programs, and its `## Fake` may take any of the three forms. When the section describes a fake, the project ships that fake for the tests of its users, so a library comes with a stand-in they can test against; when it says `the real implementation`, there is none, and its users test against the real code. Either way the project's own integration tests drive the real units through a test client. Which form fits is the project's choice.

## Folders

A contract that outgrows the line limit becomes a folder: `docs/references/<topic>/index.md` holds the header, the notation and `## Parts` as a list of links, and every part is a file `<topic>/<part>.md` whose body is what a `###` section would hold. The manifests name `index.md` as the contract; a part name resolves to a heading in the file or to a file in the folder.

## Template

The template of a contract, with the outer fence shown as four backticks only here:

````markdown
# frames

Contract of `codec.frames`, the layout of a frame. Notation: wit.
Sources: proto §4

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
